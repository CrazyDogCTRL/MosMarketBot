import telebot
import requests
from datetime import datetime
from telebot import types

# Токен вашего телеграм-бота
TOKEN = '6969605692:AAGjOdUYxj00QWlOlK35wnBbVIcmxXo4Qes'
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения информации о портфелях пользователей
user_portfolios = {}

# Получение текущей цены акции с Московской биржи
def get_stock_price(ticker):
    try:
        url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json'
        response = requests.get(url)
        data = response.json()
        last_price = data['marketdata']['data'][0][8]  # Индекс 8 соответствует последней цене
        return last_price
    except Exception as e:
        return None

# Команда старт
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить акцию")
    item2 = types.KeyboardButton("Просмотр портфеля")
    item3 = types.KeyboardButton("Текущая цена акции")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)

# Обработка нажатий кнопок
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Добавить акцию":
        bot.send_message(message.chat.id, "Введите данные акции в формате: TICKER PRICE DATE (в формате YYYY-MM-DD)")
        bot.register_next_step_handler(message, add_stock)
    elif message.text == "Просмотр портфеля":
        view_portfolio(message)
    elif message.text == "Текущая цена акции":
        bot.send_message(message.chat.id, "Введите тикер акции:")
        bot.register_next_step_handler(message, current_stock_price)
    else:
        bot.send_message(message.chat.id, "Неверная команда. Пожалуйста, используйте кнопки для взаимодействия с ботом.")

# Добавление акции в портфель
def add_stock(message):
    try:
        msg = message.text.split()
        if len(msg) != 3:
            raise ValueError("Некорректный формат команды. Используйте: TICKER PRICE DATE (в формате YYYY-MM-DD)")
        ticker = msg[0].upper()
        price = float(msg[1])
        date = datetime.strptime(msg[2], '%Y-%m-%d')
        user_id = message.chat.id

        if user_id not in user_portfolios:
            user_portfolios[user_id] = []

        user_portfolios[user_id].append({"ticker": ticker, "price": price, "date": date})

        bot.send_message(user_id, f"Акция {ticker} добавлена в ваш портфель по цене {price} на дату {date.date()}.")
    except ValueError as ve:
        bot.send_message(message.chat.id, str(ve))
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении акции. Убедитесь, что формат команды правильный.")

# Вывод стоимости портфеля
def view_portfolio(message):
    user_id = message.chat.id
    if user_id not in user_portfolios or not user_portfolios[user_id]:
        bot.send_message(user_id, "Ваш портфель пуст.")
        return

    total_value = 0.0
    total_initial_value = 0.0
    response_message = "Ваш портфель:\n\n"
    for stock in user_portfolios[user_id]:
        ticker = stock["ticker"]
        initial_price = stock["price"]
        current_price = get_stock_price(ticker)
        if current_price is not None:
            change = (current_price - initial_price) / initial_price * 100
            response_message += f"{ticker}: покупка по {initial_price} руб., текущая цена {current_price} руб., изменение {change:.2f}%\n"
            total_value += current_price
            total_initial_value += initial_price
        else:
            response_message += f"{ticker}: покупка по {initial_price} руб., текущая цена не доступна\n"

    if total_initial_value == 0:
        bot.send_message(user_id, "Не удалось рассчитать изменение стоимости портфеля, так как нет доступных данных о текущих ценах акций.")
    else:
        total_change = (total_value - total_initial_value) / total_initial_value * 100
        response_message += f"\nОбщая стоимость портфеля: {total_value:.2f} руб.\nОбщее изменение: {total_change:.2f}%"
        bot.send_message(user_id, response_message)

# Получение текущей цены акции
def current_stock_price(message):
    ticker = message.text.upper()
    current_price = get_stock_price(ticker)
    if current_price is not None:
        bot.send_message(message.chat.id, f"Текущая цена акции {ticker}: {current_price} руб.")
    else:
        bot.send_message(message.chat.id, "Не удалось получить текущую цену акции. Проверьте правильность тикера.")

# Запуск бота
bot.polling(none_stop=True, interval=0)
