from vk_api import VkApi
from SpotifyBot.client import SpotifyClient
from .keyboard import *
from vk_api.utils import get_random_id
from SpotifyBot import UserRepository, QueueRepository
import texts_reader as txt_reader

userRepository = UserRepository()
queueRepository = QueueRepository()

def get_callback(callback, user: SpotifyClient, event=None, session=None, cache_client=None):
    if callback.find("setLanguage") != -1:
        language = callback.split(' ')[1]
        if user:
            user.language = language
        else:
            userRepository.add_user(tgid=event.obj.user_id, access_token=None, refresh_token=None,
                                    expires_in=None, language=language)
            userId = event.obj.user_id
            cache_client.update(userId)
            user = cache_client.get(userId)
            keyboard, message = get_callback('welcome', user, event=event, session=session)
            return (keyboard, message)
    elif callback == 'welcome':
        keyboard, message = get_welcome_menu(event=event, queueRepository=queueRepository, session=session, user=user)
        return (keyboard, message)
    elif callback == "help":
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
    elif callback == 'Menu':
        return get_main_menu(user)
    else:
        return get_languages_panel()

def send_message(vk: VkApi.get_api, user:SpotifyClient, event, callback, session=None, cache_client=None):
    if callback == 'Menu' or callback == 'selectLang' or callback == "welcome" :
        keyboard, message = get_callback(callback, user, event, session=session, cache_client=cache_client)
        vk.messages.send(
            keyboard=keyboard,
            random_id=get_random_id(),
            message=message,
            user_id=event.message.from_id,
            peer_id=event.message.from_id
        )
    elif callback.find('setLanguage') != -1:
        keyboard, message = get_callback(callback=callback, user=user, event=event, session=session, cache_client=cache_client)
        vk.messages.send(
            keyboard=keyboard,
            random_id=get_random_id(),
            message=message,
            user_id=event.obj.user_id,
            peer_id=event.obj.user_id
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

