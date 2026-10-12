"""Клиент для любого OpenAI-совместимого API.

Подходит для облачных сервисов (OpenRouter, Groq и др.) и локальных моделей
(Ollama, LM Studio): меняются только AI_BASE_URL, AI_API_KEY и AI_MODEL.
"""

import aiohttp
from vkbottle.modules import logger

from .base import AIClient, AIError, ChatMessage


class OpenAICompatibleClient(AIClient):
    def __init__(
        self, base_url: str, api_key: str, model: str, timeout: float, reasoning_effort: str = ""
    ) -> None:
        if not model:
            raise AIError("Не задана модель: укажите AI_MODEL в .env")
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def generate(self, messages: list[ChatMessage]) -> str:
        headers = {"Content-Type": "application/json"}
        # Локальным моделям (Ollama, LM Studio) ключ не нужен
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": self.model, "messages": messages}
        # Для «думающих» моделей (qwen3 и др.): none — отвечать сразу, без размышлений
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort

        try:
            async with self._get_session().post(self.url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise AIError(f"HTTP {resp.status}: {(await resp.text())[:500]}")
                data = await resp.json()
        except aiohttp.ClientError as e:
            raise AIError(f"Не удалось подключиться к {self.url}: {e}") from e
        except TimeoutError as e:
            raise AIError(f"Модель не ответила за {self.timeout.total} с") from e

        try:
            choice = data["choices"][0]
            content = choice["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            raise AIError(f"Неожиданный формат ответа: {str(data)[:500]}") from e

        if not content:
            logger.warning(
                "Модель вернула пустой ответ (finish_reason={}, usage={})",
                choice.get("finish_reason"),
                data.get("usage"),
            )
        return content

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
