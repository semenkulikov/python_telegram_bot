from telebot.handler_backends import State, StatesGroup


class HotelPriceState(StatesGroup):
    city = State()
    check_city = State()
    price_min = State()
    price_max = State()
    distance_min = State()
    distance_max = State()
    check_in = State()
    check_out = State()
    count_hotel = State()
    count_photos = State()
    info = State()
