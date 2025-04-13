# # app/state_management/state_manager.py
from typing import Dict, Callable, Awaitable

from aiogram import types
from aiogram.fsm.context import FSMContext

from app.stats.question_stats import QuestionStates
from app.stats.state_transitions import STATE_TRANSITIONS
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def validate_booking_data(state: FSMContext):
    """Проверяет, заполнены ли все необходимые данные"""
    user_data = await state.get_data()
    required_fields = ['date', 'user_id', 'question', 'user_name']

    if not all(field in user_data for field in required_fields):
        return False, "❌ Ошибка: недостаточно данных. Начните заново."

    return True, user_data


class StateManager:
    """
    Класс для управления переходами между состояниями бронирования.

    Обоснование:
      - Централизованное управление состояниями позволяет легко отслеживать логику переходов.
      - Разделение логики для каждого шага (например, ввод имени, телефона, выбор мастера) упрощает сопровождение и тестирование.
      - Использование единственного метода для обработки переходов снижает вероятность ошибок при добавлении новых состояний.
    """

    def __init__(self):
        # Регистрируем обработчики для состояний, если потребуется расширение функционала.
        self.state_handlers: Dict[str, Dict[str, Callable[[types.Message, FSMContext], Awaitable[None]]]] = {}

    def register_state(self, state_name: str, entry_handler: Callable[[types.Message, FSMContext], Awaitable[None]]):
        """
        Регистрирует обработчик для конкретного состояния.
        Обоснование: Позволяет динамически добавлять новые обработчики без изменения основной логики переходов.
        """
        self.state_handlers[state_name] = {"entry": entry_handler}

    async def handle_transition(self, msg: types.Message, state: FSMContext, action: str = "next"):
        """
        Централизованная обработка переходов между состояниями.

        Обоснование:
          - Позволяет управлять переходами (например, вперед или назад) в одном месте.
          - Облегчает отслеживание и логирование переходов для дальнейшей отладки.
        """
        current_state = await state.get_state()
        if current_state is None:
            logger.error("Текущее состояние не установлено.")
            return  # Если состояние не установлено, выходим

        # Обработка нажатия кнопки "назад"
        if action == "back":
            previous_state = STATE_TRANSITIONS.get(current_state, {}).get("back")
            if previous_state:
                await state.set_state(previous_state)
                logger.info(f"Переход назад: {current_state} -> {previous_state}")
                await self._handle_state_entry(msg, state, previous_state)
                return

        # Переход к следующему состоянию по умолчанию
        next_state = STATE_TRANSITIONS.get(current_state, {}).get(action)
        if not next_state:
            logger.warning(f"Нет перехода для действия '{action}' из состояния '{current_state}'")
            return

        await state.set_state(next_state)
        logger.info(f"Переход: {current_state} -> {next_state} по действию '{action}'")
        await self._handle_state_entry(msg, state, next_state)


    async def _handle_state_entry(self, msg: types.Message, state: FSMContext, next_state: str):
        """
        Вызывает обработчик для нового состояния.

        Обоснование:
          - Разделение логики входа в состояние позволяет легко изменять поведение для каждого шага.
          - Если обработчик для нового состояния не найден, это логируется для дальнейшей диагностики.
        """
        handlers = {
            QuestionStates.waiting_for_question.state: self._handle_question_entry,
            QuestionStates.waiting_for_creating_record_request.state: self._handle_show_recording_user_request,
            QuestionStates.finish.state: self._handle_finish

        }
        handler = handlers.get(next_state)
        if handler:
            await handler(msg, state)
        else:
            logger.error(f"Обработчик для состояния {next_state} не найден.")

    async def _handle_question_entry(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния ожидания ввода имени.

        Обоснование:
          - Изолированный метод для ввода имени облегчает модификацию или расширение логики данного шага.
        """

        await msg.answer(
            f"🙋Напиши ваш вопрос или опишите проблему",
            parse_mode="HTML"

        )

    async def _handle_show_recording_user_request(self, msg: types.Message, state: FSMContext):
        """
        Обработка входа в состояние показа сводки. Запись и уведомление УЖЕ произошли.
        """
        logger.info(f"Вход в состояние waiting_for_creating_record_request для user {msg.chat.id}")
        user_data = await state.get_data()

        # Получаем данные, сохраненные на предыдущем шаге
        user_name = user_data.get("user_name", "Неизвестный пользователь")
        user_id = user_data.get("user_id", "N/A")
        id_query = user_data.get("id_query", "N/A")
        query_text = user_data.get("query", "Текст вопроса не сохранен")
        date_str = user_data.get("date", "Дата не сохранена")  # Дата должна быть уже в нужном формате
        await state.update_data(user_name=user_name, user_id=user_id, id_query=id_query, date=date_str, query=query_text)
        logger.info(f"Для user_name {user_name},создан question_id {id_query}")


        summary_question_text = (

            f"<b>❕Сводная информация об обращении❕:</b>\n\n"
            f"👤<b>{user_name}</b>\n\n>"
            f"<i>Ваш № 🆔заявки(обращения):</i> <b>{id_query}</b>\n"
            f"📝<i>Описание вашего обращения:</i> <b>{query_text}</b>\n\n"
            f"📅<i>Дата обращения :</i> <b>{date_str}</b>\n"
            f"Принято в работу на рассмотрение - позже мы сообщим о результате"

            # Лучше \n для читаемости
        )
        await msg.answer(
            summary_question_text,
            parse_mode="HTML"
        )
        # Сразу переходим к финальному состоянию
        logger.debug("Автоматический переход из waiting_for_creating_record_request в finish")
        # Используем message, который был передан в этот метод
        await self.handle_transition(msg, state, "next")

    async def _handle_finish(self, msg: types.Message, state: FSMContext):
        """
        Обработка входа в финальное состояние.
        """
        logger.info(f"Вход в состояние finish для user {msg.chat.id}. Завершение процесса.")
        await msg.answer(
            f"🙏Спасибо что обратились в нашу службу поддержки",
            parse_mode="HTML"
        )
        await state.clear()

# Инициализация state_manager для использования в остальной части проекта
state_manager = StateManager()

