import requests as r
import json
import datetime
import base64
from SpotifyBot import TokenRepository, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, Playlist, Track, PageManager
import texts_reader as txt_reader

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
        player_info = self._get_player_info()
        if not player_info:
            return None
        return Track(player_info['track']['id'], player_info['track']['name'], player_info['track']['album']['artists'])

    @property
    def is_spotify_active(self):
        devices = self._get_devices()
        return len(devices) != 0

    @property
    def is_premium(self):
        me = self.get_me()["product"]
        return me != 'open'

    @property
    def is_playing(self):
        player_info = self._get_player_info()
        _is_playing = player_info['is_playing']
        return _is_playing
    
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

    def get_player(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me/player", headers=headers)
        if response.ok:
            return json.loads(response.text)

    def play(self, use_current_tracks=False, playlist_id=None, position=0):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        player_info = self._get_player_info()
        if not player_info:
            return None
        self.is_playing = player_info["is_playing"]
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
        response = r.post(
            "https://api.spotify.com/v1/me/player/next", headers=headers)
        return response.ok

    def prev(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.post(
            "https://api.spotify.com/v1/me/player/previous", headers=headers)
        return response.ok

    def shuffle(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return None
        self.shuffle_state = not player_info["shuffle_state"]

        response = r.put("https://api.spotify.com/v1/me/player/shuffle?state=" +
                         str(self.shuffle_state), headers=headers)
        return response.ok

    def get_playlists(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return []

        response = r.get(
            "https://api.spotify.com/v1/me/playlists", headers=headers)
        if response.ok:
            result = list(map(lambda x: Playlist(x['id'], x['name']), json.loads(response.text)['items']))
            self.pageManagerPlaylists = PageManager(result)
            return self.pageManagerPlaylists
        return []

    def get_tracks_of_playlist(self, playlist_id):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return None

        response = r.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=90&market=ES", headers=headers)
        if response.ok:
            result = list(map(lambda x: Track(x['track']['id'], x['track']['name'], x['track']['album']['artists'],  playlist_id=playlist_id), json.loads(response.text)['items']))
            self.pageManagerTracks = PageManager(result)
            return self.pageManagerTracks

        return []
        
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

    def cycle_track(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return None

        if player_info["repeat_state"] == 'off' or 'context':
            self.repeat_state = 'track'
        if player_info["repeat_state"] == 'track':
            self.repeat_state = 'off'

        response = r.put("https://api.spotify.com/v1/me/player/repeat?state=" +
                         str(self.repeat_state), headers=headers)
        return response.ok

    def cycle_playlist(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return None

        if player_info["repeat_state"] == 'off' or 'track':
            self.repeat_state = 'context'
        if player_info["repeat_state"] == 'context':
            self.repeat_state = 'off'

        response = r.put("https://api.spotify.com/v1/me/player/repeat?state=" +
                         str(self.repeat_state), headers=headers)
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

    def _get_player_info(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get(
            "https://api.spotify.com/v1/me/player", headers=headers)
        if response.status_code == 204:
            devices = self._get_devices()
            if len(devices) == 0:
                return None
            #active_device = list(filter(lambda x: x["is_active"] == True, devices))[0]
            r.put("https://api.spotify.com/v1/me/player?", headers=headers, data=json.dumps({
                "device_ids": [devices[0]['id']],
                "play": True
            }))

            response = r.get(
                "https://api.spotify.com/v1/me/player", headers=headers)
            if response.status_code == 204:
                return None
        if response.ok:
            return json.loads(response.text)

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
