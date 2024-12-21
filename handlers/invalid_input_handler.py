from aiogram import Router, F
from aiogram.types import Message

# Инициализация Router
router = Router()

@router.message(F.text)
async def handle_invalid_input(message: Message):
    """Обработка некорректного ввода"""
    await message.answer("Пожалуйста, введи целое число для ПАНО или нажми 'Ввести ПАНО'.")
