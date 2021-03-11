import time
from extensions import db
from . import BaseRepository

class QueueRepository(BaseRepository):
    def __init__(self):
        super().__init__("queue")

    def get_free_link(self, tgid):
        cursor = db.execute(f"SELECT * FROM {self.tableName} WHERE tgid=%s OR tgid IS NULL OR endtime < %s LIMIT 1",
                        (tgid, round(time.time())))
        data = cursor.fetchone()
        db.close_cursor()
        return data
    def get_tgid_by_urlid(self, urlid):
        cursor = db.execute("SELECT * FROM queue WHERE link LIKE %s AND endtime > %s", ('%' + urlid + '%', round(time.time())))
        data = cursor.fetchone()
        db.close_cursor()
        return data
    def block_link(self, id, tgid):
        db.execute(f"UPDATE {self.tableName} SET tgid=%s, endtime=%s WHERE id=%s", (tgid, time.time() + 300, id))
        db.close_cursor()