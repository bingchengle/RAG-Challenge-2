"""
大模型与向量：本工程**不调用 OpenAI 官方 API**。

- 对话：智谱 GLM（OpenAI 兼容 HTTP），需 `GLM_API_KEY` 或 `ZHIPU_API_KEY`
- 向量：BGE（如硅基流动 OpenAI 兼容），需 `BGE_API_KEY`

仍使用 pypi 包 `openai` 作为 **HTTP 客户端**（与智谱/硅基流动兼容），非 OpenAI 公司接口。
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
load_dotenv(_REPO / ".env")
load_dotenv(override=False)

ZHIPU_V4_BASE = "https://open.bigmodel.cn/api/paas/v4"
SILICONFLOW_BASE = "https://api.siliconflow.cn/v1"

_ERR_GLM = (
    "未配置智谱 GLM：请设置系统环境变量或 .env 中的 GLM_API_KEY 或 ZHIPU_API_KEY"
)
_ERR_BGE = "未配置 BGE 向量：请设置 BGE_API_KEY（及可选 BGE_BASE_URL、BGE_EMBEDDING_MODEL）"


def get_chat_client() -> OpenAI:
    key = (os.environ.get("GLM_API_KEY") or os.environ.get("ZHIPU_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(_ERR_GLM)
    base = (os.environ.get("GLM_BASE_URL") or ZHIPU_V4_BASE).rstrip("/")
    return OpenAI(api_key=key, base_url=base, timeout=120, max_retries=2)


def get_default_chat_model() -> str:
    m = (os.environ.get("GLM_MODEL") or os.environ.get("ZHIPU_CHAT_MODEL") or "").strip()
    if m:
        return m
    return "glm-4-flash"


def get_embed_client() -> OpenAI:
    key = (os.environ.get("BGE_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(_ERR_BGE)
    base = (os.environ.get("BGE_BASE_URL") or SILICONFLOW_BASE).rstrip("/")
    return OpenAI(api_key=key, base_url=base, timeout=120, max_retries=2)


def get_default_embed_model() -> str:
    m = (os.environ.get("BGE_EMBEDDING_MODEL") or os.environ.get("EMBEDDING_MODEL") or "").strip()
    if m:
        return m
    return "BAAI/bge-m3"


def use_openai_native_parse(_client: OpenAI) -> bool:
    """本仓库不使用 OpenAI 官方 `parse` 接口，一律走 JSON 模式 + 校验。"""
    return False


def get_chat_completions_url() -> str:
    custom = (os.environ.get("LLM_CHAT_COMPLETIONS_URL") or "").strip()
    if custom:
        return custom
    base = (os.environ.get("GLM_BASE_URL") or ZHIPU_V4_BASE).rstrip("/")
    return f"{base}/chat/completions"


def get_api_key_for_parallel_processor() -> str:
    k = (os.environ.get("GLM_API_KEY") or os.environ.get("ZHIPU_API_KEY") or "").strip()
    if not k:
        raise RuntimeError(_ERR_GLM)
    return k
