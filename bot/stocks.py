import sqlite3
from telebot import TeleBot
from database.portfolio_db import db_path


def add_stock(user_id, purchase_price, purchase_date, quantity, nominal_value=None, name=None):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, nominal_value, name) 
                     VALUES (?, 'stocks', ?, ?, ?, ?, ?)''',
                  (user_id, purchase_price, purchase_date, quantity, nominal_value, name))
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
        price = float(message.text.replace(',', '.'))
        bot.send_message(message.chat.id, "Введите дату покупки акции в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(message, process_stock_purchase_date_step, bot, price)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректная стоимость акции. Пожалуйста, введите число.")


def process_stock_purchase_date_step(message, bot: TeleBot, price):
    date = message.text.strip()
    bot.send_message(message.chat.id, "Введите количество акций:")
    bot.register_next_step_handler(message, process_stock_quantity_step, bot, price, date)


def process_stock_quantity_step(message, bot: TeleBot, price, date):
    try:
        quantity = int(message.text.strip())
        bot.send_message(message.chat.id, "Введите номинальную стоимость акции (опционально, оставьте пустым, если нет):")
        bot.register_next_step_handler(message, process_stock_nominal_step, bot, price, date, quantity)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество акций. Пожалуйста, введите целое число.")


def process_stock_nominal_step(message, bot: TeleBot, price, date, quantity):
    nominal = message.text.strip() if message.text.strip() else None
    bot.send_message(message.chat.id, "Введите название акции (опционально):")
    bot.register_next_step_handler(message, lambda msg: process_stock_name_step(msg, bot, price, date, quantity, nominal))


def process_stock_name_step(message, bot: TeleBot, price, date, quantity, nominal):
    name = message.text.strip() if message.text.strip() else None
    if add_stock(message.chat.id, price, date, quantity, nominal_value=nominal, name=name):
        bot.send_message(message.chat.id, "Акция успешно добавлена в портфель!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении акции. Пожалуйста, попробуйте позже.")
