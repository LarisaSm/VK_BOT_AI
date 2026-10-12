"""Приветствие новых пользователей."""

from vkbottle import ABCAPI, GroupEventType, GroupTypes, VKAPIError
from vkbottle.bot import BotLabeler, Message
from vkbottle.modules import logger

welcome_labeler = BotLabeler()
welcome_labeler.vbml_ignore_case = True

WELCOME_TEXT = (
    "Привет, {name}! 👋\n"
    "Рады видеть вас в нашем сообществе. "
    "Напишите мне любой вопрос — я постараюсь помочь."
)


async def get_first_name(api: ABCAPI, user_id: int) -> str:
    try:
        users = await api.users.get(user_ids=[user_id])
        return users[0].first_name or "друг"
    except (VKAPIError, IndexError):
        return "друг"


async def send_welcome(api: ABCAPI, user_id: int) -> None:
    name = await get_first_name(api, user_id)
    try:
        await api.messages.send(
            peer_id=user_id, message=WELCOME_TEXT.format(name=name), random_id=0
        )
    except VKAPIError[901]:
        # Пользователь не разрешил сообщения от сообщества — написать ему нельзя
        logger.info("Не могу поприветствовать {}: сообщения от сообщества запрещены", user_id)


# Пользователь вступил в сообщество
@welcome_labeler.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def on_group_join(event: GroupTypes.GroupJoin) -> None:
    await send_welcome(event.ctx_api, event.object.user_id)


# Пользователь разрешил сообщения от сообщества
@welcome_labeler.raw_event(GroupEventType.MESSAGE_ALLOW, dataclass=GroupTypes.MessageAllow)
async def on_message_allow(event: GroupTypes.MessageAllow) -> None:
    await send_welcome(event.ctx_api, event.object.user_id)


# Кнопка «Начать» в новом диалоге присылает payload {"command": "start"}
@welcome_labeler.private_message(payload={"command": "start"})
@welcome_labeler.private_message(text=["начать", "start", "/start"])
async def on_start(message: Message) -> None:
    name = await get_first_name(message.ctx_api, message.from_id)
    await message.answer(WELCOME_TEXT.format(name=name))
