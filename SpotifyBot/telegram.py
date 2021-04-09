import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository, get_reply_panel, get_inline_control, get_inline_auth_panel, get_inline_playlist, get_inline_tracks_of_playlist, get_inline_search_tracks, TelegramError
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
from telebot import types
from extensions import userlog
import texts_reader as txt_reader

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
        old_playing_state = user.is_playing
        user.play()
        #if old_playing_state != user.is_playing:
            #TODO: исправить баг с не изменным маркупом
            #bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_control(user))
    elif call.data == "next":
        old_playing_state = user.is_playing
        user.next()
        if old_playing_state != user.is_playing:
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_control(user))
    elif call.data == "prev":
        old_playing_state = user.is_playing
        user.prev()
        if old_playing_state != user.is_playing:
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_control(user))
    elif call.data == "cplaylist":
        user.cycle_playlist()
    elif call.data == "shuffle":
        user.shuffle()
    elif call.data == "ctrack":
        user.cycle_track()
    elif call.data == "nav_prev_control":
        if user.pageManagerTracks.page != 1:
            user.pageManagerTracks.page -= 1
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_track"), reply_markup=get_inline_tracks_of_playlist(user))
    elif call.data == "nav_next_control":
        if user.pageManagerTracks.page != user.pageManagerTracks.max_pages:
            user.pageManagerTracks.page += 1
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_track"), reply_markup=get_inline_tracks_of_playlist(user))
    elif call.data == "nav_prev_playlist":
        if user.pageManagerPlaylists.page != 1:
            user.pageManagerPlaylists.page -= 1
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=get_inline_playlist(user))
    elif call.data == "nav_next_playlist":
        if user.pageManagerPlaylists.page != user.pageManagerPlaylists.max_pages:
            user.pageManagerPlaylists.page += 1
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=get_inline_playlist(user))
    elif call.data == "nav_prev_search":
        if user.pageManagerTracks.page != 1:
            user.pageManagerTracks.page -= 1
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_search_tracks(user))        
    elif call.data == "nav_next_search":
        if user.pageManagerTracks.page != user.pageManagerTracks.max_pages:
            user.pageManagerTracks.page += 1
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_search_tracks(user))        
    elif call.data.find("selectPlaylist") != -1:
        idPlaylist = call.data.split(' ')[1]
        user.get_tracks_of_playlist(idPlaylist)
        bot.edit_message_text(chat_id = call.message.chat.id,message_id=call.message.message_id,text=txt_reader.get_text("select_playlist"), reply_markup=get_inline_tracks_of_playlist(user))
    elif call.data.find("selectTrackByPlaylistId") != -1:
        idAlbum = call.data.split(' ')[1]
        position = int(call.data.split(' ')[2]) - 1

        old_playing_state = user.is_playing
        user.play(playlist_id = idAlbum, position = position)
        if old_playing_state != user.is_playing:
            bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=get_inline_control(user))
    elif call.data.find("selectTracks") != -1:
        position = int(call.data.split(' ')[1]) - 1
        user.play(use_current_tracks = True, position = position)
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.text == txt_reader.get_text("about"))
def about_us(message):
    bot.send_message(message.chat.id, txt_reader.get_text("help_message"))

@bot.message_handler(func=lambda message: message.text == txt_reader.get_text("playlists"))
def playlists(message):
    user = cache_client.take(message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return

    result = user.get_playlists()
    if isinstance(result, TelegramError):
        error_message(message, f"Status: {result.status} Message: {result.message}", user.tgid)

    bot.send_message(user.tgid, text=txt_reader.get_text("select_playlist"), reply_markup=get_inline_playlist(user))

@bot.message_handler(func=lambda message: message.text == txt_reader.get_text('control'))
def control(message):
    user = cache_client.take(message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return

    if user.pageManagerTracks == None:
        data = user.get_player()
        if isinstance(data, TelegramError):
            error_message(message, f"Status: {data.status} Message: {data.message}", user.tgid)
        if data["context"]["type"] == "playlist":
            playlistId = data["context"]["uri"].split(":")[-1]
            result = user.get_tracks_of_playlist(playlistId)
            if isinstance(result, TelegramError):
                error_message(message, f"Status: {result.status} Message: {result.message}", user.tgid)

    bot.send_message(user.tgid, text=txt_reader.get_text('control'), reply_markup=get_inline_control(user))

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

@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    user = cache_client.take(message.from_user.id)

    if user:
        

        user_info = user.get_me()
        if not user_info:
            pass  # TODO: Сделать удаление юзера из кэша и базы данных
        username = user_info["display_name"]
        bot.send_message(message.chat.id, txt_reader.get_text(
            "registration").format(username), reply_markup=get_reply_panel())
        userlog.info(txt_reader.get_text("registration_log").format(
            message.from_user.username, message.from_user.id))
        return

    data = queueRepository.get_free_link(message.from_user.id)
    queueRepository.block_link(data[0], message.from_user.id)

    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    responseMessage = txt_reader.get_text("response_message")

    bot.send_message(message.chat.id, responseMessage, reply_markup=get_inline_auth_panel(link))


def next_step_search(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    user.search(message.text)
    
    bot.send_message(chat_id=message.chat.id, text=txt_reader.get_text("search_result").format(message.text), reply_markup=get_inline_search_tracks(user))

def check_spotify_active(message, user):
    if user:
        if _check_error(message, user, user.is_premium, "not_premium"):
            return False
        elif _check_error(message, user, user.is_spotify_active, "not_active"):
            return False
        return True
    return False

def error_message(message, msg, user_id):
    user = cache_client.take(user_id)
    if user:
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, txt_reader.get_text("not_register"))

def _check_error(message, user, data, idText):
    if isinstance(data, TelegramError):
        if data.status == 429:
            error_message(message, txt_reader.get_text("rate_limit"), user.tgid) 
        return True
    else:
        if not data:
            error_message(message, txt_reader.get_text(idText), user.tgid) 
            return True
        return False
