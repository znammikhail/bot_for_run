import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import gpxpy
import requests
from geopy.distance import geodesic

from gpx_parser import parse_gpx # импорт парсера
from heart_rate import calculate_heart_rate_zones # импорт функции расчёта пульсовых зон

# Загружаем переменные из .env файла
load_dotenv()

# Токен бота из переменной окружения
API_TOKEN = os.getenv("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Ввести ПАНО")], [KeyboardButton(text="Отправить GPX файл")]], resize_keyboard=True
)

# Словарь для хранения данных пользователя
user_data = {}


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    """Отправка приветственного сообщения"""
    await message.answer(
        "Привет! Я помогу рассчитать твои пульсовые зоны. Нажми кнопку 'Ввести ПАНО', чтобы начать или отправь GPX файл.",
        reply_markup=main_keyboard,
    )

# Обработчик кнопки "Ввести ПАНО"
@dp.message(F.text == "Ввести ПАНО")
async def enter_pano(message: Message):
    """Запрос ПАНО у пользователя"""
    await message.answer("Пожалуйста, введи своё ПАНО (целое число):")
    user_data[message.from_user.id] = {"state": "waiting_for_pano"}

# Обработчик ввода ПАНО
@dp.message(F.text.regexp(r"^\d+$"))  # Проверяем, что текст - это число
async def handle_pano_input(message: Message):
    user_id = message.from_user.id

    # Проверяем, ждёт ли пользователь ввода ПАНО
    if user_data.get(user_id, {}).get("state") == "waiting_for_pano":
        pano = int(message.text)
        user_data[user_id]["pano"] = pano
        user_data[user_id]["state"] = None

        # Рассчитываем зоны
        zones = calculate_heart_rate_zones(pano)

        # Отправляем результат
        response = "Твои пульсовые зоны:\n"
        for zone_name, (min_val, max_val) in zones.items():
            response += f"{zone_name}: {min_val:.0f} - {max_val:.0f} уд/мин\n"

        await message.answer(response, reply_markup=main_keyboard)
    else:
        await message.answer("Нажми кнопку 'Ввести ПАНО', чтобы начать.")

# Обработчик отправки GPX файла
@dp.message(F.document.mime_type == 'application/gpx+xml')  # Проверяем MIME тип файла
async def handle_gpx_file(message: Message):
    # Скачиваем файл
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

    # Загружаем GPX файл
    response = requests.get(file_url)
    gpx_data = response.text

    try:
        # Сохраняем GPX файл во временный файл
        with open('temp.gpx', 'w') as f:
            f.write(gpx_data)
        
        # Парсим GPX файл
        gpx_result, gpx_df = parse_gpx('temp.gpx')

        # Отправляем результаты пользователю
        result_message = "\n".join([f"{key}: {value}" for key, value in gpx_result.items()])
        await message.answer(result_message)
    except Exception as e:
        await message.answer(f"Не удалось обработать файл. Ошибка: {e}")

# Обработчик некорректного ввода
@dp.message(F.text)
async def handle_invalid_input(message: Message):
    """Обработка некорректного ввода"""
    await message.answer("Пожалуйста, введи целое число для ПАНО или нажми 'Ввести ПАНО'.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
