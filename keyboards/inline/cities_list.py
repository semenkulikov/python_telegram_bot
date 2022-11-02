from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(cities):
    """
    Функция для создания Inline кнопок, которые указывают на города

    :param cities: список городов
    :return: кнопки, текст - имя города, callback_data - id города
    """
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=f'{city["destination_id"]}'))
    return destinations
