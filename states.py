from aiogram.dispatcher.filters.state import StatesGroup, State


class Advertisement(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()

    class AdvertisementActions(StatesGroup):
        del_action = State()
        change_param = State()


