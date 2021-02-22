import mysql.connector
from mysql.connector import Error

class MySQLDatabase():
    def __init__(self):
        self.connection = None
        self.cursor = None
    def create_connection(self, host_name, user_name, user_password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=database
            )
            self.cursor = self.connection.cursor()
            print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_database(self, query):
        try:
            self.cursor.execute(query)
        except Error as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def execute(self, query, data = None):
        try:
            self.cursor.execute(query, data)
        except Error as e:
            print(f"The error '{e}' occurred")
            return False

        return self.cursor

    def close():
        self.cursor.close()
        self.connection.close()