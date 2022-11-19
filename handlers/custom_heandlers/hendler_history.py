from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['history'])
def print_info(message: Message):
    bot.send_message(message.from_user.id, 'История поиска отелей')
