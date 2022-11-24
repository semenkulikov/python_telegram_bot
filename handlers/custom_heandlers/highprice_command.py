from loader import bot
from states.hotel_info import HotelPriceState
from telebot.types import Message


@bot.message_handler(commands=['highprice'])
def send_highprice(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Привет, {message.from_user.first_name}, напиши город, где будем искать отели')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        hotels_data['command'] = message.text
