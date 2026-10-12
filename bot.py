"""Точка входа: python bot.py"""

import logging
import sys

from vkbottle.bot import Bot
from vkbottle.modules import logger

import config
from ai import ai_client
from handlers import labelers

# Без этого vkbottle показывает только предупреждения и ошибки.
# Поставьте "DEBUG", чтобы видеть каждое пришедшее событие.
logging.getLogger("vkbottle").setLevel("INFO")

if not config.VK_BOT_TOKEN:
    sys.exit("Не задан VK_BOT_TOKEN в файле .env")

bot = Bot(token=config.VK_BOT_TOKEN)

for custom_labeler in labelers:
    bot.labeler.load(custom_labeler)


async def on_startup() -> None:
    logger.info(
        "Бот запущен, AI-провайдер: {}, таймаут ответа: {} с", config.AI_PROVIDER, config.AI_TIMEOUT
    )


if __name__ == "__main__":
    # В on_startup / on_shutdown передаются корутины (вызов функции без await)
    bot.on_startup.append(on_startup())
    bot.on_shutdown.append(ai_client.close())
    bot.run()
