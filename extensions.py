from MySQL import MySQLDatabase, initDb
from loger import get_logger

log = get_logger('userlog', 'userlog.txt')
db = MySQLDatabase()