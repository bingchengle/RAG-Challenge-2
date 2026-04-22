"""从 Docling 导出的 `report` JSON 拼成长文本，供大模型或规则使用。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def iter_text_blocks(page_content: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for block in page_content.get("content", []):
        if not isinstance(block, dict):
            continue
        t = block.get("text", "")
        if t:
            out.append(t)
    return out


def flatten_report_to_text(report_data: dict, max_chars: int = 120_000) -> str:
    """正文块 + 表格（markdown），截断在 max_chars 内。"""
    parts: list[str] = []
    n = 0
    for page in report_data.get("content", []):
        for line in iter_text_blocks(page):
            if n + len(line) + 1 > max_chars:
                parts.append(line[: max(0, max_chars - n)])
                return "\n".join(parts)
            parts.append(line)
            n += len(line) + 1
    text_blob = "\n".join(parts)
    tables = report_data.get("tables") or []
    if not tables or len(text_blob) >= max_chars:
        return text_blob
    t_parts: list[str] = [text_blob, "\n\n=== 文档内表格( Markdown ) ===\n"]
    n = len(t_parts[0]) + len(t_parts[1])
    for t in tables:
        if not isinstance(t, dict):
            continue
        page = t.get("page", "")
        md = (t.get("markdown") or "").strip()
        if not md:
            continue
        block = f"\n--- page {page} ---\n{md}\n"
        if n + len(block) > max_chars:
            t_parts.append(block[: max(0, max_chars - n)])
            return "".join(t_parts)
        t_parts.append(block)
        n += len(block)
    return "".join(t_parts)


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
