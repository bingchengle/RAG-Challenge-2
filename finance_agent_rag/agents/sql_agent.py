"""
任务二：Text-to-SQL + 只读执行。

TODO: 基于 schema/字段说明生成 SQL，禁止写操作；对 report_period 等口径与附件3 一致。
"""
from __future__ import annotations


def build_and_run_sql(natural: str, schema_hint: str) -> tuple[str, list]:
    raise NotImplementedError
