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
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📍 Переглянути локації", callback_data="view_locations"),
        InlineKeyboardButton("📦 Орендувати бокс", callback_data="rent_box")
    )
    await message.answer("👋 Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "view_locations")
async def view_locations(callback_query: types.CallbackQuery):
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

    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="start"))

    await callback_query.message.edit_text("📌 Оберіть локацію для перегляду на карті:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "rent_box")
async def start_request(callback_query: types.CallbackQuery):
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
    await bot.send_message(callback_query.from_user.id, "📍 Оберіть локацію для оренди:", reply_markup=kb)

@dp.message_handler(state=Form.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("📐 5 м²", "📐 10 м²", "📐 15 м²")
    await Form.next()
    await message.answer("📦 Оберіть розмір контейнера:", reply_markup=kb)

@dp.message_handler(state=Form.size)
async def get_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("🧾 <b>Знижка діє лише при повній оплаті за вибраний період.</b>", parse_mode="HTML")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        "🗓 1–3 місяці",
        "🗓 3–6 місяців (-5%)",
        "🗓 6–12 місяців (-10%)"
    )
    await Form.next()
    await message.answer("⏳ Оберіть термін оренди:", reply_markup=kb)

# Додано обробник телефону
@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=Form.phone)
async def get_phone_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    text = f"✅ Нова заявка!\n\n📍 Локація: {data['location']}\n📐 Розмір: {data['size']}\n⏳ Термін: {data['duration']}\n👤 Ім’я: {data['name']}\n📞 Телефон: {data['phone']}"
    await bot.send_message(ADMIN_ID, text)
    await message.answer("🚀 Ваша заявка надіслана!", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
