from aiogram.filters.callback_data import CallbackData


class MainAdMenuOption(CallbackData, prefix="ad"):
    action: str


class ParamOnEdit(CallbackData, prefix="param"):
    param_name: str


class WatchAllAdsMenuOption(CallbackData, prefix="all_ads"):
    action: str
