import telebot
import requests
import threading
#from SpotifyBot import TELEGRAM_TOKEN
from configReader import SPOTIFY_CLIENT_ID,BASE_DOMEN

bot = telebot.TeleBot("1613587240:AAGNSShlZ65cjeGWKfTCNLP56eu5Dcn8bjU")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Привет привет!")

@bot.message_handler(commands=['google'])
def google(message):
    bot.reply_to(message, requests.get("https://www.google.com").text[0:10])

@bot.message_handler(commands=['start_test'])
def send_welcome_callback(message):
        domen = BASE_DOMEN.replace(":","%3A").replace("/","%2F")
        link = "https://accounts.spotify.com/authorize?client_id="+SPOTIFY_CLIENT_ID+"esponse_type=code&redirect_uri="+domen
        msg = "какой то текст\n\nссылка" + link
        bot.reply_to(message, msg)


th = threading.Thread(target=bot.polling)
th.start()
