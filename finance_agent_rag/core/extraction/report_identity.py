"""从财报 PDF 文件名判断证券身份（由 pipeline 根据上交所/深交文件夹传入 exchange）。"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

Exchange = Literal["SH", "SZ"]


@dataclass
class FileIdentity:
    exchange: Exchange
    pdf_path: Path
    filename_code: Optional[str] = None
    filename_abbr_hint: Optional[str] = None
    report_period_hint: Optional[str] = None
    filing_date_yyyymmdd: Optional[str] = None
    filename_note: str = ""


_RE_SH = re.compile(r"^(\d{6})_(\d{8})_.+\.pdf$", re.IGNORECASE)
_RE_SZ = re.compile(
    r"^(.+?)[：:](\d{4})年(.+?)(报告(?:摘要)?)\.pdf$",
    re.IGNORECASE,
)

_PERIOD_MAP = [
    ("一季度", "Q1"),
    ("二季度", "Q2"),
    ("三季度", "Q3"),
    ("四季度", "Q4"),
    ("半年度", "HY"),
    ("年度", "FY"),
]


def _sz_fragment_to_report_period(year: str, period_zh: str) -> Optional[str]:
    for key, mark in _PERIOD_MAP:
        if key in period_zh:
            if mark in ("Q1", "Q2", "Q3", "Q4"):
                return f"{year}{mark}"
            if mark == "HY":
                return f"{year}HY"
            if mark == "FY":
                return f"{year}FY"
    return None


def parse_pdf_identity(pdf_path: Path, exchange: Exchange) -> FileIdentity:
    name = pdf_path.name
    if exchange == "SH":
        m = _RE_SH.match(name)
        if m:
            return FileIdentity(
                "SH",
                pdf_path,
                filename_code=m.group(1),
                filing_date_yyyymmdd=m.group(2),
                filename_note="sh_regex",
            )
        return FileIdentity("SH", pdf_path, filename_note="no_regex")
    m2 = _RE_SZ.match(name)
    if m2:
        abbr = m2.group(1).strip()
        y = m2.group(2)
        frag = m2.group(3)
        rp = _sz_fragment_to_report_period(y, frag)
        return FileIdentity("SZ", pdf_path, filename_abbr_hint=abbr, report_period_hint=rp, filename_note=frag)
    return FileIdentity("SZ", pdf_path, filename_note="unparsed")
