import os
from aiogram import Bot
from config import TELEGRAM_BOT_TOKEN

# Используем BOT_TOKEN из твоего config.py
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в config.py")

bot = Bot(token=TELEGRAM_BOT_TOKEN)