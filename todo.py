""" Работа с данными"""
import re
from typing import List, NamedTuple, Optional
from datetime import datetime, date, timedelta
from urllib import response

import dateutil.parser

import pytz


def check_valid(message) -> str:
    """Чекаем на валидность дату"""
    fulldate = None
    try:
        fulldate = datetime.strptime(message, '%H:%M')
    except ValueError:
        pass

    if fulldate is None:
        try:
            fulldate = datetime.strptime(message, '%H-%M')
        except ValueError:
            pass

    if fulldate is None:
        try:
            fulldate = dateutil.parser.parse(message, dayfirst=True)
        except ValueError:
            return "error"
        try:
            if (_get_now_datetime() - fulldate).total_seconds() > 0:
                return "error"
        except Exception:
            try:
                if (_get_now_datetime() - fulldate).total_seconds() > 0:
                    return "error"
            except Exception:
                return "error"
    else:
        if ((_get_now_datetime() - fulldate).total_seconds()/60) > 0:
            fulldate = _get_now_datetime().replace(hour=fulldate.hour, minute=fulldate.minute)
        else:
            fulldate = _get_now_datetime().replace(hour=fulldate.hour, minute=fulldate.minute, day=_get_now_datetime().day+1)
    return fulldate.strftime("%H:%M %Y-%m-%d")


async def parsing_text(i, text):
    message_text = ""
    try:
        if (len(text[0]) // 10 - i) == 0:
            for m in range(0, (len(text[0]) % 10)):
                if str(text[0][m][3]) != 'None':
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m][2]) + "\nУведомление: " + str(
                        text[0][m][3]) + "\n\n"
                else:
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m][2]) + "\n\n"
        else:
            for m in range(0, 10):
                if str(text[0][m][3]) != 'None':
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m][2]) + "\nУведомление: " + str(
                        text[0][m][3]) + "\n\n"
                else:
                    message_text += "Задача №" + str(m + 1) + ": " + str(text[0][m][2]) + "\n\n"
    except KeyError:
        pass
    return message_text


def _get_now_datetime() -> datetime:
    """Возвращает сегодняшний datetime с учётом временной зоны Уфы."""
    tz = pytz.timezone("Asia/Yekaterinburg")
    now = datetime.now(tz)
    return now.replace(tzinfo=None)

