from bot.consts import FORBIDDEN_CHARS

ERR_PREF = "❗️Некорректный формат\n"


def check_valid_text_param(param_to_change: str, msg_text: str) -> tuple[str | None, ...]:
    match param_to_change:
        case "photo":
            new_val, err = None, "Incorrect format"
        case "title":
            new_val, err = check_valid_title(msg_text)
        case "description":
            new_val, err = check_valid_description(msg_text)
        case "price":
            new_val, err = check_valid_price(msg_text)
        case _:
            new_val, err = msg_text, None

    return new_val, err


def check_valid_title(text: str):
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if not 2 <= len(text) <= 40:
        return None, ERR_PREF + "Длина заголовка должна быть не меньше 2 и не больше 40 символов"
    return text, None


def check_valid_description(text: str):
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if len(text) < 25:
        return None, ERR_PREF + "Длина описания должна быть не меньше 25 символов"
    return text, None


def check_valid_price(text: str):
    if not text.isdigit():
        return None, ERR_PREF + "Введенное значение не является числом"
    if not 1 <= int(text) <= 40000:
        return None, ERR_PREF + "Цена должна быть не меньше 1$ и не больше 40000$"
    return int(text), None


def check_valid_msg(text: str) -> tuple[str | None, ...]:
    if any(ch in text for ch in FORBIDDEN_CHARS):
        return None, ERR_PREF + "Вы использовали запрещенный символ из этого списка: " + repr(FORBIDDEN_CHARS)
    return text, None
