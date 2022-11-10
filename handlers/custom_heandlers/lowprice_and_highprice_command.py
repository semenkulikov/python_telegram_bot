from loader import bot, calendar, calendar_1_callback
from states.price_info import HotelPriceState
from telebot.types import Message, InputMediaPhoto
from keyboards.inline.cities_list import city_markup
from datetime import date
from telebot.types import CallbackQuery
from handlers.custom_heandlers.request_to_api import request_by_city, request_hotels, requests_photos
from keyboards.inline.yes_or_no import yes_or_no_markup
from keyboards.inline.create_calendar import create_calendar
import telebot.apihelper
import datetime


@bot.message_handler(commands=['lowprice', 'highprice'])
def send_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        if message.text.endswith('lowprice'):
            hotels_data['sort_order'] = 'PRICE'
        elif message.text.endswith('highprice'):
            hotels_data['sort_order'] = 'PRICE_HIGHEST_FIRST'


@bot.message_handler(state=HotelPriceState.city)
def get_city(message: Message) -> None:
    """ Хендлер, ловит город и кидает кнопки для уточнения """
    try:
        city = message.text
        answer = request_by_city(city)

        bot.send_message(message.from_user.id,
                         f'Уточни, пожалуйста:', reply_markup=city_markup(answer))
        bot.set_state(message.from_user.id, HotelPriceState.check_city, message.chat.id)
    except ValueError as exc:
        bot.send_message(message.from_user.id, exc)


@bot.callback_query_handler(func=None, state=HotelPriceState.check_city)
def check_city(call) -> None:
    """
    Обработчик inline кнопок, запоминает id города

    :param call: данные о кнопке

    :return: None
    """

    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data['city_id'] = call.data

    bot.send_message(call.message.chat.id,
                     'Окей! Когда заезжаем в отель?')
    create_calendar(call.message)
    bot.set_state(call.message.chat.id, HotelPriceState.check_in)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=HotelPriceState.check_in
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов для даты въезда в отель
    """
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    my_date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Ты выбрал эту дату: {my_date.strftime('%d.%m.%Y')}"
        )
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
            if int(day) >= int(datetime.date.today().day):
                hotels_data['check_in'] = date(my_date.year, my_date.month, my_date.day)
                bot.send_message(call.message.chat.id, 'Теперь выбери дату выезда')
                create_calendar(call.message, hotels_data['check_in'])
                bot.set_state(call.message.chat.id, HotelPriceState.check_out)
            else:
                bot.send_message(call.message.chat.id, 'Некорректная дата! Попробуй еще раз')
                create_calendar(call.message)
    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=HotelPriceState.check_out
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов для даты выезда из отеля
    """
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    my_date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Ты выбрал эту дату: {my_date.strftime('%d.%m.%Y')}"
        )
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
            if int(day) >= int(hotels_data['check_in'].day):
                end_date = date(my_date.year, my_date.month, my_date.day)
                hotels_data['check_out'] = end_date
                hotels_data['total_days'] = end_date - hotels_data['check_in']
                bot.send_message(call.message.chat.id, 'Хорошо, сколько отелей выводить? Только не больше 25')
                bot.set_state(call.message.chat.id, HotelPriceState.count_hotel)
            else:
                bot.send_message(call.message.chat.id, 'Ты выезжаешь из отеля раньше, чем приезжаешь туда!')
                create_calendar(call.message, hotels_data['check_in'])

    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.message_handler(state=HotelPriceState.count_hotel)
def get_count_hotel(message: Message) -> None:
    """ Хендлер для получения количества выводимых отелей """
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if 1 <= int(message.text) <= 25:
                hotels_data['hotels_count'] = int(message.text)
                bot.send_message(message.from_user.id, 'Отлично, а фотографии к ним прилагать?',
                                 reply_markup=yes_or_no_markup())
                bot.set_state(message.from_user.id, HotelPriceState.photo_upload, message.chat.id)
            else:
                bot.send_message(message.from_user.id,
                                 f'Я не нашел столько отелей! Максимум - 25')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.callback_query_handler(func=None, state=HotelPriceState.photo_upload)
