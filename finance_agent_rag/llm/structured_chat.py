"""结构化输出：OpenAI parse 与智谱等 JSON 模式双路径。"""
from __future__ import annotations

from typing import Any, Tuple, Type

from json_repair import repair_json
from openai import OpenAI
from pydantic import BaseModel

from finance_agent_rag.llm.llm_env import use_openai_native_parse


def chat_structured_parse(
    client: OpenAI,
    model: str,
    messages: list,
    response_format: Type[BaseModel],
    temperature: float = 0.5,
    seed: Any = None,
) -> Tuple[dict, Any]:
    """
    返回 (content_dict, completion)；content 为 Pydantic model_dump。
    """
    kwargs: dict = {"model": model, "messages": messages}
    if "o3-mini" not in model:
        kwargs["temperature"] = temperature
    if seed is not None:
        kwargs["seed"] = seed

    if use_openai_native_parse(client):
        kwargs["response_format"] = response_format
        completion = client.beta.chat.completions.parse(**kwargs)
        parsed = completion.choices[0].message.parsed
        content = parsed.model_dump() if hasattr(parsed, "model_dump") else parsed.dict()
        return content, completion

    kwargs["response_format"] = {"type": "json_object"}
    try:
        completion = client.chat.completions.create(**kwargs)
    except Exception:
        kwargs.pop("seed", None)
        completion = client.chat.completions.create(**kwargs)

    raw = (completion.choices[0].message.content or "").strip() or "{}"
    text = repair_json(raw)
    obj = response_format.model_validate_json(text)
    return obj.model_dump(), completion
