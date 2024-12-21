
from gpx_parser import parse_gpx # импорт парсера
from map_plotter import plot_map # импрот построения карты
from heart_rate import calculate_heart_rate_zones, analyze_time_in_zones, plot_time_in_zones # импорт функциий пульса
from db_writer import create_runs_table, insert_run_data # импорт записи в базу данных
import sqlite3

#file_path = "Zepp_test_run.gpx"

# === Главная программа ===
if __name__ == "__main__":
    gpx_file_path = "Zepp_test_run.gpx"
    threshold = 171  # Уровень ПАНО

    summary, df = parse_gpx(gpx_file_path)
    print("Резюме данных:", summary)

    user_id = 3 # Уникальный id пользователя

    try:  # Оборачивание кода в try предотвращает падение программы в случае ошибки
        with sqlite3.connect('run_data.db') as conn:
            cursor = conn.cursor()
            create_runs_table(cursor)
            insert_run_data(cursor, user_id, summary)
            conn.commit()
    except Exception as e:
        print(f"Произошла ошибка: {e}")


    plot_map(df)

    zones = calculate_heart_rate_zones(threshold)
    time_in_zones_percent = analyze_time_in_zones(df, zones)
    plot_time_in_zones(time_in_zones_percent)
