import pytest
from SpotifyBot import TokenRepository, QueueRepository
from extensions import db, initDb
from configReader import DATABASE_CONNECT

def test_TokenRepository():
    db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])

    initDb(db)

    rep = TokenRepository()
    rep.add_token(123123, "qwerty", "wasd", 321321)

    data = rep.get_token(123123)

    db.close_connection()
    assert data[1] == 123123 and data[2] == "qwerty" and data[3] == "wasd" and data[4] == 321321

def test_QueueRepository():
    db.create_connection(DATABASE_CONNECT["SERVER"], DATABASE_CONNECT["USER"], DATABASE_CONNECT["PASSWORD"], DATABASE_CONNECT["DATABASE"])

    initDb(db)

    rep = QueueRepository()
    link1 = rep.get_free_link(1)
    rep.block_link(link1[0], 1)

    link2 = rep.get_free_link(2)
    rep.block_link(link2[0], 2)

    link3 = rep.get_free_link(3)
    rep.block_link(link3[0], 3)

    link3_1 = rep.get_free_link(3)
    rep.block_link(link3_1[0], 3)

    db.close_connection()
    assert link1[2] != link2[2] and link1[2] != link3[2] and link2[2] != link3[2] and link3[2] == link3_1[2]