"""Общий интерфейс для всех AI-провайдеров."""

from abc import ABC, abstractmethod
from typing import TypedDict


class ChatMessage(TypedDict):
    role: str  # "system", "user" или "assistant"
    content: str


class AIError(Exception):
    """Ошибка при обращении к AI-провайдеру."""


class AIClient(ABC):
    """Чтобы подключить нового провайдера, унаследуйте этот класс и реализуйте generate()."""

    @abstractmethod
    async def generate(self, messages: list[ChatMessage]) -> str:
        """Получает историю диалога и возвращает текст ответа модели."""

    async def close(self) -> None:
        """Освобождает ресурсы (HTTP-сессии и т.п.) при остановке бота."""
