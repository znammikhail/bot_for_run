from aiogram import Router, F
from aiogram.types import Message
import requests
from utils.gpx_parser import parse_gpx  # Импортируем парсер

# Инициализация Router
router = Router()

# Глобальная переменная для API_TOKEN
API_TOKEN = None

def set_api_token(token: str):
    global API_TOKEN
    API_TOKEN = token

# Обработчик отправки GPX файла
@router.message(F.document.mime_type == 'application/gpx+xml')  # Проверяем MIME тип файла
async def handle_gpx_file(message: Message):
    if API_TOKEN is None:
        await message.answer("API_TOKEN не настроен!")
        return

    # Скачиваем файл
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)  # Используем bot, так как передаем через router
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
