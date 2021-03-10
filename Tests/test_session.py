import pytest
from SpotifyBot import SpotifyClient, session, TokenRepository
from extensions import db, initDb
from configReader import DATABASE_CONNECT

def test_session():
    db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])

    initDb(db)
    tk = TokenRepository()
    tk.add_token(1,'185','135',3600)
    tk.add_token(2,'185','135',3600)
    tk.add_token(3,'185','135',3600)
    tk.add_token(4,'185','135',3600)
    tk.add_token(5,'185','135',3600)
    cache = session.Session(5)

    client1 = cache.take(1)
    client2 = cache.take(2)
    client3 = cache.take(3)
    client4 = cache.take(4)
    client5 = cache.take(5)
    client6 = cache.take(6)
    client7 = cache.take(777)
    assert client1.tgid == 1 and client2.tgid == 2 and client3.tgid == 3 and client4.tgid == 4 and client5.tgid == 5 and client6 == None and client7 == None