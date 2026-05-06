# weather.py という名前で保存
import sys
import requests
import json
import datetime

# 本来は環境変数から取るべきだが、便宜上ここに置く
API_KEY = "ここにAPIキー"

def get_season(month):
    if 3 <= month <= 5: return "春"
    if 6 <= month <= 8: return "夏"
    if 9 <= month <= 11: return "秋"
    return "冬"

def get_weather(city_name):
    # 都道府県名からデータを取るようURLを変更
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},JP&appid={API_KEY}&units=metric&lang=ja"
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        month = datetime.datetime.now().month
        
        # 四捨五入などの処理をして辞書にまとめる
        return {
            "season": get_season(month),
            "condition": data["weather"][0]["main"],
            "temperature": round(data["main"]["temp"]),       # 小数点第一位を四捨五入
            "wind_speed": round(data["wind"]["speed"], 1)     # 小数点第二位を四捨五入
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Javaから渡された引数（都道府県名）を受け取る
    city = sys.argv[1] if len(sys.argv) > 1 else "Tokyo"
    print(json.dumps(get_weather(city), ensure_ascii=False))