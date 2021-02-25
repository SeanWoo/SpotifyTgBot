import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN
from configReader import SPOTIFY_CLIENT_ID,REDIRECT_URL
from extensions import db


bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    cursor = db.execute(f"SELECT * FROM queue WHERE tgid={message.from_user.id} OR tgid IS NULL OR endtime < {round(time.time())} LIMIT 1")
    data = cursor.fetchone()
    db.close_cursor()

    link = "https://accounts.spotify.com/authorize?client_id="+SPOTIFY_CLIENT_ID+"&response_type=code&redirect_uri="+data[2]
    msg = "какой то текст\n\nссылка" + link

    db.execute(f"UPDATE queue SET tgid=%s, endtime=%s WHERE id={data[0]}", (message.from_user.id, time.time() + 300))
    db.close_cursor()

    bot.reply_to(message, msg)


th = threading.Thread(target=bot.polling)
th.start()