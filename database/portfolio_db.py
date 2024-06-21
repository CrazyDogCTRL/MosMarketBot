import sqlite3
import os

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
                ticker TEXT
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

        # Вставка данных об активе в портфель пользователя
        cursor.execute('''
            INSERT INTO portfolio (id_user, type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        user_id, asset_type, purchase_price, purchase_date, quantity, nominal_value, maturity_date, dividend, name, ticker))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error adding asset: {e}")
        return False


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


# Вызываем инициализацию базы данных при импорте модуля
initialize_database()

print(get_portfolio(986804319))
