import telebot
import os
from dotenv import load_dotenv
from telebot import types
from database.portfolio_db import create_portfolio, delete_portfolio, check_portfolio_exists
from bot.stocks import *
from bot.bonds import *

load_dotenv()

# Подключение к боту через токен
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Создать портфель")
    item2 = types.KeyboardButton("Добавить акцию")
    item3 = types.KeyboardButton("Удалить акцию")
    item4 = types.KeyboardButton("Добавить облигацию")
    item5 = types.KeyboardButton("Удалить облигацию")
    markup.row(item1)
    markup.row(item2, item3)
    markup.row(item4, item5)
    bot.send_message(message.chat.id, 'Добро пожаловать в наш телеграмм бот!', reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Создать портфель":
        if not check_portfolio_exists(message.chat.id):
            create_portfolio(message.chat.id)
            bot.send_message(message.chat.id, "Портфель успешно создан!")
        else:
            bot.send_message(message.chat.id, "У вас уже есть портфель.")
    elif message.text == "Добавить акцию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите стоимость покупки акции:")
            bot.register_next_step_handler(message, process_stock_price_step(message, bot))
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
            bot.register_next_step_handler(message, process_bond_price_step)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для добавления облигации.")
    elif message.text == "Удалить облигацию":
        if check_portfolio_exists(message.chat.id):
            bot.send_message(message.chat.id, "Введите название облигации для удаления:")
            bot.register_next_step_handler(message, delete_bond)
        else:
            bot.send_message(message.chat.id, "У вас нет портфеля для удаления облигаций.")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
