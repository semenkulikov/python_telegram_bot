import telebot
from telebot import types

from bestdeal import bestdeal
from history import history
from highprice import highprice
from lowprice import lowprice

from dotenv import load_dotenv
import os


load_dotenv(dotenv_path='.env')
bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     'Начинаем! Я - бот для поиска отелей! Для того, чтобы узнать меня получше, введи команду /help.'
                     )


@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lowprice_command = types.KeyboardButton(text='/lowprice')
    highprice_command = types.KeyboardButton('/highprice')
    bestdeal_command = types.KeyboardButton('/bestdeal')
    history_command = types.KeyboardButton('/history')
    help_command = types.KeyboardButton('/help')
    markup.add(lowprice_command, highprice_command, bestdeal_command, history_command, help_command)
    bot.send_message(
        message.chat.id,
        f"""
Привет, {message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name is not None else ''}!

Вот мои команды:
1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра
(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать историю поиска отелей (команда /history)
""",
        reply_markup=markup
    )


@bot.message_handler(content_types=['text'])
def work(message):
    if message.text.lower() in ['привет', 'салям алейкум', 'hello world', 'hello', 'hi']:
        help(message)
    elif message.text == '/bestdeal':
        bestdeal()
    elif message.text == '/highprice':
        highprice()
    elif message.text == '/history':
        history()
    elif message.text == '/lowprice':
        lowprice(message)
        # bot.send_message(message.chat.id, 'Функция отработала!')
        # Вот здесь lowprice заканчивает сразу после выполнения send_message
        # Как это исправить?
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю ((')


bot.polling(none_stop=True)
