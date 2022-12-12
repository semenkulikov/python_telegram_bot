from loader import bot
from states.bestdeal_info import HotelBestPriceState
from states.hotel_info import HotelPriceState
from telebot.types import Message
from keyboards.inline.cities_list import city_markup
from handlers.custom_heandlers.work.request_to_api import request_by_city
from keyboards.inline.create_calendar import create_calendar
from keyboards.inline.metric_system import distance

import datetime


@bot.message_handler(commands=['bestdeal'])
def send_bestdeal(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelBestPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        hotels_data['command'] = message.text
        date = datetime.datetime.now()
        hotels_data['date'] = f"{date.date().strftime('%d.%m.%Y')} {date.time()}"
        hotels_data['chat_id'] = message.chat.id


@bot.message_handler(state=HotelBestPriceState.city)
def get_city(message: Message, stop_iter=5) -> None:
    """ Хендлер, ловит город и кидает кнопки для уточнения """
    if stop_iter:
        try:
            city = message.text
            with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
                hotels_data['city'] = message.text
            answer = request_by_city(city)

            bot.send_message(message.from_user.id,
                             f'Уточни, пожалуйста:', reply_markup=city_markup(answer))
            bot.set_state(message.from_user.id, HotelBestPriceState.check_city, message.chat.id)
        except ValueError:
            stop_iter -= 1
            get_city(message, stop_iter=stop_iter)
        except PermissionError as exc:
            bot.send_message(message.from_user.id, exc)
    else:
        bot.send_message(message.from_user.id, 'Не удалось связаться с сервером. Проверь соединение с интернетом')
        bot.send_message(message.from_user.id, None, message.chat.id)


@bot.callback_query_handler(func=None, state=HotelBestPriceState.check_city)
def check_city(call) -> None:
    """
    Обработчик inline кнопок, запоминает id города

    :param call: данные о кнопке

    :return: None
    """

    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data['city_id'] = call.data

    bot.send_message(call.message.chat.id,
                     'Окей! Укажи минимальную цену за ночь ($)')
    bot.set_state(call.message.chat.id, HotelBestPriceState.price_min)


@bot.message_handler(state=HotelBestPriceState.price_min)
def price_min(message: Message) -> None:
    """ Хендлер для получения минимальной цены """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if int(message.text) >= 0:
                hotels_data['price_min'] = int(message.text)
                bot.send_message(message.from_user.id, 'Хорошо, теперь укажи максимальную цену ($)')
                bot.set_state(message.from_user.id, HotelBestPriceState.price_max, message.chat.id)
            else:
                bot.send_message(message.from_user.id, 'Некорректная цена!')
    except (TypeError, ValueError):
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelBestPriceState.price_max)
def price_max(message: Message) -> None:
    """ Хендлер для получения максимальной цены """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if int(message.text) > hotels_data['price_min']:
                hotels_data['price_max'] = int(message.text)
                bot.send_message(message.from_user.id, 'Таак, напиши максимальное расстояние от центра города')
                bot.set_state(message.from_user.id, HotelBestPriceState.distance_max, message.chat.id)
            else:
                bot.send_message(message.from_user.id, 'Некорректная цена!')
    except (TypeError, ValueError):
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelBestPriceState.distance_max)
def distance_max(message: Message) -> None:
    """ Хендлер для получения максимального расстояния """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data['distance_max'] = message.text
            bot.send_message(message.from_user.id, 'Хорошо, а в чем его измерять?', reply_markup=distance())
            bot.set_state(message.from_user.id, HotelBestPriceState.metric_system, message.chat.id)

    except (TypeError, ValueError):
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.callback_query_handler(func=None, state=HotelBestPriceState.metric_system)
def metric_system(call):
    """ Обработчик inline кнопок, запоминает метрическую систему расстояний """
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data['metric'] = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.id,
                          text=f'Мера длины: {call.data.split()[2]}')
    bot.send_message(call.message.chat.id,
                     'Окей! Когда заезжаем в отель?')
    create_calendar(call.message)
    bot.set_state(call.message.chat.id, HotelPriceState.check_in)
