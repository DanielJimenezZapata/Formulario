from repository.connection_db import ConnectionDB
import mysql.connector

class QuotaRepository:
    def __init__(self):
        self.db = ConnectionDB()

    # Métodos para gestión de cupos
    def get_remaining_slots(self):
        conn = self.db.connect_db()
        if not conn:
            return -1
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT remaining FROM quota WHERE id=1")
            remaining = cursor.fetchone()
            return int(remaining[0]) if remaining else 0
        except Exception as e:
            print(f"Error al obtener cupos: {e}")
            return -1
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
            return {"message": "Cupo registrado"} if cursor.rowcount > 0 else {"error": "No hay cupos disponibles"}
        except Exception as e:
            return {"error": f"Error al actualizar: {e}"}
        finally:
            if conn.is_connected():
                conn.close()

    def reset_slots(self, new_value=100):
        conn = self.db.connect_db()
        if not conn:
            return {"error": "Error de conexión"}
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quota (id, remaining) 
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE remaining = %s
            """, (new_value, new_value))
            conn.commit()
            return {"message": f"Cupos reseteados a {new_value}"}
        except Exception as e:
            return {"error": f"Error al resetear: {e}"}
        finally:
            if conn.is_connected():
                conn.close()

    # Métodos para gestión de contraseñas
    def verify_admin_password(self, password):
        conn = self.db.connect_db()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT password FROM admin_credentials WHERE id=1")
                result = cursor.fetchone()
                if result:
                    stored_password = result[0]
                    return password == stored_password
                else:
                    # If no record exists, use default password
                    return password == "admin123"
            except mysql.connector.Error as err:
                if err.errno == 1146:  # Table doesn't exist
                    return password == "admin123"
                raise
        except Exception as e:
            print(f"Error verificando contraseña: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def update_admin_password(self, new_password):
        conn = self.db.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO admin_credentials (id, password) 
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE password = %s
            """, (new_password, new_password))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizando contraseña: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()