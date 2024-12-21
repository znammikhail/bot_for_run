import sqlite3

# Подключение к базе данных SQLite
db_path = "run_data.db"

def get_training_by_date_and_user(date, user_id):
    
    # Подключаемся к базе
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    try:
        # Выполняем запрос, используя DATE() для игнорирования времени
        cursor.execute(
            "SELECT * FROM runs WHERE DATE(date) = ? AND user_id = ?",
            (date, user_id)
        )
        row = cursor.fetchone()
        
        # Если данные найдены
        if row:
            # Конвертируем в словарь
            columns = [column[0] for column in cursor.description]  # Получаем имена столбцов
            training_data = dict(zip(columns, row))
            return training_data
        else:
            print("Тренировка с указанной датой не найдена.")
            return None
    except sqlite3.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        # Закрываем соединение
        connection.close()

# Пример вызова функции
if __name__ == "__main__":
    training_date = "2024-10-02"  # Укажите дату тренировки в формате 'YYYY-MM-DD'
    user_id = 1  # Укажите ID пользователя
    
    training_data = get_training_by_date_and_user(training_date, user_id)
    
    if training_data:
        print("Данные тренировки:", training_data)
    else:
        print("Данных по тренировке нет.")