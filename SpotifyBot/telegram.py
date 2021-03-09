import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository
from configReader import SPOTIFY_CLIENT_ID,SPOTIFY_SCOPE
from telebot import types

cache_client = Session(200)
queueRepository = QueueRepository()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

help_message = "Благодаря синхронизации Spotify, Вы можете слушать музыку на чём угодно. Наша команда решила создать бота для телеграмма, благодаря которому у Вас появится возможность выполнять различные действия используя телеграмм бота. Функционал бота практически ничем не будет отличаться от обычного плеера или же того же Spotify. Вы с лёгкостью сможете изменять плейлисты и также искать нужные вам треки. \n\n With Spotify synchronization, users are able listen to music nearly on every device. Our team came up with an idea to create a bot for a messenger known as Telegram. With this Bot, users can use messenger just like a regular player, yet many people might think that it would be complicated to use and it would be much easier to use just Spotify app. Nonetheless, our Telegram bot will have same functional as regular app. Without a doubt, users with ease can change playlists, change music or search for it."

def start_telegram_bot():
    th = threading.Thread(target=bot.polling)
    th.start()

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user = cache_client.take(call.from_user.id)
    if call.data == 'help':
       bot.send_message(call.message.chat.id, help_message)
    elif call.data == "play":
        user.play()
    elif call.data == "next":
        user.next()
    elif call.data == "prev":
        user.prev()
    elif call.data == "cplaylist":
        user.cycle_playlist()
    elif call.data == "shuffle":
        user.shuffle()
    elif call.data == "ctrack":
        user.cycle_track()
    elif call.data == "like":
        user.like()
    elif call.data.find("selectPlaylist") != -1:
        namePlaylist = call.data.split(' ')[1]
        tracks = user.get_music_of_playlist(namePlaylist)
        user.tracks = tracks
        control(call.message, call.from_user.id)

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text == "Плейлисты")
def playlists(message):
    user = cache_client.take(message.from_user.id)
    msg = "Ваши плейлисты: \n"

    markup = types.InlineKeyboardMarkup()

    counter = 0
    for playlist in user.get_playlists():
        counter += 1
        msg += f"{counter}) {playlist.name}\n"

        button = types.InlineKeyboardButton(playlist.name, callback_data=f"selectPlaylist {playlist.name}")
        markup.add(button)
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "О нас")
def find_track(message):
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(func=lambda message: message.text == "Управление")
def control(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    msg = "Ваши треки: \n"
    counter = 0
    for track in user.tracks:
        if track == user.current_track:
            msg += f"Текущий трек: {track.name}\n"
        else:
            msg += f"{track.name}\n"
        counter += 1

    markup = types.InlineKeyboardMarkup()
    prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
    play_button = types.InlineKeyboardButton('Play/Pause', callback_data="play")
    next_button = types.InlineKeyboardButton('Next', callback_data='next')

    cplaylist_button = types.InlineKeyboardButton('Cycle playlist', callback_data='cplaylist')
    shufle_button = types.InlineKeyboardButton('Shuffle', callback_data='shuffle')
    ctrack_button = types.InlineKeyboardButton('Cycle track', callback_data='ctrack')

    like_button = types.InlineKeyboardButton('Like', callback_data='like')
    markup.add(prev_button, play_button, next_button, cplaylist_button, shufle_button, ctrack_button, like_button)

    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Поиск треков")
def find_track(message):
    bot.send_message(message.chat.id, "Поиск треков")

@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    user = cache_client.take(message.from_user.id)

    if user:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        playlists_button = types.KeyboardButton('Плейлисты')
        control_button = types.KeyboardButton('Управление')
        find_track_button = types.KeyboardButton('Поиск треков')
        help_button = types.KeyboardButton('О нас')
        markup.add(playlists_button, control_button, find_track_button, help_button)

        user_info = user.get_me()
        if not user_info:
            pass #TODO: Сделать удаление юзера из кэша и базы данных
        username = user_info["display_name"]
        bot.send_message(message.chat.id, f"Аккаунт {username} был зарегестрирован", reply_markup=markup)
        return

    data = queueRepository.get_free_link(message.from_user.id)
    queueRepository.block_link(data[0], message.from_user.id)

    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    responseMessage = "Привет! Я музыкальный бот. Чтобы начать со мной взаимодействия, авторизируйтесь в Spotify нажав кнопку ниже."

    markup = types.InlineKeyboardMarkup()
    auth_button = types.InlineKeyboardButton('Авторизация', url=link)
    help_button = types.InlineKeyboardButton('О боте', callback_data='help')
    markup.add(auth_button, help_button)

    bot.send_message(message.chat.id, responseMessage, reply_markup=markup)


