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

# -----------------Функция для получения строк из документа с оригинальным разделением.-----------------
def read_and_combine_lines(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        combined_lines = ''.join(lines)
    return combined_lines

# -----------------Функция для получения строки из документа.-----------------
def get_string_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        str_data = f.readline().strip()
    return str_data

# -----------------Функция для записи данных в файл.-----------------
def save_data_to_file(file_path, user_dict):
    with open(file_path, "w") as f:
        json.dump(user_dict, f, default=lambda o: o.__json__(), indent=4)
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(moscow_tz)
    print("Time: " + str(now.hour)+":"+str(now.minute) +" Данные сохранены в файл.")

# -----------------Функция для чтения данных пользователей из файла.-----------------
def load_data_from_file(file_path):
    with open(file_path, "r") as f:
        file_content = f.read()
        if not file_content:
            print("Файл пуст.")
            return {}
        user_dict = json.loads(file_content)
        new_user_dict = {}
        for user_id, user_data in user_dict.items():
            user_books = user_data.pop('books', [])
            user = User(**user_data)
            for book_data in user_books:
                user.add_book(**book_data)
            new_user_dict[int(user_id)] = user
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = datetime.datetime.now(moscow_tz)
        print("Time: " + str(now.hour)+":"+str(now.minute) +" Данные загружены из файла.")
        return new_user_dict

# -----------------Создание книги из строки запроса пользователя.-----------------
def create_book_from_string(book_string):
    if not book_string:
        raise ValueError("Пустая строка недопустима.")

    book_parts = book_string.split(',')
    if len(book_parts) != 2:
        raise ValueError("Строка должна содержать только название книги и количество страниц, разделенные запятой.")

    title = book_parts[0].strip()
    if not title:
        raise ValueError("Название книги не может быть пустым.")

    try:
        pages = int(book_parts[1].strip())
    except ValueError:
        raise ValueError("Количество страниц должно быть целым числом.")

    if pages <= 0:
        raise ValueError("Количество страниц должно быть положительным числом.")

    return Book(title=title, pages=pages, progress=0)

# -----------------Подключение бота по токену.-----------------
bot = telebot.TeleBot(get_string_from_file("token.txt"))

# -----------------Времменная база данных для хранения информации о прогрессе пользователей.-----------------
user_dict = {}

# -----------------Класс хранения данных о книгах пользователя.-----------------
class Book:
    def __init__(self, title, pages, progress):
        self.title = str(title)
        self.pages = int(pages)
        self.progress = int(progress)

    def __json__(self):
        return {
            "title": self.title,
            "pages": self.pages,
            "progress": self.progress
        }

    def __str__(self):
        percent = round(self.progress / self.pages * 100, 2)
        return f"{self.title}: прочитано {self.progress} из {self.pages} - ({percent}%)"

# -----------------Класс хранения данных о пользователе.-----------------
class User:
    def __init__(self, user_id, condition, current, hour=None, minute=None):
        self.user_id = int(user_id)
        self.condition = str(condition)
        self.hour = int(hour) if hour is not None else None
        self.minute = int(minute) if minute is not None else None
        self.books = []
        self.current = str(current)

    def __json__(self):
        return {
            "user_id": self.user_id,
            "condition": self.condition,
            "hour": self.hour,
            "minute": self.minute,
            "books": [book.__json__() for book in self.books],
            "current": self.current
        }

    def __str__(self):
        books_str = ', '.join(str(book) for book in self.books)
        return f"User ID: {self.user_id}, Condition: {self.condition}, Time: {self.hour:02d}:{self.minute:02d}, Books: [{books_str}], Current: {self.current}"

    def set_time(self, time_str):
        hour, minute = map(int, time_str.split(':'))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("Invalid time format")
        self.hour = hour
        self.minute = minute

    def add_book(self, title, pages, progress):
        self.books.append(Book(title, pages, progress))

    def get_books_info(self):
        books_info = []
        books_info.append("\n")
        for book in self.books:
            books_info.append(str(book))
        return "\n".join(books_info)

    def update_book_progress(self, progress_to_add):
        if not isinstance(progress_to_add, int):
            raise ValueError("Значение прогресса должно быть целым числом.")

        book_found = False
        for book in self.books:
            if book.title == self.current:
                bookSum = book.progress + progress_to_add
                bookDiv = book.pages-book.progress
                if(book.pages < bookSum):
                    stringEx = "Кажется в книге осталось меньше страниц, чем вы прочитали. В книге осталось: "+ str(bookDiv) +" страниц."
                    raise ValueError(stringEx)
                else :
                    book.progress += progress_to_add
                    book_found = True
                    break

        if not book_found:
            raise ValueError(f"Книга с названием '{self.current}' не найдена.")

    def remove_book(self, title):
        for book in self.books:
            if book.title == title:
                self.books.remove(book)
                return
        raise ValueError(f"Книга с названием '{title}' не найдена.")


# -----------------Функция обработки команды start.-----------------
@bot.message_handler(commands=['start'])
def start_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    user = message.from_user.username
    chat_id = message.chat.id
    log_users()

    user = User(chat_id, "0", "", 12, 0)
    user_dict[user.user_id] = user

    save_data_to_file("user_data.json", user_dict)
    with open(r'start.mp4', 'rb') as start_video:
        bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"startcommand.txt").format(message.from_user), reply_markup=markup)
        bot.send_video(message.chat.id, start_video, timeout=15)

