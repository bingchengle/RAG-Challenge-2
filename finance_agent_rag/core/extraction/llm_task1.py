"""用智谱 GLM 从财报长文本中抽取四张表字段（JSON）。"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from json_repair import repair_json

from finance_agent_rag.core.extraction.report_identity import FileIdentity
from finance_agent_rag.core.database import schema_fields as sf
from finance_agent_rag.llm.llm_env import get_chat_client, get_default_chat_model

_SYSTEM = """你是 A 股财报数据抽取器。只输出**一个** JSON 对象，不要 markdown。
顶层键必须包含:
- "report_period": 本套报表报告期，格式如 2023Q1、2022FY、2022HY、2023Q3（与证监会格式一致，FY=年报名称对应年度、HY=半年度、Q1-Q3=季报）
- "report_year": 整数，如 2023
- "core_performance_indicators_sheet": 对象，键为列名(英文)见用户说明，无则 null
- "balance_sheet": 对象
- "cash_flow_sheet": 对象
- "income_sheet": 对象
数值用数字，增长率用小数(如 0.12 表示 12% 若原文是百分比可换算为小数，若附件要求百分数用原文数值也可)；金额单位与原文一致，尽量**万元**（与数据库 decimal 一致，若只找到亿元请*10000 为万元）。"""


def _field_catalog() -> str:
    return f"""
[core_performance 字段] {", ".join(sf.CORE_PERF)}
[balance 字段] {", ".join(sf.BALANCE)}
[cash_flow 字段] {", ".join(sf.CASH_FLOW)}
[income 字段] {", ".join(sf.INCOME)}
"""


def extract_financial_payload(
    text: str,
    identity: FileIdentity,
    stock_code: str,
    stock_abbr: str,
) -> Dict[str, Any]:
    if not (text and text.strip()):
        raise ValueError("财报文本为空，无法抽数")
    client = get_chat_client()
    model = get_default_chat_model()
    hint = identity.report_period_hint or ""
    if identity.filing_date_yyyymmdd:
        hint += f" 文件日期(上交):{identity.filing_date_yyyymmdd}"
    user = (
        f"文件名: {identity.pdf_path.name}\n"
        f"证券代码/简称(已知): {stock_code} / {stock_abbr}\n"
        f"文件侧辅助信息: {hint}\n"
        f"{_field_catalog()}\n\n"
        f"==== 财报正文（或截断）====\n{text[:100_000]}"
    )
    comp = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    raw = (comp.choices[0].message.content or "").strip() or "{}"
    data = json.loads(repair_json(raw))
    if not isinstance(data, dict):
        raise ValueError("LLM 返回非 JSON 对象")
    return data


def apply_identity_to_tables(
    data: Dict[str, Any], stock_code: str, stock_abbr: str, identity: FileIdentity
) -> Dict[str, Any]:
    """补全主键/公共字段，并在 report_period 缺失时尝试用文件推断。"""
    rp = data.get("report_period") or identity.report_period_hint
    ry = data.get("report_year")
    if rp and ry is None and isinstance(rp, str) and len(rp) >= 4 and rp[:4].isdigit():
        try:
            ry = int(rp[:4])
        except Exception:
            ry = None
    out: Dict[str, Any] = {}
    for key in (
        "core_performance_indicators_sheet",
        "balance_sheet",
        "cash_flow_sheet",
        "income_sheet",
    ):
        part = data.get(key)
        if not isinstance(part, dict):
            part = {}
        row = {**part}
        row["stock_code"] = stock_code
        row["stock_abbr"] = stock_abbr
        if rp:
            row["report_period"] = rp
        if ry is not None:
            row["report_year"] = ry
        out[key] = row
    return out
