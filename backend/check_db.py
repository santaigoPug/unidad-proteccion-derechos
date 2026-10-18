
from backend.app.db import get_db_connection
import mysql.connector


conexion = None

try:
    conexion = get_db_connection()

    cursor = conexion.cursor()
    cursor.execute("SELECT DATABASE()")

    resultado = cursor.fetchone()
    print("Conexión correcta.")
    print("Base de datos:", resultado[0])

    cursor.close()

except mysql.connector.Error as error:
    print("Error de MySQL:", error)

finally:
    if conexion is not None and conexion.is_connected():
        conexion.close()
        print("Conexión cerrada.")
