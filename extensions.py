from MySQL import MySQLDatabase, initDb
from loger import get_logger

userlog = get_logger('userlog', 'userlog.txt')
errorlog = get_logger('errorlog', 'errorlog.txt')
db = MySQLDatabase()