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
        ("вул. Кирилівська, 41", "https://maps.google.com/?q=50.471213,30.486702")
    ]
    for name, link in locations:
        btn = InlineKeyboardMarkup().add(InlineKeyboardButton("Відкрити на карті", url=link))
        await bot.send_message(callback_query.from_user.id, f"Локація: {name}", reply_markup=btn)

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Бот працює!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)