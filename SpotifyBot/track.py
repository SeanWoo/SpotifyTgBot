class Track:
    def __init__(self, id, name, playlist_id = None):
        self.id = id
        self.name = name
        self.playlist_id = playlist_id

    def __eq__(self, other):
        return self.id == other.id