# Библиотека API Telegram.
import telebot
import asyncio
import datetime
import pytz
import logging
import threading
import os
import json
# Для указания Типов и создания внутренней клавиатуры.
from telebot import types

# Функция для получения строк из документа с оригинальным разделением.
def read_and_combine_lines(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        combined_lines = ''.join(lines)
    return combined_lines

# Функция для получения строки из документа.
def get_string_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        str_data = f.readline().strip()
    return str_data

# Функция для записи данных в файл.
def save_data_to_file(file_path, user_dict):
    with open(file_path, "w") as f:
        json.dump(user_dict, f, default=lambda o: o.__json__(), indent=4)
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(moscow_tz)
    print("Time: " + str(now.hour)+":"+str(now.minute) +" Данные сохранены в файл.")

# Функция для чтения данных пользователей из файла.
def load_data_from_file(file_path):
    with open(file_path, "r") as f:
        file_content = f.read()
        if not file_content:
            print("Файл пуст.")
            return {}
        user_dict = json.loads(file_content)
        new_user_dict = {}
        for user_id, user_data in user_dict.items():
            new_user_dict[int(user_id)] = User(**user_data)
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = datetime.datetime.now(moscow_tz)
        print("Time: " + str(now.hour)+":"+str(now.minute) +" Данные загружены из файла.")
        return new_user_dict

# Подключение бота по токену.
bot = telebot.TeleBot(get_string_from_file("token.txt"))

# Времменная база данных для хранения информации о прогрессе пользователей.
user_dict = {}

# Класс хранения данных о пользователе.
class User:
    def __init__(self, user_id, current_book, pages, book_progress, condition, hour=None, minute=None):
        self.user_id = int(user_id)
        self.current_book = str(current_book)
        self.pages = int(pages)
        self.book_progress = int(book_progress)
        self.condition = str(condition)
        self.hour = int(hour) if hour is not None else None
        self.minute = int(minute) if minute is not None else None

    def __json__(self):
        return {
            "user_id": self.user_id,
            "current_book": self.current_book,
            "pages": self.pages,
            "book_progress": self.book_progress,
            "condition": self.condition,
            "hour": self.hour,
            "minute": self.minute
        }

    def __str__(self):
        return f"User ID: {self.user_id}, Current Book: {self.current_book}, Pages: {self.pages}, Book Progress: {self.book_progress}, Condition: {self.condition}, Time: {self.hour:02d}:{self.minute:02d}"

    def set_time(self, time_str):
        hour, minute = map(int, time_str.split(':'))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("Invalid time format")
        self.hour = hour
        self.minute = minute

# Функция обработки команды start.
@bot.message_handler(commands=['start'])
def start_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    user = message.from_user.username
    chat_id = message.chat.id
    log_users()
    
    user = User(chat_id, "", 0, 0, '0', 0, 0)
    user_dict[user.user_id] = user
    
    save_data_to_file("user_data.json", user_dict)
    with open(r'start.mp4', 'rb') as start_video:
        bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"startcommand.txt").format(message.from_user), reply_markup=markup)
        bot.send_video(message.chat.id, start_video, timeout=10)

# Функция обработки команды setatarget.
@bot.message_handler(commands=['setatarget'])
def setatarget_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    try:
        user_dict[message.chat.id].condition = 'STB'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"setatarget.txt").format(message.from_user))
    save_data_to_file("user_data.json", user_dict)

# Функция обработки команды addpages.
@bot.message_handler(commands=['addpages'])
def addpages_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    try:
        user_dict[message.chat.id].condition = 'APB'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"addpages.txt").format(message.from_user))
    save_data_to_file("user_data.json", user_dict)

# Функция обработки команды progress.
@bot.message_handler(commands=['progress'])
def progress_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    user_dict = load_data_from_file("user_data.json")

    try:
        bot.send_message(message.chat.id, 
                     text=read_and_combine_lines("commands"+os.sep+"progress.txt")
                     .format(message.from_user,
                              user_dict[message.chat.id].current_book,
                              user_dict[message.chat.id].book_progress,
                              user_dict[message.chat.id].pages), reply_markup=markup)
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return
    save_data_to_file("user_data.json", user_dict)

# Функция обработки команды help.
@bot.message_handler(commands=['info'])
def info_command(message):
    print(log_commands(message))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/progress")
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"infocommand.txt"), reply_markup=markup)

# Функция обработки команды donate.
@bot.message_handler(commands=['donate'])
def donate_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    bot.send_message(message.chat.id,
                     text="{0.first_name}, Спасибо за поддержку!"
                     .format(message.from_user), reply_markup=markup)

