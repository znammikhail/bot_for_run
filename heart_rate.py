import matplotlib.pyplot as plt
import seaborn as sns

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