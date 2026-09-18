from __future__ import annotations

import os
from .openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek Provider using OpenAI SDK compatible client."""

    def __init__(
        self,
        *,
        api_key_env: str = "DEEPSEEK_API_KEY",
        base_url: str | None = None,
        default_model: str = "deepseek-chat",
    ) -> None:
        resolved_base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        super().__init__(
            api_key_env=api_key_env,
            base_url=resolved_base_url,
            default_model=default_model,
        )
