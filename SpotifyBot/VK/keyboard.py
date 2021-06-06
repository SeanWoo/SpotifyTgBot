import json
from SpotifyBot import SpotifyClient
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
import texts_reader as txt_reader
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

        if len(self.elements) <= 10 or len(setting_buttons) <= 3:
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

def get_languages_panel():
    keyboard = Keyboard(inline=True)
    keyboard.add_callback_button('English', payload={"callback":"setLanguage en"})
    keyboard.add_line()
    keyboard.add_callback_button('Русский', payload={"callback":"setLanguage ru"})

    message = txt_reader.get_text('en',"select_language")
    return (keyboard.get_keyboard(), message)
def get_welcome_menu(event, queueRepository, session, user):
    keyboard = Keyboard(inline=True)
    data = queueRepository.get_free_link(event.obj.user_id)
    queueRepository.block_link(data[0], event.obj.user_id)
    message = txt_reader.get_text(user.language, 'response_message')
    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
    shortLink = session.method('utils.getShortLink', {'url': link})
    keyboard.add_callback_button(label=txt_reader.get_text(user.language, 'login'), color=VkKeyboardColor.POSITIVE, payload={"type": "open_link",
                                                                                        "link": shortLink[
                                                                                            "short_url"]
                                                                                        }
                                 )
    return (keyboard.get_keyboard(), message)
def get_main_menu(user):
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
    message = txt_reader.get_text(user.language, "registration")
    return (keyboard.get_keyboard(), message)


def get_inline_control(user):
    keyboard = Keyboard(carousel=True)

    counter = 10 * (user.pageManagerPlaylists.page - 1)

    for track in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        keyboard.add_element("405804467_457255162", track.artists, track.name,
                             [['text', "Выбрать", f"selectTrack {track.id}"]])

    return keyboard.get_carousel()


def get_inline_playlist(user: SpotifyClient):
    keyboard = Keyboard(carousel=True)
    counter = 10 * (user.pageManagerPlaylists.page - 1)
    for playlist in user.pageManagerPlaylists[user.pageManagerPlaylists.page]:
        counter += 1
        keyboard.add_element("405804467_457255162", playlist.name, 'playlist',
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
