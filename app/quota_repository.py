import time
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

    def delete_url(self, url_name):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 1. Eliminar primero de url_quotas (por la foreign key)
            cursor.execute("DELETE FROM url_quotas WHERE url_name = %s", (url_name,))
            
            # 2. Luego eliminar de app_urls
            cursor.execute("DELETE FROM app_urls WHERE name = %s", (url_name,))
            
            conn.commit()
            return cursor.rowcount > 0  # True si se eliminó algún registro
            
        except mysql.connector.Error as err:
            print(f"Error deleting URL: {err}")
            conn.rollback()
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


    def get_url_quota(self, url_name):
        conn = self.db.connect_db()
        if not conn:
            return {"remaining_quota": 0, "max_quota": 0}
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT remaining_quota, max_quota 
                FROM url_quotas 
                WHERE url_name = %s
            """, (url_name,))
            result = cursor.fetchone()
            
            # Si no existe el registro, lo creamos con valores por defecto
            if not result:
                cursor.execute("""
                    INSERT INTO url_quotas (url_name, url_path, max_quota, remaining_quota)
                    VALUES (%s, (SELECT url FROM app_urls WHERE name = %s), 100, 100)
                    ON DUPLICATE KEY UPDATE 
                        max_quota = IF(remaining_quota <= 0, 100, max_quota),
                        remaining_quota = IF(remaining_quota <= 0, 100, remaining_quota)
                """, (url_name, url_name))
                conn.commit()
                return {"remaining_quota": 100, "max_quota": 100}
                
            return result
        except Exception as e:
            print(f"Error getting URL quota: {e}")
            return {"remaining_quota": 100, "max_quota": 100}  # Fallback seguro
        finally:
            if conn.is_connected():
                conn.close()

    def decrement_url_quota(self, url_name):
        conn = self.db.connect_db()
        if not conn:
            return {"error": "Database error"}
            
        try:
            cursor = conn.cursor()
            # Verificamos primero si hay cupos
            cursor.execute("""
                SELECT remaining_quota FROM url_quotas 
                WHERE url_name = %s FOR UPDATE
            """, (url_name,))
            result = cursor.fetchone()
            
            if not result or result[0] <= 0:
                return {"error": "No hay cupos disponibles"}
            
            # Actualizamos
            cursor.execute("""
                UPDATE url_quotas 
                SET remaining_quota = remaining_quota - 1 
                WHERE url_name = %s
            """, (url_name,))
            conn.commit()
            return {"success": True, "remaining": result[0] - 1}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            if conn.is_connected():
                conn.close()

    def reset_url_quota(self, url_name, new_quota=100):
        conn = self.db.connect_db()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE url_quotas 
                SET remaining_quota = %s,
                    max_quota = %s,
                    last_reset = CURRENT_TIMESTAMP
                WHERE url_name = %s
            """, (new_quota, new_quota, url_name))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error resetting quota: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def get_all_quotas(self):
        conn = self.db.connect_db()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT url_name, remaining_quota, max_quota FROM url_quotas")
            return {item['url_name']: item for item in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting quotas: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()
                
    def record_failed_attempt(self, ip_address):
        """Registra un intento fallido desde una IP"""
        conn = self.db.connect_db()
        if not conn:
            return 0
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Obtener el estado actual de la IP
            cursor.execute("""
                SELECT attempts, blocked_until 
                FROM failed_logins 
                WHERE ip_address = %s
                FOR UPDATE
            """, (ip_address,))
            result = cursor.fetchone()
            
            # 2. Si no existe registro o el bloqueo expiró, reiniciar contador
            if not result or (result['blocked_until'] and result['blocked_until'] < time.strftime('%Y-%m-%d %H:%M:%S')):
                cursor.execute("""
                    INSERT INTO failed_logins (ip_address, attempts, last_attempt, blocked_until)
                    VALUES (%s, 1, NOW(), NULL)
                    ON DUPLICATE KEY UPDATE 
                        attempts = 1,
                        blocked_until = NULL,
                        last_attempt = NOW()
                """, (ip_address,))
                attempts = 1
            else:
                # 3. Incrementar intentos si no está bloqueado
                if not result['blocked_until']:
                    attempts = result['attempts'] + 1
                    cursor.execute("""
                        UPDATE failed_logins 
                        SET attempts = %s,
                            last_attempt = NOW()
                        WHERE ip_address = %s
                    """, (attempts, ip_address))
                else:
                    attempts = result['attempts']
            
            # 4. Bloquear si alcanza 3 intentos
            if attempts >= 3:
                cursor.execute("""
                    UPDATE failed_logins
                    SET blocked_until = DATE_ADD(NOW(), INTERVAL 3 MINUTE)
                    WHERE ip_address = %s
                """, (ip_address,))
                print(f"🚨 [BLOQUEO] IP {ip_address} bloqueada por 3 minutos")
            
            conn.commit()
            return attempts
        except Exception as e:
            print(f"Error recording failed attempt: {e}")
            conn.rollback()
            return 0
        finally:
            if conn.is_connected():
                conn.close()

    def is_ip_blocked(self, ip_address):
        """Verifica si una IP está bloqueada"""
        conn = self.db.connect_db()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            
            # Primero limpiar bloqueos expirados
            cursor.execute("""
                UPDATE failed_logins 
                SET attempts = 0, 
                    blocked_until = NULL 
                WHERE ip_address = %s 
                AND blocked_until IS NOT NULL 
                AND blocked_until < NOW()
            """, (ip_address,))
            conn.commit()
            
            # Luego verificar si está bloqueado
            cursor.execute("""
                SELECT blocked_until FROM failed_logins 
                WHERE ip_address = %s 
                AND blocked_until IS NOT NULL
                AND blocked_until > NOW()
            """, (ip_address,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error checking blocked IP: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()