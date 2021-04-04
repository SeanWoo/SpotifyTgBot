import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
from telebot import types
from extensions import log
import texts_reader as t

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
        bot.send_message(call.message.chat.id, t.get_text("help_message"))
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
    elif call.data == "nav_prev_control":
        user.is_current_playlist = True
        if user.page != 1:
            user.page_prev
            control(call.message, call.from_user.id)
    elif call.data == "nav_prev_playlist":
        if user.page != 1:
            user.page_prev
            playlists(call.message, call.from_user.id)
    elif call.data == "nav_next_control":
        user.is_current_playlist = True
        if user.page != user.max_pages:
            user.page_next
            control(call.message, call.from_user.id)
    elif call.data == "nav_next_playlist":
        if user.page != user.max_pages:
            user.page_next
            playlists(call.message, call.from_user.id)
    elif call.data.find("selectPlaylist") != -1:
        idPlaylist = call.data.split(' ')[1]
        tracks = user.get_track_in_playlist(idPlaylist)
        user.tracks = tracks
        control(call.message, call.from_user.id)
    elif call.data.find("selectTrack") != -1:
        idAlbum = call.data.split(' ')[1]
        position = int(call.data.split(' ')[2]) - 1
        tracks = user.play(playlist_id=idAlbum, position=position)

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.text == t.get_text("playlists"))
def playlists(message, user_id=None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return
    if user.is_current_playlist:
        user.page = 1
        user.is_current_playlist = False
    msg = t.get_text("your_playlists")

    user.playlists = user.get_playlists()
    markup = types.InlineKeyboardMarkup()
    playlists = user.playlists[user.page]

    for playlist in playlists:
        button = types.InlineKeyboardButton(
            playlist.name, callback_data=f"selectPlaylist {playlist.id}")
        markup.add(button)
    nav_prev_pl_button = types.InlineKeyboardButton(
        '❮', callback_data="nav_prev_playlist")
    nav_page_pl_button = types.InlineKeyboardButton(
        f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
    nav_next_pl_button = types.InlineKeyboardButton(
        '❯', callback_data="nav_next_playlist")
    markup.row(nav_prev_pl_button, nav_page_pl_button, nav_next_pl_button)
    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == t.get_text("about"))
def find_track(message):
    bot.send_message(message.chat.id, t.get_text("help_message"))


@bot.message_handler(func=lambda message: message.text == t.get_text("control"))
def control(message, user_id=None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return

    msg = t.get_text("your_tracks")
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons_row = []
    if not user.inclube_playlist:
        user.page = 1
        user.inclube_playlist = True
    if user.is_current_playlist:
        counter = 5*(user.page - 1)
        tracks = user.tracks[user.page]
        for track in tracks:
            counter += 1
            button = types.InlineKeyboardButton(
                f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectTrack {track.playlist_id} {counter}")
            buttons_row.append(button)
            if len(buttons_row) % 5 == 0:
                markup.add(*buttons_row)
                buttons_row.clear()
        if len(buttons_row) > 0:
            markup.add(*buttons_row)
            buttons_row.clear()
        nav_prev_button = types.InlineKeyboardButton(
            '❮', callback_data="nav_prev_control")
        nav_page_button = types.InlineKeyboardButton(
            f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
        nav_next_button = types.InlineKeyboardButton(
            '❯', callback_data="nav_next_control")

        markup.row(nav_prev_button, nav_page_button, nav_next_button)

        prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
        play_button = types.InlineKeyboardButton(
            'Play/Pause', callback_data="play")
        next_button = types.InlineKeyboardButton('Next', callback_data='next')
        markup.row(prev_button, play_button, next_button)
        cplaylist_button = types.InlineKeyboardButton(
            'Cycle playlist', callback_data='cplaylist')
        shufle_button = types.InlineKeyboardButton(
            'Shuffle', callback_data='shuffle')
        ctrack_button = types.InlineKeyboardButton(
            'Cycle track', callback_data='ctrack')

        like_button = types.InlineKeyboardButton('Like', callback_data='like')
        markup.row(cplaylist_button, shufle_button, ctrack_button)
        markup.add(like_button)
    else:
        nav_prev_button = types.InlineKeyboardButton(
            '❮', callback_data="nav_prev_control")
        nav_page_button = types.InlineKeyboardButton(
            f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
        nav_next_button = types.InlineKeyboardButton(
            '❯', callback_data="nav_next_control")

        prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
        play_button = types.InlineKeyboardButton(
            'Play/Pause', callback_data="play")
        next_button = types.InlineKeyboardButton('Next', callback_data='next')
        markup.row(prev_button, play_button, next_button)
        cplaylist_button = types.InlineKeyboardButton(
            'Cycle playlist', callback_data='cplaylist')
        shufle_button = types.InlineKeyboardButton(
            'Shuffle', callback_data='shuffle')
        ctrack_button = types.InlineKeyboardButton(
            'Cycle track', callback_data='ctrack')

        like_button = types.InlineKeyboardButton('Like', callback_data='like')
        markup.row(cplaylist_button, shufle_button, ctrack_button)
        markup.add(like_button)

    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == t.get_text("track_finder"))
def find_track(message):
    bot.send_message(message.chat.id, t.get_text("track_finder"))


@bot.message_handler(commands=['start'])
def send_welcome_callback(message):
    user = cache_client.take(message.from_user.id)

    if user:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        playlists_button = types.KeyboardButton(t.get_text("playlists"))
        control_button = types.KeyboardButton(t.get_text("control"))
        find_track_button = types.KeyboardButton(t.get_text("track_finder"))
        help_button = types.KeyboardButton(t.get_text("about"))
        markup.add(playlists_button, control_button,
                   find_track_button, help_button)

        user_info = user.get_me()
        if not user_info:
            pass  # TODO: Сделать удаление юзера из кэша и базы данных
        username = user_info["display_name"]
        bot.send_message(message.chat.id, t.get_text(
            "registration").format(username), reply_markup=markup)
        log.info(t.get_text("registration_log").format(
            message.from_user.username, message.from_user.id))
        return

    data = queueRepository.get_free_link(message.from_user.id)
    queueRepository.block_link(data[0], message.from_user.id)

    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    responseMessage = t.get_text("response_message")

    markup = types.InlineKeyboardMarkup()
    auth_button = types.InlineKeyboardButton(
        t.get_text("autorization"), url=link)
    help_button = types.InlineKeyboardButton(
        t.get_text("about_bot"), callback_data='help')
    markup.add(auth_button, help_button)

    bot.send_message(message.chat.id, responseMessage, reply_markup=markup)


def check_spotify_active(message, user):
    if user:
        if not user.is_premium:
            error_message(message, t.get_text("not_premium"))
            return False
        if not user.is_spotify_active:
            error_message(message, t.get_text("not_active"))
            return False
        if not user.is_tracks_in_playlist:
            error_message(message, t.get_text("empty_playlist"))
            return False
        return True
    return False


def error_message(message, msg):
    user = cache_client.take(message.from_user.id)

    if user:
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, t.get_text("not_register"))
