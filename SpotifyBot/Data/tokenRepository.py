import datetime
from extensions import db
from . import BaseRepository

class TokenRepository(BaseRepository):
    def __init__(self):
        super().__init__("tokens")

    def add_token(self, tgid, access_token, refresh_token, expires_in):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(f"INSERT INTO {self.tableName}(tgid, access_token, refresh_token, expires_in, registration_at) VALUES (%s, %s, %s, %s, %s)",
                (tgid, access_token, refresh_token, expires_in, now))
        db.close_cursor()
    def update_token(self, tgid, access_token, refresh_token, expires_in):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(f"UPDATE {self.tableName} SET access_token=%s, refresh_token=%s, expires_in=%s, registration_at=%s WHERE tgid=%s", 
                            (access_token, refresh_token, expires_in, now, tgid))
        db.close_cursor()
    def get_token(self, tgid):
        cursor = db.execute(f"SELECT * FROM {self.tableName} WHERE tgid = {tgid} LIMIT 1")
        data = cursor.fetchone()
        db.close_cursor()
        return data