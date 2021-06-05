import json
from SpotifyBot import SpotifyClient
from vk_api.keyboard import VkKeyboard


# from error import MaxElement


class Keyboard(VkKeyboard):
    def __init__(self, one_time=False, inline=False, carousel=False):
        VkKeyboard.__init__(self, one_time, inline)
        self.сarousel = carousel
        self.elements = []

    def add_element(self, photo_id=None, title=None, description=None, setting_buttons=None):
        """
        :param photo_id: id фотографии
        :param title: заголовок
        :param description: обычный текст
        :param setting_buttons: настроки кнопки каждого элемента[[type, payload, label],...]. Пример [['text','callback','кнопка']]
        :return:
        """

        if len(self.elements) <= 10 and len(setting_buttons) <= 3:
            setting = ['type', 'label', 'payload']
            element = dict(photo_id=photo_id, title=title, description=description, action={
                "type": "open_photo"
            }, buttons=list(map(lambda x: dict(action=dict(zip(setting, x))), setting_buttons)))
            self.elements.append(element)
        # else:
        #     raise MaxElement

    def get_carousel(self):
        res = dict(type='carousel', elements=self.elements)
        print(res)
        return json.dumps(res)


def get_main_menu():
    keyboard = Keyboard(one_time=True)
    keyboard.add_button('Управление', payload={
        'type': 'get_inline_control'
    })
    keyboard.add_button('Плейлист', payload={
        'type': 'get_inline_playlist'
    })

    keyboard.add_line()

    keyboard.add_button('Поиск треков', payload={
        'type': 'set_search'
    })
    keyboard.add_button('О нас', payload={
        'type': 'get_info'
    })

    return keyboard.get_keyboard()


def get_inline_control(user):
    keyboard = Keyboard(carousel=True)

    counter = 10 * (user.pageManagerPlaylists.page - 1)

    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        keyboard.add_element("-109837093_457242811", track.artists, track.name,
                             [['text', "Выбрать", f"selectTrack {track.id}"]])

    return keyboard.get_carousel()


def get_inline_playlist(user: SpotifyClient):
    keyboard = Keyboard(carousel=True)
    counter = 10 * (user.pageManagerPlaylists.page - 1)
    for playlist in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        keyboard.add_element("-109837093_457242811", playlist.name, 'playlist',
                             [['text', "Выбрать", {"type":f"selectPlaylist {playlist.id}"}]])
    return keyboard.get_carousel()


def get_inline_track_of_playlist(user):
    keyboard = Keyboard(carousel=True)
    counter = 10 * (user.pageManagerTracks.page - 1)
    for track in user.pageManagerTracks[user.pageManagerTracks.page]:
        counter += 1
        keyboard.add_element("-109837093_457242811", track.artists, track.name,
                             [["callback", "Выбрать", {"type":f"selectTrackByPlaylistId {track.playlist_id} {counter}"}]])
    return keyboard.get_carousel()


def get_inline_search_tracks(user):
    keyboard = Keyboard(carousel=True)
    counter = 10 * (user.pageManagerPlaylists.page - 1)
    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        keyboard.add_element("-109837093_457242811", track.artists, track.name,
                             [['text', "Выбрать", {"type":f"selectTrack {track.playlist.id} {counter}"}]])
    return keyboard.get_carousel()
