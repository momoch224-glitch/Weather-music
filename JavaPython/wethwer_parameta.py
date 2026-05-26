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

# 降水量は晴れだとデータが存在しない場合があるため .get() で安全に取得
df = pd.DataFrame({
    "time": [h["dt"] for h in forecast],
    "wind_speed": [h["wind"]["speed"] for h in forecast],
    "temp": [h["main"]["temp"] for h in forecast],         # 気温 (℃)
    "humidity": [h["main"]["humidity"] for h in forecast], # 湿度 (%)
    "pressure": [h["main"]["pressure"] for h in forecast], # 気圧 (hPa)
    "rain": [h.get("rain", {}).get("3h", 0) for h in forecast] # 降水量 (3時間あたりmm)
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
# MIDI変換（風速）
# =========================
min_wind = notes["wind_smooth"].min()
max_wind = notes["wind_smooth"].max()

notes["midi_note"] = (
    48
    + (
        (notes["wind_smooth"] - min_wind)
        / (max_wind - min_wind)
    ) * 24
)

# 整数化 (四捨五入)
notes["midi_note"] = notes["midi_note"].round().astype(int)

# =========================
# 変化量の計算 (風速の変動を0-10に変換)
# =========================
diff = notes["wind_smooth"].diff().fillna(0)
abs_diff = diff.abs()

min_diff = abs_diff.min()
max_diff = abs_diff.max()

if max_diff == min_diff:
    notes["change_rate"] = 0
else:
    notes["change_rate"] = (abs_diff - min_diff) / (max_diff - min_diff) * 10

notes["change_rate"] = notes["change_rate"].round().astype(int)

# =========================
# その他の気象データの音楽変換
# =========================
# ① 気温 → 和音の展開
base_temp = notes["temp"].iloc[0] 
notes["chord_inversion"] = ((notes["temp"] - base_temp) // 1).astype(int)

# ② 降水量 → リズム密度（0〜10段階）
max_rain = notes["rain"].max()
if max_rain == 0:
    notes["rhythm_density"] = 0
else:
    notes["rhythm_density"] = ((notes["rain"] / max_rain) * 10).round().astype(int)

# ③ 湿度 → コードの種類・テンション（0〜10段階）
notes["humidity_code"] = (notes["humidity"] / 10).round().astype(int)

# ④ 気圧 → オクターブや音の重さ
notes["pressure_diff"] = (notes["pressure"] - 1013).round().astype(int)

# =========================
# 出力
# =========================
# 全ての列を一気に表示して確認
print(notes[[
    "wind_smooth", "midi_note", "change_rate", 
    "chord_inversion", "rhythm_density", "humidity_code", "pressure_diff"
]])

# CSVにもすべての列を出力（1回だけでOK）
notes.to_csv("wind_notes.csv")

print("saved: wind_notes.csv")