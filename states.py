from aiogram.dispatcher.filters.state import StatesGroup, State


class Advertisement(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()

    class AdvertisementActions(StatesGroup):
        class SearchStates(StatesGroup):
            get_value = State()
            check_value = State()
            processing_value = State()

        del_action = State()
        change_param = State()




