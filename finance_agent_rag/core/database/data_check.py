"""
任务一：入库前校验（主键、报告期格式、四表公共字段一致）。
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional, Set

REPORT_PERIOD_RE = re.compile(r"^(\d{4})(Q[1-4]|HY|FY)$")
_TABLE_NAMES: Set[str] = {
    "core_performance_indicators_sheet",
    "balance_sheet",
    "cash_flow_sheet",
    "income_sheet",
}


def is_valid_report_period(rp: Optional[str]) -> bool:
    if not rp or not isinstance(rp, str):
        return False
    s = rp.strip()
    return bool(REPORT_PERIOD_RE.match(s))


def is_valid_stock_code(code: Optional[str]) -> bool:
    if not code or not isinstance(code, str):
        return False
    c = code.strip()
    return len(c) == 6 and c.isdigit()


def is_valid_report_year(ry: Any) -> bool:
    if ry is None:
        return True
    try:
        y = int(ry)
    except (TypeError, ValueError):
        return False
    return 1990 <= y <= 2100


def collect_payload_errors(payload: Mapping[str, Any]) -> List[str]:
    """返回可累积的错误信息列表；空列表表示可入库。"""
    err: list[str] = []
    if not payload:
        return ["payload 为空"]

    for tname in _TABLE_NAMES:
        if tname not in payload:
            err.append(f"缺少表 {tname}")
        elif not isinstance(payload[tname], dict):
            err.append(f"{tname} 不是对象")

    if err:
        return err

    rows = {k: payload[k] for k in _TABLE_NAMES if isinstance(payload.get(k), dict)}
    codes = {r.get("stock_code") for r in rows.values()}
    periods = {r.get("report_period") for r in rows.values()}
    if len(codes) > 1 or None in codes:
        err.append("四表 stock_code 不一致或缺失")
    if len(periods) > 1 or None in periods:
        err.append("四表 report_period 不一致或缺失")
    for c in codes:
        if c is not None and not is_valid_stock_code(str(c)):
            err.append(f"股票代码非法: {c!r}")
    for p in periods:
        if p is not None and not is_valid_report_period(str(p)):
            err.append(f"报告期非法: {p!r}（需如 2023Q1、2022HY、2021FY）")

    for tname, row in rows.items():
        if not is_valid_report_year(row.get("report_year")):
            err.append(f"{tname} report_year 非法")
    # 同套报表 report_year 应一致
    yvals = {r.get("report_year") for tname, r in rows.items() if r.get("report_year") is not None}
    if len(yvals) > 1:
        err.append("四表 report_year 不一致")

    return err


def check_payload_for_upsert(payload: Optional[Mapping[str, Any]] = None) -> None:
    """入库前强校验，失败时抛出 ValueError。"""
    errors = collect_payload_errors(payload or {})
    if errors:
        raise ValueError("; ".join(errors))


def run_all_checks() -> None:
    """
    全库一致性检查（预留）：可在任务一跑完后做跨行校验。
    当前仅占位，避免 import 失败。
    """
    pass
