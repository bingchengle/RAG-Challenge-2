"""
MySQL 连接（pymysql）。在仓库根目录 `.env` 中设置 TEDDY_MYSQL_DSN。
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from dotenv import load_dotenv

# 加载仓库根 .env
_REPO = Path(__file__).resolve().parents[3]
load_dotenv(_REPO / ".env")

import pymysql  # noqa: E402


def _parse_dsn(dsn: str) -> dict:
    """
    支持：mysql+pymysql://user:password@host:port/database
    密码中若含特殊字符，请做 URL 编码或改用环境变量分拆方式（可再扩展）。
    """
    m = re.match(
        r"^mysql\+pymysql://([^:@/]+):([^@/]*)@([^:/]+):(\d+)/(.+)$",
        dsn.strip(),
    )
    if not m:
        raise ValueError(
            "TEDDY_MYSQL_DSN 格式应为 "
            "mysql+pymysql://用户名:密码@主机:端口/库名"
        )
    user, password, host, port, database = m.groups()
    return {
        "user": unquote(user),
        "password": unquote(password),
        "host": host,
        "port": int(port),
        "database": database,
    }


def get_connection(*, database: str | None = None) -> Any:
    """
    返回 pymysql 连接。若传入 database，可覆盖 DSN 中的库名。
    """
    dsn = os.environ.get("TEDDY_MYSQL_DSN", "").strip()
    if not dsn:
        raise RuntimeError(
            "未配置 MySQL：请在仓库根目录创建 .env，设置 "
            "TEDDY_MYSQL_DSN=mysql+pymysql://用户:密码@127.0.0.1:3306/teddy_b"
        )
    kw = _parse_dsn(dsn)
    if database:
        kw["database"] = database
    kw["charset"] = "utf8mb4"
    return pymysql.connect(**kw)
