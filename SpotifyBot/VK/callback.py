from vk_api import VkApi
from SpotifyBot.client import SpotifyClient
from .keyboard import get_inline_control,get_inline_playlist,get_inline_track_of_playlist,get_inline_search_tracks, get_main_menu
from vk_api.utils import get_random_id





def get_callback(callback, user: SpotifyClient):
    if callback == "help":
        return
    elif callback == 'get_inline_playlist':
        result = user.get_playlists()
        return get_inline_playlist(user)
    elif callback == "play":
        old_playing_state = user.is_playing
        user.play()
        if old_playing_state != user.is_playing:
            return
    elif callback == "next":
        old_playing_state = user.is_playing
        user.next()
        if old_playing_state != user.is_playing:
            return
    elif callback == "prev":
        old_playing_state = user.is_playing
        user.prev()
        if old_playing_state != user.is_playing:
            return
    elif callback == "cplaylist":
        user.cycle_playlist()
    elif callback == "shuffle":
        user.shuffle()
    elif callback == "ctrack":
        user.cycle_track()
    elif callback == "nav_prev_control":
        if user.pageManagerTracks.page != 1:
            user.pageManagerTracks.page -= 1
            return get_inline_control(user)
    elif callback == "nav_next_control":
        if user.pageManagerTracks.page != user.pageManagerTracks.max_pages:
            user.pageManagerTracks.page += 1
            return get_inline_control(user)
    elif callback == "nav_prev_playlist":
        if user.pageManagerTracks.page != 1:
            user.pageManagerTracks.page -= 1
            return get_inline_playlist(user)
    elif callback == "nav_next_playlist":
        if user.pageManagerTracks.page != user.pageManagerTracks.max_pages:
            user.pageManagerTracks.page += 1
            return get_inline_playlist(user)
    elif callback == "nav_prev_search":
        if user.pageManagerTracks.page != 1:
            user.pageManagerTracks.page -= 1
            return get_inline_search_tracks(user)
    elif callback == "nav_next_search":
        if user.pageManagerTracks.page != user.pageManagerTracks.max_pages:
            user.pageManagerTracks.page += 1
            return get_inline_search_tracks(user)
    elif callback.find("selectPlaylist") != -1:
        idPlaylist = callback.split(' ')[1]
        user.get_tracks_of_playlist(idPlaylist)
        return get_inline_track_of_playlist(user)
    elif callback.find('selectTrack') != -1:
        idAlbum = callback.split(' ')[1]
        position = int(callback.split(' ')[2]) - 1
        user.play(playlist_id=idAlbum, position= position)
        return
    elif callback == 'None':
        return get_main_menu()

def send_message(vk: VkApi.get_api, user:SpotifyClient, event, callback):
    if callback == 'None':
        vk.messages.send(
            keyboard=get_callback(callback, user),
            random_id=get_random_id(),
            message='Привет! Я музыкальный бот. Чтобы начать со мной взаимодействия, авторизируйтесь в Spotify нажав кнопку ниже.',
            user_id=event.message.from_id,
            peer_id=event.message.from_id
        )
    else:
        template = get_callback(callback, user)
        vk.messages.send(
            template=template,
            random_id=get_random_id(),
            message='....',
            user_id=event.message.from_id,
            peer_id=event.message.from_id
        )

