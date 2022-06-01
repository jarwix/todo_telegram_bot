""" Работа с данными"""
from datetime import datetime

import dateutil.parser

import pytz


def check_valid(message) -> str:
    """Чекаем на валидность дату"""
    fulldate = None
    try:
        fulldate = datetime.strptime(message, '%H:%M')
    except ValueError:
        pass

    if fulldate is None or fulldate == "":
        try:
            fulldate = datetime.strptime(message, '%H-%M')
        except ValueError:
            pass

    if fulldate is None or fulldate == "":
        try:
            fulldate = dateutil.parser.parse(message, dayfirst=True)
        except ValueError:
            return "error"
        try:
            if (_get_now_datetime() - fulldate).total_seconds() > 0:
                return "error"
        except Exception:
            return "error"

    else:
        datetime_current = _get_now_datetime()
        fulldate = datetime_current.replace(year=datetime_current.year, month=datetime_current.month,
                                               day=datetime_current.day, hour=fulldate.hour, minute=fulldate.minute)
        if ((datetime_current - fulldate).total_seconds()//60) > 0:
            fulldate = fulldate.replace(day=datetime_current.day+1)
    return fulldate.strftime("%H:%M %Y-%m-%d")


async def parsing_text(i, text):
    message_text = ""
    try:
        if (len(text[0]) // 10 - i) == 0:
            for m in range(0, (len(text[0]) % 10)):
                if str(text[0][m + (i*10)][3]) != 'None':
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m + (i*10)][2]) + "\nУведомление: " + str(
                        text[0][m + (i*10)][3]) + "\n\n"
                else:
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m + (i*10)][2]) + "\n\n"
        else:
            for m in range(0, 10):
                if str(text[0][m + (i*10)][3]) != 'None':
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m + (i*10)][2]) + "\nУведомление: " + str(
                        text[0][m + (i*10)][3]) + "\n\n"
                else:
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m + (i*10)][2]) + "\n\n"
    except KeyError:
        pass
    return message_text


def _get_now_datetime() -> datetime:
    """Возвращает сегодняшний datetime с учётом временной зоны Уфы."""
    tz = pytz.timezone("Asia/Yekaterinburg")
    now = datetime.now(tz)
    return now.replace(tzinfo=None)

