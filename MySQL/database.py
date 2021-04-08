import mysql.connector
from mysql.connector import Error

class MySQLDatabase():
    def __init__(self):
        self.connection = None
        self.cursor = None

        self.host_name = None
        self.user_name = None
        self.user_password = None
        self.database = None
    def create_connection(self, host_name, user_name, user_password, database):
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.database = database
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
        except Error as e:
            print(f"The error '{e}' occurred")




    def create_database(self, query):
        if not self.connection.is_connected():
            self.create_connection(self.host_name, self.user_name, self.user_password, self.database)
            self.close_cursor()

        try:
            self.cursor.execute(query)
        except Error as e:
            print(f"The error '{e}' occurred")

        return True

    def execute(self, query, data = None):
        if not self.connection.is_connected():
            self.create_connection(self.host_name, self.user_name, self.user_password, self.database)
            self.close_cursor()

        try:
            self.cursor = self.connection.cursor(buffered=True)
            self.cursor.execute(query, data)
        except Error as e:
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