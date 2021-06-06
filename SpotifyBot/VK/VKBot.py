from datetime import time
import texts_reader as txt_reader
import requests
import vk_api
import json
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll
from SpotifyBot import QueueRepository, Session, UserRepository
from configReader import SPOTIFY_CLIENT_ID, SPOTIFY_SCOPE
import threading
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
    try:
        for event in longpoll.listen():

            if event.type == VkBotEventType.MESSAGE_NEW:
                userId = event.message.from_id
                cache_client.update(userId)
                user = cache_client.get(userId)
                callback = event.object.message
                if  event.message.text in ['Начать','start','/start','Привет', 'st','m','menu','м','меню']:
                    if user:
                        if user.access_token:
                            user_info = user.get_me()
                            username = session.method('users.get', {'user_ids':str(event.message.from_id)}, raw=False)[0]
                            if event.from_user:
                                send_message(vk=vk,event=event, user=user, callback='Menu')
                        else:
                           send_message(vk=vk, event=event, user=user, callback='welcome', session=session)
                    else:
                        send_message(vk=vk,event=event, callback="selectLang", user=user, session=session, cache_client=cache_client)
                elif event.message.text in ['stats', 'стастистика', '/stats','st']:
                    all, registered = userRepository.stats()
                    vk.messages.send(
                        keyboard=get_callback('None', user),
                        random_id=get_random_id(),
                        message=txt_reader.get_text(user.language,"stats").format(all[0], registered[0]),
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
                elif event.object.payload.get('callback') in ['setLanguage en', 'setLanguage ru']:
                    send_message(vk=vk,event=event,callback=event.object.payload.get('callback'), user=user, session=session, cache_client=cache_client)
                else:
                    get_callback(callback=event.object.payload.get('type'),user=user, event=event)
                    r = vk.messages.sendMessageEventAnswer(
                        event_id=event.object.event_id,
                        user_id=event.object.user_id,
                        peer_id=event.object.peer_id,
                        )
    except requests.exceptions.ReadTimeout:
        print("\n Переподключение к серверам ВК \n")
        time.sleep(3)

def start_vk():
    th = threading.Thread(target=start)
    th.start()
