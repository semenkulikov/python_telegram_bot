from telebot.types import Message
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния

@bot.message_handler(state=None)
def bot_echo(message: Message):
    bot.reply_to(message, f"Введи любую команду из меню, чтобы я начал работать\n"
                          f"Либо выбери одну из кнопок, которые я тебе прислал")

