from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import litellm
from litellm import completion

from .config import ModelSpec


litellm.suppress_debug_info = True


@dataclass
class GatewayResult:
    text: str
    tool_calls: list[dict[str, Any]]
    finish_reason: str | None
    usage: dict[str, Any]
    raw_response: Any


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            parts.append(_content_to_text(item))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        for key in ("text", "content", "value"):
            value = content.get(key)
            if isinstance(value, str) and value:
                return value
        return str(content)
    for attr in ("text", "content", "value"):
        value = getattr(content, attr, None)
        if isinstance(value, str) and value:
            return value
    return str(content)


def _extract_text(response: Any) -> str:
    message = response.choices[0].message
    text = _content_to_text(getattr(message, "content", None)).strip()
    if text:
        return text
    reasoning = _content_to_text(getattr(message, "reasoning_content", None)).strip()
    if reasoning:
        return reasoning
    return ""


def _extract_usage(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "dict"):
        return usage.dict()
    return {"usage": str(usage)}


def _extract_tool_calls(response: Any) -> list[dict[str, Any]]:
    message = response.choices[0].message
    tool_calls = getattr(message, "tool_calls", None) or []
    normalized: list[dict[str, Any]] = []
    for tool_call in tool_calls:
        function = getattr(tool_call, "function", None)
        normalized.append(
            {
                "id": getattr(tool_call, "id", None),
                "type": getattr(tool_call, "type", "function"),
                "function": {
                    "name": getattr(function, "name", None),
                    "arguments": getattr(function, "arguments", "{}"),
                },
            }
        )
    return normalized


class LiteLLMGateway:
    def __init__(self, api_key: str | None = None, api_base: str | None = None, temperature: float | None = None) -> None:
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature

    def generate(
        self,
        model: ModelSpec,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> GatewayResult:
        kwargs: dict[str, Any] = {
            "model": model.model_name,
            "messages": messages,
        }
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base
            if "/" not in model.model_name:
                kwargs["custom_llm_provider"] = "openai"
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if model.reasoning_effort:
            kwargs["reasoning_effort"] = model.reasoning_effort
        elif self.temperature is not None:
            kwargs["temperature"] = self.temperature
        response = completion(**kwargs)

        return GatewayResult(
            text=_extract_text(response),
            tool_calls=_extract_tool_calls(response),
            finish_reason=getattr(response.choices[0], "finish_reason", None),
            usage=_extract_usage(response),
            raw_response=response,
        )


__all__ = ["GatewayResult", "LiteLLMGateway", "litellm"]
