import requests
# requests — библиотека для HTTP запросов к API

import pandas as pd
# pandas — работа с таблицами данных

from datetime import datetime
# datetime — работа с датой и временем

import os
# os — работа с файловой системой (создание папок)


def extract(base_currency="USD"):
    """
    Шаг 1 пайплайна: ИЗВЛЕЧЕНИЕ данных из API
    Возвращает DataFrame с курсами валют
    """
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    # f"..." = f-string, подставляет переменную base_currency в строку
    # Итого URL будет: https://open.er-api.com/v6/latest/USD

    print(f"Запрашиваем данные: {url}")

    response = requests.get(url)
    # requests.get = отправить GET запрос на этот URL
    # response = ответ от сервера

    if response.status_code != 200:
        raise Exception(f"Ошибка API: {response.status_code}")
    # status_code 200 = успех
    # если не 200 = что-то пошло не так, останавливаем пайплайн

    data = response.json()
    # .json() = превращает текстовый ответ API в словарь Python

    rows = []
    # пустой список — будем добавлять строки таблицы сюда

    for currency, rate in data['rates'].items():
        # data['rates'] = словарь {валюта: курс}
        # .items() = перебираем пары ключ-значение
        # currency = название валюты ('KZT', 'EUR' ...)
        # rate = курс к доллару (448.5, 0.92 ...)
        rows.append({
            'base':       base_currency,
            'target':     currency,
            'rate':       rate,
            'fetched_at': datetime.utcnow().isoformat()
            # datetime.utcnow() = текущее время UTC
            # .isoformat() = превращает в строку '2026-05-04T10:30:00'
        })

    df = pd.DataFrame(rows)
    # pd.DataFrame(rows) = превращает список словарей в таблицу
    print(f"Получено {len(df)} курсов валют")
    return df
    
def load_parquet(df, folder="data"):
    """
    Шаг 2 пайплайна: ЗАГРУЗКА данных в Parquet файл
    df = таблица которую получили из extract()
    folder = папка куда сохраняем
    """
    os.makedirs(folder, exist_ok=True)
    # os.makedirs = создать папку
    # exist_ok=True = не ругаться если папка уже существует

    today = datetime.utcnow().strftime('%Y%m%d')
    # .strftime('%Y%m%d') = форматировать дату как строку
    # Например: '20260504' (год+месяц+день)
    # Зачем: каждый день будет свой файл rates_20260504.parquet

    filename = f"{folder}/rates_{today}.parquet"
    # Итого путь к файлу: data/rates_20260504.parquet

    df.to_parquet(filename, index=False)
    # .to_parquet() = сохранить DataFrame в Parquet формат
    # index=False = не сохранять индекс строк (0,1,2...) — он не нужен

    print(f"Сохранено в {filename}")
    return filename
    # возвращаем путь к файлу — пригодится в следующем шаге


def run_pipeline():
    """
    Главная функция — запускает весь пайплайн по порядку
    """
    print("=== Запуск пайплайна ===")

    df = extract("USD")
    # Шаг 1: получаем данные из API

    filename = load_parquet(df)
    # Шаг 2: сохраняем в Parquet

    print("\n=== Проверка результата ===")
    result = pd.read_parquet(filename)
    # читаем обратно чтобы убедиться что всё записалось

    print(f"Строк в файле: {len(result)}")
    print("\nВалюты рядом с KZ:")
    print(result[result['target'].isin(['KZT', 'EUR', 'RUB', 'CNY'])])
    # фильтруем только нужные валюты для проверки

    print("\n=== Пайплайн завершён успешно ===")
    return filename


if __name__ == "__main__":
    run_pipeline()
# if __name__ == "__main__" = запускать run_pipeline()
# только если запускаем этот файл напрямую (python pipeline.py)
# если импортируем из другого файла — не запускать автоматически