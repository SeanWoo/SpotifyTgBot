import requests as r
import json
import datetime
import base64
from SpotifyBot import TokenRepository, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, Playlist, Track, PageManager, TelegramError
import texts_reader as txt_reader
from extensions import errorlog

tokenRepository = TokenRepository()

class SpotifyClient():
    def __init__(self, data):
        self.Id, self.tgid, self.access_token, self.refresh_token, self.expires_in, self.registration_at = data
        self.pageManagerTracks = PageManager([])
        self.pageManagerPlaylists = PageManager([])
        self.is_tracks_in_playlist = True
        self.shuffle_state = False
        self.inclube_playlist = False
        self.repeat_state = 'off'
        self.language = "ru"

        self._is_playing = False
        

    @property
    def current_track(self):
        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info
        return Track(player_info['track']['id'], player_info['track']['name'], player_info['track']['album']['artists'])

    @property
    def is_spotify_active(self):
        devices = self._get_devices()
        if isinstance(devices, TelegramError):
            return devices
        return len(devices) != 0

    @property
    def is_premium(self):
        me = self.get_me()
        if isinstance(me, TelegramError):
            return me
        return me["product"] != 'open'

    @property
    def is_playing(self):
        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return TelegramError(player_info)
        
        return self._is_playing
    
    @is_playing.setter
    def is_playing(self, value):
        self._is_playing = value

    def get_me(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me", headers=headers)
        if response.ok:
            return json.loads(response.text)
        else:
            return TelegramError(json.loads(response.text))

    def play(self, use_current_tracks=False, playlist_id=None, position=0):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        if use_current_tracks:
            data = {
                "uris": ["spotify:track:" + track.id for track in self.pageManagerTracks.raw_data],
                "offset": {
                    "position": position
                },
                "position_ms": 0
            }
        elif playlist_id:
            data = {
                "context_uri": "spotify:playlist:" + playlist_id,
                "offset": {
                    "position": position
                },
                "position_ms": 0
            }
            self._current_playlist = playlist_id
        else:
            data = {}

        if self.is_playing and playlist_id == None and use_current_tracks == False:
            response = r.put("https://api.spotify.com/v1/me/player/pause", headers=headers, data=json.dumps(data))
            self.is_playing = False
        else:
            response = r.put("https://api.spotify.com/v1/me/player/play", headers=headers, data=json.dumps(data))
            self.is_playing = True
        return response.ok

    def next(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.post(
            "https://api.spotify.com/v1/me/player/next", headers=headers)
        return response.ok

    def prev(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info
        
        response = r.post(
            "https://api.spotify.com/v1/me/player/previous", headers=headers)
        return response.ok

    def shuffle(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.put("https://api.spotify.com/v1/me/player/shuffle?state=" +
                         str(self.shuffle_state), headers=headers)
        return response.ok

    def get_playlists(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.get(
            "https://api.spotify.com/v1/me/playlists", headers=headers)
        if response.ok:
            result = list(map(lambda x: Playlist(x['id'], x['name']), json.loads(response.text)['items']))
            self.pageManagerPlaylists = PageManager(result)
            return self.pageManagerPlaylists
        else:
            return TelegramError(json.loads(response.text))

    def get_tracks_of_playlist(self, playlist_id):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=90&market=ES", headers=headers)
        if response.ok:
            errorlog.warn(response.text)
            result = list(map(lambda x: Track(x['track']['id'], x['track']['name'], x['track']['album']['artists'],  playlist_id=playlist_id), json.loads(response.text)['items']))
            self.pageManagerTracks = PageManager(result)
            return self.pageManagerTracks
        else:
            return TelegramError(json.loads(response.text))
        
    def search(self, message, typ="track"):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        market = txt_reader.get_text("market", self.language)
        response = r.get(f"https://api.spotify.com/v1/search?q={message}&type={typ}%2Cartist&market={market}", headers=headers)
        if response.ok:
            if typ == "track":
                result = list(map(lambda x: Track(x['id'], x['name'], x['artists']), json.loads(response.text)['tracks']['items']))
                self.pageManagerTracks = PageManager(result)
                return self.pageManagerTracks
            return []
        else:
            return TelegramError(json.loads(response.text))

    def cycle_track(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.put("https://api.spotify.com/v1/me/player/repeat?state=" +
                         str(self.repeat_state), headers=headers)
        if not response.ok:
            return TelegramError(json.loads(response.text))
        return response.ok

    def cycle_playlist(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self.get_player()
        if isinstance(player_info, TelegramError):
            return player_info

        response = r.put("https://api.spotify.com/v1/me/player/repeat?state=" +
                         str(self.repeat_state), headers=headers)
        if not response.ok:
            return TelegramError(json.loads(response.text))
        return response.ok

    def _get_devices(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get(
            "https://api.spotify.com/v1/me/player/devices", headers=headers)
        if response.ok:
            return json.loads(response.text)["devices"]
        else:
            return TelegramError(json.loads(response.text))

    def get_player(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me/player", headers=headers)
        if response.status_code == 204:
            devices = self._get_devices()
            if isinstance(devices, TelegramError):
                return devices
            elif len(devices) == 0:
                return TelegramError({"status": 1000, "message": "Empty devices"})
            #active_device = list(filter(lambda x: x["is_active"] == True, devices))[0]
            response = r.put("https://api.spotify.com/v1/me/player?", headers=headers, data=json.dumps({
                "device_ids": [devices[0]['id']],
                "play": True
            }))
            if not response.ok:
                return TelegramError({"status": 1001, "message": "Couldn't activate the device"})

            response = r.get("https://api.spotify.com/v1/me/player", headers=headers)
            if response.status_code == 204:
                return TelegramError({"status": 1001, "message": "Couldn't activate the device"})
            elif not response.ok:
                return TelegramError(json.loads(response.text))
        elif not response.ok:
            return TelegramError(json.loads(response.text))

        if response.ok:
            result = json.loads(response.text)
            self.is_playing = result["is_playing"]
            self.shuffle_state = result["shuffle_state"]

            if result["repeat_state"] == 'off' or 'track':
                self.repeat_state = 'context'
            if result["repeat_state"] == 'context':
                self.repeat_state = 'off'

            return result
        

    def _check_valid_token(self):
        if self.registration_at + datetime.timedelta(seconds=self.expires_in) <= datetime.datetime.today():
            self._refresh_token()

    def _refresh_token(self):
        auth = base64.urlsafe_b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        response = r.post(f"https://accounts.spotify.com/api/token",
                          headers={
                              "Authorization": f"Basic {auth}",
                              "Content-Type": "application/x-www-form-urlencoded"
                          },
                          data={
                              "grant_type": "refresh_token",
                              "refresh_token": self.refresh_token,
                              "client_id": SPOTIFY_CLIENT_ID
                          })
        tokens = json.loads(response.text)
        if "refresh_token" not in tokens:
            tokens["refresh_token"] = self.refresh_token
        if "access_token" in tokens:
            tokenRepository.update_token(
                self.Id, tokens["access_token"], tokens["refresh_token"], tokens["expires_in"])

            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.expires_in = tokens["expires_in"]
            self.registration_at = datetime.datetime.today()

    def _get_auth_header(self):
        return f"Bearer {self.access_token}"

    def __repr__(self):
        return str(self.Id)
