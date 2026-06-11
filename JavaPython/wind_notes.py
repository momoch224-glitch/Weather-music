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

# 整数化 (四捨五入して整数に)
notes["midi_note"] = notes["midi_note"].round().astype(int)

# =========================
# 変化量の計算 (0-10に変換)
# =========================
# 1. 1ステップ(10分)前との差分を計算（最初の行はNaNになるため0で埋める）
diff = notes["wind_smooth"].diff().fillna(0)

# 2. 変化の「大きさ（絶対値）」を取得 (減少も増加も「変化」として扱う)
abs_diff = diff.abs()

# 3. 0〜10の範囲にスケーリング
min_diff = abs_diff.min()
max_diff = abs_diff.max()

# ゼロ除算対策（風速がずっと一定の場合はすべて0にする）
if max_diff == min_diff:
    notes["change_rate"] = 0
else:
    notes["change_rate"] = (abs_diff - min_diff) / (max_diff - min_diff) * 10

# 4. 整数化 (四捨五入して整数に)
notes["change_rate"] = notes["change_rate"].round().astype(int)

# =========================
# 出力
# =========================
# ターミナルで確認しやすくするために change_rate も表示
print(notes[["wind_smooth", "midi_note", "change_rate"]])

# CSVにもすべての列を出力
notes.to_csv("wind_notes.csv")

print("saved: wind_notes.csv")