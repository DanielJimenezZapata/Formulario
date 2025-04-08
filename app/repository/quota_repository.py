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
        except:
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
            cursor.execute("UPDATE quota SET remaining = remaining - 1 WHERE id=1 AND remaining > 0")
            conn.commit()
            return {"message": "Success"} if cursor.rowcount > 0 else {"error": "No hay cupos"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if conn.is_connected():
                conn.close()

    def reset_slots(self, value=100):
        conn = self.db.connect_db()
        if not conn:
            return {"error": "Error de conexión"}
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quota (id, remaining) 
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE remaining = %s
            """, (value, value))
            conn.commit()
            return {"message": f"Cupos actualizados a {value}"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if conn.is_connected():
                conn.close()

    def verify_admin_password(self, password):
        conn = self.db.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM admin_credentials WHERE id=1")
            result = cursor.fetchone()
            return password == (result[0] if result else "admin123")
        except mysql.connector.Error as err:
            if err.errno == 1146:  # Tabla no existe
                return password == "admin123"
            raise
        finally:
            if conn.is_connected():
                conn.close()