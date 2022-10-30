from telebot.handler_backends import State, StatesGroup


class HotelLowPriceState(StatesGroup):
    city = State()
    count_hotel = State()
    photo_upload = State()
    count_photos = State()
    info = State()