# -----------------Функция обработки команды setatarget.-----------------
@bot.message_handler(commands=['setatarget'])
def setatarget_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    try:
        user_dict[message.chat.id].condition = 'STB'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"setatarget.txt").format(message.from_user), reply_markup=markup)
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды addpages.-----------------
@bot.message_handler(commands=['addpages'])
def addpages_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    try:
        if(len(user_dict[message.chat.id].books) == 0):
            bot.send_message(message.chat.id,
                     text="У тебя пока нет ни одной книги в списке. Введи команду /setatarget и добавь свою первую книгу."
                     .format(message.from_user))
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for book in user_dict[message.chat.id].books:
            btn = types.KeyboardButton(book.title)
            markup.add(btn)

        user_dict[message.chat.id].condition = 'APB'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"addpages.txt").format(message.from_user), reply_markup=markup)
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды notification.-----------------
@bot.message_handler(commands=['notification'])
def notification_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    try:
        user_dict[message.chat.id].condition = 'NT'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text="Введи время в которое я буду напоминать тебе о прочитанных страницах.\nПример ввода: 17:00", reply_markup=markup)
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды delete.-----------------
@bot.message_handler(commands=['delete'])
def delete_command(message):
    print(log_commands(message))

    user_dict = load_data_from_file("user_data.json")

    try:
        if(len(user_dict[message.chat.id].books) == 0):
            bot.send_message(message.chat.id,
                     text="У тебя пока нет ни одной книги в списке. Введи команду /setatarget и добавь свою первую книгу."
                     .format(message.from_user))
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for book in user_dict[message.chat.id].books:
            btn = types.KeyboardButton(book.title)
            markup.add(btn)

        user_dict[message.chat.id].condition = 'DEL'
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return

    bot.send_message(message.chat.id, text="Выбери книгу которую хочешь удалить из отслеживаемых", reply_markup=markup)
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды progress.-----------------
@bot.message_handler(commands=['progress'])
def progress_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/notification")
    btn4 = types.KeyboardButton("/progress")
    btn5 = types.KeyboardButton("/delete")
    btn6 = types.KeyboardButton("/rating")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    user_dict = load_data_from_file("user_data.json")

    try:
        if(len(user_dict[message.chat.id].books) == 0):
            bot.send_message(message.chat.id,
                     text="У тебя пока нет ни одной книги в списке. Введи команду /setatarget и добавь свою первую книгу."
                     .format(message.from_user))
            return
        bot.send_message(message.chat.id,
                     text=read_and_combine_lines("commands"+os.sep+"progress.txt")
                     .format(message.from_user,
                              user_dict[message.chat.id].get_books_info()), reply_markup=markup)
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды rating.-----------------
@bot.message_handler(commands=['rating'])
def progress_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/notification")
    btn4 = types.KeyboardButton("/progress")
    btn5 = types.KeyboardButton("/delete")
    btn6 = types.KeyboardButton("/rating")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    user_dict = load_data_from_file("user_data.json")

    try:
        write_user_progress_to_file("rating.txt", user_dict)
        bot.send_message(message.chat.id, text=get_user_info("rating.txt", message.chat.id))
        with open(r'adv2.jpg', 'rb') as adv:
            bot.send_photo(message.chat.id, adv, timeout=10, caption=read_and_combine_lines("commands"+os.sep+"adv.txt"))
    except:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, бот перезапускался, для корректной работы начни с команды /start."
                     .format(message.from_user))
        return
    save_data_to_file("user_data.json", user_dict)

