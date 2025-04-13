
# app/handlers/common.py
"""Модуль содержит общие обработчики и функции для работы с ботом."""

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter # Добавляем фильтр состояний
from aiogram.fsm.state import default_state # Состояние по умолчанию

from app.keyboards.inline_buttons import create_inline_universal_keyboard # Нужна функция для кнопок
from app.utils.constants import WELCOME_TEXT, FEEDBACK_TEXT, HELP_BUTTON_TEXT, START_QUERY_CALLBACK # Константы
from app.utils.logger import setup_logger
from app.stats.state_manager import state_manager # Нужен state_manager

logger = setup_logger(__name__)

async def send_message_with_keyboard(message: types.Message, text: str, keyboard=None, parse_mode="HTML"):
    # Эта функция остается без изменений
    try:
        if not text:
            logger.warning("Пустой текст сообщения")
            text = "..."
        return await message.answer(text, parse_mode=parse_mode, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
        return await message.answer("Произошла ошибка при отправке сообщения. Попробуйте позже.")

# 🔹 Обработчик /start
async def start_handler(message: types.Message, state: FSMContext):
    """Обрабатывает команду /start, приветствует и ПОКАЗЫВАЕТ КНОПКУ."""
    await state.clear() # Всегда очищаем состояние при /start
    user_name = message.from_user.first_name
    logger.info(f"Пользователь {message.from_user.id} ({user_name}) запустил /start.")

    # Создаем кнопку
    buttons = {HELP_BUTTON_TEXT: START_QUERY_CALLBACK}
    # Убедись, что функция create_inline_universal_keyboard существует и работает
    keyboard = create_inline_universal_keyboard(buttons, 1)

    # Отправляем приветствие с кнопкой
    await send_message_with_keyboard(
        message,
        WELCOME_TEXT.format(user_name=user_name),
        keyboard=keyboard # Передаем клавиатуру
    )
    # НЕ устанавливаем состояние и НЕ вызываем state_manager здесь

# 🔹 НОВЫЙ обработчик для нажатия кнопки "Написать обращение"
async def start_query_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие кнопки и ЗАПУСКАЕТ машину состояний."""
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} нажал кнопку '{START_QUERY_CALLBACK}'")

    # Отвечаем на callback, чтобы убрать "часики"
    await callback_query.answer()

    # Опционально: убираем кнопку из предыдущего сообщения
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.message.edit_text(FEEDBACK_TEXT,parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Не удалось убрать кнопку из сообщения {callback_query.message.message_id} для user {user_id}: {e}")

    # Устанавливаем ФИКТИВНОЕ начальное состояние "start" для State Manager
    # Это нужно, чтобы State Manager знал, откуда начинать переход
    await state.set_state("start")
    logger.debug(f"Установлено временное состояние 'start' для user {user_id} после нажатия кнопки")

    # Запускаем переход к первому реальному состоянию (waiting_for_question)
    # Передаем именно callback_query, StateManager разберется
    await state_manager.handle_transition(callback_query, state, "next")