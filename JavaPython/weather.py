# weather.py
import sys
import requests
import json
import datetime
import os

def load_api_key():
   
    # このファイル (weather.py) があるディレクトリのパスを取得
    current_dir = os.path.dirname(__file__)
    # apikey.txt へのフルパスを作成
    key_path = os.path.join(current_dir, "apikey.txt")
    
    try:
        with open(key_path, "r", encoding="utf-8") as f:
            # 中身を読み込んで、前後の余計な空白や改行を削除
            return f.read().strip()
    except FileNotFoundError:
        return None

# ファイルからキーを読み込む
API_KEY = load_api_key()

def get_season(month):
    if 3 <= month <= 5: return "春"
    if 6 <= month <= 8: return "夏"
    if 9 <= month <= 11: return "秋"
    return "冬"

def get_weather(city_name):
    # APIキーが読み込めていない場合のガード
    if not API_KEY:
        return {"error": "apikey.txt が見つからないか、中身が空です。"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},JP&appid={API_KEY}&units=metric&lang=ja"
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        month = datetime.datetime.now().month
        
        return {
            "season": get_season(month),
            "condition": data["weather"][0]["main"],
            "temperature": round(data["main"]["temp"]),
            "wind_speed": round(data["wind"]["speed"], 1)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Javaから渡された引数（都道府県名）を受け取る
    city = sys.argv[1] if len(sys.argv) > 1 else "Tokyo"
    # 結果をJSON形式で標準出力に出す
    print(json.dumps(get_weather(city), ensure_ascii=False))