# ------------------------------ keyboards/inline_buttons.py ------------------------------
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_universal_keyboard(buttons, row_width=2, additional_buttons=None):
    """Создает инлайн-клавиатуру из кнопок"""
    # Создаем список для хранения рядов кнопок
    keyboard_buttons = []
    current_row = []

    # Проверяем тип данных и обрабатываем соответственно
    if isinstance(buttons, dict):
        for key, value in buttons.items():
            current_row.append(InlineKeyboardButton(text=key, callback_data=value))
            # Если достигли нужного количества кнопок в ряду
            if len(current_row) == row_width:
                keyboard_buttons.append(current_row)
                current_row = []

    elif isinstance(buttons, list):
        for button in buttons:
            if isinstance(button, dict) and 'text' in button and 'callback_data' in button:
                # Если элемент списка - это словарь с ключами 'text' и 'callback_data'
                current_row.append(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
            elif isinstance(button, (list, tuple)):
                # Если элемент списка - это список/кортеж [текст, callback_data]
                current_row.append(InlineKeyboardButton(text=button[0], callback_data=button[1]))
            else:
                # Если элемент списка - это строка (текст = callback_data)
                current_row.append(InlineKeyboardButton(text=str(button), callback_data=str(button)))

            # Если достигли нужного количества кнопок в ряду
            if len(current_row) == row_width:
                keyboard_buttons.append(current_row)
                current_row = []

    # Добавляем оставшиеся кнопки, если они есть
    if current_row:
        keyboard_buttons.append(current_row)

    # Добавляем дополнительные кнопки
    if additional_buttons:
        extra_row = []
        for key, value in additional_buttons.items():
            extra_row.append(InlineKeyboardButton(text=key, callback_data=value))
        keyboard_buttons.append(extra_row)

    # Создаем и возвращаем инлайн-клавиатуру
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

