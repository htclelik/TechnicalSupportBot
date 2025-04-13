# utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import LOG_FORMAT, LOG_FILE

def setup_logger(name: str) -> logging.Logger:
    """Sets up and returns a logger with file rotation.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Уровень логирования можно настроить через переменную окружения LOG_LEVEL (по умолчанию INFO)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(level)

    logger.propagate = False
    formatter = logging.Formatter(LOG_FORMAT)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Файловый обработчик с ротацией
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
