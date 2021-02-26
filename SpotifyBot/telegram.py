import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN
from configReader import SPOTIFY_CLIENT_ID,REDIRECT_URL
from extensions import db
from telebot import types

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'help':
       bot.send_message(call.message.chat.id, "Сообщение с информацией о функционале")

@bot.message_handler(func=lambda message: message.text == "Плейлисты")
def playlists(message):
    bot.send_message(message.chat.id, "Плейлисты")

@bot.message_handler(func=lambda message: message.text == "Поиск треков")
def find_track(message):
    bot.send_message(message.chat.id, "Поиск треков")

@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    cursor = db.execute("SELECT * FROM tokens WHERE tgid=%s", (message.from_user.id,))
    user = cursor.fetchone()
    db.close_cursor()

    if user:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        playlists_button = types.KeyboardButton('Плейлисты')
        find_track_button = types.KeyboardButton('Поиск треков')
        markup.add(playlists_button, find_track_button)

        bot.send_message(message.chat.id, "Вы были зарегестрированы", reply_markup=markup)
        return

    cursor = db.execute("SELECT * FROM queue WHERE tgid=%s OR tgid IS NULL OR endtime < %s LIMIT 1",
                        (message.from_user.id,round(time.time())))
    data = cursor.fetchone()
    db.close_cursor()

    db.execute(f"UPDATE queue SET tgid=%s, endtime=%s WHERE id={data[0]}", (message.from_user.id, time.time() + 300))
    db.close_cursor()

    link = "https://accounts.spotify.com/authorize?client_id="+SPOTIFY_CLIENT_ID+"&response_type=code&redirect_uri="+data[2]
    responseMessage = "Привет! Я музыкальный бот. Чтобы начать со мной взаимодействия, авторизируйтесь в Spotify нажав кнопку ниже."

    markup = types.InlineKeyboardMarkup()
    auth_button = types.InlineKeyboardButton('Авторизация', url=link)
    help_button = types.InlineKeyboardButton('О боте', callback_data='help')
    markup.add(auth_button, help_button)

    bot.send_message(message.chat.id, responseMessage, reply_markup=markup)


th = threading.Thread(target=bot.polling)
th.start()