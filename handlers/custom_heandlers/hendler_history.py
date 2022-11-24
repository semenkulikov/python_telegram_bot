from loader import bot
from telebot.types import Message
from handlers.custom_heandlers.work import dbworker


@bot.message_handler(commands=["history"])
def history(message: Message) -> None:
    history_info = dbworker.get_history(chat_id=str(message.chat.id))
    if history_info:
        for record in history_info:
            uid = record[0]
            string = f'Дата и время запроса: {record[1]}' \
                     f'\nКоманда: {record[3]}' \
                     f'\nГород: {record[2]}'
            bot.send_message(chat_id=message.chat.id, text=string)
            hotels = dbworker.get_hotels(uid=uid)
            if hotels:
                for hotel in hotels:
                    bot.send_message(chat_id=message.chat.id,
                                     text=f"Название отеля: {hotel[3]}\n"
                                          f"Адрес: {hotel[3]}"
                                          f"\nСсылка: {hotel[5]}"
                                          f"\n1Цена за сутки: {hotel[4]} RUB",
                                     disable_web_page_preview=True)
    else:
        bot.send_message(chat_id=message.chat.id, text='Записей не найдено')
