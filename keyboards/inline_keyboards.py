from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


async def choice_add(i, message):
    choice = InlineKeyboardMarkup(row_width=2)
    if (len(message[0]) // 10 - i) == 0:
        for m in range(1, (len(message[0]) % 10) + 1):
            choice.insert(InlineKeyboardButton(text=str(m), callback_data=str(m)))
    else:
        for m in range(1, 11):
            choice.insert(InlineKeyboardButton(text=str(m), callback_data=str(m)))
    if i > 0:
        update_back = InlineKeyboardButton(text="⬅Предыдущие", callback_data="backbut")
        choice.insert(update_back)

    if (len(message[0])-1) // 10 - i > 0:
        update_next = InlineKeyboardButton(text="➡Следующие", callback_data="nextbut")
        choice.insert(update_next)

    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    choice.insert(cancel_button)
    return choice


setup = InlineKeyboardMarkup(row_width=2)

update_success = InlineKeyboardButton(text="Отметить как выполненное", callback_data="success")
setup.insert(update_success)

update_prev = InlineKeyboardButton(text="⬅Назад", callback_data="back")
setup.insert(update_prev)

cancel_success = InlineKeyboardButton(text="Отмена", callback_data="cancel")
setup.insert(cancel_success)
