"""
研报/长文档加载。可复用 core.pdf_parser 解析 PDF，再经 splitter + vector_store 建索引。
"""
from __future__ import annotations

from pathlib import Path


def list_research_pdfs(root: Path) -> list[Path]:
    raise NotImplementedError
