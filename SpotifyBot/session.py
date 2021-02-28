from extensions import db
from SpotifyBot import SpotifyClient

class Session():
    def __init__(self,size):
        self.size = size
        self.clients = [None]*size
        self.first = 0
        self.last = self.first-size

    def add(self,client):
        self.clients[self.first] = client
        
        self.first += 1
        self.last += 1
        
        if self.first == self.size:
            self.first = 0
            
        if self.last == self.size:
            self.last = 0

        return True

    def get(self,id):
        for i in self.clients:
            if not i:
                break
            if i.tgid == id:
                return i

    def take(self,id):
        client = self.get(id)
        if client:
            return client
        else:
            cursor = db.execute(f"SELECT * FROM tokens WHERE tgid = {id}")
            data = cursor.fetchone()
            db.close_cursor()
            if data:
                client = SpotifyClient(data)
                self.add(client)
                return client
            else:
                return None