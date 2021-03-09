import requests as r
import json
import datetime
import base64
from SpotifyBot import TokenRepository, SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET

tokenRepository = TokenRepository()

class SpotifyClient():
    def __init__(self,data):
        self.Id,self.tgid,self.access_token,self.refresh_token,self.expires_in,self.registration_at = data
        self.current_track = "Отсутствует"
        self.favorites = []
        self.playlists = []
        self.tracks = []



    def get_me(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me", headers=headers)
        if response.ok:
            return json.loads(response.text)

    def play(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        r.put("https://api.spotify.com/v1/me/player/play", headers=headers)

    def stop(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        r.put("https://api.spotify.com/v1/me/player/pause", headers=headers)

    def next(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        r.post("https://api.spotify.com/v1/me/player/next", headers=headers)

    def prev(self):
       self._check_valid_token()
       headers = {
            "Authorization": self._get_auth_header()
        }
       r.post("https://api.spotify.com/v1/me/player/previous", headers=headers)

    def shuffle(self):
        self._check_valid_token()
        headers = {
            "Authorization": self._get_auth_header()
        }
        r.put("https://api.spotify.com/v1/me/player/shuffle", headers=headers)

    def like(self):
        pass

    def get_music_of_playlist(self):
        pass

    def search(self):
        pass

    def cycle_track(self):
        pass

    def cycle_playlist(self):
        pass

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