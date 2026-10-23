from app.db import get_db_connection


def obtener_municipios():
    """Obtiene los municipios registrados en la base de datos."""
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                id_municipio,
                nombre_municipio,
                departamento_estado
            FROM Municipios
            ORDER BY nombre_municipio ASC
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()