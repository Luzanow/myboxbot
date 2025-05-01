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
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📍 Переглянути локації", callback_data="view_locations"),
        InlineKeyboardButton("📦 Орендувати бокс", callback_data="make_request")
    )
    await message.answer("Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "view_locations")
async def view_locations(callback_query: types.CallbackQuery):
    locations = [
        ("вул. Новокостянтинівська, 22/15", "https://maps.google.com/?q=50.484716,30.490153"),
        ("просп. Відрадний, 107", "https://maps.google.com/?q=50.421183,30.413375"),
        ("вул. Кирилівська, 41", "https://maps.google.com/?q=50.471213,30.486702")
    ]
    for name, link in locations:
        btn = InlineKeyboardMarkup().add(InlineKeyboardButton("Відкрити на карті", url=link))
        await bot.send_message(callback_query.from_user.id, f"Локація: {name}", reply_markup=btn)

@dp.callback_query_handler(lambda c: c.data == "make_request")
async def start_request(callback_query: types.CallbackQuery):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("вул. Новокостянтинівська, 22/15", "просп. Відрадний, 107", "вул. Кирилівська, 41")
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
    await message.answer("Введіть ваше ім’я:")

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
    await message.answer("Дякуємо! Ваша заявка надіслана. Ми з вами зв'яжемось.")
    await state.finish()

if name == "__main__":
    executor.start_polling(dp, skip_updates=True)
