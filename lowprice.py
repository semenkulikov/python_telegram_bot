import requests
from dotenv import load_dotenv
import os
import telebot

from pprint import pprint


# locations/v2/search (Deprecating)

# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше
# заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
# a. При положительном ответе пользователь также вводит количество
# необходимых фотографий (не больше заранее определённого
# максимума)

load_dotenv(dotenv_path='.env')

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(os.getenv('TOKEN'))


city = ''
response = {}
max_hotel = 0
max_photos = 0
is_photo = False


def lowprice(message):
    bot.send_message(message.chat.id, 'В каком городе ищем?')
    bot.register_next_step_handler(message, work)


def work(message):

    global city, response, max_hotel
    city = message.text

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    max_hotel = len(response["suggestions"][1]["entities"])

    bot.send_message(
        message.chat.id,
        f'Сколько отелей искать? '
        f'(Максимум - {max_hotel})'
        )
    bot.register_next_step_handler(message, count_hotel)


def count_hotel(message):
    global max_hotel

    if int(message.text) <= max_hotel:
        bot.send_message(message.chat.id, 'Процесс пошел!')
    else:
        bot.send_message(message.chat.id, 'Превышено максимальное количество отелей!')

    bot.send_message(message.chat.id, 'Загружать фотографии? Y/N')
    bot.register_next_step_handler(message, is_photo_output)


def is_photo_output(message):
    pass