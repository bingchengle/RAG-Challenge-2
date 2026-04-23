"""PDF/Docling 解析。`TableSerializer` 依赖 LLM 客户端，延迟导入以免任务一仅规则抽数时受 openai 版本影响。"""

from __future__ import annotations

from finance_agent_rag.core.pdf_parser.parser import JsonReportProcessor, PDFParser
from finance_agent_rag.core.pdf_parser.utils import PageTextPreparation

__all__ = [
    "PDFParser",
    "JsonReportProcessor",
    "TableSerializer",
    "PageTextPreparation",
]


def __getattr__(name: str):
    if name == "TableSerializer":
        from finance_agent_rag.core.pdf_parser.table_serialize import TableSerializer

        return TableSerializer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
