import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import start_handler, pano_handler, gpx_handler, invalid_input_handler

# Загружаем переменные из .env файла
load_dotenv()

# Токен бота из переменной окружения
API_TOKEN = os.getenv("BOT_TOKEN")

# Устанавливаем API_TOKEN для gpx_handler
gpx_handler.set_api_token(API_TOKEN)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Подключение обработчиков
dp.include_router(start_handler.router)
dp.include_router(pano_handler.router)
dp.include_router(gpx_handler.router)
dp.include_router(invalid_input_handler.router) 

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
