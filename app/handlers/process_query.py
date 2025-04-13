# Лучше назвать process_query.py

from datetime import datetime

import pytz
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from app.bot_instance import bot
from app.config import SUPPORT_CHAT_ID, TIMEZONE
from app.stats import state_manager
from app.stats.question_stats import QuestionStates
from app.stats.state_manager import state_manager
from app.utils.google_sheet_utils import add_support_log_to_sheet
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()


async def process_enter_query(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод вопроса пользователем в состоянии waiting_for_question.
    Сохраняет данные, записывает в таблицу, уведомляет поддержку и переходит к следующему шагу.
    """
    current_state = await state.get_state()
    # Доп. проверка, что мы точно в нужном состоянии
    if current_state != QuestionStates.waiting_for_question.state:
        logger.warning(f"Получено сообщение от {message.from_user.id} в неожиданном состоянии: {current_state}. Ожидалось: {QuestionStates.waiting_for_question.state}")
        return

    # Проверка, что пришел именно текст
    if not message.text or message.text.startswith('/'):
        logger.warning(f"Получено нетекстовое сообщение или команда от {message.from_user.id} в состоянии waiting_for_question.")
        await message.answer("Пожалуйста, введите ваш вопрос текстом.")
        # Остаемся в том же состоянии, ждем корректный ввод
        return

    query_text = message.text.strip()
    user_id = message.from_user.id
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name

    # Получаем текущую дату и время в нужном формате и зоне
    tz = pytz.timezone(TIMEZONE)
    current_datetime = datetime.now(tz)
    # Формат для таблицы и для сообщения пользователю
    date_str_sheet = current_datetime.strftime('%Y-%m-%d %H:%M:%S') # Для таблицы
    date_str_display = current_datetime.strftime('%d.%m.%Y %H:%M') # Для пользователя

    # Генерируем ID, если нужно
    id_query = f"q_{user_id}_{current_datetime.strftime('%y%m%d%H%M%S')}" # Уникальный ID

    logger.info(f"User {user_id} ('{user_name}') ввел вопрос: '{query_text}'. Date: {date_str_sheet}, ID_Query: {id_query}")

    # 1. Сохраняем ВСЕ необходимые данные в state для следующего шага (показ сводки)
    await state.update_data(
        query=query_text,
        user_id=str(user_id), # Сохраняем как строку
        user_name=user_name,
        date=date_str_display, # Сохраняем дату для показа пользователю
        id_query=id_query,
        date_for_sheet=date_str_sheet # Отдельно сохраняем дату для таблицы
    )
    logger.debug(f"Данные сохранены в state для user {user_id}")

    # --- Выполнение действий: Запись в таблицу и Уведомление ---
    # Эти действия выполняются ЗДЕСЬ, перед переходом к показу сводки

    # 2. Попытка записи в Google Sheets
    sheet_log_data = {
        "date": date_str_sheet, # Дата для таблицы
        'user_id': str(user_id),
        'user_name': user_name,
        'query': query_text,
        'id_query': id_query # Добавь, если столбец есть в таблице и EXPECTED_HEADERS
    }
    try:
        # Можно показать временное сообщение "Обрабатываю..."
        # await message.answer("⏳ Минутку, обрабатываю ваш запрос...")
        log_added = await add_support_log_to_sheet(sheet_log_data)
        if log_added:
            logger.info(f"Вопрос user_id={user_id} успешно записан в Google Sheets.")
        else:
            logger.error(f"Не удалось записать вопрос user_id={user_id} в Google Sheets (add_support_log_to_sheet вернул False).")
    except Exception as log_err:
        logger.error(f"Ошибка при вызове add_support_log_to_sheet для user_id={user_id}: {log_err}", exc_info=True)
    # Ошибка записи не должна прерывать основной поток для пользователя

    # 3. Отправка уведомления в чат поддержки
    try:
        if not SUPPORT_CHAT_ID:
             logger.error("ID чата поддержки (SUPPORT_CHAT_ID) не настроен!")
        else:
            notification_body = (
                f"<b>❗️ Новое обращение!</b>\n\n"
                f"🆔 <b>ID Заявки:</b> {id_query}\n"
                f"👤 <b>Пользователь:</b> {user_name} (ID: {user_id})\n"
                f"📅 <b>Время:</b> {date_str_sheet}\n\n" # Используем время записи
                f"📝 <b>Вопрос/Проблема:</b>\n{query_text}\n"
            )
            await bot.send_message(
                chat_id=SUPPORT_CHAT_ID,
                text=notification_body,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            logger.info(f"Уведомление об обращении user_id={user_id} отправлено в чат {SUPPORT_CHAT_ID}.")
    except Exception as notify_err:
        logger.error(f"Не удалось отправить уведомление в чат поддержки {SUPPORT_CHAT_ID} для user_id={user_id}: {notify_err}", exc_info=True)

    # --- Конец выполнения действий ---

    # 4. Переход к следующему состоянию через StateManager
    # Следующее состояние покажет пользователю сводку
    logger.debug(f"Запуск перехода в следующее состояние из process_enter_query для user {user_id}")
    await state_manager.handle_transition(message, state, "next")
