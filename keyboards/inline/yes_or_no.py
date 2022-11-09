from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def yes_or_no_markup():
    """
    Функция для создания да/нет Inline кнопок
    """
    dest = InlineKeyboardMarkup()
    dest.add(InlineKeyboardButton(text='Да', callback_data='Да'))
    dest.add(InlineKeyboardButton(text='Нет', callback_data='Нет'))
    return dest
