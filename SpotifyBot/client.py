import requests as r
import json

class SpotifyClient():
    def __init__(self,data):
        self.Id,self.tgid,self.access_token,self.refresh_token,self.expires_in,self.registration_at = data
        self.current_track = "Отсутствует"
        self.favorites = []
        self.playlists = []
        self.tracks = []

    def get_me(self):
        headers = {
            "Authorization": self._get_auth_header()
        }
        response = r.get("https://api.spotify.com/v1/me", headers=headers)
        if response.ok:
            return json.loads(response.text)

    def play(self):
        pass

    def stop(self):
        pass

    def next(self):
        pass

    def prev(self):
        pass

    def shuffle(self):
        pass

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

    def _get_auth_header(self):
        return f"Bearer {self.access_token}"

    def __repr__(self):
        return str(self.Id)