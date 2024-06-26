import sqlite3
import pandas as pd
import requests
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from dotenv import load_dotenv
from database.portfolio_db import db_path
import os
from start import bot

load_dotenv()
moscow_exchange_url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/{}.json"


def get_portfolio(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, type, purchase_date, purchase_price, ticker FROM portfolio WHERE id_user = ?",
                   (user_id,))
    portfolio = cursor.fetchall()
    conn.close()
    return portfolio


def get_current_price(ticker):
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        marketdata = data.get('marketdata')

        if not marketdata:
            return None

        columns = marketdata.get('columns', [])
        if 'LAST' not in columns:
            return None

        last_index = columns.index('LAST')
        market_data = marketdata.get('data', [])
        if not market_data:
            return None

        current_price = market_data[0][last_index]
        return current_price
    except (requests.RequestException, ValueError, KeyError):
        return None


def create_excel(user_id, save_path='.'):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        print("Портфель пуст или не существует.")
        return None

    data = []
    for item in portfolio:
        name, type_, purchase_date, purchase_price, ticker = item
        current_price = get_current_price(ticker)
        if current_price is not None:
            change = ((current_price - purchase_price) / purchase_price) * 100 if purchase_price != 0 else None
        else:
            current_price = None
            change = None

        link = f"https://www.moex.com/ru/issue.aspx?code={ticker}"
        data.append([name, type_, purchase_date, purchase_price, current_price, change, ticker, link])

    columns = ["Имя", "Тип", "Дата покупки", "Цена покупки", "Текущая цена", "Изменение (%)", "Тикер",
               "Ссылка на Московскую биржу"]
    df = pd.DataFrame(data, columns=columns)

    wb = Workbook()
    ws = wb.active
    ws.title = "Портфель"

    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    filename = f"portfolio_{user_id}.xlsx"
    full_path = os.path.join(save_path, filename)
    wb.save(full_path)
    print(f"Excel файл '{full_path}' успешно создан.")
    return full_path


def send_portfolio_as_excel(message):
    try:
        # Определение текущей директории, где находится скрипт
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = create_excel(message.chat.id, save_path=script_directory)
        if file_path is None:
            bot.send_message(message.chat.id, "Произошла ошибка при создании Excel файла.")
            return
        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove(file_path)  # Удаление файла после отправки
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при создании Excel файла: {e}")


# Пример вызова функции
# user_id = 730171729
# print("hello")
# save_directory = os.path.dirname(os.path.abspath(__file__))
# create_excel(user_id, save_path=save_directory)
