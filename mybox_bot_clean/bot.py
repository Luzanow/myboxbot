import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📍 Переглянути локації", callback_data="view_locations"))
    kb.add(InlineKeyboardButton("📝 Залишити заявку", callback_data="make_request"))
    await message.answer("Вітаємо в MyBox! Оберіть дію:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'view_locations')
async def show_locations(callback_query: types.CallbackQuery):
    locations = [
        ("вул. Новокостянтинівська, 22/15", "https://maps.google.com/?q=50.484716,30.490153"),
        ("просп. Відрадний, 107", "https://maps.google.com/?q=50.421183,30.413375"),
        ("вул. Кирилівська, 41", "https://maps.google.com/?q=50.471213,30.486702"),
        ("вул. Дегтярівська, 21", "https://maps.google.com/?q=50.456731,30.446587"),
        ("вул. Плодова, 1", "https://maps.google.com/?q=50.470805,30.509093"),
        ("вул. Безняковська, 21", "https://maps.google.com/?q=50.402645,30.532423"),
        ("вул. Свято-Покровська, 213", "https://maps.google.com/?q=50.479441,30.645763"),
        ("вул. Миколи Василенка, 2", "https://maps.google.com/?q=50.424185,30.412937"),
        ("вул. Магнітогорська, 1", "https://maps.google.com/?q=50.480893,30.625463"),
        ("вул. Лугова, 9", "https://maps.google.com/?q=50.501441,30.482916"),
        ("вул. Євгенія Харченка, 35", "https://maps.google.com/?q=50.438159,30.723826"),
        ("вул. Володимира Брожка, 38/58", "https://maps.google.com/?q=50.501147,30.617984"),
        ("вул. Межигірська, 78", "https://maps.google.com/?q=50.472167,30.512769")
    ]
    for name, link in locations:
        btn = InlineKeyboardMarkup().add(InlineKeyboardButton("Відкрити на карті", url=link))
        await bot.send_message(callback_query.from_user.id, f"Локація: {name}", reply_markup=btn)

@dp.callback_query_handler(lambda c: c.data == 'make_request')
async def request_start(callback_query: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name, _ in [
        ("вул. Новокостянтинівська, 22/15", ""),
        ("просп. Відрадний, 107", ""),
        ("вул. Кирилівська, 41", ""),
        ("вул. Дегтярівська, 21", ""),
        ("вул. Плодова, 1", ""),
        ("вул. Безняковська, 21", ""),
        ("вул. Свято-Покровська, 213", ""),
        ("вул. Миколи Василенка, 2", ""),
        ("вул. Магнітогорська, 1", ""),
        ("вул. Лугова, 9", ""),
        ("вул. Євгенія Харченка, 35", ""),
        ("вул. Володимира Брожка, 38/58", ""),
        ("вул. Межигірська, 78", "")
    ]:
        kb.add(name)
    await Form.location.set()
    await bot.send_message(callback_query.from_user.id, "Оберіть локацію:", reply_markup=kb)

@dp.message_handler(state=Form.location)
async def set_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("5 м²", "10 м²", "15 м²")
    await Form.next()
    await message.answer("Оберіть розмір контейнера:", reply_markup=kb)

@dp.message_handler(state=Form.size)
async def set_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1–3 місяці", "3–6 місяців (-5%)", "6–12 місяців (-10%)")
    await Form.
    next()
    await message.answer("Оберіть термін оренди:\n\n🧾 Знижка діє лише при повній оплаті за вибраний період", reply_markup=kb)

@dp.message_handler(state=Form.duration)
async def set_duration(message: types.Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await Form.next()
    await message.answer("Введіть ваше ім’я:")

@dp.message_handler(state=Form.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Поділитися номером", request_contact=True))
    await Form.next()
    await message.answer("Надішліть ваш номер телефону:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def process_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish_request(message, phone, state)

@dp.message_handler(state=Form.phone)
async def set_phone_manual(message: types.Message, state: FSMContext):
    await finish_request(message, message.text, state)

async def finish_request(message: types.Message, phone, state: FSMContext):
    data = await state.get_data()
    text = (
        f"Нова заявка на оренду контейнера:\n\n"
        f"Локація: {data['location']}\n"
        f"Розмір: {data['size']}\n"
        f"Термін: {data['duration']}\n"
        f"Ім’я: {data['name']}\n"
        f"Телефон: {phone}"
    )
    await bot.send_message(ADMIN_ID, text)
    await message.answer("Дякуємо! Ваша заявка надіслана. Очікуйте дзвінка.")
    await state.finish()
