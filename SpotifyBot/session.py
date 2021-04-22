from extensions import db
from SpotifyBot import SpotifyClient, UserRepository

userRepository = UserRepository()


class Session():
    def __init__(self, size):
        self.size = size
        self.clients = [None]*size
        self.first = 0
        self.last = self.first-size

    def add(self, client):
        self.clients[self.first] = client

        self.first += 1
        self.last += 1

        if self.first == self.size:
            self.first = 0

        if self.last == self.size:
            self.last = 0

        return True

    def find_by_tgid(self, tgid):
        for i in self.clients:
            if not i:
                break
            if i.tgid == tgid:
                return i
                
    def find_place_by_tgid(self, tgid):
        for i in range(len(self.clients)):
            if not self.clients[i]:
                break
            if self.clients[i].tgid == tgid:
                return i

    def get(self, tgid):
        client = self.find_by_tgid(tgid)
        if client:
            return client
        else:
            data = userRepository.get_user(tgid)
            if data:
                client = SpotifyClient(data)
                self.add(client)
                return client
            else:
                return None

    def update(self, tgid):
        data = userRepository.get_user(tgid)
        if data:
            client = SpotifyClient(data)
            self.clients[self.find_place_by_tgid(tgid)] = client
        