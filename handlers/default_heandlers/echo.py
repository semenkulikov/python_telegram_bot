from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния

# Мне пришлось закомментировать этот хендлер, так как не срабатывает survey.
# Почему? Вроде все __init__ прописаны, все хендлеры проверены,
# А все равно при вызове команды survey ловит юзера именно этот. Странно
# Может, все зависит от порядка вызова хендлеров? Типа сначала вызывается echo, поэтому он и ловит не ту команду
# Но тогда где искать эти самые вызовы?
# В main? Или в loader? Или в config? Или в set_bot_commands?
# Там ничего напоминающего порядковый импорт хендлеров нет ((
# Помогите, пожалуйста, разобраться

# @bot.message_handler(state=None)
# def bot_echo(message: Message):
#     bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение: "
#                           f"{message.text}")
