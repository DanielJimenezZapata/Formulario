import mysql.connector
import os
from dotenv import load_dotenv

class ConnectionDB:
    def __init__(self):
        load_dotenv()

        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "root")
        self.database = os.getenv("DB_NAME", "users_registration")

    def connect_db(self):
        try:

            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error al conectar con la base de datos: {err}")
            return None
