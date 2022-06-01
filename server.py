import asyncio
import logging


import config
import todo
import keyboards
import keyboards.inline_keyboards
import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

API_TOKEN = config.TELEGRAM_API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler()


class NewTasks(StatesGroup):
    save_data = State()
    new_time = State()
    numbers = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для планировки задач\n\n"
        "Для добавления новой задачи: ➕Добавить\n"
        "Посмотреть список задач: 📅Все задачи\n",
        reply_markup=keyboards.home)


@dp.message_handler(Text(equals=["➕Добавить"]))
async def add_new_task(message: types.Message):
    """Добавляем новую задачу в БД"""
    answer_message = "Введите текст того, о чем Вам напомнить."
    await message.answer(answer_message)


@dp.message_handler(Text(equals=["📅Все задачи"]))
async def all_tasks(message: types.Message, state: FSMContext):
    """Отправляет все задачи текущего аккаунта"""
    message_send = await db.take_all_tasks(message.from_user.id)
    choice_key = await keyboards.inline_keyboards.choice_add(0, message_send)
    await state.update_data(todo_list=message_send, current_page=0, user_id=message.from_user.id)
    message_send = await todo.parsing_text(0, message_send)
    if message_send is not None and message_send != "":
        await message.answer(message_send, reply_markup=choice_key)
    else:
        await message.answer("😐Ничего нет", reply_markup=keyboards.home)
        await state.finish()


@dp.message_handler(state=NewTasks.new_time)
async def add_time(message: types.Message, state: FSMContext):
    """Находимся в меню времени"""
    if message.text == "📝Сохранить как заметку":
        user_data = await state.get_data()
        await db.add_new_task(message.from_user.id, user_data['newtask'])
        await state.finish()
        await message.answer("Сохранили заметку",
                             reply_markup=keyboards.home)
        return

    elif message.text == "🔙Отмена":
        await state.finish()
        await message.answer("Ладно, ничего не сохраняем",
                             reply_markup=keyboards.home)
        return

    check_datetime = todo.check_valid(message.text)
    if check_datetime == "error":
        await message.answer("Введите время напоминания в нормальном формате и в будущем времени, либо нажмите"
                             "\"📝Сохранить как заметку\", если хотите сохранить её без времени.",
                             reply_markup=keyboards.save)
        return

    await state.update_data(newtime=check_datetime)
    user_data = await state.get_data()
    await message.answer(
        f"Проверьте заметку:\n{user_data['newtask']}\n\nCо временем напоминания:\n{user_data['newtime']}\n\n"
        f"И нажмите \"📝Сохранить как заметку\", если всё верно.",
        reply_markup=keyboards.save)
    await NewTasks.save_data.set()


@dp.message_handler(state=NewTasks.save_data)
async def add_data(message: types.Message, state: FSMContext):
    """Находимся в меню сохранения новой задачи"""
    if message.text == "📝Сохранить как заметку":
        user_data = await state.get_data()
        await db.add_new_task(message.from_user.id, user_data['newtask'], user_data['newtime'])
        await state.finish()
        await message.answer("Сохранили заметку",
                             reply_markup=keyboards.home)
        await state.finish()

    elif message.text == "🔙Отмена":
        await state.finish()
        await message.answer("Ладно, ничего не сохраняем",
                             reply_markup=keyboards.home)

    else:
        await message.answer("Непонятная команда",
                             reply_markup=keyboards.save)


