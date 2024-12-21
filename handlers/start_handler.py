from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Инициализация Router
router = Router()

# Клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Ввести ПАНО")], [KeyboardButton(text="Отправить GPX файл")]], resize_keyboard=True
)

@router.message(Command("start"))
async def start_command(message: Message):
    """Отправка приветственного сообщения"""
    await message.answer(
        "Привет! Я помогу рассчитать твои пульсовые зоны. Нажми кнопку 'Ввести ПАНО', чтобы начать или отправь GPX файл.",
        reply_markup=main_keyboard,
    )
