import sqlite3

# === Модуль 5: Запись в базу данных ===

# Создание таблицы, если она не существует
def create_runs_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        date DATETIME,
        distance REAL,
        total_time REAL,
        average_speed REAL,
        average_heart_rate REAL,
        average_pace REAL,
        average_cadence REAL
    )
    """)
    # Создаём уникальный индекс для user_id и date (ускоряет поиск и предотвращает дубли)
    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_user_date ON runs (user_id, date)
    """)

def insert_run_data(cursor, user_id, run_summary):
    cursor.execute("""
    INSERT OR IGNORE INTO runs (user_id, date, distance, total_time, average_speed, average_heart_rate, average_pace, average_cadence)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        run_summary.get("Дата создания файла", None),
        run_summary.get("Расстояние (км)", None),
        run_summary.get("Общее время (сек)", None),  
        run_summary.get("Средняя скорость (км/ч)", None),  
        run_summary.get("Средний пульс", None),  
        run_summary.get("Средний темп (мин:сек)", None),  
        run_summary.get("Средний каденс (шагов/мин)", None)  
    ))
    if cursor.rowcount == 0:
        print("Запись для этой даты и пользователя уже существует, вставка пропущена.")
    else:
        print("Новая запись успешно добавлена.")