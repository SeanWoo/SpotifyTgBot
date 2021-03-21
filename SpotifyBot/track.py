class Track:
    def __init__(self, id, name, artists, playlist_id = None):
        self.id = id
        self.name = name
        self.playlist_id = playlist_id

        self._artists = artists

    @property
    def artists(self):
        result = ""
        for artist in self._artists:
            result += artist["name"] + ", "
        return result.rstrip(', ')
    @artists.setter
    def artists(self, value):
        self._artists = value

    def __eq__(self, other):
        return self.id == other.id