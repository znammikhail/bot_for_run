import gpxpy
import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import seaborn as sns
import folium

file_path = "Zepp_test_run.gpx"

# === Модуль 1: Парсинг GPX данных ===
def parse_gpx(file_path):
    """
    Парсит GPX-файл, извлекает данные координат, времени, пульса и каденса.
    
    Аргументы:
        file_path (str): Путь к GPX-файлу.
    
    Возвращает:
        tuple: Резюме данных (dict) и DataFrame с деталями.
    """
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = {"latitude": [], "longitude": [], "time": [], "heart_rate": [], "cadence": []}
    total_distance = 0.0
    previous_point = None
    start_time, end_time = None, None
    total_heart_rate, heart_rate_count = 0, 0
    total_cadence, cadence_count = 0, 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data["latitude"].append(point.latitude)
                data["longitude"].append(point.longitude)
                data["time"].append(point.time)

                # Расчет расстояния
                if previous_point:
                    distance = geodesic(
                        (previous_point.latitude, previous_point.longitude),
                        (point.latitude, point.longitude)
                    ).meters
                    total_distance += distance
                previous_point = point

                # Расчет времени
                if not start_time:
                    start_time = point.time
                end_time = point.time

                # Извлечение пульса и каденса
                heart_rate, cadence = None, None
                if point.extensions:
                    for ext in point.extensions:
                        if ext.tag.endswith("TrackPointExtension"):
                            for child in ext:
                                if child.tag.endswith("hr"):
                                    heart_rate = int(child.text)
                                    total_heart_rate += heart_rate
                                    heart_rate_count += 1
                                if child.tag.endswith("cad"):
                                    cadence = int(child.text) * 2
                                    total_cadence += cadence
                                    cadence_count += 1
                data["heart_rate"].append(heart_rate)
                data["cadence"].append(cadence)

    df = pd.DataFrame(data)
    total_time = (end_time - start_time).total_seconds()
    total_distance_km = round(total_distance / 1000, 1)
    average_speed_kmh = total_distance_km / (total_time / 3600) if total_time > 0 else 0
    average_heart_rate = total_heart_rate / heart_rate_count if heart_rate_count > 0 else None
    average_cadence = total_cadence / cadence_count if cadence_count > 0 else None
    average_pace_min = int((total_time / total_distance_km) // 60) if total_distance_km > 0 else 0
    average_pace_sec = int((total_time / total_distance_km) % 60) if total_distance_km > 0 else 0

    summary = {
        "Расстояние (км)": total_distance_km,
        "Средняя скорость (км/ч)": round(average_speed_kmh, 1),
        "Средний пульс": round(average_heart_rate, 1) if average_heart_rate else None,
        "Средний темп (мин:сек)": f"{average_pace_min}:{average_pace_sec:02}",
        "Общее время (сек)": int(total_time),
        "Средний каденс (шагов/мин)": round(average_cadence, 1) if average_cadence else None
    }
    return summary, df


# === Модуль 2: Построение карты ===
def plot_map(df):
    start_coords = (df["latitude"].iloc[0], df["longitude"].iloc[0])
    m = folium.Map(location=start_coords, zoom_start=15)
    points = list(zip(df["latitude"], df["longitude"]))
    folium.PolyLine(points, color="blue", weight=5, opacity=0.8).add_to(m)
    folium.Marker(points[0], popup="Начало").add_to(m)
    folium.Marker(points[-1], popup="Конец").add_to(m)
    m.save("map.html")
    print("Карта сохранена в 'map.html'. Откройте файл в браузере.")


# === Модуль 3: Расчет пульсовых зон ===
def calculate_heart_rate_zones(threshold):
    zones = {
        "Zone 1 (легкая)": (0, 0.8 * threshold),
        "Zone 2 (средняя)": (0.8 * threshold, 0.89 * threshold),
        "Zone 3 (тяжелая)": (0.9 * threshold, 0.99 * threshold),
        "Zone 4 (очень тяжелая)": (threshold, 1.09 * threshold),
        "Zone 5 (максимальная)": (1.1 * threshold, float("inf")),
    }
    return zones


def analyze_time_in_zones(df, zones):
    df["duration"] = (df["time"].shift(-1) - df["time"]).dt.total_seconds()
    df = df.iloc[:-1]
    time_in_zones = {zone: 0 for zone in zones}

    for _, row in df.iterrows():
        hr = row["heart_rate"]
        duration = row["duration"]
        for zone, (lower, upper) in zones.items():
            if lower <= hr < upper:
                time_in_zones[zone] += duration
                break

    total_time = df["duration"].sum()
    return {zone: round((time / total_time) * 100, 1) for zone, time in time_in_zones.items()}


# === Модуль 4: Визуализация зон ===
def plot_time_in_zones(time_in_zones_percent):
    zones = list(time_in_zones_percent.keys())
    times = list(time_in_zones_percent.values())
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=zones, y=times, palette="viridis")
    plt.title("Время в пульсовых зонах (%)", fontsize=16)
    plt.xlabel("Пульсовые зоны", fontsize=14)
    plt.ylabel("Время (%)", fontsize=14)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()


# === Главная программа ===
if __name__ == "__main__":
    gpx_file_path = "Zepp_test_run.gpx"
    threshold = 171  # Уровень ПАНО

    summary, df = parse_gpx(gpx_file_path)
    print("Резюме данных:", summary)

    plot_map(df)

    zones = calculate_heart_rate_zones(threshold)
    time_in_zones_percent = analyze_time_in_zones(df, zones)
    plot_time_in_zones(time_in_zones_percent)
