from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider


def make_provider(name: str):
    if name == "openai":
        return OpenAIProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown provider: {name}")
