from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def distance():
    """
    Функция, создает Inline кнопки для выбора метрики расстояний
    """
    dest = InlineKeyboardMarkup(row_width=3)
    dest.add(InlineKeyboardButton(text='Километры', callback_data='километров 1.609344 километры'))
    dest.add(InlineKeyboardButton(text='Метры', callback_data='метров 0.1609344 метры'))
    dest.add(InlineKeyboardButton(text='Мили', callback_data='миль 1 мили'))

    return dest
