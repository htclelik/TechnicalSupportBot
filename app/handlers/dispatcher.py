from aiogram import Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from app.handlers.common import start_handler, start_query_callback_handler
from app.handlers.process_query import process_enter_query
from app.stats.question_stats import QuestionStates
from app.utils.constants import HELP_BUTTON_CALLBACK, HELP_BUTTON_TEXT, START_QUERY_CALLBACK
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()


def setup_dispatcher(dp: Dispatcher):
    """Регистрируем все обработчики команд и состояний"""

    # 📌 Общие команды
    router.message.register(start_handler, Command("start"))

    router.callback_query.register(start_query_callback_handler,
        F.data == START_QUERY_CALLBACK,
        StateFilter(default_state))

    # 📌 Обработка ввода вопроса
    router.message.register(
        process_enter_query,
        StateFilter(QuestionStates.waiting_for_question), # <--- ИЗМЕНИ ЗДЕСЬ
        F.text,
        ~F.text.startswith('/')
    )


    logger.info("Все обработчики бота успешно зарегистрированы")
    dp.include_router(router)
