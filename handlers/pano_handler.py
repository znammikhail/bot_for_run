from aiogram import Router, F
from aiogram.types import Message

from utils.heart_rate import calculate_heart_rate_zones # импорт функции расчёта пульсовых зон.
# calculate_heart_rate_zones можно импортировать не сюда, а в онсновой файл, и передавать функцию в качестве аргумента обработчика

# Инициализация Router
router = Router()

# Словарь для хранения данных пользователя
user_data = {}

@router.message(F.text == "Ввести ПАНО")
async def enter_pano(message: Message):
    """Запрос ПАНО у пользователя"""
    await message.answer("Пожалуйста, введи своё ПАНО (целое число):")
    user_data[message.from_user.id] = {"state": "waiting_for_pano"}

@router.message(F.text.regexp(r"^\d+$"))  # Проверяем, что текст - это число
async def handle_pano_input(message: Message):
    user_id = message.from_user.id

    # Проверяем, ждёт ли пользователь ввода ПАНО
    if user_data.get(user_id, {}).get("state") == "waiting_for_pano":
        pano = int(message.text)
        user_data[user_id]["pano"] = pano
        user_data[user_id]["state"] = None

        # Пример расчёта пульсовых зон
        zones = calculate_heart_rate_zones(pano)

        # Отправляем результат
        response = "Твои пульсовые зоны:\n"
        for zone_name, (min_val, max_val) in zones.items():
            response += f"{zone_name}: {min_val} - {max_val} уд/мин\n"

        await message.answer(response)
    else:
        await message.answer("Нажми кнопку 'Ввести ПАНО', чтобы начать.")
