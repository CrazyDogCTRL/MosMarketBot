import sqlite3
import os
import requests
from start import *
# Путь к файлу базы данных SQLite
db_path = os.path.join(os.path.dirname(__file__), 'portfolio_db.sqlite')


def initialize_database():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Создание таблицы, если она не существует
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user BIGINT NOT NULL,
                type TEXT NOT NULL,
                purchase_price DECIMAL(10, 2) NOT NULL,
                purchase_date DATE NOT NULL,
                quantity INT NOT NULL,
                nominal_value DECIMAL(10, 2),
                maturity_date DATE,
                dividend DECIMAL(10, 2),
                name TEXT,
                ticker TEXT,
                exist BOOLEAN DEFAULT 0  -- Добавляем столбец exist
            )
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")


def check_portfolio_exists(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверка наличия портфеля для конкретного пользователя
        cursor.execute('SELECT COUNT(*) FROM portfolio WHERE id_user = ?', (user_id,))
        count = cursor.fetchone()[0]

        conn.close()

        return count > 0
    except Exception as e:
        print(f"Error checking portfolio existence: {e}")
        return False


def create_portfolio(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Вставка данных о портфеле
        cursor.execute('''
            INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker)
            VALUES (?, '', 0.0, '', 0, 0.0, '', 0.0, '', '')
        ''', (user_id,))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error creating portfolio: {e}")
        return False


def delete_portfolio(user_id):
    try:
        # Проверяем, существует ли портфель для данного пользователя
        if not check_portfolio_exists(user_id):
            print(f"Portfolio does not exist for user {user_id}")
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Удаление портфеля для конкретного пользователя
        cursor.execute('DELETE FROM portfolio WHERE id_user = ?', (user_id,))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error deleting portfolio: {e}")
        return False

def add_asset(user_id, asset_type, purchase_price, purchase_date, quantity, nominal_value=None, maturity_date=None,
              dividend=None, name=None, ticker=None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        stock_exists = True
        # Вставка данных об активе в портфель пользователя
        cursor.execute('''
            INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker, exist)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, asset_type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name,
            ticker, stock_exists))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error adding asset: {e}")
        return False


def handle_portfolio_management(message):
    if message.text == "Добавить акцию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите стоимость покупки акции:")
            bot.register_next_step_handler(message, process_stock_price_step, bot)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для добавления акции.")
    elif message.text == "Удалить акцию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите название акции для удаления:")
            bot.register_next_step_handler(message, delete_stock)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для удаления акций.")
    elif message.text == "Добавить облигацию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите стоимость покупки облигации:")
            bot.register_next_step_handler(message, process_bond_price_step, bot)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для добавления облигации.")
    elif message.text == "Удалить облигацию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите название облигации для удаления:")
            bot.register_next_step_handler(message, delete_bond)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для удаления облигаций.")
    elif message.text == "Назад к управлению портфелем":
        show_portfolio_management_menu(message)


def rename_asset(user_id, new_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Обновление имени актива для конкретного пользователя
        cursor.execute('UPDATE portfolio SET name = ? WHERE id_user = ?', (new_name, user_id))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error renaming asset: {e}")
        return False


def get_portfolio(user_id):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''SELECT purchase_price, purchase_date, quantity, name, ticker
                     FROM portfolio
                     WHERE id_user = ? AND type = 'stocks' ''', (user_id,))
        portfolio = {}
        rows = c.fetchall()
        # Нумерация с 1
        for index, row in enumerate(rows, start=1):
            portfolio[index] = {
                'purchase_price': row[0],
                'purchase_date': row[1],
                'quantity': row[2],
                'name': row[3],
                'ticker': row[4]
            }
        conn.close()
        return portfolio
    except sqlite3.Error as e:
        print(f"Error retrieving portfolio: {e}")
        return None


def generate_portfolio_message_for_user(user_id):
    portfolio = get_portfolio(user_id)

    if not portfolio:
        return "Ваш портфель пуст или произошла ошибка при получении данных."

    message = "Ваш портфель (первые 5 акций):\n"
    total_value = 0
    count = 0

    # Считаем общую стоимость портфеля и формируем сообщение для первых 5 акций
    for stock_id, stock_data in portfolio.items():
        total_value += stock_data['purchase_price'] * stock_data['quantity']

    for index, (stock_id, stock_data) in enumerate(portfolio.items(), start=1):
        if index > 5:
            break
        message += (
            f"\nАкция {index}:\n"
            f"Название: {stock_data['name'] if stock_data['name'] else 'Не указано'}\n"
            f"Тикер: {stock_data['ticker'] if stock_data['ticker'] else 'Не указан'}\n"
            f"Цена покупки: {stock_data['purchase_price']}\n"
            f"Дата покупки: {stock_data['purchase_date']}\n"
            f"Количество: {stock_data['quantity']}\n"
            f"Стоимость: {stock_data['purchase_price'] * stock_data['quantity']}\n"
        )

    message += f"\nИтоговая стоимость всего портфеля: {total_value}"
    return message


# Вызываем инициализацию базы данных при импорте модуля
initialize_database()

# Debug
# print(generate_portfolio_message_for_user(986804319))
# print(check_stock_exists_on_moex("ABIO1"))
