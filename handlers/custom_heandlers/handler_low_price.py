from handlers.custom_heandlers.request_to_api import request_to_api
from dotenv import load_dotenv
from loader import bot
from states.low_price_info import HotelLowPriceState
from telebot.types import Message, InputMediaPhoto
from keyboards.inline.cities_list import city_markup
from typing import List, Dict, Any
from datetime import date

import telebot.apihelper
import re
import json
import os

load_dotenv()


def request_by_city(city_name: str) -> List:
    """
    Формирует и обрабатывает первый запрос, возвращает районы города

    :param city_name: город, где идет поиск отелей

    :return: список всех найденных мест
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city_name, "locale": "ru_RU", "currency": "RUB"}
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    try:
        response = json.loads(request_to_api(url, querystring=querystring, headers=headers).text)

        result = response['suggestions'][0]
        if result['entities']:
            cities = list()
            for dest in result['entities']:
                cities.append({'city_name': dest['name'],
                               'destination_id': dest['destinationId']
                               })
        else:
            raise ValueError('К сожалению, такой город не найден, попробуй еще раз)')

        return cities

    except (LookupError, TypeError, AttributeError):
        raise ValueError('Упс! Что-то пошло не так. Попробуй еще раз')


def request_hotels(message: Message):
    """
    Функция для обработки второго запроса по отелям. Возвращает словарь, где ключ - имя отеля,
    значение - словарь с такими ключами - [id, адрес, расстояние от центра, цена, суммарная цена, рейтинг, ссылка]
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": hotels_data['city_id'],
                       "pageNumber": "1",
                       "pageSize": hotels_data['count_hotels'],
                       "checkIn": hotels_data['check_in'],
                       "checkOut": hotels_data['check_out'],
                       "adults1": "1",
                       "sortOrder": "PRICE",
                       "locale": "ru_RU",
                       "currency": "RUB"}
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }
        data = dict()
        try:
            response = json.loads(request_to_api(url, querystring=querystring, headers=headers).text)
            result = response['data']['body']['searchResults']['results']

            for hotel in result:
                name = hotel['name']
                distances = []

                for index in hotel['landmarks']:
                    distances.append([index['label'], index['distance']])

                price = hotel['ratePlan']['price']['exactCurrent']  # Цена за одну ночь
                total_days = hotels_data['total_days']
                total_price = round(price * total_days)  # Цена за все

                data[name] = {
                    'hotel_id': hotel['id'],
                    'address': f'{response["data"]["body"]["header"]}',
                    'distance': distances,
                    'total_days': total_days,
                    'price': price,
                    'total_price': total_price,
                    'rating': hotel['guestReviews']['rating'],
                    'linc': f'https://www.hotels.com/ho{hotel["id"]}'
                }

            return data

        except (LookupError, TypeError, AttributeError):
            raise ValueError('Упс! Что-то пошло не так. Попробуй еще раз')


def requests_photos(hotel_id, max_photos) -> List[str]:
    """ Функция, формирует и обрабатывает третий запрос к фотографиям отеля, возвращает ссылки на них """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        response = json.loads(request_to_api(url, querystring=querystring, headers=headers).text)
        photos_list = list()
        for index in response['hotelImages']:
            if max_photos:
                base_url = index['baseUrl']
                linc = re.sub('{size}', 'z', base_url)
                photos_list.append(linc)
                max_photos -= 1
            else:
                break
        return photos_list
    except (LookupError, TypeError, AttributeError):
        raise ValueError('Упс! Что-то пошло не так. Попробуй еще раз')


@bot.message_handler(commands=['lowprice'])
def send_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelLowPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')


@bot.message_handler(state=HotelLowPriceState.city)
def get_city(message: Message) -> None:
    """ Хендлер, ловит город и кидает кнопки для уточнения """
    try:
        city = message.text
        answer = request_by_city(city)

        bot.send_message(message.from_user.id,
                         f'Уточни, пожалуйста:', reply_markup=city_markup(answer))
        bot.set_state(message.from_user.id, HotelLowPriceState.check_city, message.chat.id)
    except ValueError as exc:
        bot.send_message(message.from_user.id, exc)


@bot.callback_query_handler(func=lambda call: True, state=HotelLowPriceState.check_city)
def check_city(call) -> None:
    """
    Обработчик inline кнопок, запоминает id города

    :param call: данные о кнопке

    :return: None
    """

    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data['city_id'] = call.data
        hotels_data['max_photos'] = 10

    bot.send_message(call.message.chat.id,
                     'Окей! Когда заезжаем в отель?\nУкажи дату в формате {год} - {месяц} - {день}')
    bot.set_state(call.message.chat.id, HotelLowPriceState.check_in)


@bot.message_handler(state=HotelLowPriceState.check_in)
def check_in(message: Message) -> None:
    """ Хендлер проверки даты въезда в отель """
    try:
        year, month, day = re.split(",|-|:|' , '|' : '| |' - '", message.text)
        start_date = date(year=int(year), month=int(month), day=int(day))
        if start_date < date.today():
            raise ArithmeticError('Некорректная дата!')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data['check_in'] = start_date
        bot.send_message(message.from_user.id, 'Хорошо, записал. Теперь напиши дату выезда')
        bot.set_state(message.from_user.id, HotelLowPriceState.check_out, message.chat.id)

    except SyntaxError:
        bot.send_message(message.from_user.id, 'Ошибка! Проверь написание')
    except TypeError:
        bot.send_message(message.from_user.id, 'Дата состоит из чисел, а ты что написал?')
    except ValueError:
        bot.send_message(message.from_user.id, 'Что-то не так с датой! Перепроверь формат')
    except ArithmeticError as exc:
        bot.send_message(message.from_user.id, exc)
    except Exception:
        bot.send_message(message.from_user.id, 'Что-то пошло не так! Попробуй еще раз')


