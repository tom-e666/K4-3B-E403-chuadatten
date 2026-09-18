from __future__ import annotations

import json
import os
from typing import Any

from .base import ModelResponse, ToolCall


class OpenAIProvider:
    """OpenAI Chat Completions provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = default_model
        self._client = None   # tạo một lần rồi dùng lại: mỗi lần tạo mới là một lần bắt tay TLS

    def _get_client(self):
        """Dùng lại một client duy nhất cho cả tiến trình (giữ connection pool, đỡ bắt tay TLS mỗi lượt)."""
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install openai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self._client = OpenAI(api_key=api_key, base_url=self.base_url, timeout=timeout)
        return self._client

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
        max_tokens: int | None = None,
    ) -> ModelResponse:
        client = self._get_client()
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            args = json.loads(call.function.arguments or "{}")
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)

    def stream(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ):
        """Sinh văn bản theo từng đoạn để UI hiện chữ chạy dần thay vì đứng im chờ cả câu."""
        client = self._get_client()
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        for chunk in client.chat.completions.create(**kwargs):
            if not getattr(chunk, "choices", None):
                continue
            piece = getattr(chunk.choices[0].delta, "content", None)
            if piece:
                yield piece
