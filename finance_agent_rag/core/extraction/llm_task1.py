"""
任务一抽数已改为**规则从表格抽取**（见 `rule_task1`），本模块仅保留对外的 `apply_identity_to_tables`
别名，避免旧 import 立即报错。新代码应使用 `task1_payload.apply_identity_to_tables`。
"""
from __future__ import annotations

from finance_agent_rag.core.extraction.task1_payload import apply_identity_to_tables

__all__ = ["apply_identity_to_tables"]
