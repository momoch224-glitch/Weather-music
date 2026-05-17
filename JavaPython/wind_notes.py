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
LAT = 35.6812
LON = 139.7671

# =========================
# forecast API
# =========================
url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={LAT}&lon={LON}"
    f"&units=metric"
    f"&appid={API_KEY}"
)

response = requests.get(url)
data = response.json()

# =========================
# データ抽出
# =========================
forecast = data["list"]

df = pd.DataFrame({
    "time": [h["dt"] for h in forecast],
    "wind_speed": [h["wind"]["speed"] for h in forecast]
})

# time変換
df["time"] = pd.to_datetime(df["time"], unit="s")

# index化
df = df.set_index("time")

# =========================
# 1分補間
# =========================
df_resampled = df.resample("1min").interpolate(method="cubic")

# =========================
# smoothing
# =========================
df_resampled["wind_smooth"] = (
    df_resampled["wind_speed"]
    .rolling(window=15, center=True)
    .mean()
)

df_resampled["wind_smooth"] = (
    df_resampled["wind_smooth"]
    .bfill()
    .ffill()
)

# =========================
# 10分ごと抽出
# =========================
notes = df_resampled.iloc[::10].copy()

# =========================
# MIDI変換
# =========================
# 風速を 48〜72 に変換
min_wind = notes["wind_smooth"].min()
max_wind = notes["wind_smooth"].max()

notes["midi_note"] = (
    48
    + (
        (notes["wind_smooth"] - min_wind)
        / (max_wind - min_wind)
    ) * 24
)

# 整数化
notes["midi_note"] = notes["midi_note"].astype(int)

# =========================
# 出力
# =========================
print(notes[["wind_smooth", "midi_note"]])

notes.to_csv("wind_notes.csv")

print("saved: wind_notes.csv")