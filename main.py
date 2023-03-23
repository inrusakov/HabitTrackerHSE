# Библиотека API Telegram.
import telebot
# Для указания Типов и создания внутренней клавиатуры.
from telebot import types
from datetime import datetime, date, time
# Функция для получения строки из документа.
def get_string_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        str_data = f.readline().strip()
    return str_data
# Подключение бота по токену.
bot = telebot.TeleBot(get_string_from_file("token.txt"))
# Времменная база данных для хранения информации о прогрессе пользователей.
users = {}
# Функция для добавления/обновления информации о пользователя.
def update_user_data(chat_id, user):
    users[chat_id] = {user, datetime.now()}


# Функция обработки команды start.
@bot.message_handler(commands=['start'])
def start_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    user = message.from_user.username
    chat_id = message.chat.id
    update_user_data(chat_id, user)
    markup.add(btn1)
    bot.send_message(message.chat.id, text=get_string_from_file("startcommand.txt").format(message.from_user), reply_markup=markup)

# Функция обработки команды setatarget.
@bot.message_handler(commands=['setatarget'])
def start_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)
    bot.send_message(message.chat.id, text="“Добавить цель” - выбери цель, к которой будешь стремиться".format(message.from_user), reply_markup=markup)

# Функция обработки команды addpages.
@bot.message_handler(commands=['addpages'])
def start_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)
    bot.send_message(message.chat.id, 
                     text="“Добавить количество прочитанных страниц” - Что ты сделал для достижения своей цели? введи число прочитанных страниц"
                     .format(message.from_user), reply_markup=markup)

# Функция обработки команды progress.
@bot.message_handler(commands=['progress'])
def start_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)
    bot.send_message(message.chat.id, text="“Отследить прогресс” - посмотри свою статистику за месяц".format(message.from_user), reply_markup=markup)


# Функция обработки команды help.
@bot.message_handler(commands=['info'])
def help_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/progress")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text=get_string_from_file("infocommand.txt").format(message.from_user), reply_markup=markup)

# Функция обработки команды donate.
@bot.message_handler(commands=['donate'])
def help_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="{0.first_name}, Спасибо за поддержку!"
                     .format(message.from_user), reply_markup=markup)

# Функция для логгирования всех пришедших боту обращений.
def log_commands(message):
    text = ""
    if message.caption is not None:
        text = message.caption
    if message.text is not None:
        text = message.text
    user = message.from_user.username
    chat_id = message.chat.id
    return "I got this message: " + text + " from @" + user + " chat ID: " + str(chat_id)

# Команда которая говорит боту, что нужно забирать полученные сообщения.
bot.infinity_polling()
