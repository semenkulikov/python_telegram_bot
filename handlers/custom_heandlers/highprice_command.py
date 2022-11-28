from loader import bot
from states.hotel_info import HotelPriceState
from telebot.types import Message

import datetime


@bot.message_handler(commands=['highprice'])
def send_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        hotels_data['command'] = message.text
        date = datetime.datetime.now()
        hotels_data['date'] = f"{date.date().strftime('%d.%m.%Y')} {date.time()}"
        hotels_data['chat_id'] = message.chat.id
