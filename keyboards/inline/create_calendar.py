from loader import bot, calendar, calendar_1_callback
import datetime


def create_calendar(message, now=None):
    """
    Эта функция кидает юзеру календарь
    """

    now = datetime.datetime.now() if now is None else now
    bot.send_message(
        message.chat.id,
        "Выбери дату",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )
