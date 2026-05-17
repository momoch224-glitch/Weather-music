import requests
import pandas as pd
import numpy as np

# =========================
# APIキー読み込み
# =========================
with open("apikey.txt", "r", encoding="utf-8") as f:
    API_KEY = f.read().strip()

# =========================
# 地点設定
# =========================
LAT = 35.6812   # 東京駅付近
LON = 139.7671

# =========================
# OpenWeather API
# =========================
url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={LAT}&lon={LON}"
    f"&exclude=minutely,daily,alerts"
    f"&units=metric"
    f"&appid={API_KEY}"
)

response = requests.get(url)
data = response.json()
print(data)
# =========================
# hourlyデータ抽出
# =========================
forecast = data["list"]

df = pd.DataFrame({
   "time": [h["dt"] for h in forecast],
    "wind_speed": [h["wind"]["speed"] for h in forecast]
})

# UNIX時刻 → datetime
df["time"] = pd.to_datetime(df["time"], unit="s")

# timeをindexへ
df = df.set_index("time")

# =========================
# 1時間 → 1分補間
# =========================
df_resampled = df.resample("1min").interpolate(method="cubic")

# =========================
# ローパスフィルタ
# 15分移動平均
# =========================
df_resampled["wind_smooth"] = (
    df_resampled["wind_speed"]
    .rolling(window=15, center=True)
    .mean()
)

# NaN補完
df_resampled["wind_smooth"] = (
    df_resampled["wind_smooth"]
    .bfill()
    .ffill()
)

# =========================
# dv/dt 計算
# =========================
# 1分刻みなので dt = 60 sec
dt = 60

df_resampled["dv_dt"] = np.gradient(
    df_resampled["wind_smooth"],
    dt
)

# =========================
# 標準化
# =========================
mean = df_resampled["wind_smooth"].mean()
std = df_resampled["wind_smooth"].std()

df_resampled["wind_zscore"] = (
    (df_resampled["wind_smooth"] - mean) / std
)

# =========================
# 0〜1スケーリング
# =========================
def minmax(x):
    return (x - x.min()) / (x.max() - x.min())

df_resampled["volume"] = minmax(df_resampled["wind_zscore"])

# dv/dt は負もあるので別処理
max_abs = np.abs(df_resampled["dv_dt"]).max()

df_resampled["drama"] = (
    df_resampled["dv_dt"] / max_abs
)

# =========================
# 出力
# =========================
df_resampled.to_csv("processed_weather.csv")

print(df_resampled.head())
print("saved: processed_weather.csv")

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

plt.plot(
    df_resampled.index,
    df_resampled["wind_smooth"]
)

plt.title("Wind Story")
plt.xlabel("Time")
plt.ylabel("Wind Speed")

plt.grid()

plt.show()

plt.figure(figsize=(12, 4))

plt.plot(
    df_resampled.index,
    df_resampled["dv_dt"]
)

plt.title("Wind Acceleration")
plt.xlabel("Time")
plt.ylabel("dv/dt")

plt.grid()

plt.show()