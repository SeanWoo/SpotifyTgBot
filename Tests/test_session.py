import pytest
from SpotifyBot import SpotifyClient, session, UserRepository
from extensions import db, initDb
from configReader import DATABASE_CONNECT

def test_session():
    db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])

    initDb(db)
    tk = UserRepository()
    tk.add_token(1,'185','135',3600)
    tk.add_token(2,'185','135',3600)
    tk.add_token(3,'185','135',3600)
    tk.add_token(4,'185','135',3600)
    tk.add_token(5,'185','135',3600)
    cache = session.Session(5)

    client1 = cache.get(1)
    client2 = cache.get(2)
    client3 = cache.get(3)
    client4 = cache.get(4)
    client5 = cache.get(5)
    client6 = cache.get(6)
    client7 = cache.get(777)
    assert client1.tgid == 1 and client2.tgid == 2 and client3.tgid == 3 and client4.tgid == 4 and client5.tgid == 5 and client6 == None and client7 == None