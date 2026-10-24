from datetime import datetime
from app.db import get_db_connection


def listar_expedientes():
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id_expediente,
                e.codigo_unico,
                e.fecha_apertura,
                e.motivo_atencion,
                e.descripcion,
                e.estado,
                e.id_responsable,
                u.username AS responsable
            FROM expedientes AS e
            LEFT JOIN usuarios AS u
                ON u.id_user = e.id_responsable
            ORDER BY e.fecha_apertura DESC,
                     e.id_expediente DESC
        """)

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def obtener_expediente(id_expediente):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id_expediente,
                e.codigo_unico,
                e.fecha_apertura,
                e.motivo_atencion,
                e.descripcion,
                e.estado,
                e.id_responsable,
                u.username AS responsable
            FROM expedientes AS e
            LEFT JOIN usuarios AS u
                ON u.id_user = e.id_responsable
            WHERE e.id_expediente = %s
            LIMIT 1
        """, (id_expediente,))

        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def crear_expediente(
    motivo_atencion,
    descripcion,
    id_responsable,
):
    conexion = get_db_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        # Bloquea la fila del año durante la asignación del folio.
        anio = datetime.now().year
        cursor.execute("""
            INSERT INTO contadores_folio (anio, ultimo_numero)
            VALUES (%s, 0)
            ON DUPLICATE KEY UPDATE anio = VALUES(anio)
        """, (anio,))

        cursor.execute("""
            SELECT ultimo_numero
            FROM contadores_folio
            WHERE anio = %s
            FOR UPDATE
        """, (anio,))

        contador = cursor.fetchone()
        siguiente = contador["ultimo_numero"] + 1

        cursor.execute("""
            UPDATE contadores_folio
            SET ultimo_numero = %s
            WHERE anio = %s
        """, (siguiente, anio))

        codigo_unico = f"DIF-{anio}-{siguiente:04d}"

        cursor.execute("""
            INSERT INTO expedientes (
                codigo_unico,
                motivo_atencion,
                descripcion,
                estado,
                id_responsable
            )
            VALUES (%s, %s, %s, 'recibido', %s)
        """, (
            codigo_unico,
            motivo_atencion,
            descripcion,
            id_responsable,
        ))

        id_expediente = cursor.lastrowid
        conexion.commit()

        return {
            "id_expediente": id_expediente,
            "codigo_unico": codigo_unico,
            "estado": "recibido",
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

def vincular_persona(id_expediente, id_persona, rol_en_caso):
    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO expediente_persona (
                id_expediente,
                id_persona,
                rol_en_caso
            )
            VALUES (%s, %s, %s)
            """,
            (id_expediente, id_persona, rol_en_caso),
        )

        conexion.commit()
        return True

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()

def listar_personas_de_expediente(id_expediente):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id_persona, rol_en_caso
            FROM expediente_persona
            WHERE id_expediente = %s
            ORDER BY id_persona
            """,
            (id_expediente,),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()

