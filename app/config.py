# config.py
import base64
import os
import tempfile

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# API ключи и токены
# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TIMEZONE = os.getenv("TIMEZONE")
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID")

# Google
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
# GOOGLE_CREDENTIALS_PATH = os.path.abspath(os.getenv("GOOGLE_CREDENTIALS_PATH"))
GOOGLE_CREDENTIALS_B64 = os.getenv("GOOGLE_CREDENTIALS_B64")

# Если есть GOOGLE_CREDENTIALS_B64, создаем временный файл с учетными данными
if GOOGLE_CREDENTIALS_B64:
    try:
        credentials_json = base64.b64decode(GOOGLE_CREDENTIALS_B64).decode('utf-8')
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write(credentials_json)
        temp_file.close()
        # Переопределяем путь к файлу учетных данных
        GOOGLE_CREDENTIALS_PATH = temp_file.name
    except Exception as e:
        print(f"Ошибка при декодировании GOOGLE_CREDENTIALS_B64: {e}")

SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_FEED_DRIVE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar']
SUPPORT_LOG_WORKSHEET_NAME = os.getenv("SUPPORT_LOG_WORKSHEET_NAME")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")




# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "bot.log"

# Проверка наличия файла учетных данных Google
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    raise FileNotFoundError(f"Файл {GOOGLE_CREDENTIALS_PATH} не найден! Проверьте путь или наличие GOOGLE_CREDENTIALS_B64.")

# Проверка обязательных переменных окружения
if not TELEGRAM_BOT_TOKEN:
    raise EnvironmentError("Не все обязательные переменные окружения установлены!")