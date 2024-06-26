import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from database.portfolio_db import db_path


# Функция для получения текущей цены акции по тикеру с Московской биржи (Moex)
def get_stock_price_moex(ticker, date):
    try:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
        params = {'date': date.strftime('%Y-%m-%d')}
        response = requests.get(url, params=params)
        data = response.json()
        if 'marketdata' in data:
            return float(data['marketdata']['data'][0][11])  # Последняя цена закрытия
        else:
            return None
    except Exception as e:
        print(f"Error fetching stock price for {ticker} on {date}: {e}")
        return None


# Функция для получения исторической цены акции на заданную дату
def get_historical_stock_price(cursor, ticker, date):
    try:
        cursor.execute('''
            SELECT purchase_price, exist
            FROM portfolio
            WHERE ticker = ? AND purchase_date <= ?
            ORDER BY purchase_date DESC
            LIMIT 1
        ''', (ticker, date))

        row = cursor.fetchone()
        if row:
            purchase_price = float(row[0])
            exist = row[1]  # 'True' или 'False'

            if exist == 'True':
                current_price = get_stock_price_moex(ticker, date)
                if current_price is not None:
                    return current_price
                else:
                    return purchase_price  # Используем цену покупки, если не удалось получить текущую цену
            else:
                return purchase_price  # Используем цену покупки, если акция не торгуется на бирже

        return None

    except Exception as e:
        print(f"Error fetching historical stock price for {ticker}: {e}")
        return None


# Функция для построения графика роста портфеля
def plot_portfolio_growth(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем все виды акций пользователя с уникальными тикерами и условиями существования
        cursor.execute('''
            SELECT DISTINCT ticker, exist
            FROM portfolio
            WHERE id_user = ? AND type = 'stocks'
        ''', (user_id,))
        stocks = cursor.fetchall()

        if not stocks:
            print("Портфель пользователя пуст.")
            conn.close()
            return

        # Получаем уникальные даты покупок акций
        purchase_dates = set()
        for stock in stocks:
            ticker = stock[0]
            cursor.execute('''
                SELECT DISTINCT purchase_date
                FROM portfolio
                WHERE ticker = ? AND exist = ?
            ''', (ticker, stock[1]))
            purchase_dates.update([datetime.strptime(row[0], '%Y-%m-%d') for row in cursor.fetchall()])

        # Строим график на каждую уникальную дату покупки
        dates = sorted(purchase_dates)
        portfolio_value = []

        for date in dates:
            total_value = 0
            for stock in stocks:
                ticker = stock[0]
                exist = stock[1]

                # Получаем историческую цену акции на заданную дату
                historical_price = get_historical_stock_price(cursor, ticker, date)

                if historical_price is None:
                    print(f"Не удалось получить историческую цену для акции {ticker} на дату {date}. Пропускаем.")
                    continue

                # Получаем общее количество акций данного вида
                cursor.execute('''
                    SELECT SUM(quantity)
                    FROM portfolio
                    WHERE ticker = ? AND exist = ?
                ''', (ticker, exist))
                quantity = cursor.fetchone()[0]
                if quantity is None:
                    print(f"Не удалось получить количество акций для акции {ticker}. Пропускаем.")
                    continue

                current_value = historical_price * quantity
                total_value += current_value

            portfolio_value.append(total_value)

        conn.close()

        # Построение графика
        plt.figure(figsize=(10, 6))
        plt.plot_date(dates, portfolio_value, marker='o', linestyle='-')
        plt.title('Рост портфеля акций')
        plt.xlabel('Дата')
        plt.ylabel('Общая стоимость портфеля')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error plotting portfolio growth: {e}")


# Пример использования: построение графика для пользователя с ID 123456789
plot_portfolio_growth(123456789)
