
from aiogram import types
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def sanitize_callback_data(data: str) -> str:
    """
    Очищает callback_data:
      - Заменяет пробелы на подчёркивания.
      - Усечёт результат до 64 байт в UTF-8, гарантируя корректное декодирование.
    """
    # Заменяем пробелы на подчеркивания
    data = data.replace(" ", "_")
    # Кодируем в UTF-8 и усекаем до 64 байт
    encoded = data.encode("utf-8")[:64]
    # Декодируем, игнорируя обрезанные символы
    return encoded.decode("utf-8", "ignore")

def split_message(response):

    """Разбивает длинный текст на части, чтобы избежать ошибки Telegram."""
    return [response[i:i + 4096] for i in range(0, len(response), 4096)]


async def send_response(message: types.Message, response: str):
    """
    Отправляет пользователю основной ответ и дополнительные данные (если есть).

    :param response:
    :param message: Объект сообщения Telegram

    """
    # Отправляем основной текст, если он есть
    for part in split_message(response or ""):
        await message.answer(part, parse_mode="HTML")


