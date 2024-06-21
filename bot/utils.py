import sqlite3
import pandas as pd
import requests
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from dotenv import load_dotenv
from database.portfolio_db import db_path
import os

load_dotenv()
moscow_exchange_url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/{}.json"  # URL для получения данных с Московской биржи


def get_portfolio(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, type, purchase_date, purchase_price, ticker FROM portfolio WHERE id_user = ?",
                   (user_id,))
    portfolio = cursor.fetchall()
    conn.close()
    return portfolio


def get_current_price(ticker):
    try:
        response = requests.get(moscow_exchange_url.format(ticker))
        response.raise_for_status()
        data = response.json()
        if 'marketdata' in data['securities']:
            current_price = data['securities']['marketdata'][0]['LAST']
            return current_price
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        print(f"Error fetching price for {ticker}: {e}")
    return None


def create_excel(user_id, save_path='.'):
    portfolio = get_portfolio(user_id)
    if not portfolio:
        print("Портфель пуст или не существует.")
        return

    data = []
    for item in portfolio:
        name, type_, purchase_date, purchase_price, ticker = item
        current_price = get_current_price(ticker)
        if current_price is not None:
            change = ((current_price - purchase_price) / purchase_price) * 100
        else:
            current_price = "None"
            change = "None"

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


# Пример вызова функции
user_id = 730171729  # Замените на ID пользователя
save_directory = '/Users/crazydogctrl/PycharmProjects/TGbotMosBirga'
create_excel(user_id, save_path=save_directory)
