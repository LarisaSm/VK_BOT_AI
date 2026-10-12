"""Ответы на входящие сообщения с помощью AI."""

from collections import defaultdict, deque

from vkbottle import VKAPIError
from vkbottle.bot import BotLabeler, Message
from vkbottle.modules import logger

import config
from ai import AIError, ChatMessage, ai_client

chat_labeler = BotLabeler()

VK_MESSAGE_LIMIT = 4096
THINKING_TEXT = "⏳ Думаю…"

# История диалогов хранится в памяти и сбрасывается при перезапуске бота
_histories: defaultdict[int, deque[ChatMessage]] = defaultdict(
    lambda: deque(maxlen=config.AI_HISTORY_SIZE)
)


async def _send_thinking(message: Message) -> int | None:
    """Отправляет заглушку «Думаю…» и возвращает её id в диалоге (или None, если не вышло)."""
    try:
        sent = await message.answer(THINKING_TEXT)
    except VKAPIError as e:
        logger.warning("Не удалось отправить «Думаю…»: {}", e)
        return None
    return sent.conversation_message_id


async def _reply(message: Message, thinking_id: int | None, text: str) -> None:
    """Заменяет заглушку «Думаю…» на текст ответа. Если заменить не вышло — шлёт новым сообщением."""
    text = text[:VK_MESSAGE_LIMIT]
    if thinking_id is not None:
        try:
            await message.ctx_api.messages.edit(
                peer_id=message.peer_id,
                conversation_message_id=thinking_id,
                message=text,
            )
            return
        except VKAPIError as e:
            logger.warning("Не удалось отредактировать «Думаю…»: {}", e)
    await message.answer(text)


@chat_labeler.private_message(text=["/reset", "сброс"])
async def reset_history(message: Message) -> None:
    _histories.pop(message.from_id, None)
    await message.answer("Начинаем разговор с чистого листа 🙂")


@chat_labeler.private_message()
async def ai_answer(message: Message) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пока я понимаю только текстовые сообщения.")
        return

    history = _histories[message.from_id]
    user_message: ChatMessage = {"role": "user", "content": text}
    messages: list[ChatMessage] = [
        {"role": "system", "content": config.AI_SYSTEM_PROMPT},
        *history,
        user_message,
    ]

    # Индикатор «печатает...» VK не даёт включить ключом сообщества (ошибка 5),
    # поэтому сразу отвечаем «Думаю…», а потом заменяем это сообщение ответом
    thinking_id = await _send_thinking(message)

    try:
        reply = await ai_client.generate(messages)
    except AIError as e:
        logger.error("Ошибка AI для пользователя {}: {}", message.from_id, e)
        await _reply(message, thinking_id, "Извините, сейчас не получается ответить. Попробуйте чуть позже.")
        return

    if not reply:
        reply = "Не знаю, что ответить 🤔"

    history.append(user_message)
    history.append({"role": "assistant", "content": reply})

    await _reply(message, thinking_id, reply)
