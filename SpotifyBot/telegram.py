import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session
from configReader import SPOTIFY_CLIENT_ID,SPOTIFY_SCOPE
from extensions import db
from telebot import types

cache_client = Session(200)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def start_telegram_bot():
    th = threading.Thread(target=bot.polling)
    th.start()

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
    user = cache_client.take(message.from_user.id)

    if user:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        playlists_button = types.KeyboardButton('Плейлисты')
        find_track_button = types.KeyboardButton('Поиск треков')
        markup.add(playlists_button, find_track_button)

        user_info = user.get_me()
        username = user_info["display_name"]
        bot.send_message(message.chat.id, f"Аккаунт {username} был зарегестрирован", reply_markup=markup)
        return

    cursor = db.execute("SELECT * FROM queue WHERE tgid=%s OR tgid IS NULL OR endtime < %s LIMIT 1",
                        (message.from_user.id,round(time.time())))
    data = cursor.fetchone()
    db.close_cursor()

    db.execute(f"UPDATE queue SET tgid=%s, endtime=%s WHERE id={data[0]}", (message.from_user.id, time.time() + 300))
    db.close_cursor()

    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    responseMessage = "Привет! Я музыкальный бот. Чтобы начать со мной взаимодействия, авторизируйтесь в Spotify нажав кнопку ниже."

    markup = types.InlineKeyboardMarkup()
    auth_button = types.InlineKeyboardButton('Авторизация', url=link)
    help_button = types.InlineKeyboardButton('О боте', callback_data='help')
    markup.add(auth_button, help_button)

    bot.send_message(message.chat.id, responseMessage, reply_markup=markup)


