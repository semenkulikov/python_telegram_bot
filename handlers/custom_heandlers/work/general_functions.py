from telebot.types import Message, InputMediaPhoto
from handlers.custom_heandlers.work.request_to_api import request_hotels, requests_photos
from loader import bot
from states.hotel_info import HotelPriceState

from handlers.custom_heandlers.work import dbworker


@bot.message_handler(state=HotelPriceState.info)
def get_search_results(message: Message, count_photos=0, stop_iter=5, sort_order="PRICE", call_chat_id=None) -> None:
    """
    Хендлер для вывода информации

    :param call_chat_id: Нужен для того, чтобы правильно открывать контекстовый мессенджер
    :param sort_order: режим запроса
    :param message: сообщение юзера
    :param count_photos: кол-во фотографий для каждого отеля
    :param stop_iter: при ошибке вся загрузка начнется сначала, и этот параметр нужен для предотвращения рекурсии
    :return: None
    """

    if call_chat_id is None:
        user_id = message.from_user.id
        chat_id = message.chat.id
    else:
        user_id, chat_id = call_chat_id, call_chat_id

    if stop_iter:
        try:
            with bot.retrieve_data(user_id, chat_id) as hotels_data:
                data = request_hotels(user_id=user_id, chat_id=chat_id, sort_order=sort_order)
                hotel_count = 0

                dbworker.set_history((
                    hotels_data['city_id'],
                    str(hotels_data['chat_id']),
                    hotels_data['date'],
                    hotels_data['city'],
                    hotels_data['command']
                ))

                for name, hotel in data.items():
                    hotel_count += 1
                    text = f'Имя отеля: {name}\n' \
                           f'Id отеля: {hotel["hotel_id"]}\n' \
                           f'Адрес: {hotel["address"]}\n'
                    for distance in hotel['distance']:
                        text += f'Расстояние от {distance[0]} - {distance[1]}\n'

                        text += f'Диапазон цен: от {hotels_data["price_min"]} до {hotels_data["price_max"]}\n' \
                            if "price_min" in hotels_data.keys() else ''

                        text += f'Диапазон расстояний: от {hotels_data["distance_min"]} до ' \
                                f'{hotels_data["distance_max"]}\n'\
                            if "distance_min" in hotels_data.keys() else ''

                    text += f'На сколько дней бронируем: {hotel["total_days"].days}\n'

                    text += f'Цена за ночь: {int(hotel["price"]):,d} рублей\n' \
                        if hotel['price'] is not None else ''

                    text += f'Суммарная цена: {hotel["total_price"]:,d} рублей\n' \
                        if hotel['price'] is not None else ''

                    text += f'Рейтинг: {hotel["rating"]}\n' \
                            f'Ссылка на отель: {hotel["linc"]}\n'

                    dbworker.set_hotels((
                        hotels_data['city_id'],
                        hotel['hotel_id'],
                        name,
                        hotel['address'],
                        hotel['price'],
                        hotel['linc']
                    ))

                    if count_photos:
                        data = requests_photos(
                            hotel_id=hotel["hotel_id"],
                            max_photos=count_photos
                        )
                        photos = [InputMediaPhoto(elem) for elem in data]
                        if len(photos) >= 2:
                            bot.send_media_group(user_id, photos)
                        else:
                            bot.send_photo(user_id, photo=data[0])

                        for photo in data:
                            dbworker.set_photos((
                                hotel['hotel_id'],
                                photo
                            ))

                    bot.send_message(user_id, text)
                    bot.send_message(user_id, f'Топ {hotel_count}')

                if data:
                    bot.send_message(user_id, 'Готово!')
                else:
                    bot.send_message(user_id, 'К сожалению, такие отели не найдены ((')
                bot.set_state(user_id, None, chat_id)

        except ValueError:
            stop_iter -= 1
            get_search_results(message, count_photos=count_photos, stop_iter=stop_iter, call_chat_id=call_chat_id)
        except Exception:
            stop_iter -= 1
            get_search_results(message, count_photos=count_photos, stop_iter=stop_iter, call_chat_id=call_chat_id)
    else:
        bot.send_message(user_id,
                         'Упс, ошибочка!\nПроверь соединение с интернетом')
        bot.set_state(user_id, None, chat_id)
