import os
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider


def make_provider(name: str):
    if name == "openai":
        return OpenAIProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    if name == "deepseek":
        return DeepSeekProvider()
    raise ValueError(f"Unknown provider: {name}")
