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
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("📍 Переглянути локації"),
        KeyboardButton("📦 Орендувати бокс")
    )
    await message.answer("👋 Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.message_handler(lambda message: message.text == "📍 Переглянути локації")
async def view_locations(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    locations = [
        ("📍 вул. Новокостянтинівська, 22/15", "https://maps.app.goo.gl/RpDz2E671UVgkQg57"),
        ("📍 просп. Відрадний, 107", "https://maps.app.goo.gl/gjmy3mC4TmWH27r87"),
        ("📍 вул. Кирилівська, 41", "https://maps.app.goo.gl/5QYTYfAWqQ7W8pcm7"),
        ("📍 вул. Дегтярівська, 21", "https://maps.app.goo.gl/2zrWpCkeF3r5TMh39"),
        ("📍 вул. Cадова, 16", "https://maps.app.goo.gl/sCb6wYY3YQtVwVao7"),
        ("📍 вул. Безняковская, 21", "https://maps.google.com/?q=50.402645,30.324247"),
        ("📍 вул. Миколи Василенка, 2", "https://maps.app.goo.gl/Cp6tUB7DGbLz3bdFA"),
        ("📍 вул. Вінстона Черчилля, 42", "https://maps.app.goo.gl/FNuaeyQHFxaxgCai9"),
        ("📍 вул. Лугова 9", "https://maps.app.goo.gl/aCrfjN9vbBjhM17YA"),
        ("📍 вул. Євгенія Харченка, 35", "https://maps.app.goo.gl/MpGAvtA6awMYKn7s6"),
        ("📍 вул. Володимира Брожка, 38/58", "https://maps.app.goo.gl/vZAjD6eo84t8qyUk6"),
        ("📍 вул. Межигірська, 78", "https://maps.app.goo.gl/MpGAvtA6awMYKn7s6")
    ]
    for name, url in locations:
        kb.add(InlineKeyboardButton(name, url=url))

    await message.answer("📌 Оберіть локацію для перегляду на карті:", reply_markup=kb)

@dp.message_handler(lambda message: message.text == "📦 Орендувати бокс")
async def start_request(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        "📍 вул. Новокостянтинівська, 22/15",
        "📍 просп. Відрадний, 107",
        "📍 вул. Кирилівська, 41",
        "📍 вул. Дегтярівська, 21",
        "📍 вул. Cадова, 16",
        "📍 вул. Безняковская, 21",
        "📍 вул. Миколи Василенка, 2",
        "📍 вул. Вінстона Черчилля, 42",
        "📍 вул. Лугова 9",
        "📍 вул. Євгенія Харченка, 35",
        "📍 вул. Володимира Брожка, 38/58",
        "📍 вул. Межигірська, 78"
    )
    await Form.location.set()
    await message.answer("✅ Обрано режим оренди.\n📍 Будь ласка, оберіть локацію:", reply_markup=kb)

@dp.message_handler(state=Form.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("📐 5 м²", "📐 10 м²", "📐 15 м²")
    await Form.size.set()
    await message.answer("✅ Локація збережена.\n📦 Оберіть розмір контейнера:", reply_markup=kb)

@dp.message_handler(state=Form.size)
async def get_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await Form.duration.set()
    await message.answer("🧾Увага! Знижка діє лише при повній оплаті за вибраний період.")
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        "🗓 1–3 місяці",
        "🗓 3–6 місяців (-3%)",
        "🗓 6-11 місяців (-5%)",
        "🗓 від 12 місяців (-10%)"
    )
    await message.answer("⏳ Оберіть термін оренди:", reply_markup=kb)

@dp.message_handler(state=Form.duration)
async def get_duration(message: types.Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await Form.name.set()
    await message.answer("👤 Введіть ваше ім’я:")

@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton("📱 Поділитися номером", request_contact=True)
    )
    await Form.phone.set()
    await message.answer("📞 Надішліть ваш номер телефону:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def get_phone_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    text = (
        f"✅ Нова заявка!\n\n📍 Локація: {data['location']}\n"
        f"📐 Розмір: {data['size']}\n"
        f"⏳ Термін: {data['duration']}\n"
        f"👤 Ім’я: {data['name']}\n"
        f"📞 Телефон: {data['phone']}"
    )
    await bot.send_message(ADMIN_ID, text)
    main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add("⬅️ Повернутись на головну")
    await message.answer("🚀 Ваша заявка надіслана! Дякуємо за користування MyBox!", reply_markup=main_kb)
    await state.finish()

@dp.message_handler(lambda message: message.text == "⬅️ Повернутись на головну")
async def return_home(message: types.Message):
    await start(message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
