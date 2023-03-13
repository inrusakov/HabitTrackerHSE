# Библиотека API Telegram.
import telebot
# Для указания Типов и создания внутренней клавиатуры.
from telebot import types
# Подключение бота по токену.
bot = telebot.TeleBot("5664679299:AAH-a6GwPCpPCHbaScJx4DB2iIe6mgdMljQ")

# Функция обработки команды start.
@bot.message_handler(commands=['start'])
def start_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! ".format(
                         message.from_user), reply_markup=markup)

# Функция обработки команды help.
@bot.message_handler(commands=['help'])
def help_command(message):
    print(log_commands(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/donate")
    btn2 = types.KeyboardButton("/message")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="rules"
                     .format(message.from_user), reply_markup=markup)

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
