import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
from telebot import types
from extensions import log
import texts_reader as txt_reader
from .markup import *

cache_client = Session(200)
queueRepository = QueueRepository()

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def start_telegram_bot():
    th = threading.Thread(target=bot.polling)
    th.start()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user = cache_client.take(call.from_user.id)
    if call.data == 'help':
        bot.send_message(call.message.chat.id, txt_reader.get_text("help_message"))
    elif call.data == "play":
        user.play()
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Control_Markups(user))
    elif call.data == "next":
        user.next()
        if user.is_playing == 'Play':
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Control_Markups(user))
    elif call.data == "prev":
        user.prev()
        if user.is_playing == 'Play':
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Control_Markups(user))
    elif call.data == "cplaylist":
        user.cycle_playlist()
    elif call.data == "shuffle":
        user.shuffle()
    elif call.data == "ctrack":
        user.cycle_track()
    elif call.data == "like":
        user.like()
    elif call.data == "nav_prev_control":
        user.is_current_playlist = True
        if user.page != 1:
            user.page_prev()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_track"), reply_markup=Tracks_in_playlist_Markups(user))
    elif call.data == "nav_prev_playlist":
        if user.page != 1:
            user.page_prev()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=Playlists_Markups(user))
    elif call.data == "nav_next_control":
        user.is_current_playlist = True
        if user.page != user.max_pages:
            user.page_next()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_track"), reply_markup=Tracks_in_playlist_Markups(user))
    elif call.data == "nav_next_playlist":
        if user.page != user.max_pages:
            user.page_next()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=Playlists_Markups(user))
    elif call.data.find("selectPlaylist") != -1:
        idPlaylist = call.data.split(' ')[1]
        tracks = user.get_track_in_playlist(idPlaylist)
        user.tracks = tracks
        bot.edit_message_text(chat_id = call.message.chat.id,message_id=call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=Tracks_in_playlist_Markups(user))
    elif call.data.find("selectTrack") != -1:
        idAlbum = call.data.split(' ')[1]
        position = int(call.data.split(' ')[2]) - 1
        if user.is_playing == 'Play':
            tracks = user.play(playlist_id=idAlbum, position=position)
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Tracks_in_playlist_Markups(call.message, user.tgid))
            return
        tracks = user.play(playlist_id=idAlbum, position=position)
    elif call.data.find("selectSingleTrack") != -1:
        id = call.data.split(' ')[1]
        tracks = user.play(track_id = id)
    elif call.data == "nav_prev_search":
        if user.page != 1:
            user.page_prev()
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Search(user))        
    elif call.data == "nav_next_search":
        if user.page != user.max_pages:
            user.page_next()
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=Search(user))        
    bot.answer_callback_query(call.id)



@bot.message_handler(func=lambda message: message.text == txt_reader.get_text("about"))
def about_us(message):
    bot.send_message(message.chat.id, txt_reader.get_text("help_message"))

@bot.message_handler(func=lambda message: message.text == txt_reader.get_text("playlists"))
def playlists_nav(message):
    user = cache_client.take(message.from_user.id)
    bot.send_message(user.tgid,text=txt_reader.get_text("select_playlist"), reply_markup=Playlists_Markups(user))

@bot.message_handler(func=lambda message: message.text == txt_reader.get_text('control'))
def control(message):
    user = cache_client.take(message.from_user.id)
    bot.send_message(user.tgid, text=txt_reader.get_text('control'), reply_markup=Control_Markups(user))


@bot.message_handler(func=lambda message: message.text == txt_reader.get_text("track_finder"))
def search(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return

    bot.send_message(message.chat.id, txt_reader.get_text("search"))
    
    bot.register_next_step_handler(message, next_step_search)

def next_step_search(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)
    if user.last_message != message.text:
        ls = txt_reader.get_text("search_result").format(user.last_message)
        if message.text != '' and message.text != ls:
            user.page = 1
            user.tracks = []
            user.last_message = message.text
    
    bot.send_message(chat_id=message.chat.id, text=txt_reader.get_text('search_result').format(user.last_message), reply_markup=Search(user))


@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    user = cache_client.take(message.from_user.id)
    
    Authorization(user, message, bot)

<<<<<<< HEAD
    if user:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        playlists_button = types.KeyboardButton(txt_reader.get_text("playlists"))
        control_button = types.KeyboardButton(txt_reader.get_text("control"))
        find_track_button = types.KeyboardButton(txt_reader.get_text("track_finder"))
        help_button = types.KeyboardButton(txt_reader.get_text("about"))
        markup.add(playlists_button, control_button,
                   find_track_button, help_button)

        user_info = user.get_me()
        if not user_info:
            pass  # TODO: Сделать удаление юзера из кэша и базы данных
        username = user_info["display_name"]
        bot.send_message(message.chat.id, txt_reader.get_text(
            "registration").format(username), reply_markup=markup)
        log.info(txt_reader.get_text("registration_log").format(
            message.from_user.username, message.from_user.id))
        return

    data = queueRepository.get_free_link(message.from_user.id)
    queueRepository.block_link(data[0], message.from_user.id)

    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    responseMessage = txt_reader.get_text("response_message")

    markup = types.InlineKeyboardMarkup()
    auth_button = types.InlineKeyboardButton(
        txt_reader.get_text("autorization"), url=link)
    help_button = types.InlineKeyboardButton(
        txt_reader.get_text("about_bot"), callback_data='help')
    markup.add(auth_button, help_button)

    bot.send_message(message.chat.id, responseMessage, reply_markup=markup)
=======
>>>>>>> str_search


def check_spotify_active(message, user):
    if user:
        if not user.is_premium:
            error_message(message, txt_reader.get_text("not_premium"), user.tgid) 
            return False
        if not user.is_spotify_active:
            error_message(message, txt_reader.get_text("not_active"), user.tgid)
            return False
        if not user.is_tracks_in_playlist:
            error_message(message, txt_reader.get_text("empty_playlist"), user.tgid)
            return False
        return True
    return False
def error_message(message, msg, user_id):
    user = cache_client.take(user_id)
    print(str(user_id)+' error')
    if user:
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, txt_reader.get_text("not_register"))
