import telebot
import requests
#from SpotifyBot import TELEGRAM_TOKEN

bot = telebot.TeleBot("1613587240:AAGNSShlZ65cjeGWKfTCNLP56eu5Dcn8bjU")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Привет привет!")

@bot.message_handler(commands=['google'])
def google(message):
    bot.reply_to(message, requests.get("https://www.google.com").text[0:10])

bot.polling()