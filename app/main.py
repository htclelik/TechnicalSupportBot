# main.py
import asyncio
import logging
import sys # Добавь sys для логирования в stdout

# Используем общий экземпляр бота
from bot_instance import bot
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.handlers.dispatcher import setup_dispatcher

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def set_default_commands(bot_instance: Bot): # Принимаем bot как аргумент
    commands = [
        BotCommand(command="start", description="🏁Начало работы\n🛟Написать обращение или вопрос\n"),
        # BotCommand(command="help", description="🛟Написать обращение или вопрос"),
    ]
    await bot_instance.set_my_commands(commands)


async def main():
    # Конфигурируем логирование
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Добавим формат
    logger.info("Запуск бота...")

    # Инициализация хранилища FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка обработчиков (передаем bot для единообразия, если другие хендлеры его ожидают)
    setup_dispatcher(dp)
    await set_default_commands(bot) # Используем импортированный bot


    logger.info("Запуск polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Остановка бота...")
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    # Используем try-except для корректного завершения
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Выход из бота (KeyboardInterrupt/SystemExit)")
    except Exception as e:
         logger.critical(f"Критическая ошибка в asyncio.run(main): {e}", exc_info=True)