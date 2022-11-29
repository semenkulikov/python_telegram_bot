from loader import bot
import handlers  # noqa
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from handlers.custom_heandlers.work.dbworker import create_tables, clear_database

if __name__ == '__main__':
    create_tables()
    clear_database()
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()
