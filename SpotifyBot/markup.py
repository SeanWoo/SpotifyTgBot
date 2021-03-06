from telebot import types, TeleBot
import texts_reader as txt_reader
from SpotifyBot import PageManager
from extensions import userlog

def get_inline_auth_panel(user, link):
    markup = types.InlineKeyboardMarkup()

    auth_button = types.InlineKeyboardButton(
        txt_reader.get_text(user.language, "autorization"), url=link)
    help_button = types.InlineKeyboardButton(
        txt_reader.get_text(user.language, "about_bot"), callback_data='help')

    markup.add(auth_button, help_button)
    return markup

def get_languages_panel():
    markup = types.InlineKeyboardMarkup()
    ru_button = types.InlineKeyboardButton('Русский', callback_data="setLanguage ru")
    en_button = types.InlineKeyboardButton('English', callback_data="setLanguage en")
    markup.row(ru_button, en_button)
    return markup

def get_reply_panel(user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    playlists_button = types.KeyboardButton(
        txt_reader.get_text(user.language, "playlists"))
    control_button = types.KeyboardButton(
        txt_reader.get_text(user.language, "control"))
    find_track_button = types.KeyboardButton(
        txt_reader.get_text(user.language, "track_finder"))
    help_button = types.KeyboardButton(
        txt_reader.get_text(user.language, "about"))
    language_button = types.KeyboardButton(
        txt_reader.get_text(user.language, "changeLanguage"))

    markup.add(playlists_button, control_button,
               find_track_button, help_button,language_button)
    return markup


def get_inline_control(user):
    markup = types.InlineKeyboardMarkup()

    counter = 5*(user.pageManagerTracks.page - 1)

    for track in user.pageManagerTracks[user.pageManagerTracks.page]:
        counter += 1
        if user.pageManagerTracks[user.pageManagerTracks.page][0].playlist_id == None:
            button = types.InlineKeyboardButton(
                text=f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectTrack {counter}")
        else:
            button = types.InlineKeyboardButton(
                text=f'{str(counter)}. {str(track.artists)} - {str(track.name)}', callback_data=f"selectTrackByPlaylistId {track.playlist_id} {counter}")
        markup.add(button)

    #play_state = "Pause" if user.is_playing else "Play"
    play_state = "Play/Pause"

    nav_prev_pl_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_control")
    nav_page_pl_button = types.InlineKeyboardButton(f'{user.pageManagerTracks.page}/{user.pageManagerTracks.max_pages}', callback_data="nav_page_control")
    nav_next_pl_button = types.InlineKeyboardButton('❯', callback_data="nav_next_control")

    markup.row(nav_prev_pl_button, nav_page_pl_button, nav_next_pl_button)

    prev_button = types.InlineKeyboardButton('Prev', callback_data="prev")
    play_button = types.InlineKeyboardButton(play_state, callback_data="play")
    next_button = types.InlineKeyboardButton('Next', callback_data='next')
    markup.row(prev_button, play_button, next_button)
    cplaylist_button = types.InlineKeyboardButton(
        'Cycle playlist', callback_data='cplaylist')
    shufle_button = types.InlineKeyboardButton(
        'Shuffle', callback_data='shuffle')
    ctrack_button = types.InlineKeyboardButton(
        'Cycle track', callback_data='ctrack')

    markup.row(cplaylist_button, shufle_button, ctrack_button)
    return markup


def get_inline_playlist(user):
    markup = types.InlineKeyboardMarkup()
    
    for playlist in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        button = types.InlineKeyboardButton(playlist.name, callback_data=f"selectPlaylist {playlist.id}")
        markup.add(button)

    nav_prev_pl_button = types.InlineKeyboardButton('❮', callback_data="nav_prev_playlist")
    nav_page_pl_button = types.InlineKeyboardButton(f'{user.pageManagerPlaylists.page}/{user.pageManagerPlaylists.max_pages}', callback_data="nav_page_control")
    nav_next_pl_button = types.InlineKeyboardButton('❯', callback_data="nav_next_playlist")

    markup.row(nav_prev_pl_button, nav_page_pl_button, nav_next_pl_button)
    return markup
