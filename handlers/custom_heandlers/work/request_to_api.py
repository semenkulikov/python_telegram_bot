import requests
from typing import List
import json
import os
from dotenv import load_dotenv
from loader import bot
import re

load_dotenv()


def request_to_api(url, headers, querystring):
    try:
        response = requests.get(url=url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
    except (ConnectionError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
        raise ValueError('Ошибка! Какие-то проблемы с интернетом!')


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
            raise PermissionError('К сожалению, такой город не найден. Напиши другой)')

        return cities

    except (LookupError, TypeError, AttributeError):
        raise ValueError('Упс! Что-то пошло не так. Погоди, сейчас исправлю')


def request_hotels(user_id, chat_id, sort_order):
    """
    Функция для обработки второго запроса по отелям. Возвращает словарь, где ключ - имя отеля,
    значение - словарь с такими ключами - [id, адрес, расстояние от центра, цена, суммарная цена, рейтинг, ссылка]
    """
    with bot.retrieve_data(user_id, chat_id) as hotels_data:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": hotels_data['city_id'],
                       "pageNumber": "1",
                       "pageSize": hotels_data['hotels_count'],
                       "checkIn": hotels_data['check_in'],
                       "checkOut": hotels_data['check_out'],
                       "priceMin": hotels_data['price_min'] if 'price_min' in hotels_data.keys() else None,
                       "priceMax": hotels_data['price_max'] if 'price_max' in hotels_data.keys() else None,
                       "adults1": "1",
                       "sortOrder": sort_order,
                       "locale": "ru_RU",
                       "currency": "RUB",
                       "landmarkIds": f'{hotels_data["distance_min"]}, {hotels_data["distance_max"]}'
                       if 'distance_min' and 'distance_max' in hotels_data.keys() else None}
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

                price = hotel['ratePlan']['price']['exactCurrent'] if 'ratePlan' in hotel.keys() else None
                total_days = hotels_data['total_days']
                total_price = round(price * total_days.days if total_days.days != 0 else price)\
                    if isinstance(price, float) else None

                data[name] = {
                    'hotel_id': hotel['id'],
                    'address': f'{response["data"]["body"]["header"]}',
                    'distance': distances,
                    'total_days': total_days,
                    'price': price,
                    'total_price': total_price,
                    'rating': hotel['guestReviews']['rating'] if 'guestReviews' in hotel.keys() else 'Нет',
                    'linc': f'https://www.hotels.com/ho{hotel["id"]}'
                }

            return data

        except (LookupError, TypeError, AttributeError):
            raise ValueError('Упс! Что-то пошло не так. Погоди, сейчас исправлю')


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
        raise ValueError('Упс! Что-то пошло не так. Погоди, сейчас исправлю')