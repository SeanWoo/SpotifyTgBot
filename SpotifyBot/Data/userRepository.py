import datetime
from extensions import db
from . import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("users")

    def add_user(self, tgid, access_token, refresh_token, expires_in, language):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(f"INSERT INTO {self.tableName}(tgid, access_token, refresh_token, expires_in, language, registration_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (tgid, access_token, refresh_token, expires_in, language, now))
        db.close_cursor()
    def update_token(self, tgid, access_token, refresh_token, expires_in):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(f"UPDATE {self.tableName} SET access_token=%s, refresh_token=%s, expires_in=%s, registration_at=%s WHERE tgid=%s", 
                            (access_token, refresh_token, expires_in, now, tgid))
        db.close_cursor()
    def get_user(self, tgid):
        cursor = db.execute(f"SELECT * FROM {self.tableName} WHERE tgid = {tgid}")
        data = cursor.fetchone()
        db.close_cursor()
        return data
    def update_language(self, tgid, language):
        db.execute(f"UPDATE {self.tableName} SET language=%s WHERE tgid=%s", 
                            (language, tgid))
        db.close_cursor()