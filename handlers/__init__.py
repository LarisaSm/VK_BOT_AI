from .chat import chat_labeler
from .welcome import welcome_labeler

# Порядок важен: приветствие и команды проверяются раньше, чем «ответ AI на всё остальное»
labelers = [welcome_labeler, chat_labeler]

__all__ = ("labelers",)
