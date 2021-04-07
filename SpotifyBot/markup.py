from telebot import types, TeleBot
from SpotifyBot import TELEGRAM_TOKEN, SpotifyClient, Session, QueueRepository
import texts_reader as txt_reader
from extensions import log
def Authorization(user: SpotifyClient, message, bot: TeleBot):
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

def Control_Markups(user: SpotifyClient):
    markup = types.InlineKeyboardMarkup()
    prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
    play_button = types.InlineKeyboardButton(user.is_playing, callback_data="play")
    next_button = types.InlineKeyboardButton('Next', callback_data='next')
    markup.row(prev_button, play_button, next_button)
    cplaylist_button = types.InlineKeyboardButton('Cycle playlist', callback_data='cplaylist')
    shufle_button = types.InlineKeyboardButton('Shuffle', callback_data='shuffle')
    ctrack_button = types.InlineKeyboardButton('Cycle track', callback_data='ctrack')
    markup.row(cplaylist_button,shufle_button,ctrack_button)
    return markup

def Playlists_Markups(user: SpotifyClient):
    user.playlists = user.get_playlists()
    if len(user.tracks) != 0 and user.page != 1:
        user.tracks = []
        user.page = 1 
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

def Tracks_in_playlist_Markups(user: SpotifyClient):

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
            button = types.InlineKeyboardButton(text=f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectTrack {track.playlist_id} {counter}")
            buttons_row.append(button)
            if len(buttons_row) % 5 == 0:
                markup.add(*buttons_row)
                buttons_row.clear()
        if len(buttons_row) > 0:
            markup.add(*buttons_row)
            buttons_row.clear()
    nav_prev_pl_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_control")
    nav_page_pl_button = types.InlineKeyboardButton(f'{user.page}/{user.max_pages}', callback_data="nav_page_control")
    nav_next_pl_button = types.InlineKeyboardButton('❯', callback_data="nav_next_control")
    markup.row(nav_prev_pl_button,nav_page_pl_button,nav_next_pl_button)
    return markup
def Search(user: SpotifyClient):

    result = user.search()[user.page]

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
    if len(user.tracks) == 0:
        user.tracks = result
        return markup
    else:
        return markup

