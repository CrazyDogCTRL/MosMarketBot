import sqlite3
from telebot import TeleBot
from database.portfolio_db import db_path

def add_bond(user_id, purchase_price, purchase_date, quantity, nominal_value=None, maturity_date=None, dividend=None, name=None, ticker=None):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker) 
                     VALUES (?, 'bonds', ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding bond: {e}")
        return False

def delete_bond(user_id, name):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''DELETE FROM portfolio WHERE id_user = ? AND type = 'bonds' AND name = ?''', (user_id, name))
        conn.commit()
        rows_deleted = c.rowcount
        conn.close()
        return rows_deleted > 0
    except sqlite3.Error as e:
        print(f"Error deleting bond: {e}")
        return False

def process_bond_price_step(message, bot):
    try:
        price = float(message.text.replace(',', '.'))
        bot.send_message(message.chat.id, "Введите дату покупки облигации в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(message, process_bond_purchase_date_step, bot, price)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректная стоимость облигации. Пожалуйста, введите число.")

def process_bond_purchase_date_step(message, bot: TeleBot, price):
    date = message.text.strip()
    bot.send_message(message.chat.id, "Введите количество облигаций:")
    bot.register_next_step_handler(message, process_bond_quantity_step, bot, price, date)

def process_bond_quantity_step(message, bot: TeleBot, price, date):
    try:
        quantity = int(message.text.strip())
        bot.send_message(message.chat.id, "Введите номинальную стоимость облигации (опционально, оставьте пустым, если нет):")
        bot.register_next_step_handler(message, process_bond_nominal_step, bot, price, date, quantity)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество облигаций. Пожалуйста, введите целое число.")

def process_bond_nominal_step(message, bot: TeleBot, price, date, quantity):
    nominal = message.text.strip() if message.text.strip() else None
    bot.send_message(message.chat.id, "Введите дату погашения облигации в формате ГГГГ-ММ-ДД (опционально):")
    bot.register_next_step_handler(message, process_bond_maturity_date_step, bot, price, date, quantity, nominal)

def process_bond_maturity_date_step(message, bot: TeleBot, price, date, quantity, nominal):
    maturity_date = message.text.strip() if message.text.strip() else None
    bot.send_message(message.chat.id, "Введите размер дивиденда (опционально):")
    bot.register_next_step_handler(message, process_bond_dividend_step, bot, price, date, quantity, nominal, maturity_date)

def process_bond_dividend_step(message, bot: TeleBot, price, date, quantity, nominal, maturity_date):
    dividend = message.text.strip() if message.text.strip() else None
    bot.send_message(message.chat.id, "Введите название облигации (опционально):")
    bot.register_next_step_handler(message, lambda msg: process_bond_name_step(msg, bot, price, date, quantity, nominal, maturity_date, dividend))

def process_bond_name_step(message, bot: TeleBot, price, date, quantity, nominal, maturity_date, dividend):
    name = message.text.strip() if message.text.strip() else None
    bot.send_message(message.chat.id, "Введите тикер облигации:")
    bot.register_next_step_handler(message, lambda msg: process_bond_ticker_step(msg, bot, price, date, quantity, nominal, maturity_date, dividend, name))

def process_bond_ticker_step(message, bot: TeleBot, price, date, quantity, nominal, maturity_date, dividend, name):
    ticker = message.text.strip() if message.text.strip() else None
    if add_bond(message.chat.id, price, date, quantity, nominal_value=nominal, maturity_date=maturity_date, dividend=dividend, name=name, ticker=ticker):
        bot.send_message(message.chat.id, "Облигация успешно добавлена в портфель!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении облигации. Пожалуйста, попробуйте позже.")
