from connection_db import ConnectionDB
import mysql.connector

class QuotaRepository:
    def __init__(self):
        self.db = ConnectionDB()

    def _initialize_database(self):
        """Inicializa las tablas necesarias si no existen"""
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            # Tabla de cupos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quota (
                    id INT PRIMARY KEY,
                    remaining INT
                )
            """)
            # Tabla de URLs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_urls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE,
                    url VARCHAR(512)
                )
            """)
            # Tabla de credenciales admin
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_credentials (
                    id INT PRIMARY KEY,
                    password VARCHAR(255)
                )
            """)
            # Insertar datos iniciales si no existen
            cursor.execute("""
                INSERT IGNORE INTO quota (id, remaining)
                VALUES (1, 100)
            """)
            cursor.execute("""
                INSERT IGNORE INTO admin_credentials (id, password)
                VALUES (1, 'admin123')
            """)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    # ========== MÉTODOS DE GESTIÓN DE CUPOS ==========
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
            cursor.execute("""
                UPDATE quota 
                SET remaining = GREATEST(0, remaining - 1) 
                WHERE id=1
            """)
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
            print(f"Error resetting slots: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    # ========== MÉTODOS DE ADMINISTRACIÓN ==========
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
                self._initialize_database()
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
                INSERT INTO admin_credentials (id, password)
                VALUES (1, %s)
                ON DUPLICATE KEY UPDATE password = %s
            """, (new_password, new_password))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    # ========== MÉTODOS DE GESTIÓN DE URLs ==========
    def save_url(self, name, url):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            # Asegurar que la tabla existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_urls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE,
                    url VARCHAR(512))
            """)
            # Insertar/actualizar URL
            cursor.execute("""
                INSERT INTO app_urls (name, url)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE url = VALUES(url)
            """, (name, url))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving URL: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def delete_url(self, name):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM app_urls WHERE name = %s", (name,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting URL: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def get_all_urls(self):
        conn = self.db.connect_db()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, url FROM app_urls")
            return {item['name']: item['url'] for item in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting URLs: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def update_url(self, old_name, new_name, new_url):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE app_urls 
                SET name = %s, url = %s 
                WHERE name = %s
            """, (new_name, new_url, old_name))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error updating URL: {err}")
            return False
        finally:
            if conn.is_connected():
                conn.close()