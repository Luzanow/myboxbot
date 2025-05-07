import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    location = State()
    size = State()
    duration = State()
    name = State()
    phone = State()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📍 Переглянути локації", callback_data="view_locations"),
        InlineKeyboardButton("📦 Орендувати бокс", callback_data="make_request")
    )
    await message.answer("Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "view_locations")
async def view_locations(callback_query: types.CallbackQuery):
    locations = [
        ("📍вул. Новокостянтинівська, 22/15", "https://maps.app.goo.gl/RpDz2E671UVgkQg57"),
        ("📍просп. Відрадний, 107", "https://maps.app.goo.gl/gjmy3mC4TmWH27r87"),
        ("📍вул. Кирилівська, 41", "https://maps.app.goo.gl/5QYTYfAWqQ7W8pcm7"),
        ("📍вул. Дегтярівська, 21", "https://maps.app.goo.gl/2zrWpCkeF3r5TMh39"),
        ("📍вул. Cадова, 16", "https://maps.app.goo.gl/sCb6wYY3YQtVwVao7"),
        ("📍вул. Безняковская, 21", "https://maps.google.com/?q=50.402645,30.324247"),
        ("📍вул. Миколи Василенка, 2", "https://maps.app.goo.gl/Cp6tUB7DGbLz3bdFA"),
        ("📍вул. Вінстона Черчилля, 42", "https://maps.app.goo.gl/FNuaeyQHFxaxgCai9"),
        ("📍вул. Лугова 9", "https://maps.app.goo.gl/aCrfjN9vbBjhM17YA"),
        ("📍вул. Євгенія Харченка, 35", "https://maps.app.goo.gl/MpGAvtA6awMYKn7s6"),
        ("📍вул. Володимира Брожка, 38/58", "https://maps.app.goo.gl/vZAjD6eo84t8qyUk6"),
        ("📍вул. Межигірська, 78", "https://maps.app.goo.gl/MpGAvtA6awMYKn7s6")
    ]
    for name, url in locations:
        btn = InlineKeyboardMarkup().add(InlineKeyboardButton("Відкрити на карті", url=url))
        await bot.send_message(callback_query.from_user.id, f"Локація: {name}", reply_markup=btn)

@dp.callback_query_handler(lambda c: c.data == "make_request")
async def start_request(callback_query: types.CallbackQuery):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        "вул. Новокостянтинівська, 22/15",
        "просп. Відрадний, 107",
        "вул. Кирилівська, 41",
        "вул. Дегтярівська, 21",
        "вул. Cадова, 16",
        "вул. Безняковская, 21",
        "вул. Миколи Василенка, 2",
        "вул. Вінстона Черчилля, 42",
        "вул. Лугова 9",
        "вул. Євгенія Харченка, 35",
        "вул. Володимира Брожка, 38/58",
        "вул. Межигірська, 78"
    )
    await Form.location.set()
    await bot.send_message(callback_query.from_user.id, "Оберіть локацію:", reply_markup=kb)

@dp.message_handler(state=Form.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("5 м²", "10 м²", "15 м²")
    await Form.next()
    await message.answer("Оберіть розмір контейнера:", reply_markup=kb)

@dp.message_handler(state=Form.size)
async def get_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        "1–3 місяці", "3–6 місяців (-5%)", "6–12 місяців (-10%)"
    )
    await Form.next()
    await message.answer("Оберіть термін оренди:\n\n🧾 Знижка діє лише при повній оплаті за вибраний період", reply_markup=kb)

@dp.message_handler(state=Form.duration)
async def get_duration(message: types.Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await Form.next()
    await message.answer("Введіть ваше ім’я:", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton("📱 Поділитися номером", request_contact=True)
    )
    await Form.next()
    await message.answer("Надішліть ваш номер телефону:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def get_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish(message, phone, state)

@dp.message_handler(state=Form.phone)
async def get_phone_text(message: types.Message, state: FSMContext):
    await finish(message, message.text, state)

async def finish(message: types.Message, phone, state: FSMContext):
    data = await state.get_data()
    text = (
        f"Нова заявка:\n\n"
        f"Локація: {data['location']}\n"
        f"Розмір: {data['size']}\n"
        f"Термін: {data['duration']}\n"
        f"Ім’я: {data['name']}\n"
        f"Телефон: {phone}"
    )
    await bot.send_message(ADMIN_ID, text)
    await message.answer("Дякуємо! Ваша заявка надіслана. Ми з вами зв'яжемось найближчим часом.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