@bot.message_handler(state=HotelLowPriceState.check_out)
def check_out(message: Message) -> None:
    """ Хендлер проверки даты выезда из отеля """
    try:

        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            year, month, day = re.split(",|-|:|' , '|' : '| |' - '", message.text)
            end_date = date(year=int(year), month=int(month), day=int(day))
            if end_date < date.today():
                raise ArithmeticError('Некорректная дата!')
            total_days = end_date - hotels_data['check_in']

            if total_days.days >= 0:
                hotels_data['check_out'] = end_date
                hotels_data['total_days'] = total_days.days
                bot.send_message(message.chat.id,
                                 'Хорошо, запрос отправлен. '
                                 'Сколько отелей выводить? (Не больше 25)')
                bot.set_state(message.from_user.id, HotelLowPriceState.count_hotel, message.chat.id)
            else:
                bot.send_message(message.from_user.id,
                                 'Твоя дата выезда из отеля раньше, чем дата въезда!')

    except SyntaxError:
        bot.send_message(message.from_user.id, 'Ошибка! Проверь написание')
    except TypeError:
        bot.send_message(message.from_user.id, 'Дата состоит из чисел, а ты что написал?')
    except ValueError:
        bot.send_message(message.from_user.id, 'Что-то не так с датой! Перепроверь формат')
    except ArithmeticError as exc:
        bot.send_message(message.from_user.id, exc)
    except Exception:
        bot.send_message(message.from_user.id, 'Что-то пошло не так! Попробуй еще раз')


@bot.message_handler(state=HotelLowPriceState.count_hotel)
def get_count_hotel(message: Message) -> None:
    """ Хендлер для получения количества выводимых отелей """
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if int(message.text) <= 25:
                hotels_data['count_hotels'] = int(message.text)
                bot.send_message(message.from_user.id, 'Отлично, а фотографии к ним прилагать? (Да/Нет)')
                bot.set_state(message.from_user.id, HotelLowPriceState.photo_upload, message.chat.id)
            else:
                bot.send_message(message.from_user.id,
                                 f'Я не нашел столько отелей! Максимум - 25')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelLowPriceState.photo_upload)
def get_is_photos(message: Message) -> None:
    """ Хендлер для выяснения необходимости загрузки фотографий """
    if message.text.isalpha():
        if message.text.lower() == 'да':
            bot.send_message(message.from_user.id,
                             f'Хорошо, а сколько фотографий для каждого отеля? Только не больше 10')
            bot.set_state(message.from_user.id, HotelLowPriceState.count_photos, message.chat.id)
        elif message.text.lower() == 'нет':
            bot.send_message(message.from_user.id,
                             'Без проблем! Подожди, идет загрузка ...')
            bot.set_state(message.from_user.id, HotelLowPriceState.info)
            info_output(message)
        else:
            bot.send_message(message.from_user.id,
                             f'Я тебя не понимаю. Ответь прямо: да или нет?')
    else:
        bot.send_message(message.from_user.id, 'Так да или нет?')


@bot.message_handler(state=HotelLowPriceState.count_photos)
def get_count_photos(message: Message) -> None:
    """ Хендлер для получения количества фотографий """
    if message.text.isdigit():
        if int(message.text) <= 10:
            bot.send_message(message.from_user.id, 'Подожди ... Идет загрузка фотографий ...')
            bot.set_state(message.from_user.id, HotelLowPriceState.info, message.chat.id)
            info_output(message, count_photos=int(message.text))
        else:
            bot.send_message(message.from_user.id, 'Не могу загрузить столько! Максимум - 10')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelLowPriceState.info)
def info_output(message: Message, count_photos=0) -> None:
    """ Хендлер для вывода информации """
    try:
        data = request_hotels(message)
        for name, hotel in data.items():
            text = f'Имя отеля: {name}\n' \
                   f'Id отеля: {hotel["hotel_id"]}\n' \
                   f'Адрес: {hotel["address"]}\n'
            for distance in hotel['distance']:
                text += f'Расстояние от {distance[0]} - {distance[1]}\n'
            text += f'На сколько дней бронируем: {hotel["total_days"]}\n' \
                    f'Цена за ночь: {int(hotel["price"]):,d} рублей\n' \
                    f'Суммарная цена: {hotel["total_price"]:,d} рублей\n' \
                    f'Рейтинг: {hotel["rating"]}\n' \
                    f'Ссылка на отель: {hotel["linc"]}\n'

            with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
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

            bot.set_state(message.from_user.id, None, message.chat.id)
    except ValueError as exc:
        bot.send_message(message.from_user.id, exc)
    except telebot.apihelper.ApiException:
        bot.send_message(message.from_user.id, 'Появилась проблема с интернетом! Попробуй еще раз)')
        # При ошибке со стороны Telegram возвращаем юзера к состоянию photo_upload
        bot.send_message(message.from_user.id, 'Надо ли прилагать фотографии к отелям?')
        bot.set_state(message.from_user.id, HotelLowPriceState.photo_upload)
    except Exception:
        bot.send_message(message.from_user.id, 'Технические шоколадки! Не обращай внимания)')