# -----------------Функция обработки команды help.-----------------
@bot.message_handler(commands=['info'])
def info_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/notification")
    btn4 = types.KeyboardButton("/progress")
    btn5 = types.KeyboardButton("/delete")
    btn6 = types.KeyboardButton("/rating")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands"+os.sep+"infocommand.txt"), reply_markup=markup)

# -----------------Функция обработки команды donate.-----------------
@bot.message_handler(commands=['donate'])
def donate_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    bot.send_message(message.chat.id,
                     text="{0.first_name}, Спасибо за поддержку!"
                     .format(message.from_user), reply_markup=markup)

# -----------------Функция обработки сообщений и проверки состояния диалога для пользователей.-----------------
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/notification")
    btn4 = types.KeyboardButton("/progress")
    btn5 = types.KeyboardButton("/delete")
    btn6 = types.KeyboardButton("/rating")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    user_dict = load_data_from_file("user_data.json")


    #---------------------------------------------------------Введена команда /setatarget-----------------------------------
    try:
        if(user_dict[message.chat.id].condition == 'STB'):
            try:
                book = create_book_from_string(message.text)
                user_dict[message.chat.id].books.append(book)
                bot.send_message(message.chat.id,
                        text="Поздравляю! Добавлена новая книга:\nНазвание - {0}\nКоличество страниц - {1}.\nНе забудь ввести команду /notification и задать время, в которое я буду напоминать тебе о чтении."
                        .format(book.title, book.pages), reply_markup=markup)
            except ValueError as inst:
                bot.send_message(message.chat.id, text="{0}".format(inst))
                return

            user_dict[message.chat.id].condition = '0'
            save_data_to_file("user_data.json", user_dict)
            return

    #---------------------------------------------------------Введена команда /notification-----------------------------------
        if(user_dict[message.chat.id].condition == 'NT'):
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
    #---------------------------------------------------------Введена команда /addpages-----------------------------------
        if(user_dict[message.chat.id].condition == 'APB'):
            try:
                user_dict[message.chat.id].current = message.text
            except ValueError:
                bot.send_message(message.chat.id,
                        text="Что-то пошло не так, попробуй перезапустить бота.")
                return
            bot.send_message(message.chat.id,
                        text="Выбрана книга: {0.text}, теперь введи количество страниц, которое ты прочитал."
                        .format(message), reply_markup=markup)
            user_dict[message.chat.id].condition = 'APN'
            log_users()
            save_data_to_file("user_data.json", user_dict)
            return

    #---------------------------------------------------------Введена команда /delete-----------------------------------
        if(user_dict[message.chat.id].condition == 'DEL'):
            try:
                user_dict[message.chat.id].remove_book(message.text)
            except ValueError as inst:
                bot.send_message(message.chat.id, text="{0}".format(inst))
                return
            bot.send_message(message.chat.id,
                        text="Книга {0.text} удалена из вашего списка."
                        .format(message), reply_markup=markup)
            user_dict[message.chat.id].condition = '0'
            log_users()
            save_data_to_file("user_data.json", user_dict)
            return

    #---------------------------------------------------------2 шаг команды /addpages-----------------------------------
        if(user_dict[message.chat.id].condition == 'APN'):
            try:
                if(message.text.isnumeric()):
                    user_dict[message.chat.id].update_book_progress(int(message.text))
                    bot.send_message(message.chat.id,
                                text="{0.text} страниц добавлено к вашиму прогрессу, текущий прогресс по вашим книгам такой: {1}"
                                .format(message, user_dict[message.chat.id].get_books_info()), reply_markup=markup)
            except ValueError as inst:
                bot.send_message(message.chat.id, text="{0}".format(inst), reply_markup=markup)
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

