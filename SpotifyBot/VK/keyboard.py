import json
from SpotifyBot import SpotifyClient
from vk_api.keyboard import VkKeyboard
from error import MaxElement




class Keyboard(VkKeyboard):
    def __init__(self, one_time=False, inline=False, carousel=False):
        super(VkKeyboard.__init__(one_time, inline))
        self.сarousel = carousel
        self.buttons = []

    def add_element(self,photo_id=None, title=None, description=None ,type='text', label=None, callback=None):
            if self.carousel:
                if len(self.buttons) != 10:
                    button = dict(photo_id=photo_id, title=title, description=description, action={
                        "type": "open_photo"
                    })
                    self.buttons.append(button)
                else:
                    raise MaxElement
            return
    def get_carousel(self):
            pass


def get_main_menu():
    keyboard = Keyboard(one_time=True)
    keyboard.add_button('Управление',payload={
        'type':'get_inline_control'
    })
    keyboard.add_button('Плейлист', payload={
        'type':'get_inline_playlist'
    })

    keyboard.add_line()

    keyboard.add_button('Поиск треков', payload={
        'type':'set_search'
    })
    keyboard.add_button('О нас', payload={
        'type':'get_info'
    })

    return keyboard.get_keyboard()
def get_inline_control(user):
    keyboard = VkKeyboard(inline=True)

    counter = 10 * (user.pageManagerPlaylists.page - 1)
    elements = []

    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        element = {
            "photo_id": "109837093_457242811",
            "title": track.name,
            "action":{
                "type":"open_photo"
            },
            "buttons": [{
                "action": {
                    "type":"text",
                    "label": "Выбрать",
                    "payload": {
                        "type":f"selectTrack {track.id}"
                    }
                }
            }]
        }
        elements.append(element)

    play_state = "Pause" if user.is_playing else 'Play'
    keyboard.add_callback_button('Prev', payload={
        'type': 'prev'
    })
    keyboard.add_callback_button(play_state, payload={
        'type':'play'
    })
    keyboard.add_callback_button('Next', payload={
        'type':'next'
    })
    keyboard.add_line()
    keyboard.add_callback_button('cplaylist', payload={
        'type':'cplaylist'
    })
    keyboard.add_callback_button('Shufle', payload={
        'type':'shufle'
    })

    keyboard.add_callback_button('ctrack', payload={
        'type':'ctrack'
    })
    return elements

def get_inline_playlist(user: SpotifyClient):
    counter = 10 * (user.pageManagerPlaylists.page - 1)
    elements = []
    for playlist in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        element = {
            "photo_id": "-109837093_457242811",
            "title": playlist.name,
            "description": 'Playlist',
            "action":{
                "type":"open_photo"
            },
            "buttons": [{
                "action": {
                    "type":"text",
                    "label": "Выбрать",
                    "payload": {
                        "type":f"selectPlaylist {playlist.id}"
                    }
                }
            }]
        }
        elements.append(element)
    return json.dumps({"type":"carousel","elements":elements})

def get_inline_track_of_playlist(user):
    counter = 10 * (user.pageManagerPlaylists.page - 1)
    elements = []
    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        element = {
            "photo_id": "-109837093_457242811",
            "title": track.name,
            "description": track.artists,
            "action":{
                "type":"open_photo"
            },
            "buttons": [{
                "action": {
                    "type":"inline",
                    "label": "Выбрать",
                    "payload": {
                        "type":f"selectTrackByPlaylistId {track.playlist.id} {counter}"
                    }
                }
            }]
        }
        elements.append(element)
    return json.dumps({"type":"carousel","elements":elements})

def get_inline_search_tracks(user):

    counter = 10 * (user.pageManagerPlaylists.page - 1)
    elements = []
    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        element = {
            "photo_id": "109837093_457242811",
            "title": f'{counter}. {track.artists} - {track.name}',
            "action":{
                "type":"open_photo"
            },
            "buttons": [{
                "action": {
                    "type":"text",
                    "label": "Выбрать",
                    "payload": {
                        "type":f"selectTrackByPlaylistId {track.playlist.id} {counter}"
                    }
                }
            }]
        }
        elements.append(element)
    return elements