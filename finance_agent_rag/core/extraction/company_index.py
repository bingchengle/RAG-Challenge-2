"""附件1 公司代码与简称索引。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_company_tuples(path: Path) -> list[tuple[str, str]]:
    """
    返回 (stock_code, stock_abbr) 列表。
    使用列位置：第2列为股票代码、第3列为 A 股简称（与赛题附件1 模板一致）。
    """
    df = pd.read_excel(path, dtype=str)
    if len(df.columns) < 3:
        raise ValueError(f"附件1 列数不足: {path}")
    code_col = df.columns[1]
    abbr_col = df.columns[2]
    out: list[tuple[str, str]] = []
    for _, row in df.iterrows():
        code = (row[code_col] or "").strip()
        abbr = (str(row[abbr_col]) or "").strip() if pd.notna(row[abbr_col]) else ""
        if not code:
            continue
        if "." in code:
            code = code.split(".")[0]
        code = code.zfill(6) if code.isdigit() and len(code) < 6 else code
        out.append((code, abbr))
    return out


def build_lookup(company_excel: Path) -> dict[str, tuple[str, str]]:
    """
    多键查找 -> (stock_code, stock_abbr)
    键：6 位代码、A股简称、简称去「股份」后。
    """
    mp: dict[str, tuple[str, str]] = {}
    for code, abbr in load_company_tuples(company_excel):
        mp[code] = (code, abbr)
        if abbr:
            mp[abbr] = (code, abbr)
            short = abbr.replace("股份", "").strip()
            if short and short not in mp:
                mp[short] = (code, abbr)
    return mp


def resolve_stock(
    lookup: dict[str, tuple[str, str]], *, by_code: Optional[str] = None, by_name: Optional[str] = None
) -> Optional[tuple[str, str]]:
    if by_code and by_code in lookup and len(by_code) == 6 and by_code.isdigit():
        return lookup[by_code]
    if not by_name:
        return None
    name = by_name.strip()
    if name in lookup:
        return lookup[name]
    n2 = name.replace("股份", "").strip()
    if n2 in lookup:
        return lookup[n2]
    return None
