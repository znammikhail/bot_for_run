import gpxpy
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime
from lxml import etree # Для пасринга gpx-файла (библиотека gpxpy не обрабатывает данные из раздела metadata)

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
        gpx_file.seek(0) # Для парсинга даты сооздания файла
        tree = etree.parse(gpx_file) # Для парсинга даты сооздания файла

    # === Парсинг даты создания файла ===
    metadata_time = tree.xpath('//default:metadata/default:time', namespaces={'default': 'http://www.topografix.com/GPX/1/1'})

    if metadata_time:
        creation_date = metadata_time[0].text
        try:
            creation_date = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            creation_date = None
    else:
        creation_date = None

    # === Парсинг остальных данных ===
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

    # summary_tech = [
    # total_distance_km,
    # round(average_speed_kmh, 1),
    # round(average_heart_rate, 1) if average_heart_rate else None,
    # f"{average_pace_min}:{average_pace_sec:02}",
    # int(total_time),
    # round(average_cadence, 1) if average_cadence else None
    # ]

    summary = {
        "Дата создания файла": creation_date.strftime('%Y-%m-%d %H:%M:%S') if creation_date else None,
        "Расстояние (км)": total_distance_km,
        "Общее время (сек)": int(total_time),
        "Средняя скорость (км/ч)": round(average_speed_kmh, 1),
        "Средний пульс": round(average_heart_rate, 1) if average_heart_rate else None,
        "Средний темп (мин:сек)": f"{average_pace_min}:{average_pace_sec:02}",
        "Средний каденс (шагов/мин)": round(average_cadence, 1) if average_cadence else None
    }
    return summary, df