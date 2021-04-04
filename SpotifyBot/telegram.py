import telebot
import requests
import threading
import time
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository
from configReader import SPOTIFY_CLIENT_ID,SPOTIFY_SCOPE
from telebot import types
from extensions import log

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
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=control(call.message, user.tgid))
    elif call.data == "next":
        user.next()
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=control(call.message, user.tgid))
    elif call.data == "prev":
        user.prev()
        bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=control(call.message, user.tgid))        
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
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text='Выбор трека:', reply_markup=control(call.message, user.tgid))
    elif call.data == "nav_prev_playlist":
        if user.page != 1:
            user.page_prev()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text='Выбор плейлиста:', reply_markup=playlists(call.message, user.tgid))
    elif call.data == "nav_next_control":
        user.is_current_playlist = True
        if user.page != user.max_pages:
            user.page_next()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text='Выбор трека:', reply_markup=control(call.message, user.tgid))
    elif call.data == "nav_next_playlist":
        if user.page != user.max_pages:
            user.page_next()
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,text='Выбор плейлиста:', reply_markup=playlists(call.message, user.tgid))
    elif call.data.find("selectPlaylist") != -1:
        idPlaylist = call.data.split(' ')[1]
        tracks = user.get_track_in_playlist(idPlaylist)
        user.tracks = tracks
        control_nav(call.message, user.tgid)
    elif call.data.find("selectTrack") != -1:
        idAlbum = call.data.split(' ')[1]
        position = int(call.data.split(' ')[2]) - 1
        tracks = user.play(playlist_id=idAlbum, position=position)
    elif call.data.find("selectSingleTrack") != -1:
        id = call.data.split(' ')[1]
        tracks = user.play(track_id = id)
    elif call.data == "nav_prev_search":
        if user.page != 1:
            user.page_prev()
            next_step_search(call.message, user.tgid)
    elif call.data == "nav_next_search":
        if user.page != user.max_pages:
            user.page_next()
            next_step_search(call.message, user.tgid)
    bot.answer_callback_query(call.id)


def playlists(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)
    user.is_tracks_in_playlist = True
    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return
    if user.is_current_playlist:
        user.page = 1
        user.is_current_playlist = False
    msg = "Ваши плейлисты: \n"
    
    user.playlists = user.get_playlists()
    markup = types.InlineKeyboardMarkup()
    playlists = user.playlists[user.page]
    
    for playlist in playlists:
        button = types.InlineKeyboardButton(playlist.name, callback_data=f"selectPlaylist {playlist.id}")
        markup.add(button)
    nav_prev_pl_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_playlist")
    nav_page_pl_button = types.InlineKeyboardButton(f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
    nav_next_pl_button = types.InlineKeyboardButton('❯', callback_data="nav_next_playlist")
    markup.row(nav_prev_pl_button,nav_page_pl_button,nav_next_pl_button)
    return markup

@bot.message_handler(func=lambda message: message.text == "О нас")
def about_us(message):
    bot.send_message(message.chat.id, help_message)

def control(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)
    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return
    msg = "Ваши треки: \n"
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
            button = types.InlineKeyboardButton(f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectTrack {track.playlist_id} {counter}" )
            buttons_row.append(button)
            if len(buttons_row) % 5 == 0:
                markup.add(*buttons_row)
                buttons_row.clear()
        if len(buttons_row) > 0:
            markup.add(*buttons_row)
            buttons_row.clear()
        nav_prev_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_control")
        nav_page_button = types.InlineKeyboardButton(f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
        nav_next_button = types.InlineKeyboardButton('❯', callback_data="nav_next_control")

        markup.row(nav_prev_button, nav_page_button, nav_next_button)

        prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
        play_button = types.InlineKeyboardButton(user.playing, callback_data="play")
        next_button = types.InlineKeyboardButton('Next', callback_data='next')
        markup.row(prev_button, play_button, next_button)
        cplaylist_button = types.InlineKeyboardButton('Cycle playlist', callback_data='cplaylist')
        shufle_button = types.InlineKeyboardButton('Shuffle', callback_data='shuffle')
        ctrack_button = types.InlineKeyboardButton('Cycle track', callback_data='ctrack')

        like_button = types.InlineKeyboardButton('Like', callback_data='like')
        markup.row(cplaylist_button, shufle_button, ctrack_button)
        markup.add(like_button)
    return markup

@bot.message_handler(func=lambda message: message.text == "Управление")
def controls(message):
    markup = types.InlineKeyboardMarkup()
    prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
    play_button = types.InlineKeyboardButton('Play/Pause', callback_data="play")
    next_button = types.InlineKeyboardButton('Next', callback_data='next')
    markup.row(prev_button, play_button, next_button)
    cplaylist_button = types.InlineKeyboardButton('Cycle playlist', callback_data='cplaylist')
    shufle_button = types.InlineKeyboardButton('Shuffle', callback_data='shuffle')
    ctrack_button = types.InlineKeyboardButton('Cycle track', callback_data='ctrack')

    like_button = types.InlineKeyboardButton('Like', callback_data='like')
    markup.row(cplaylist_button, shufle_button, ctrack_button)
    markup.add(like_button)
    bot.send_message(chat_id=message.from_user.id, text='Управление',reply_markup=markup)
def control_nav(message, id):
    bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text='Выбор трека:', reply_markup=control(message, id))
@bot.message_handler(func=lambda message: message.text == "Плейлисты")
def playlists_nav(message):
    user = cache_client.take(message.from_user.id)
    bot.send_message(user.tgid,text='Выбор плейлиста', reply_markup=playlists(message))


@bot.message_handler(func=lambda message: message.text == "Поиск треков")
def search(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    if not user:
        send_welcome_callback(message)
        return

    if not check_spotify_active(message, user):
        return

    bot.send_message(message.chat.id, "Введите название трека")
    user.page = 1
    
    bot.register_next_step_handler(message, next_step_search)

def next_step_search(message, user_id = None):
    user = cache_client.take(user_id if user_id else message.from_user.id)

    bot.send_message(message.chat.id, f"Вы ввели {message.text}")

    result = user.search(message.text)

    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons_row = []
    
    counter = 5*(user.page - 1)

    for track in result:
        counter += 1
        button = types.InlineKeyboardButton(f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectSingleTrack {track.id}")
        buttons_row.append(button)

    markup.add(*buttons_row)

    nav_prev_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_search")
    nav_page_button = types.InlineKeyboardButton(f'{user.page}/{user.max_pages}', callback_data="nav_page_search")
    nav_next_button = types.InlineKeyboardButton('❯', callback_data="nav_next_search")

    markup.row(nav_prev_button, nav_page_button, nav_next_button)
    bot.send_message(message.chat.id, "Вот что мы нашли:", reply_markup=markup)


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
        log.info(f'User {message.from_user.username}({message.from_user.id}) logged in Spotify account')
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

def check_spotify_active(message, user):
    if user:
        if not user.is_premium:
            error_message(message, 'У вас не имеется Premium.', user.tgid) 
            return False
        if not user.is_spotify_active:
            error_message(message, "Запустите приложение спотифай и включите музыку чтоб получить доступ к Вам", user.tgid)
            return False
        if not user.is_tracks_in_playlist:
            error_message(message, 'Пустой плейлист', user.tgid)
            return False
        return True
    return False
def error_message(message, msg, user_id):
    user = cache_client.take(user_id)
    print(str(user_id)+' error')
    if user:
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "Аккаунт не был зарегестрирован")
