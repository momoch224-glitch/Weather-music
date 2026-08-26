# weather.py
import sys
import requests
import json
import datetime
import os
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def load_api_key():
    # このファイル (weather.py) があるディレクトリのパスを取得
    current_dir = os.path.dirname(__file__)
    # apikey.txt へのフルパスを作成
    key_path = os.path.join(current_dir, "apikey.txt")
    
    try:
        with open(key_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

API_KEY = load_api_key()

def get_season(month):
    if 3 <= month <= 5: return "春"
    if 6 <= month <= 8: return "夏"
    if 9 <= month <= 11: return "秋"
    return "冬"

def get_weather(city_name):
    if not API_KEY:
        return {"error": "apikey.txt が見つかりません"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},JP&appid={API_KEY}&units=metric&lang=ja"
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        month = datetime.datetime.now().month
        
        weather_data = {
            "season": get_season(month),
            "condition": data["weather"][0]["main"],
            "temperature": round(data["main"]["temp"]),
            "wind_speed": round(data["wind"]["speed"], 1)
        }
        
        # wind_notes.csv から湿度と風速変化量を取得
        current_dir = os.path.dirname(__file__)
        csv_path = os.path.join(current_dir, "wind_notes.csv")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            weather_data["humidity"] = round(df["humidity"].mean(), 2)
            weather_data["change_rate"] = round(df["change_rate"].mean(), 2)
        
        return weather_data
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "Tokyo"
    print(json.dumps(get_weather(city), ensure_ascii=False))
