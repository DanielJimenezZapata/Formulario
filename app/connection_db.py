from turtle import st
import mysql.connector
import os
from dotenv import load_dotenv

class ConnectionDB:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "quota_system")

    def connect_db(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as err:
            st.error(f"Error de base de datos: {err}")
            return None

