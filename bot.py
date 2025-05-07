import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
    await send_main_menu(message.chat.id)

async def send_main_menu(chat_id):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("📦 Орендувати BOX", callback_data="order"),
        InlineKeyboardButton("📍 Переглянути локації", callback_data="locations"),
        InlineKeyboardButton("📞 Зв’язатись з нами", callback_data="contact")
    )
    await bot.send_message(chat_id, "👋 Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "start")
async def back_to_main(callback_query: types.CallbackQuery):
    await send_main_menu(callback_query.from_user.id)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "contact")
async def contact_info(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🌐 Сайт MyBox", url="https://www.mybox.kiev.ua"),
        InlineKeyboardButton("💬 Написати в Telegram", url="https://t.me/+380959387317"),
        InlineKeyboardButton("⬅️ Повернутись назад", callback_data="start")
    )
    await bot.send_message(callback_query.from_user.id, "📞 Контакт:\n👤 Тарас\n📱 +380959387317", reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "locations")
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
    kb.add(InlineKeyboardButton("⬅️ Повернутись назад", callback_data="start"))
    await bot.send_message(callback_query.from_user.id, "📌 Оберіть локацію:", reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "order")
async def start_order(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    addresses = [
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
    ]
    for addr in addresses:
        kb.add(InlineKeyboardButton(addr, callback_data=f"loc_{addr}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="start"))
    await Form.location.set()
    await bot.send_message(callback_query.from_user.id, "📍 Оберіть локацію для оренди:", reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("loc_"), state=Form.location)
async def get_location(callback_query: types.CallbackQuery, state: FSMContext):
    location = callback_query.data.replace("loc_", "")
    await state.update_data(location=location)
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("📐 5м² – 1850грн", callback_data="size_5"),
        InlineKeyboardButton("📐 7.5м² – 2350грн", callback_data="size_7"),
        InlineKeyboardButton("📐 15м² – 3800грн", callback_data="size_15"),
        InlineKeyboardButton("📐 30м² – 6650грн", callback_data="size_30"),
    ).add(InlineKeyboardButton("⬅️ Назад", callback_data="order"))
    await Form.size.set()
    await bot.send_message(callback_query.from_user.id, "📦 Оберіть розмір! ціна вказана за місяць оренди!:", reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("size_"), state=Form.size)
async def get_size(callback_query: types.CallbackQuery, state: FSMContext):
    size_map = {
        "size_5": "5м² – 1850грн",
        "size_7": "7.5м² – 2350грн",
        "size_15": "15м² – 3800грн",
        "size_30": "30м² – 6650грн"
    }
    size = size_map.get(callback_query.data)
    await state.update_data(size=size)
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🗓 1–3 місяці", callback_data="dur_1"),
        InlineKeyboardButton("🗓 3–6 місяців (-3%)", callback_data="dur_3"),
        InlineKeyboardButton("🗓 6–12 місяців (-5%)", callback_data="dur_6"),
        InlineKeyboardButton("🗓 від 12 місяців (-10%)", callback_data="dur_12"),
        InlineKeyboardButton("⬅️ Назад", callback_data="order")
    )
    await Form.duration.set()
    await bot.send_message(callback_query.from_user.id, "🧾 Увага! Знижка діє лише при повній оплаті за вибраний період.\n⏳ Оберіть термін:", reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("dur_"), state=Form.duration)
async def get_duration(callback_query: types.CallbackQuery, state: FSMContext):
    duration_map = {
        "dur_1": "1–3 місяці",
        "dur_3": "3–6 місяців (-3%)",
        "dur_6": "6–12 місяців (-5%)",
        "dur_12": "від 12 місяців (-10%)"
    }
    duration = duration_map.get(callback_query.data)
    await state.update_data(duration=duration)
    await Form.name.set()
    await bot.send_message(callback_query.from_user.id, "👤 Введіть ваше ім’я:")
    await callback_query.answer()

@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.phone.set()
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton("📱 Поділитися номером", request_contact=True)
    )
    await message.answer("📞 Надішліть номер телефону:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def get_phone_contact(message: types.Message, state: FSMContext):
    await message.answer("✅ Дякуємо!", reply_markup=ReplyKeyboardRemove())
    await finish(message, message.contact.phone_number, state)

@dp.message_handler(state=Form.phone)
async def get_phone_text(message: types.Message, state: FSMContext):
    await message.answer("✅ Дякуємо!", reply_markup=ReplyKeyboardRemove())
    await finish(message, message.text, state)

async def finish(message, phone, state):
    data = await state.get_data()
    text = (
        f"✅ Нова заявка:\n📍 {data['location']}\n📐 {data['size']}\n⏳ {data['duration']}\n"
        f"👤 {data['name']}\n📞 {phone}"
    )
    await bot.send_message(ADMIN_ID, text)
    await message.answer("🚀 Ваша заявка надіслана! Ми зв'яжемося з Вами найближчим часом!", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("⬅️ Повернутись на головну", callback_data="start")
    ))
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
