"""AI-модуль. Провайдер выбирается переменной AI_PROVIDER в .env."""

import config

from .base import AIClient, AIError, ChatMessage


def create_ai_client() -> AIClient:
    provider = config.AI_PROVIDER

    if provider == "stub":
        from .stub import StubClient

        return StubClient()

    if provider == "openai":
        from .openai_compatible import OpenAICompatibleClient

        return OpenAICompatibleClient(
            base_url=config.AI_BASE_URL,
            api_key=config.AI_API_KEY,
            model=config.AI_MODEL,
            timeout=config.AI_TIMEOUT,
            reasoning_effort=config.AI_REASONING_EFFORT,
        )

    if provider == "gigachat":
        from .gigachat import GigaChatClient

        return GigaChatClient(
            auth_key=config.GIGACHAT_AUTH_KEY,
            scope=config.GIGACHAT_SCOPE,
            model=config.GIGACHAT_MODEL,
            timeout=config.AI_TIMEOUT,
            ca_bundle=config.GIGACHAT_CA_BUNDLE,
            verify_ssl=config.GIGACHAT_VERIFY_SSL,
        )

    raise AIError(f"Неизвестный AI_PROVIDER: {provider!r}. Допустимо: stub, openai, gigachat")


ai_client = create_ai_client()

__all__ = ("AIClient", "AIError", "ChatMessage", "ai_client", "create_ai_client")
