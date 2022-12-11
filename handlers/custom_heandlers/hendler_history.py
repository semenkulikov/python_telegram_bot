from loader import bot
from telebot.types import Message, InputMediaPhoto
from handlers.custom_heandlers.work import dbworker


@bot.message_handler(commands=["history"])
def history(message: Message) -> None:
    history_info = dbworker.get_history(chat_id=str(message.chat.id))
    if history_info:
        for record in history_info:
            uid = record[0]
            text = f'Дата и время запроса: {record[2]}' \
                   f'\nКоманда: {record[4]}' \
                   f'\nГород: {record[3]}\n'
            hotels = dbworker.get_hotels(uid=uid)
            if hotels:
                text += '\nНайденные отели:\n'
                bot.send_message(message.from_user.id, text)
                for i, hotel in enumerate(hotels):
                    hotel_id = hotel[1]
                    photos = [elem[0] for elem in dbworker.get_photos(hotel_id=hotel_id)]
                    text_hotel = f"\n{i + 1}.\nНазвание отеля: {hotel[2]}\n" \
                                 f"Адрес: {hotel[3]}" \
                                 f"\nСсылка: {hotel[5]}" \
                                 f"\nЦена за сутки: {hotel[4]} USD\n"
                    bot.send_message(message.from_user.id, text=text_hotel)
                    if photos:
                        bot.send_message(message.from_user.id, 'Фото отеля:\n')
                        if len(photos) >= 2:
                            bot.send_media_group(message.from_user.id, media=[InputMediaPhoto(url) for url in photos])
                        else:
                            bot.send_photo(message.from_user.id, photo=photos[0])
            else:
                bot.send_message(message.from_user.id, text=text)
                bot.send_message(message.from_user.id, 'Отелей не найдено')
        bot.send_message(message.from_user.id, 'Готово!')

    else:
        bot.send_message(chat_id=message.chat.id, text='Записей не найдено')
