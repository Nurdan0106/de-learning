import requests
import pandas as pd
from datetime import datetime

def get_weather():
    cities = ['Almaty', 'Astana', 'Shymkent'] 
    rows = []
    for i in cities:
        url = f"https://wttr.in/{i}?format=j1"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Ошибка API для {i}: {response.status_code}")
        data = response.json()
        rows.append({
        'city': i,
        'temp_C': data['current_condition'][0]['temp_C'],
        'humidity': data['current_condition'][0]['humidity'],
        'weather': data['current_condition'][0]['weatherDesc'][0]['value']})

    df = pd.DataFrame(rows)
    today = datetime.utcnow().strftime('%Y%m%d')
    df.to_parquet(f"data/weather_{today}.parquet", index=False)

    print(f"Сохранено: weather_{today}.parquet")


if __name__ == '__main__':
    get_weather()