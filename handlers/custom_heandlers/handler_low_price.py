import requests
from loader import bot
from states.low_price_info import HotelLowPriceState
from telebot.types import Message


@bot.message_handler(commands=['lowprice'])
def send_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelLowPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')


@bot.message_handler(state=HotelLowPriceState.city)
def get_city(message: Message) -> None:
    city = message.text
    # request = requests.get('url сайта', timeout=10)
    """ Тут отправляем запрос по данному городу """
    if city:  # request.status_code == requests.codes.ok:
        """ Обработка запроса """
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data['city'] = message.text
            hotels_data['max_hotels'] = max_hotels = 10  # тут берем из request
            hotels_data['max_photos'] = 10  # Тут максимум фотографий. Ну, может быть не тут, потом разберемся

        bot.send_message(message.from_user.id,
                         f'Хорошо, запрос отправлен. Сколько отелей тебе показывать? (не больше {max_hotels})')
    else:
        bot.send_message(message.from_user.id, 'К сожалению, такой город не найден')

    """ И здесь меняем состояние """
    bot.set_state(message.from_user.id, HotelLowPriceState.count_hotel, message.chat.id)


@bot.message_handler(state=HotelLowPriceState.count_hotel)
def get_count_hotel(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if int(message.text) <= hotels_data['max_hotels']:
                hotels_data['count_hotel'] = int(message.text)
                bot.send_message(message.from_user.id, 'Отлично, а фотографии к ним прилагать? (Да/Нет)')
                bot.set_state(message.from_user.id, HotelLowPriceState.photo_upload, message.chat.id)
            else:
                bot.send_message(message.from_user.id,
                                 f'Я не нашел столько отелей! Максимум - {hotels_data["max_hotels"]}')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelLowPriceState.photo_upload)
def get_is_photos(message: Message) -> None:
    if message.text.isalpha():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if message.text.lower() == 'да':
                bot.send_message(message.from_user.id,
                                 f'Хорошо, а сколько фоток? Только не больше {hotels_data["max_photos"]}')
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
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if int(message.text) <= hotels_data['max_photos']:
                hotels_data['count_photos'] = int(message.text)
                bot.send_message(message.from_user.id, 'Подожди ... Идет загрузка фотографий ...')
                bot.set_state(message.from_user.id, HotelLowPriceState.info, message.chat.id)
                info_output(message)
            else:
                bot.send_message(message.from_user.id,
                                 f'Я не нашел столько фотографий! Максимум - {hotels_data["max_photos"]}')
    else:
        bot.send_message(message.from_user.id, 'Твой ответ должен быть числом')


@bot.message_handler(state=HotelLowPriceState.info)
def info_output(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        """ Здесь выводим всю информацию по отелям """
        text = 'Ну все, загрузилось:\n' \
               f'Город - {hotels_data["city"]}\n' \
               f'Максимум отелей - {hotels_data["max_hotels"]}\n' \
               f'Максимум фоток - {hotels_data["max_photos"]}\n' \
               f'Количество фотографий - ' \
               f'{hotels_data["count_photos"] if "count_photos" in hotels_data.keys() else "Не указано"}\n' \
               f'Кол-во отелей - {hotels_data["count_hotel"]}\n'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, None, message.chat.id)
