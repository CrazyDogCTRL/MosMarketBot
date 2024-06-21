import sqlite3
from telebot import TeleBot
from database.portfolio_db import db_path
import requests


def add_stock(user_id, purchase_price, purchase_date, quantity, name=None, ticker=None):
    try:
        print(user_id)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, name, ticker) 
                     VALUES (?, 'stocks', ?, ?, ?, ?, ?)''',
                  (user_id, purchase_price, purchase_date, quantity, name, ticker))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding stock: {e}")
        return False


def delete_stock(user_id, name):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''DELETE FROM portfolio WHERE id_user = ? AND type = 'stocks' AND name = ?''', (user_id, name))
        conn.commit()
        rows_deleted = c.rowcount
        conn.close()
        return rows_deleted > 0
    except sqlite3.Error as e:
        print(f"Error deleting stock: {e}")
        return False


def process_stock_price_step(message, bot: TeleBot):
    try:
        if not message.text or message.text.strip() == '':
            raise ValueError("Пустое или некорректное сообщение")

        print(f"Введенный текст: {message.text}")
        price = float(message.text.replace(',', '.'))
        print("Преобразование прошло успешно")

        bot.send_message(message.chat.id, "Введите дату покупки акции в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(message, process_stock_purchase_date_step, bot, price)
    except ValueError as e:
        print(f'Ошибка преобразования: {e}')
        bot.send_message(message.chat.id, "Некорректная стоимость акции. Пожалуйста, введите число.")


def process_stock_purchase_date_step(message, bot: TeleBot, price):
    date = message.text.strip()
    bot.send_message(message.chat.id, "Введите количество акций:")
    bot.register_next_step_handler(message, process_stock_quantity_step, bot, price, date)


def process_stock_quantity_step(message, bot: TeleBot, price, date):
    try:
        quantity = int(message.text.strip())
        bot.send_message(message.chat.id, "Введите название акции (опционально, введите 'empty' если нет):")
        bot.register_next_step_handler(message, process_stock_name_step, bot, price, date, quantity)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество акций. Пожалуйста, введите целое число.")


def process_stock_name_step(message, bot: TeleBot, price, date, quantity):
    name = message.text.strip()
    if name.lower() == 'empty':
        name = None
    bot.send_message(message.chat.id, "Введите тикер акции (опционально, введите 'empty' если нет):")
    bot.register_next_step_handler(message, process_stock_ticker_step, bot, price, date, quantity, name)


def process_stock_ticker_step(message, bot: TeleBot, price, date, quantity, name):
    ticker = message.text.strip()
    if ticker.lower() == 'empty':
        ticker = None
    if add_stock(message.chat.id, price, date, quantity, name=name, ticker=ticker):
        bot.send_message(message.chat.id, "Акция успешно добавлена в портфель!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении акции. Пожалуйста, попробуйте позже.")


def get_current_price(ticker):
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json'
    response = requests.get(url)
    print(response)
    data = response.json()
    marketdata = data.get('marketdata')

    if not marketdata:
        raise ValueError("Секция 'marketdata' не найдена в данных.")

    # Ищем индекс колонки 'LAST' в 'marketdata'
    columns = marketdata.get('columns', [])
    if 'LAST' not in columns:
        raise ValueError("Колонка 'LAST' не найдена в секции 'marketdata'.")

    last_index = columns.index('LAST')

    # Получаем данные из 'marketdata'
    market_data = marketdata.get('data', [])
    if not market_data:
        raise ValueError("Данные 'marketdata' отсутствуют.")

    # Извлекаем значение 'LAST' (текущую цену) из первого набора данных
    current_price = market_data[0][last_index]

    return current_price
