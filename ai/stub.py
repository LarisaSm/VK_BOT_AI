"""Заглушка: отвечает без AI. Удобна, чтобы проверить работу бота до выбора провайдера."""

from .base import AIClient, ChatMessage


class StubClient(AIClient):
    async def generate(self, messages: list[ChatMessage]) -> str:
        last_user_text = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        return f"AI пока не подключён. Вы написали: «{last_user_text}»"
