from telebot.handler_backends import State, StatesGroup


class HotelBestPriceState(StatesGroup):
    city = State()
    check_city = State()
    price_min = State()
    price_max = State()
    check_in = State()
    check_out = State()
    count_hotel = State()
    photo_upload = State()
    count_photos = State()
    info = State()