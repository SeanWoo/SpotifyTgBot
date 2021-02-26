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
            self.cursor = self.connection.cursor(buffered=True)
            print("Connection to MySQL DB successful")
            return True
        except Exception as e:
            return False
            print(f"The error '{e}' occurred")

    def create_database(self, query):
        try:
            self.cursor.execute(query)
        except Exception as e:
            print(f"The error '{e}' occurred")
            return False

        return True

    def execute(self, query, data = None):
        if self.cursor == None: return False
        try:
            self.cursor = self.connection.cursor(buffered=True)
            self.cursor.execute(query, data)
        except Exception as e:
            print(f'The error {e} occurred')

            return False

        return self.cursor

    def close_cursor(self):
        self.cursor.close()
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    def connection_exist(self):
        if self.connection:
            return True
        return False