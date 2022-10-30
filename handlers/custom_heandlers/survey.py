from keyboards.reply.contact import request_contact
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message


@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username}, введи свое имя')


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введи свой возраст')
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Имя может содержать только буквы и состоит из одного слова')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        if 1 <= int(message.text) <= 100:
            bot.send_message(message.from_user.id, 'Записано. Теперь введи страну проживания')
            bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['age'] = message.text
        else:
            bot.send_message(message.from_user.id, 'Возраст - это число от 1 до 100')
    else:
        bot.send_message(message.from_user.id, 'Возраст может быть только числом')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    if message.text.isalpha() or all([True if elem.isalpha() else False for elem in message.text.split()]):
        bot.send_message(message.from_user.id, 'Хорошо, запомнил. А теперь город, пожалуйста')
        bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['country'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Такой страны не существует')


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id,
                         'Спасибо, записал. Теперь отправь свой номер, нажав на кнопку',
                         reply_markup=request_contact())
        bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Такого города не существует')


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
def get_contact(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number

            text = f'Спасибо за предоставленную информацию. \nВаши данные:\n' \
                   f'Имя: {data["name"]}\n' \
                   f'Возраст: {data["age"]}\n' \
                   f'Страна: {data["country"]}\n' \
                   f'Город: {data["city"]}\n' \
                   f'Телефон: {data["phone_number"]}\n'
            bot.send_message(message.from_user.id, text)
            bot.set_state(message.from_user.id, None, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Чтобы отправить контактную информацию, нажми на кнопку')
