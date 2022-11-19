from telebot.handler_backends import State, StatesGroup


class HotelLowPriceState(StatesGroup):
    city = State()
    check_city = State()
    check_in = State()
    check_out = State()
    count_hotel = State()
    count_photos = State()
    info = State()
