import requests as r
import json
import datetime
import base64
from SpotifyBot import TokenRepository, SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET, Playlist, Track

tokenRepository = TokenRepository()

class SpotifyClient():
    def __init__(self,data):
        self.Id,self.tgid,self.access_token,self.refresh_token,self.expires_in,self.registration_at = data
        self._current_track = None
        self._current_playlist = None
        self.tracks = []
        self.is_playing = False
        self.is_tracks_in_playlist = True
        self.shuffle_state = False
        self.page = 1
        self.max_pages = 0
        self.positions_track = 1
    @property
    def current_track(self):
        player_info = self._get_player_info()
        if not player_info:
            return None
        return Track(player_info['item']['id'], player_info['item']['name'])

    @property
    def is_spotify_active(self):
        devices = self._get_devices()
        return len(devices) != 0 
        
    @property
    def is_premium(self):
        me = self.get_me()["product"]
        return me != 'open'

    def get_me(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me", headers=headers)
        if response.ok:
            return json.loads(response.text)

    def play(self, track_id = None, playlist_id = None, position = 0):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        player_info = self._get_player_info()
        if not player_info:
            return None
        self.is_playing = player_info["is_playing"]
        
        if track_id:
            data = {
                "uris": [track_id]
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

        if self.is_playing and playlist_id == None and track_id == None:
            response = r.put("https://api.spotify.com/v1/me/player/pause", headers=headers, data=json.dumps(data))
        else:
            response = r.put("https://api.spotify.com/v1/me/player/play", headers=headers, data=json.dumps(data))
        return response.ok

    def next(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.post("https://api.spotify.com/v1/me/player/next", headers=headers)
        return response.ok

    def prev(self):
       self._check_valid_token()
       headers = {
            "Authorization": self._get_auth_header()
        }
       response = r.post("https://api.spotify.com/v1/me/player/previous", headers=headers)
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

        response = r.put("https://api.spotify.com/v1/me/player/shuffle?state=" + str(self.shuffle_state), headers=headers)
        return response.ok

    def like(self):
        pass

    def get_playlists(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return []
        self.shuffle_state = not player_info["shuffle_state"]

        response = r.get("https://api.spotify.com/v1/me/playlists", headers=headers)
        if response.ok:
            return list(map(lambda x: Playlist(x['id'], x['name']), json.loads(response.text)['items']))
        return []

    def get_music_of_playlist(self, playlist_id):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }

        player_info = self._get_player_info()
        if not player_info:
            return None

        self.shuffle_state = not player_info["shuffle_state"]

        response = r.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=90&market=ES", headers=headers)
        if response.ok:
            return list(map(lambda x: Track(x['track']['id'], x['track']['name'], x['track']['album']['artists'][0]['name'],  playlist_id=playlist_id), json.loads(response.text)['items']))
        return []
    def get_track_in_playlist(self,id):
        tracks = self.get_music_of_playlist(id)
        if len(tracks) != 0:
            self.is_tracks_in_playlist = True
            nav = {}
            l = 1
            tracks_list = []
            while True:
                if len(tracks_list) != 10 and len(tracks) != 0: tracks_list.append(tracks.pop(0))
                else:
                    nav.update([(l,tracks_list)]) 
                    tracks_list = []
                    if len(tracks) != 0: l += 1
                    else: break
            self.max_pages = l
            return nav
        else: self.is_tracks_in_playlist = False
    def search(self):
        pass

    def cycle_track(self):
        pass

    def cycle_playlist(self):
        pass

    def _get_devices(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
        if response.ok:
            return json.loads(response.text)["devices"] 
                 
    def _get_player_info(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me/player", headers=headers)
        if response.status_code == 204:
            devices = self._get_devices()
            if len(devices) == 0:
                return None
            r.put("https://api.spotify.com/v1/me/player?", headers=headers, data=json.dumps({
                "device_ids": [devices[0]['id']],
                "play": True
            }))

            response = r.get("https://api.spotify.com/v1/me/player", headers=headers)

        if response.ok:
            return json.loads(response.text)

    def _check_valid_token(self):
        if self.registration_at + datetime.timedelta(seconds=self.expires_in) <= datetime.datetime.today():
            self._refresh_token()

    def _refresh_token(self):
        auth = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
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
            tokenRepository.update_token(self.Id, tokens["access_token"], tokens["refresh_token"], tokens["expires_in"])

            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.expires_in = tokens["expires_in"]
            self.registration_at = datetime.datetime.today()

    def _get_auth_header(self):
        return f"Bearer {self.access_token}"

    def __repr__(self):
        return str(self.Id)