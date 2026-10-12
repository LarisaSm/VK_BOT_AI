"""Настройки бота. Все значения читаются из файла .env."""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# --- ВКонтакте ---
VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN", "")

# --- AI: общие настройки ---
# stub — заглушка без AI, openai — любой OpenAI-совместимый API (OpenRouter, Groq,
# Ollama, LM Studio), gigachat — GigaChat от Сбера
AI_PROVIDER = os.getenv("AI_PROVIDER", "stub").strip().lower()
AI_SYSTEM_PROMPT = os.getenv(
    "AI_SYSTEM_PROMPT",
    "Ты дружелюбный помощник сообщества ВКонтакте. Отвечай кратко и по-русски.",
)
# Сколько последних сообщений диалога передавать модели как контекст
AI_HISTORY_SIZE = int(os.getenv("AI_HISTORY_SIZE", "10"))
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "60"))

# --- AI: OpenAI-совместимый API ---
AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:11434/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "")
# Для «думающих» моделей (qwen3 и др.): none — без размышлений, low/medium/high — с ними.
# Пусто — не передавать, модель решает сама
AI_REASONING_EFFORT = os.getenv("AI_REASONING_EFFORT", "").strip().lower()

# --- AI: GigaChat ---
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY", "")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat")
# Путь к сертификату Минцифры (рекомендуется) или отключение проверки SSL
GIGACHAT_CA_BUNDLE = os.getenv("GIGACHAT_CA_BUNDLE", "")
GIGACHAT_VERIFY_SSL = _get_bool("GIGACHAT_VERIFY_SSL", True)
