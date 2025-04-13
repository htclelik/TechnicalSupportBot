# sheets_utils.py
import gspread
from datetime import datetime
import pytz # Убедимся, что импортирован

# Убираем TIMEZONE отсюда, он должен быть в config.py
from app.config import SUPPORT_LOG_WORKSHEET_NAME # TIMEZONE убран
from app.services.google_sheet_api import get_google_sheets_client, get_support_log_worksheet
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Убедись, что эти заголовки ТОЧНО соответствуют ПЕРВОЙ строке в твоей таблице
# И порядок важен! Если id_query нужен, добавь его сюда и в sheet_log_data.
EXPECTED_SUPPORT_LOG_HEADERS = [
    'date', 'user_id', 'user_name', 'query', 'id_query' # Раскомментируй, если есть такой столбец
]

def _get_headers_with_retry(worksheet, retries=3):
    """Пытается получить заголовки из первой строки листа."""
    for i in range(retries):
        try:
            headers = worksheet.row_values(1) # Получаем значения первой строки
            if headers and isinstance(headers, list): # Проверяем, что это не пустой список
                logger.info(f"Получены заголовки из таблицы: {headers}")
                # Проверяем наличие *всех* ожидаемых заголовков
                if all(h in headers for h in EXPECTED_SUPPORT_LOG_HEADERS):
                    return headers # Возвращаем фактические заголовки из таблицы
                else:
                    missing = [h for h in EXPECTED_SUPPORT_LOG_HEADERS if h not in headers]
                    logger.warning(f"Попытка {i+1}: Не найдены все ожидаемые заголовки. Отсутствуют: {missing}. Найдены: {headers}")
            else:
                logger.warning(f"Попытка {i+1}: Первая строка пуста или не удалось получить заголовки.")

        except gspread.exceptions.APIError as e:
            # Обрабатываем специфичные ошибки API, например, квоты
            if e.response.status_code == 429:
                 logger.warning(f"Попытка {i+1}: Ошибка API (429 - Too Many Requests) при чтении заголовков. Ждем...")
            else:
                 logger.warning(f"Попытка {i+1}: Ошибка API Google Sheets ({e.response.status_code}) при чтении заголовков: {e}")
        except Exception as e:
            logger.warning(f"Попытка {i+1}: Неожиданная ошибка при чтении заголовков: {e}", exc_info=True)

        if i < retries - 1:
            import time
            delay = 2**i # Экспоненциальная задержка (1, 2, 4 секунды)
            logger.info(f"Пауза перед следующей попыткой чтения заголовков: {delay} сек.")
            time.sleep(delay)

    logger.error(f"Не удалось получить корректные заголовки из листа '{worksheet.title}' после {retries} попыток.")
    return None # Явно возвращаем None при неудаче

async def add_support_log_to_sheet(user_request_data: dict):
    """Добавляет строку с данными об обращении пользователя в лист лога поддержки."""
    try:
        worksheet = get_support_log_worksheet() # Получаем нужный лист
        if not worksheet:
            # get_support_log_worksheet уже логирует ошибку, если лист не найден
            return False

        # Получаем ЗАГОЛОВКИ из таблицы, чтобы знать порядок столбцов
        headers = _get_headers_with_retry(worksheet)
        if not headers:
            logger.error("Не удалось добавить запись в лог: не удалось получить заголовки из таблицы.")
            # Важно! Не пытаемся писать без заголовков
            return False

        # Формируем строку данных В СООТВЕТСТВИИ С ПОРЯДКОМ ЗАГОЛОВКОВ В ТАБЛИЦЕ
        row_to_insert = []
        for header in headers:
            # Используем .get() с пустой строкой по умолчанию, если ключ отсутствует в данных
            # Это безопасно, даже если в таблице больше столбцов, чем данных мы передаем
            value = user_request_data.get(header, '')
            row_to_insert.append(str(value)) # Преобразуем в строку на всякий случай

        logger.debug(f"Подготовлена строка для вставки в '{SUPPORT_LOG_WORKSHEET_NAME}': {row_to_insert}")

        # Вставляем строку в конец таблицы
        worksheet.append_row(row_to_insert, value_input_option='USER_ENTERED')
        logger.info(f"Запись для пользователя '{user_request_data.get('user_name', 'N/A')}' (ID: {user_request_data.get('user_id', 'N/A')}) добавлена в лог '{SUPPORT_LOG_WORKSHEET_NAME}'.")
        return True

    except gspread.exceptions.APIError as e:
        logger.error(f"Ошибка API Google Sheets при добавлении лога записи: {e}", exc_info=True)
        # Можно добавить специфическую обработку, например, для ошибки квот 429
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при добавлении лога записи в таблицу: {e}", exc_info=True)

    return False # Возвращаем False при любой ошибке