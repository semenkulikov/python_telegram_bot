from loader import bot, calendar, calendar_1_callback
from states.highprice_info import HotelHighPriceState
from telebot.types import Message
from keyboards.inline.cities_list import city_markup
from datetime import date
from telebot.types import CallbackQuery
from handlers.custom_heandlers.request_to_api import request_by_city
from keyboards.inline.count_hotel import get_count_photos, get_count_hotel
from keyboards.inline.create_calendar import create_calendar
import datetime
from handlers.custom_heandlers.general_functions import get_search_results


@bot.message_handler(commands=['highprice'])
def send_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelHighPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')


@bot.message_handler(state=HotelHighPriceState.city)
def get_city(message: Message, stop_iter=5) -> None:
    """ Хендлер, ловит город и кидает кнопки для уточнения """
    if stop_iter:
        try:
            city = message.text
            answer = request_by_city(city)

            bot.send_message(message.from_user.id,
                             f'Уточни, пожалуйста:', reply_markup=city_markup(answer))
            bot.set_state(message.from_user.id, HotelHighPriceState.check_city, message.chat.id)
        except ValueError as exc:
            bot.send_message(message.from_user.id, exc)
            stop_iter -= 1
            get_city(message, stop_iter=stop_iter)
        except PermissionError as exc:
            bot.send_message(message.from_user.id, exc)


@bot.callback_query_handler(func=None, state=HotelHighPriceState.check_city)
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
    bot.set_state(call.message.chat.id, HotelHighPriceState.check_in)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=HotelHighPriceState.check_in
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
            if datetime.date(int(year), int(month), int(day)) >= datetime.date.today():
                hotels_data['check_in'] = date(my_date.year, my_date.month, my_date.day)
                bot.send_message(call.message.chat.id, 'Теперь выбери дату выезда')
                create_calendar(call.message, hotels_data['check_in'])
                bot.set_state(call.message.chat.id, HotelHighPriceState.check_out)
            else:
                bot.send_message(call.message.chat.id, 'Некорректная дата! Попробуй еще раз')
                create_calendar(call.message)
    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=HotelHighPriceState.check_out
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
            if datetime.date(int(year), int(month), int(day)) >= hotels_data['check_in']:
                end_date = date(my_date.year, my_date.month, my_date.day)
                hotels_data['check_out'] = end_date
                hotels_data['total_days'] = end_date - hotels_data['check_in']
                bot.send_message(call.message.chat.id, 'Хорошо, сколько отелей выводить? Выбери одну кнопку',
                                 reply_markup=get_count_hotel())
                bot.set_state(call.message.chat.id, HotelHighPriceState.count_hotel)
            else:
                bot.send_message(call.message.chat.id, 'Ты выезжаешь из отеля раньше, чем приезжаешь туда!')
                create_calendar(call.message, hotels_data['check_in'])

    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.callback_query_handler(func=None, state=HotelHighPriceState.count_hotel)
def get_count_hotels(call) -> None:
    """ Колбэк для получения количества выводимых отелей """
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data['hotels_count'] = int(call.data)
        bot.send_message(call.message.chat.id, 'Отлично, а фотографии к ним прилагать?',
                         reply_markup=get_count_photos())
        bot.set_state(call.message.chat.id, HotelHighPriceState.count_photos, call.message.chat.id)


@bot.callback_query_handler(func=None, state=HotelHighPriceState.count_photos)
def count_photos(call) -> None:
    """ Коллбэк для получения количества фотографий """
    bot.send_message(call.message.chat.id, 'Подожди ... Идет загрузка ...')
    bot.set_state(call.message.chat.id, HotelHighPriceState.info, call.message.chat.id)
    get_search_results(call.message, count_photos=int(call.data), sort_order="PRICE_HIGHEST_FIRST",
                       call_chat_id=call.message.chat.id)
