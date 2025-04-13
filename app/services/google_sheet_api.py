
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.config import GOOGLE_CREDENTIALS_PATH, SCOPES_FEED_DRIVE, GOOGLE_SHEET_NAME, SUPPORT_LOG_WORKSHEET_NAME
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


_support_log_worksheet = None
_google_sheets_client = None



def get_google_sheets_client():

    global _google_sheets_client
    if _google_sheets_client is None:
        try:
            scope = SCOPES_FEED_DRIVE
            creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
            _google_sheets_client = gspread.authorize(creds)

            logger.info("Клиент Google Sheets успешно аутентифицирован.")

        except Exception as e:
            logger.error(f"Ошибка при получении клиента Google Sheets: {e}")
            raise e


    return _google_sheets_client


def get_support_log_worksheet():
    """Возвращает рабочий лист 'BookingsLog'."""
    global _support_log_worksheet
    if _support_log_worksheet is None:
        try:
            client = get_google_sheets_client()
            spreadsheet = client.open(GOOGLE_SHEET_NAME)
            # Используем имя листа из конфига
            _support_log_worksheet = spreadsheet.worksheet(SUPPORT_LOG_WORKSHEET_NAME)
            logger.info(f"Рабочий лист '{SUPPORT_LOG_WORKSHEET_NAME}' успешно получен.")
        except gspread.exceptions.WorksheetNotFound:
             logger.error(f"Лист '{SUPPORT_LOG_WORKSHEET_NAME}' не найден в таблице '{GOOGLE_SHEET_NAME}'!")
             raise
        except Exception as e:
            logger.error(f"Ошибка при получении рабочего листа '{SUPPORT_LOG_WORKSHEET_NAME}': {e}", exc_info=True)
            raise
    return _support_log_worksheet