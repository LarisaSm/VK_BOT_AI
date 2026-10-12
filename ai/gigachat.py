"""Клиент GigaChat (Сбер).

Ключ авторизации берётся в личном кабинете: https://developers.sber.ru/studio
Серверы GigaChat используют сертификат Минцифры. Либо укажите путь к нему
в GIGACHAT_CA_BUNDLE, либо отключите проверку: GIGACHAT_VERIFY_SSL=false.
"""

import ssl
import time
import uuid

import aiohttp

from .base import AIClient, AIError, ChatMessage

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


class GigaChatClient(AIClient):
    def __init__(
        self,
        auth_key: str,
        scope: str,
        model: str,
        timeout: float,
        ca_bundle: str = "",
        verify_ssl: bool = True,
    ) -> None:
        if not auth_key:
            raise AIError("Не задан ключ: укажите GIGACHAT_AUTH_KEY в .env")
        self.auth_key = auth_key
        self.scope = scope
        self.model = model
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        if ca_bundle:
            self.ssl: ssl.SSLContext | bool = ssl.create_default_context(cafile=ca_bundle)
        else:
            self.ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None
        self._token = ""
        self._token_expires_at = 0.0  # unix-время в секундах

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def _get_token(self) -> str:
        # Токен живёт 30 минут; обновляем его заранее, за минуту до истечения
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        headers = {
            "Authorization": f"Basic {self.auth_key}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        async with self._get_session().post(
            OAUTH_URL, data={"scope": self.scope}, headers=headers, ssl=self.ssl
        ) as resp:
            if resp.status != 200:
                raise AIError(f"Авторизация GigaChat: HTTP {resp.status}: {(await resp.text())[:500]}")
            data = await resp.json()

        self._token = data["access_token"]
        self._token_expires_at = data["expires_at"] / 1000  # приходит в миллисекундах
        return self._token

    async def generate(self, messages: list[ChatMessage]) -> str:
        try:
            token = await self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            payload = {"model": self.model, "messages": messages}
            async with self._get_session().post(
                CHAT_URL, json=payload, headers=headers, ssl=self.ssl
            ) as resp:
                if resp.status != 200:
                    raise AIError(f"GigaChat: HTTP {resp.status}: {(await resp.text())[:500]}")
                data = await resp.json()
        except aiohttp.ClientError as e:
            raise AIError(f"Не удалось подключиться к GigaChat: {e}") from e
        except TimeoutError as e:
            raise AIError(f"GigaChat не ответил за {self.timeout.total} с") from e

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            raise AIError(f"Неожиданный формат ответа: {str(data)[:500]}") from e

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
