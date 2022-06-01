from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

home = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕Добавить"),
            KeyboardButton(text="📅Все задачи"),
        ]
    ],
    resize_keyboard=True
)

save = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝Сохранить как заметку"),
            KeyboardButton(text="🔙Отмена")
        ]
    ],
    resize_keyboard=True
)
