
from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from app.db import get_db_connection


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}

    username = datos.get("username")
    password = datos.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "message": "Debes proporcionar usuario y contraseña."
        }), 400

    username = username.strip()

    if not username or not password:
        return jsonify({
            "message": "Debes proporcionar usuario y contraseña."
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                u.id_user,
                u.username,
                u.password,
                u.estado,
                r.nombre_rol
            FROM Usuarios AS u
            INNER JOIN Roles AS r
                ON r.id_rol = u.id_rol
            WHERE u.username = %s
            LIMIT 1
        """

        cursor.execute(consulta, (username,))
        usuario = cursor.fetchone()

        if (
            not usuario
            or not usuario["estado"]
            or not check_password_hash(usuario["password"], password)
        ):
            return jsonify({
                "message": "Usuario o contraseña incorrectos."
            }), 401

        session.clear()
        session["id_user"] = usuario["id_user"]
        session["username"] = usuario["username"]
        session["rol"] = usuario["nombre_rol"]

        return jsonify({
            "message": "Inicio de sesión correcto.",
            "usuario": {
                "id_user": usuario["id_user"],
                "username": usuario["username"],
                "rol": usuario["nombre_rol"],
            },
        }), 200

    except Exception:
        from flask import current_app
        current_app.logger.exception(
            "Error durante el inicio de sesión."
        )

        return jsonify({
            "message": "Ocurrió un error al consultar la base de datos."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


@auth_bp.route("/api/me", methods=["GET"])
def obtener_sesion():
    if "id_user" not in session:
        return jsonify({
            "message": "No hay una sesión activa."
        }), 401

    return jsonify({
        "usuario": {
            "id_user": session["id_user"],
            "username": session["username"],
            "rol": session["rol"],
        }
    }), 200


@auth_bp.route("/api/logout", methods=["POST"])
def cerrar_sesion():
    session.clear()

    return jsonify({
        "message": "Sesión cerrada correctamente."
    }), 200
