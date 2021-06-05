import vk_api
import json
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll
from SpotifyBot import QueueRepository, Session, UserRepository
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
import threading
from SpotifyBot.VK.keyboard import get_inline_control, get_inline_playlist,get_inline_track_of_playlist,get_inline_search_tracks
from SpotifyBot.VK.callback import get_callback, send_message
from configReader import VK_TOKEN, ID_GROUP
session = vk_api.VkApi(token=VK_TOKEN)


longpoll = VkBotLongPoll(session, ID_GROUP)
vk = session.get_api()
cache_client = Session(200)
queueRepository = QueueRepository()
LsLongPoll = VkLongPoll(session)
Lsvk = session.get_api()
userRepository = UserRepository()
def start():
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            userId = event.message.from_id
            cache_client.update(userId)
            user = cache_client.get(userId)
            callback = event.object.message
            if 'Начать' == event.message.text:
                if user:
                    if user.access_token:
                        user_info = user.get_me()
                        username = session.method('users.get', {'user_ids':str(event.message.from_id)}, raw=False)[0]
                        if event.from_user:
                            send_message(vk=vk,event=event, user=user, callback='None')
                else:
                    userRepository.add_user(tgid=event.message.from_id, access_token=None, refresh_token=None,
                                            expires_in=None, language='ru')
                    keyboard = VkKeyboard(one_time=False,
                                          inline=True
                                          )
                    data = queueRepository.get_free_link(event.message.from_id)
                    queueRepository.block_link(data[0], event.message.from_id)

                    link = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope={SPOTIFY_SCOPE}&redirect_uri={data[2]}"
                    shortLink = session.method('utils.getShortLink', {'url':link})
                    keyboard.add_callback_button(label='Вход', color=VkKeyboardColor.POSITIVE, payload={"type":"open_link",
                                                                                                 "link":shortLink["short_url"]
                                                                                                 }
                                  )
                    if event.from_user:
                        vk.messages.send(
                            keyboard=keyboard.get_keyboard(),
                            random_id=get_random_id(),
                            message='Привет! Я музыкальный бот. Чтобы начать со мной взаимодействия, авторизируйтесь в Spotify нажав кнопку ниже.',
                            user_id=event.message.from_id,
                            peer_id=event.message.from_id
                        )
            elif len(callback['payload']) != 0:
                send_message(vk=vk, callback=callback['payload'][9:][:-2], event=event, user=user)

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.object.payload.get('type') == 'open_link':
                r = vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps(event.object.payload))
            else:
                get_callback(event.object.payload.get('type'), user)
                r = vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    )

def start_vk():
    th = threading.Thread(target=start)
    th.start()
