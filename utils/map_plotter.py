import folium

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