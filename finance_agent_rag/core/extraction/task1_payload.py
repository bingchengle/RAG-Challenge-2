"""任务一：将抽取结果与证券身份、报告期合并为四表行（与是否使用 LLM 无关）。"""

from __future__ import annotations

from typing import Any, Dict

from finance_agent_rag.core.extraction.report_identity import FileIdentity


def apply_identity_to_tables(
    data: Dict[str, Any], stock_code: str, stock_abbr: str, identity: FileIdentity
) -> Dict[str, Any]:
    """补全主键/公共字段，并在 report_period 缺失时尝试用文件侧 hint。"""
    rp = data.get("report_period") or identity.report_period_hint
    ry = data.get("report_year")
    if rp and ry is None and isinstance(rp, str) and len(rp) >= 4 and rp[:4].isdigit():
        try:
            ry = int(rp[:4])
        except (TypeError, ValueError):
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