# -----------------Функция для логгирования всех пришедших боту обращений.-----------------
def log_commands(message):
    if message is None:
        message = "No message provided"
    if message.from_user is None:
        user = "Unknown user"
    else:
        try:
            user = "@" + message.from_user.username
        except:
            user = "@Unknown"
    if message.chat is None:
        chat_id = "Unknown chat"
    else:
        chat_id = message.chat.id
    text = ""
    if message.caption is not None:
        text = message.caption
    if message.text is not None:
        text = message.text
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(moscow_tz)
    return "Time: " + str(now.hour)+":"+str(now.minute) +" Message: " + text + " from " + user + " chat ID: " + str(chat_id)

# -----------------Функция для добавления/обновления информации о пользователя.-----------------
def log_users(filename="users_log.txt"):
    with open(filename, "a") as file:
        for user in user_dict.values():
            file.write(str(user) + "\n")

# -----------------Функция рейтинга пользователей.-----------------
def get_user_info(file_path, user_id):
    # Открываем файл и считываем данные
    with open(file_path, 'r') as f:
        data = f.readlines()

    # Преобразуем данные в список кортежей (id, count)
    data = [tuple(map(int, line.strip().split(','))) for line in data]

    # Сортируем список по параметру count
    data.sort(key=lambda x: x[1], reverse=True)

    # Находим место пользователя в отсортированном списке
    user_place = next((i+1 for i, (id, count) in enumerate(data) if id == user_id), None)

    # Вычисляем сумму всех count
    total_count = sum(count for id, count in data)

    # Вычисляем сумму всех id
    total_id = len(data)

    # Находим наибольшее значение count
    max_count = max(count for id, count in data)

    # Формируем сообщение
    message = f"Поздравляю, вы заняли {user_place} место среди {total_id} пользователей.\nЗа неделю всеми пользователями было прочитано {total_count} страниц.\nНаибольшее количество прочитанных страниц одним пользователем составляет: {max_count}."

    return message

# -----------------Функция записи рейтинга пользователей.-----------------
def write_user_progress_to_file(file_path, user_dict):
    with open(file_path, 'w') as f:
        for user_id, user in user_dict.items():
            progress_sum = sum(book.progress for book in user.books)
            f.write(f"{user_id},{progress_sum}\n")

# -----------------Функция проверки времени заданного пользователем, и текущим временем для отправки ему напоминаний.-----------------
async def check_user_times():
    moscow_tz = pytz.timezone('Europe/Moscow')
    while True:
        user_dict = load_data_from_file("user_data.json")
        now = datetime.datetime.now(moscow_tz)
        for user in user_dict.values():
            if user.hour == now.hour and user.minute == now.minute:
                try:
                    bot.send_message(user.user_id,text=read_and_combine_lines("commands"+os.sep+"notification.txt"))
                except:
                    print(user.user_id+" blocked bot")
        await asyncio.sleep(60)

# -----------------Запуск функции с проверкой времени.-----------------
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