def get_is_photos(call) -> None:
    """ Коллбэк для обработки да/нет Inline кнопок """
    if call.data == 'Да':
        bot.send_message(call.message.chat.id,
                         f'Хорошо, а сколько фотографий для каждого отеля? Только не больше 10')
        bot.set_state(call.message.chat.id, HotelPriceState.count_photos, call.message.chat.id)
    elif call.data == 'Нет':
        bot.send_message(call.message.chat.id,
                         'Без проблем! Подожди, идет загрузка ...\nНапиши что-нибудь')
        bot.set_state(call.message.chat.id, HotelPriceState.info)


@bot.message_handler(state=HotelPriceState.count_photos)
def get_count_photos(message: Message) -> None:
    """ Хендлер для получения количества фотографий """
    if message.text.isdigit():
        if int(message.text) <= 10:
            bot.send_message(message.from_user.id, 'Подожди ... Идет загрузка фотографий ...')
            bot.set_state(message.from_user.id, HotelPriceState.info, message.chat.id)
            info_output(message, count_photos=int(message.text))
        else:
            bot.send_message(message.from_user.id, 'Не могу загрузить столько! Максимум - 10')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelPriceState.info)
def info_output(message: Message, count_photos=0, stop_iter=5) -> None:
    """
    Хендлер для вывода информации

    :param message: сообщение юзера
    :param count_photos: кол-во фотографий для каждого отеля
    :param stop_iter: при ошибке вся загрузка начнется сначала, и этот параметр нужен для предотвращения рекурсии
    :return: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        sort_order = hotels_data['sort_order']

    if stop_iter:
        try:
            data = request_hotels(message, sort_order=sort_order)
            hotel_count = 0
            for name, hotel in data.items():
                hotel_count += 1
                text = f'Имя отеля: {name}\n' \
                       f'Id отеля: {hotel["hotel_id"]}\n' \
                       f'Адрес: {hotel["address"]}\n'
                for distance in hotel['distance']:
                    text += f'Расстояние от {distance[0]} - {distance[1]}\n'

                text += f'На сколько дней бронируем: {hotel["total_days"].days}\n'

                text += f'Цена за ночь: {int(hotel["price"]):,d} рублей\n' \
                        if hotel['price'] is not None else ''

                text += f'Суммарная цена: {hotel["total_price"]:,d} рублей\n' \
                    if hotel['price'] is not None else ''

                text += f'Рейтинг: {hotel["rating"]}\n' \
                        f'Ссылка на отель: {hotel["linc"]}\n'

                if count_photos:
                    data = requests_photos(
                        hotel_id=hotel["hotel_id"],
                        max_photos=count_photos
                    )
                    photos = [InputMediaPhoto(elem) for elem in data]
                    if len(photos) >= 2:
                        bot.send_media_group(message.from_user.id, photos)
                    else:
                        bot.send_photo(message.from_user.id, photo=data[0])
                bot.send_message(message.from_user.id, text)
                bot.send_message(message.from_user.id, f'Топ {hotel_count}')

            if data:
                bot.send_message(message.from_user.id, 'Готово!')
            else:
                bot.send_message(message.from_user.id, 'К сожалению, такие отели не найдены ((')
            bot.set_state(message.from_user.id, None, message.chat.id)

        except ValueError as exc:
            bot.send_message(message.from_user.id, exc)
            stop_iter -= 1
            info_output(message, count_photos=count_photos, stop_iter=stop_iter)
        except telebot.apihelper.ApiException:
            bot.send_message(message.from_user.id, 'Появилась проблема с интернетом! Попробуй еще раз)')
            bot.send_message(message.from_user.id, 'Надо ли прилагать фотографии к отелям?')
            bot.set_state(message.from_user.id, HotelPriceState.photo_upload)
        except Exception:
            bot.send_message(message.from_user.id,
                             'Технические шоколадки! Не обращай внимания) Сейчас пытаюсь исправить')
            stop_iter -= 1
            info_output(message, count_photos=count_photos, stop_iter=stop_iter)
    else:
        bot.send_message(message.from_user.id,
                         'Прости, но проблему исправить не удалось ((\nПроверь соединение с интернетом')
        bot.set_state(message.from_user.id, None, message.chat.id)
