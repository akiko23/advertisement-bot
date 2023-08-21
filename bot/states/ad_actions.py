from aiogram.fsm.state import State, StatesGroup


class CreateAdForm(StatesGroup):
    title = State()
    photo = State()
    description = State()
    price = State()


class EditAd(StatesGroup):
    param_to_change = State()
    new_value = State()


class WatchUserAds(StatesGroup):
    on_watch = State()


class WatchAllAds(StatesGroup):
    choose_option = State()
    on_watch = State()


class SearchForAds(StatesGroup):
    on_search = State()

