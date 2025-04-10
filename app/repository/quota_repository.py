from repository.connection_db import ConnectionDB
import mysql.connector

class QuotaRepository:
    def __init__(self):
        self.db = ConnectionDB()
    
    def get_remaining_slots(self):
        conn = self.db.connect_db()
        if not conn:
            return 0
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT remaining FROM quota WHERE id=1")
            result = cursor.fetchone()
            return result[0] if result else 0
        except mysql.connector.Error as err:
            if err.errno == 1146:  # Tabla no existe
                self._initialize_database()
                return 100
            return 0
        finally:
            if conn.is_connected():
                conn.close()

    def decrement_slot(self):
        conn = self.db.connect_db()
        if not conn:
            return {"error": "Error de conexión"}
            
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE quota SET remaining = GREATEST(0, remaining - 1) WHERE id=1")
            conn.commit()
            return {"message": "Success"} if cursor.rowcount > 0 else {"error": "No actualizado"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if conn.is_connected():
                conn.close()

    def reset_slots(self, value=100):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quota (id, remaining) 
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE remaining = %s
            """, (value, value))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def verify_admin_password(self, password):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM admin_credentials WHERE id=1")
            result = cursor.fetchone()
            return password == (result[0] if result else "admin123")
        except mysql.connector.Error as err:
            if err.errno == 1146:  # Tabla no existe
                return password == "admin123"
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def update_admin_password(self, new_password):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_credentials (
                    id INT PRIMARY KEY,
                    password VARCHAR(255)
                )
            """)
            cursor.execute("""
                INSERT INTO admin_credentials (id, password)
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE password = %s
            """, (new_password, new_password))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def _initialize_database(self):
        conn = self.db.connect_db()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS quota (id INT PRIMARY KEY, remaining INT)")
            cursor.execute("INSERT INTO quota (id, remaining) VALUES (1, 100)")
            conn.commit()
        finally:
            if conn.is_connected():
                conn.close()

    def get_current_quota_count(self, url_key: str) -> int:
        conn = self.db.connect_db()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS url_quota(url_key VARCHAR(255) PRIMARY KEY, count INT NOT NULL DEFAULT 0)""")
            cursor.execute("SELECT count FROM url_quota WHERE url_key =%s", (url_key,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error al obtener count de {url_key}: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    

    def increment_quota_count(self, url_key: str):
        conn = self.db.connect_db()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO url_quota(url_key, count) VALUES (%s, 1) ON DUPLICATE KEY UPDATE count = count + 1""", (url_key,))
            return True
        except Exception as e:
            print(f"Error al incrementar count de {url_key}: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()