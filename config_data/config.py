import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены, т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('survey', 'Опрос'),
    ('lowprice', 'Топ самых дешевых отелей в городе'),
    ('highprice', 'Топ самых дорогих отелей в городе'),
    ('bestdeal', 'Топ самых дешевых и ближе всего расположенных к центру города отелей'),
    ('history', 'История поиска отелей')
)