@dp.callback_query_handler(lambda call: call.data in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
async def menu_numbers(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if str(user_data['todo_list'][0][int(call.data) - 1 + user_data['current_page'] * 10][3]) != 'None':
        text_data = str(user_data['todo_list'][0][int(call.data) - 1 + user_data['current_page'] * 10][2]) + \
                    "\nУведомление: " + str(
            user_data['todo_list'][0][int(call.data) - 1 + user_data['current_page'] * 10][3]) + "\n\n"
    else:
        text_data = str(user_data['todo_list'][0][int(call.data) - 1 + user_data['current_page'] * 10][2]) + "\n\n"
    await state.update_data(number=int(call.data) - 1 + user_data['current_page'] * 10)
    if text_data is not None and text_data != "":
        await call.message.edit_text(text=text_data)
        await asyncio.sleep(0.3)
        await call.message.edit_reply_markup(reply_markup=keyboards.setup)
    else:
        await state.finish()
        await call.message.delete()
        await types.Message.answer("😐Ничего нет", reply_markup=keyboards.home)


@dp.callback_query_handler(lambda call: call.data == "success")
async def success_menu(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    take_data = await db.take_all_tasks(user_data['user_id'])
    await db.delete_task(take_data[0][user_data["number"]][0])
    take_data = await db.take_all_tasks(user_data['user_id'])
    choice_key = await keyboards.inline_keyboards.choice_add(user_data['current_page'], take_data)
    await state.update_data(todo_list=take_data)
    take_data = await todo.parsing_text(user_data['current_page'], take_data)
    if take_data is not None and take_data != "":
        await call.message.edit_text(text=take_data)
        await asyncio.sleep(0.3)
        await call.message.edit_reply_markup(reply_markup=choice_key)
    else:
        await state.finish()
        await call.message.delete()
        await types.Message.answer("😐Ничего нет", reply_markup=keyboards.home)


@dp.callback_query_handler(lambda call: call.data == "back")
async def success_menu(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    take_data = await db.take_all_tasks(user_data['user_id'])
    choice_key = await keyboards.inline_keyboards.choice_add(user_data['current_page'], take_data)
    await state.update_data(todo_list=take_data)
    take_data = await todo.parsing_text(user_data['current_page'], take_data)
    if take_data is not None and take_data != "":
        await call.message.edit_text(text=take_data)
        await asyncio.sleep(0.3)
        await call.message.edit_reply_markup(reply_markup=choice_key)
    else:
        await state.finish()
        await call.message.delete()
        await types.Message.answer("😐Ничего нет", reply_markup=keyboards.home)


@dp.callback_query_handler(lambda call: call.data == "backbut")
async def success_menu(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(current_page=user_data['current_page'] - 1)
    user_data = await state.get_data()
    take_data = await db.take_all_tasks(user_data['user_id'])
    choice_key = await keyboards.inline_keyboards.choice_add(user_data['current_page'], take_data)
    await state.update_data(todo_list=take_data)
    take_data = await todo.parsing_text(user_data['current_page'], take_data)
    if take_data is not None and take_data != "":
        await call.message.edit_text(text=take_data)
        await asyncio.sleep(0.3)
        await call.message.edit_reply_markup(reply_markup=choice_key)
    else:
        await state.finish()
        await call.message.delete()
        await types.Message.answer("😐Ничего нет", reply_markup=keyboards.home)


@dp.callback_query_handler(lambda call: call.data == "nextbut")
async def success_menu(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(current_page=user_data['current_page'] + 1)
    user_data = await state.get_data()
    take_data = await db.take_all_tasks(user_data['user_id'])
    choice_key = await keyboards.inline_keyboards.choice_add(user_data['current_page'], take_data)
    await state.update_data(todo_list=take_data)
    take_data = await todo.parsing_text(user_data['current_page'], take_data)
    if take_data is not None and take_data != "":
        await call.message.edit_text(text=take_data)
        await asyncio.sleep(0.3)
        await call.message.edit_reply_markup(reply_markup=choice_key)
    else:
        await types.Message.answer("😐Ничего нет", reply_markup=keyboards.home)


@dp.callback_query_handler(text="cancel")
async def cancel_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


@dp.message_handler()
async def take_task(message: types.Message, state: FSMContext):
    """Обрабатывает просто текст, как напоминание"""
    await state.update_data(newtask=message.text[:99])
    await message.answer("Введите время напоминания, или нажмите \"📝Сохранить как заметку\".",
                         reply_markup=keyboards.save)
    await NewTasks.new_time.set()


def schedule_jobs():
    scheduler.add_job(db_check, trigger='cron', minute='*/1')


async def on_startup(_):
    schedule_jobs()


async def db_check():
    take_data = await db.check_datetime()
    for m in range(0, (len(take_data[0]))):
        await bot.send_message(str(take_data[0][m][1]), "Следующая задача:" + str(take_data[0][m][2]) +
                               "\nВремя выполнения: " + str(take_data[0][m][3]))
        await asyncio.sleep(0.3)


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
