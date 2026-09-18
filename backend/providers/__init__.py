import os

from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider


def make_provider(name: str):
    if name == "openai":
        # BASE_URL cho phép trỏ tới endpoint tương thích OpenAI khác (proxy/reseller)
        # thay vì mặc định api.openai.com — dùng khi OPENAI_API_KEY không phải key OpenAI gốc.
        return OpenAIProvider(base_url=os.getenv("BASE_URL") or None)
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown provider: {name}")
