import telebot
import os
from dotenv import load_dotenv
from telebot import types
from database.portfolio_db import create_portfolio, delete_portfolio, check_portfolio_exists
from bot.stocks import *
from bot.bonds import *
from bot.utils import *

load_dotenv()

# Подключение к боту через токен
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Создать портфель")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Добро пожаловать в наш телеграмм бот!', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Создать портфель":
        if not check_portfolio_exists(message.chat.id):
            create_portfolio(message.chat.id)
            bot.send_message(message.chat.id, "Портфель успешно создан!")
            show_main_menu(message)
        else:
            bot.send_message(message.chat.id, "У вас уже есть портфель.")
            show_main_menu(message)
    elif message.text == "Посмотреть портфель":
        print('info_portfolio(message)')
    elif message.text == "Управление портфелем":
        show_portfolio_management_menu(message)
    elif message.text == "Получить портфель в виде таблицы":
        send_portfolio_as_excel(message)
    elif message.text == "Получить график":
        print('give_graph(message)')
    elif message.text == "Добавить акцию":
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
    elif message.text == "Назад к главному меню":
        show_main_menu(message)
    elif message.text == "Назад к управлению портфелем":
        show_portfolio_management_menu(message)


def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Посмотреть портфель")
    item2 = types.KeyboardButton("Управление портфелем")
    item3 = types.KeyboardButton("Получить портфель в виде таблицы")
    item4 = types.KeyboardButton("Получить график")
    item_back = types.KeyboardButton("Назад к главному меню")
    markup.row(item1)
    markup.row(item2)
    markup.row(item3, item4)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def show_portfolio_management_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить акцию")
    item2 = types.KeyboardButton("Удалить акцию")
    item3 = types.KeyboardButton("Добавить облигацию")
    item4 = types.KeyboardButton("Удалить облигацию")
    item_back = types.KeyboardButton("Назад к главному меню")
    markup.row(item1, item2)
    markup.row(item3, item4)
    markup.row(item_back)
    bot.send_message(message.chat.id, 'Управление портфелем:', reply_markup=markup)


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
