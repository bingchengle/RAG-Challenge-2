"""将抽取结果写入四张表；主键 (stock_code, report_period) 冲突则覆盖。"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Mapping, Optional

import pymysql

from finance_agent_rag.core.database import schema_fields as sf
from finance_agent_rag.core.database.db import get_connection

_TABLE_ROWS: Dict[str, list[str]] = {
    "core_performance_indicators_sheet": sf.CORE_PERF
    + ["stock_code", "stock_abbr", "report_period", "report_year"],
    "balance_sheet": sf.BALANCE + ["stock_code", "stock_abbr", "report_period", "report_year"],
    "cash_flow_sheet": sf.CASH_FLOW + ["stock_code", "stock_abbr", "report_period", "report_year"],
    "income_sheet": sf.INCOME + ["stock_code", "stock_abbr", "report_period", "report_year"],
}


def _clean_val(v: Any) -> Any:
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float, Decimal)):
        return v
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        try:
            if "." in s or "e" in s.lower():
                return float(s)
            return int(s)
        except ValueError:
            return v
    return v


def _row_for_table(table: str, src: Mapping[str, Any]) -> Dict[str, Any]:
    allowed = set(_TABLE_ROWS[table])
    out: Dict[str, Any] = {}
    for k in allowed:
        if k not in src:
            continue
        out[k] = _clean_val(src[k])
    for str_k in ("stock_code", "stock_abbr", "report_period"):
        if str_k in out and out[str_k] is not None:
            out[str_k] = str(out[str_k]).strip() or None
    return out


def upsert_table(conn: pymysql.connections.Connection, table: str, row: Mapping[str, Any]) -> None:
    if table not in _TABLE_ROWS:
        raise ValueError(f"unknown table {table}")
    r = _row_for_table(table, row)
    if "stock_code" not in r or "report_period" not in r:
        raise ValueError("stock_code / report_period 必填")
    if r.get("stock_code") in (None, "") or r.get("report_period") in (None, ""):
        raise ValueError("stock_code / report_period 不能为空")
    cols = [c for c in _TABLE_ROWS[table] if c in r]
    vals = [r[c] for c in cols]
    if not cols:
        raise ValueError("无可写入列")
    placeholders = ", ".join(["%s"] * len(cols))
    col_sql = ", ".join(f"`{c}`" for c in cols)
    update_parts = [f"`{c}`=VALUES(`{c}`)" for c in cols if c not in ("stock_code", "report_period")]
    if not update_parts:
        update_sql = "`stock_code`=VALUES(`stock_code`)"  # 无额外列时仍合法
    else:
        update_sql = ", ".join(update_parts)
    sql = f"INSERT INTO `{table}` ({col_sql}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_sql}"
    with conn.cursor() as cur:
        cur.execute(sql, vals)


def upsert_all_tables(conn: Optional[pymysql.connections.Connection] = None, payload: Optional[dict] = None) -> None:
    """
    payload: apply_identity_to_tables 的结果，4 个键为表名，值为行 dict。
    """
    if payload is None:
        raise ValueError("payload 不能为空")
    own = False
    if conn is None:
        conn = get_connection()
        own = True
    try:
        for tname, row in payload.items():
            if tname not in _TABLE_ROWS:
                continue
            if not row.get("stock_code") or not row.get("report_period"):
                continue
            upsert_table(conn, tname, row)
        if own:
            conn.commit()
    except Exception:
        if own:
            conn.rollback()
        raise
    finally:
        if own:
            conn.close()
