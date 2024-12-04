import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import gpxpy
import requests
from geopy.distance import geodesic

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

# Функция расчёта пульсовых зон с новой формулой
def calculate_heart_zones(pano: int):
    zones = { 
        "Zone 1 (легкая)": (0, 0.8 * pano),
        "Zone 2 (средняя)": (0.8 * pano, 0.89 * pano),
        "Zone 3 (тяжелая)": (0.9 * pano, 0.99 * pano),
        "Zone 4 (очень тяжелая)": (pano, 1.09 * pano),
        "Zone 5 (максимальная)": (1.1 * pano, float('inf')),
    }
    return zones

# Функция для обработки GPX файла
def parse_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    
    total_distance = 0.0  # Общая дистанция в метрах
    total_time = 0.0  # Общее время в секундах
    total_cadence = 0  # Сумма всех каденсов
    total_heart_rate = 0  # Сумма всех пульсов
    cadence_count = 0  # Количество точек с каденсом
    heart_rate_count = 0  # Количество точек с пульсом
    
    start_time = None
    end_time = None
    previous_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Работа с координатами для подсчета расстояния
                if previous_point:
                    distance = geodesic(
                        (previous_point.latitude, previous_point.longitude),
                        (point.latitude, point.longitude)
                    ).meters
                    total_distance += distance
                previous_point = point
                
                # Работа с временными метками
                if point.time:
                    if not start_time:
                        start_time = point.time
                    end_time = point.time

                # Извлечение данных из extensions
                if point.extensions:
                    for ext in point.extensions:
                        if ext.tag.endswith("TrackPointExtension"):
                            for child in ext:
                                if child.tag.endswith("hr"):  # Пульс
                                    total_heart_rate += int(child.text)
                                    heart_rate_count += 1
                                if child.tag.endswith("cad"):  # Каденс (учет двух ног)
                                    total_cadence += int(child.text) * 2
                                    cadence_count += 1
    
    # Расчет времени
    total_time = (end_time - start_time).total_seconds() if start_time and end_time else 0

    # Перевод расстояния в километры с округлением до 0.1
    total_distance_km = round(total_distance / 1000, 1)

    # Средняя скорость (км/ч)
    average_speed_kmh = (total_distance_km / (total_time / 3600)) if total_time > 0 else 0

    # Средний темп (мин:сек/км)
    average_pace_sec = (total_time / total_distance_km) if total_distance_km > 0 else 0
    average_pace_min = int(average_pace_sec // 60)
    average_pace_rem_sec = int(average_pace_sec % 60)

    # Общее время в формате ЧЧ:ММ:СС
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)

    # Средний пульс и каденс
    average_heart_rate = total_heart_rate / heart_rate_count if heart_rate_count > 0 else None
    average_cadence = total_cadence / cadence_count if cadence_count > 0 else None

    return {
        "Средний пульс": round(average_heart_rate, 1) if average_heart_rate else None,
        "Расстояние (км)": total_distance_km,
        "Средний темп (мин:сек)": f"{average_pace_min}:{average_pace_rem_sec:02}",
        "Общее время (ч:м:с)": f"{hours}:{minutes:02}:{seconds:02}",
        "Средняя скорость (км/ч)": round(average_speed_kmh, 1),
        "Средний каденс (шагов/мин)": round(average_cadence, 1) if average_cadence else None,
    }

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
        zones = calculate_heart_zones(pano)

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
        gpx_result = parse_gpx('temp.gpx')

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
