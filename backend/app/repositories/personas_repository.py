from app.db import get_db_connection


def listar_personas():
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                p.id_persona,
                p.f_nacimiento,
                p.id_municipio,
                p.datos_cifrados,
                p.hash_identidad,
                m.nombre_municipio
            FROM Personas AS p
            LEFT JOIN Municipios AS m
                ON m.id_municipio = p.id_municipio
            ORDER BY p.id_persona DESC
            """
        )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


def obtener_persona(id_persona):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                p.id_persona,
                p.f_nacimiento,
                p.id_municipio,
                p.datos_cifrados,
                p.hash_identidad,
                m.nombre_municipio
            FROM Personas AS p
            LEFT JOIN Municipios AS m
                ON m.id_municipio = p.id_municipio
            WHERE p.id_persona = %s
            LIMIT 1
            """,
            (id_persona,),
        )

        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


def obtener_por_hash(hash_identidad, excluir_id=None):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT id_persona
            FROM Personas
            WHERE hash_identidad = %s
        """
        parametros = [hash_identidad]

        if excluir_id is not None:
            consulta += " AND id_persona <> %s"
            parametros.append(excluir_id)

        consulta += " LIMIT 1"

        cursor.execute(consulta, tuple(parametros))

        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


def municipio_existe(id_municipio):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id_municipio
            FROM Municipios
            WHERE id_municipio = %s
            LIMIT 1
            """,
            (id_municipio,),
        )

        return cursor.fetchone() is not None

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


def crear_persona(
    f_nacimiento,
    id_municipio,
    datos_cifrados,
    hash_identidad,
):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO Personas (
                f_nacimiento,
                id_municipio,
                datos_cifrados,
                hash_identidad
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                f_nacimiento,
                id_municipio,
                datos_cifrados,
                hash_identidad,
            ),
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


def actualizar_persona(
    id_persona,
    f_nacimiento,
    id_municipio,
    datos_cifrados,
    hash_identidad,
):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE Personas
            SET
                f_nacimiento = %s,
                id_municipio = %s,
                datos_cifrados = %s,
                hash_identidad = %s
            WHERE id_persona = %s
            """,
            (
                f_nacimiento,
                id_municipio,
                datos_cifrados,
                hash_identidad,
                id_persona,
            ),
        )

        conexion.commit()

        return cursor.rowcount

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()