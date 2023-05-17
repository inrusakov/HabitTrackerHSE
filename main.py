# Библиотека API Telegram.
import telebot, json, pickle
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

# Подключение бота по токену.
bot = telebot.TeleBot(get_string_from_file("token.txt"))

# Времменная база данных для хранения информации о прогрессе пользователей.
user_dict = {}

# Функция для добавления/обновления информации о пользователя.
def log_users(filename="users_log.txt"):
    with open(filename, "a") as file:
        for user in user_dict.values():
            file.write(str(user) + "\n")

# Класс хранения данных о пользователе.
class User:
    def __init__(self, user_id, current_book, pages, book_progress, condition):
        self.user_id = user_id
        self.current_book = current_book
        self.pages = pages
        self.book_progress = book_progress
        self.condition = condition

    def __str__(self):
        return f"User ID: {self.user_id}, Current Book: {self.current_book}, Pages: {self.pages}, Book Progress: {self.book_progress}, condition: {self.condition}%"

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

    user = User(chat_id, "", 0, 0, '0')
    user_dict[user.user_id] = user
    
    start_video = open(r'C:\Users\Rus-P\Desktop\Work\HSE\HabitBot\HabitTrackerHSE\start.mp4', 'rb')
    bot.send_message(message.chat.id, text=read_and_combine_lines("commands\startcommand.txt").format(message.from_user), reply_markup=markup)
    bot.send_video(message.chat.id, start_video, timeout=10)

# Функция обработки команды setatarget.
@bot.message_handler(commands=['setatarget'])
def start_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    user_dict[message.chat.id].condition = 'STB'

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands\setatarget.txt").format(message.from_user), reply_markup=markup)

# Функция обработки команды addpages.
@bot.message_handler(commands=['addpages'])
def start_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    user_dict[message.chat.id].condition = 'APB'

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands\\addpages.txt").format(message.from_user), reply_markup=markup)

# Функция обработки команды progress.
@bot.message_handler(commands=['progress'])
def start_command(message):
    print(log_commands(message))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/info")
    markup.add(btn1)

    bot.send_message(message.chat.id, 
                     text=read_and_combine_lines("commands\progress.txt")
                     .format(message.from_user,
                              user_dict[message.chat.id].current_book,
                              user_dict[message.chat.id].book_progress,
                              user_dict[message.chat.id].pages), reply_markup=markup)

# Функция обработки команды help.
@bot.message_handler(commands=['info'])
def help_command(message):
    print(log_commands(message))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/setatarget")
    btn2 = types.KeyboardButton("/addpages")
    btn3 = types.KeyboardButton("/progress")
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, text=read_and_combine_lines("commands\infocommand.txt"), reply_markup=markup)

# Функция обработки команды donate.
@bot.message_handler(commands=['donate'])
def help_command(message):
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

    if(user_dict[message.chat.id].condition == 'STB'):
        bot.send_message(message.chat.id,
                     text="Название введено: {0.text}, теперь введите количество страниц."
                     .format(message))
        user_dict[message.chat.id].current_book = message.text
        user_dict[message.chat.id].condition = 'STN'
        return

    if(user_dict[message.chat.id].condition == 'STN'):
        if(message.text.isnumeric()):
            bot.send_message(message.chat.id,
                     text="Введено количество страниц: {0.text}"
                     .format(message), reply_markup=markup)
            user_dict[message.chat.id].pages = int(message.text)
        else:
            bot.send_message(message.chat.id,
                     text="Неправильный формат ввода, введите число: {0.text}"
                     .format(message))
            return
        user_dict[message.chat.id].condition = '0'
        log_users()
        return

    if(user_dict[message.chat.id].condition == 'APB'):
        if(message.text.isnumeric()):
            user_dict[message.chat.id].book_progress += int(message.text)
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
        return

    else:
        bot.send_message(message.chat.id,
                     text="{0.first_name}, Введена неправильная команда"
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
    return "Message: " + text + " from @" + user + " chat ID: " + str(chat_id)

# Команда которая говорит боту, что нужно забирать полученные сообщения.
bot.infinity_polling()
