
from werkzeug.security import generate_password_hash
from backend.app.db import get_db_connection

USERNAME = "admin"
PASSWORD = "Admin123"

def crear_usuario():
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id_user FROM Usuarios WHERE username = %s",
            (USERNAME,)
        )

        if cursor.fetchone():
            print("El usuario de prueba ya existe.")
            return

        password_hash = generate_password_hash(PASSWORD)

        consulta = """
            INSERT INTO Usuarios (username, password, estado)
            VALUES (%s, %s, TRUE)
        """

        cursor.execute(consulta, (USERNAME, password_hash))
        conexion.commit()

        print("Usuario de prueba creado correctamente.")
        print("Usuario: admin")
        print("Contraseña: Admin123")

    except Exception as error:
        if conexion:
            conexion.rollback()
        print("No se pudo crear el usuario:", error)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

if __name__ == "__main__":
    crear_usuario()
