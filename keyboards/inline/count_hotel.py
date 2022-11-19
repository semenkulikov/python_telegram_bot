from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_count_photos():
    """
    Функция, создает Inline кнопки для выбора количества фотографий
    """
    dest = InlineKeyboardMarkup(row_width=5)
    dest.add(InlineKeyboardButton(text='Нет, не надо', callback_data=str(0)))
    buts_list = []
    for num in range(1, 11):
        buts_list.append(InlineKeyboardButton(text=str(num), callback_data=str(num)))
    dest.add(*buts_list)
    return dest


def get_count_hotel():
    """
    Функция, создает Inline кнопки для выбора количества отелей
    """
    dest = InlineKeyboardMarkup(row_width=5)
    buts_list = []
    for num in range(1, 26):
        buts_list.append(InlineKeyboardButton(text=str(num), callback_data=str(num)))
    dest.add(*buts_list)
    return dest
