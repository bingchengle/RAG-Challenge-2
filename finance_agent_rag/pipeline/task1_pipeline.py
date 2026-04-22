"""
任务一：财报 PDF → Docling 解析缓存 → 长文本 → GLM 抽数 → 校验 → MySQL UPSERT。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from finance_agent_rag import config
from finance_agent_rag.core.database import data_check, loader
from finance_agent_rag.core.extraction import llm_task1
from finance_agent_rag.core.extraction.company_index import build_lookup, resolve_stock
from finance_agent_rag.core.extraction.report_identity import Exchange, parse_pdf_identity
from finance_agent_rag.core.extraction.text_flatten import flatten_report_to_text, load_json
from finance_agent_rag.core.pdf_parser.parser import PDFParser

_log = logging.getLogger(__name__)


def _resolve_identity(
    lookup: dict[str, tuple[str, str]], exchange: Exchange, identity
) -> Optional[tuple[str, str]]:
    if exchange == "SH":
        code = identity.filename_code
        if code:
            code = code.strip().zfill(6) if code.isdigit() else code
            hit = resolve_stock(lookup, by_code=code, by_name=None)
            if hit:
                return hit
        _log.warning("上交所未从文件名解析到代码或附件1无匹配: %s", identity.pdf_path)
        return None
    name = identity.filename_abbr_hint
    if name:
        hit = resolve_stock(lookup, by_code=None, by_name=name)
        if hit:
            return hit
    _log.warning("深交所未能用简称匹配附件1: %s (hint=%s)", identity.pdf_path, name)
    return None


def _ensure_parsed_json(pdf: Path, parser: PDFParser) -> Path:
    """与 PDFParser 输出一致：{output_dir}/{pdf_stem}.json。"""
    config.PARSED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PARSED_REPORTS_DIR / f"{pdf.stem}.json"
    if out.exists():
        return out
    _log.info("解析 PDF → %s", out)
    parser.parse_and_export(input_doc_paths=[pdf])
    if not out.exists():
        raise FileNotFoundError(f"解析未生成: {out}")
    return out


def run(
    reports_sh: Optional[Path] = None,
    reports_sz: Optional[Path] = None,
    max_files: Optional[int] = None,
    *,
    only_parse: bool = False,
    skip_upsert: bool = False,
) -> int:
    """
    遍历上交所、深交所报告目录。返回成功完成的文件数（跳过/失败不累计）。

    - only_parse: 为 True 时仅 Docling 解析 + 长文本（测解析链，不调用 GLM / 库）。
    - skip_upsert: 为 True 时做抽数 + 校验但**不写** MySQL（需 GLM）。

    环境变量：TEDDY_TASK1_ONLY_PARSE=1、TEDDY_TASK1_SKIP_DB=1 与上述两参数等价（便于命令行小测）。
    """
    if os.environ.get("TEDDY_TASK1_ONLY_PARSE", "0") == "1":
        only_parse = True
    if os.environ.get("TEDDY_TASK1_SKIP_DB", "0") == "1":
        skip_upsert = True
    reports_sh = reports_sh or config.REPORTS_SH
    reports_sz = reports_sz or config.REPORTS_SZ
    lookup = build_lookup(config.COMPANY_INFO)
    parser = PDFParser(output_dir=config.PARSED_REPORTS_DIR)

    pairs: list[tuple[Exchange, Path]] = []
    for ex, root in (("SH", reports_sh), ("SZ", reports_sz)):
        if not root.exists():
            _log.warning("目录不存在，跳过: %s", root)
            continue
        for p in sorted(root.glob("*.pdf")):
            pairs.append((ex, p))

    if max_files is not None:
        pairs = pairs[: max(0, max_files)]

    ok = 0
    for ex, pdf in pairs:
        try:
            identity = parse_pdf_identity(pdf, ex)
            stock = _resolve_identity(lookup, ex, identity)
            if not stock:
                continue
            code, abbr = stock
            jpath = _ensure_parsed_json(pdf, parser)
            report_data = load_json(jpath)
            text = flatten_report_to_text(report_data)
            if only_parse:
                _log.info(
                    "only_parse: 文本长=%s 字符, json=%s", len(text), jpath
                )
                ok += 1
                continue
            raw = llm_task1.extract_financial_payload(text, identity, code, abbr)
            payload = llm_task1.apply_identity_to_tables(raw, code, abbr, identity)
            data_check.check_payload_for_upsert(payload)
            if skip_upsert:
                _log.info("skip_upsert: 校验通过，未写库")
            else:
                loader.upsert_all_tables(payload=payload)
            ok += 1
        except Exception as e:
            _log.exception("处理失败 %s: %s", pdf, e)
    return ok


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="任务一：财报抽数入库")
    p.add_argument(
        "-n", "--max-files", type=int, default=None, help="最多处理 N 个 PDF（小测）"
    )
    p.add_argument(
        "--only-parse",
        action="store_true",
        help="只跑 Docling 解析+长文本，不调用 GLM / MySQL",
    )
    p.add_argument(
        "--skip-db",
        action="store_true",
        help="抽数+校验，但不 UPSERT 到 MySQL",
    )
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(
        "processed_ok:",
        run(
            max_files=args.max_files,
            only_parse=args.only_parse,
            skip_upsert=args.skip_db,
        ),
    )