# Функция обработки сообщений и проверки состояния диалога для пользователей.    
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/progress")
    markup.add(btn1, btn2, btn3)
    
    user_dict = load_data_from_file("user_data.json")

    try:
        if(user_dict[message.chat.id].condition == 'STB'):
            bot.send_message(message.chat.id,
                        text="Название введено: {0.text}, теперь введите количество страниц."
                        .format(message))
            user_dict[message.chat.id].current_book = message.text
            user_dict[message.chat.id].condition = 'STN'
            save_data_to_file("user_data.json", user_dict)
            return

        if(user_dict[message.chat.id].condition == 'STN'):
            if(message.text.isnumeric()):
                bot.send_message(message.chat.id,
                        text="Введено количество страниц: {0.text}. \nТеперь введи время в которое я буду напоминать тебе о прочитанных страницах. \nПример ввода: 17:00"
                        .format(message))
                user_dict[message.chat.id].pages = int(message.text)
                user_dict[message.chat.id].condition = 'STT'
            else:
                bot.send_message(message.chat.id,
                        text="Неправильный формат ввода, введите число: {0.text}"
                        .format(message))
                return
            log_users()
            save_data_to_file("user_data.json", user_dict)
            return
        
        if(user_dict[message.chat.id].condition == 'STT'):
            try:
                user_dict[message.chat.id].set_time(message.text)
            except ValueError:
                bot.send_message(message.chat.id,
                        text="Неверный формат времени. Используйте формат «ЧЧ:ММ» (24-часовой формат).")
                return
            bot.send_message(message.chat.id,
                        text="Введено время: {0.text}, отлично теперь я буду каждый день напоминать тебе почитать книгу в это время"
                        .format(message), reply_markup=markup)
            user_dict[message.chat.id].condition = '0'
            log_users()
            save_data_to_file("user_data.json", user_dict)
            return

        if(user_dict[message.chat.id].condition == 'APB'):
            if(message.text.isnumeric()):
                user_dict[message.chat.id].book_progress += int(message.text)
                if(user_dict[message.chat.id].book_progress >= user_dict[message.chat.id].pages):
                    bot.send_message(message.chat.id,
                        text="{0.text} страниц добавлено к вашиму прогрессу, поздравляю с прочтением книги! Введи команду /setatarget и подолжай читать."
                        .format(message), reply_markup=markup)
                else:
                    bot.send_message(message.chat.id,
                            text="{0.text} страниц добавлено к вашиму прогрессу, текущий прогресс: {1}"
                            .format(message, user_dict[message.chat.id].book_progress), reply_markup=markup)
            else:
                bot.send_message(message.chat.id,
                        text="Неправильный формат ввода, введите число: {0.text}"
                        .format(message), reply_markup=markup)
                return
            user_dict[message.chat.id].condition = '0'
            log_users()
            save_data_to_file("user_data.json", user_dict)
            return

        else:
            bot.send_message(message.chat.id,
                        text="{0.first_name}, Введена неправильная команда"
                        .format(message.from_user), reply_markup=markup)
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

# Функция для логгирования всех пришедших боту обращений.
def log_commands(message):
    text = ""
    if message.caption is not None:
        text = message.caption
    if message.text is not None:
        text = message.text
    user = message.from_user.username
    chat_id = message.chat.id
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(moscow_tz)
    return "Time: " + str(now.hour)+":"+str(now.minute) +" Message: " + text + " from @" + user + " chat ID: " + str(chat_id)

# Функция для добавления/обновления информации о пользователя.
def log_users(filename="users_log.txt"):
    with open(filename, "a") as file:
        for user in user_dict.values():
            file.write(str(user) + "\n")

# Функция проверки времени заданного пользователем, и текущим временем для отправки ему напоминаний.
async def check_user_times():
    moscow_tz = pytz.timezone('Europe/Moscow')
    while True:
        user_dict = load_data_from_file("user_data.json")
        now = datetime.datetime.now(moscow_tz)
        for user in user_dict.values():
            if user.hour == now.hour and user.minute == now.minute:
                bot.send_message(user.user_id,
                     text="Привет, ты уже читал сегодня свою книгу? Если да, нажми команду /addpages и введи свои страницы.")
        await asyncio.sleep(60)

# Запуск функции с проверкой времени.
async def main():
    tasks = [
        asyncio.create_task(check_user_times())
    ]
    for task in tasks:
        await task

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=bot.polling, kwargs={"none_stop": True}).start()
    asyncio.run(main())
