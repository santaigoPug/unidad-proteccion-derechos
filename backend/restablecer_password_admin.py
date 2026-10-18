
from werkzeug.security import generate_password_hash
from app.extensions import get_db_connection


def restablecer_password():
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        password_hash = generate_password_hash("tres rosasss")

        consulta = """
            UPDATE Usuarios
            SET password = %s, estado = TRUE
            WHERE username = %s
        """

        cursor.execute(consulta, (password_hash, "santi"))
        conexion.commit()

        if cursor.rowcount > 0:
            print("Contraseña de prueba actualizada correctamente.")
            print("Usuario: admin")
            print("Contraseña: Admin123")
        else:
            print("No se encontró el usuario admin.")

    except Exception as error:
        if conexion:
            conexion.rollback()
        print("Error al actualizar la contraseña:", error)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


if __name__ == "__main__":
    restablecer_password()
