from werkzeug.security import generate_password_hash
from flask import Flask, jsonify, request, session
from werkzeug.security import check_password_hash

from app.config import Config
from app.db import get_db_connection
from .common.decorators import role_required
from app.routes.personas_routes import personas_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from app.routes.municipios_routes import municipios_bp

    app.register_blueprint(municipios_bp, url_prefix="/api")

    from flask_cors import CORS

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    #"http://127.0.0.1:5173",
                ]
            }
        },
        supports_credentials=True
    )
    app.register_blueprint(personas_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "message": "La aplicación Flask está funcionando",
        }), 200

    @app.route("/api/login", methods=["POST"])
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
            app.logger.exception("Error durante el inicio de sesión.")

            return jsonify({
                "message": "Ocurrió un error al consultar la base de datos."
            }), 500

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()
    @app.route("/api/me", methods=["GET"])
    def obtener_sesion():
      if "id_user" not in session:
         return jsonify({
             "message": "No hay una sesión activa."}), 401

      return jsonify({
        "usuario": {
            "id_user": session["id_user"],
            "username": session["username"],
            "rol": session["rol"],
        }
        }), 200


    @app.route("/api/logout", methods=["POST"])
    def cerrar_sesion():
       session.clear()

       return jsonify({
         "message": "Sesión cerrada correctamente."}), 200
    
    @app.route("/api/usuarios", methods=["POST"])
    @role_required("Administrador")
    def crear_usuario():

     datos = request.get_json(silent=True) or {}

     username = datos.get("username")
     password = datos.get("password")
     nombre_rol = datos.get("rol")

     if not all(
        isinstance(valor, str)
        for valor in (username, password, nombre_rol)
     ):
        return jsonify({
            "message": "Debes proporcionar usuario, contraseña y rol."
        }), 400

     username = username.strip()
     nombre_rol = nombre_rol.strip()

     if not username or not password or not nombre_rol:
        return jsonify({
            "message": "Todos los campos son obligatorios."
        }), 400

     if len(username) > 100:
        return jsonify({
            "message": "El usuario no puede superar los 100 caracteres."
        }), 400

     if len(password) < 8:
        return jsonify({
            "message": "La contraseña debe tener al menos 8 caracteres."
        }), 400

     if nombre_rol not in ("Administrador", "Operador"):
        return jsonify({
            "message": "El rol seleccionado no es válido."
        }), 400

     conexion = None
     cursor = None

     try:
         conexion = get_db_connection()
         cursor = conexion.cursor(dictionary=True)

         cursor.execute(
            "SELECT id_user FROM Usuarios WHERE username = %s",
            (username,)
        )

         if cursor.fetchone():
            return jsonify({
                "message": "Ese nombre de usuario ya está registrado."
            }), 409

         cursor.execute(
            "SELECT id_rol FROM Roles WHERE nombre_rol = %s",
            (nombre_rol,)
         )

         rol = cursor.fetchone()

         if not rol:
            return jsonify({
                "message": "El rol seleccionado no existe en la base de datos."
            }), 400

         password_hash = generate_password_hash(password)

         cursor.execute(
            """
            INSERT INTO Usuarios (username, password, id_rol, estado)
            VALUES (%s, %s, %s, TRUE)
            """,
            (username, password_hash, rol["id_rol"])
        )

         conexion.commit()

         return jsonify({
            "message": "Usuario creado correctamente.",
            "usuario": {
                "id_user": cursor.lastrowid,
                "username": username,
                "rol": nombre_rol,
            }
         }), 201

     except Exception:
         if conexion:
            conexion.rollback()

         app.logger.exception("Error al crear un usuario.")

         return jsonify({
            "message": "Ocurrió un error al registrar el usuario."
         }), 500

     finally:
         if cursor:
            cursor.close()

         if conexion:
            conexion.close()
    

    @app.route("/api/usuarios", methods=["GET"])
    @role_required("Administrador")
    def listar_usuarios():

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    u.id_user,
                    u.username,
                    u.estado,
                    DATE_FORMAT(u.f_creacion, '%Y-%m-%d %H:%i:%s') AS f_creacion,
                    r.nombre_rol AS rol
                FROM Usuarios AS u
                INNER JOIN Roles AS r ON r.id_rol = u.id_rol
                ORDER BY u.id_user DESC
            """)

            usuarios = cursor.fetchall()

            return jsonify({"usuarios": usuarios}), 200

        except Exception:
            app.logger.exception("Error al consultar usuarios.")
            return jsonify({"message": "No fue posible consultar los usuarios."}), 500

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    @app.route("/api/usuarios/<int:id_user>", methods=["PUT"])
    @role_required("Administrador")
    def modificar_usuario(id_user):

        datos = request.get_json(silent=True) or {}
        username = datos.get("username")
        nombre_rol = datos.get("rol")
        estado = datos.get("estado")

        if not isinstance(username, str) or not isinstance(nombre_rol, str):
            return jsonify({"message": "Debes proporcionar usuario y rol."}), 400

        username = username.strip()
        nombre_rol = nombre_rol.strip()

        if not username or len(username) > 100:
            return jsonify({"message": "El usuario es obligatorio y no debe superar 100 caracteres."}), 400

        if nombre_rol not in ("Administrador", "Operador"):
            return jsonify({"message": "El rol seleccionado no es válido."}), 400

        if estado not in (True, False, 0, 1):
            return jsonify({"message": "El estado debe ser activo o inactivo."}), 400

        estado = 1 if estado in (True, 1) else 0

        # Evita que el administrador se quite a sí mismo el acceso.
        if id_user == session.get("id_user"):
            if nombre_rol != "Administrador" or estado != 1:
                return jsonify({
                    "message": "No puedes desactivar tu propia cuenta ni cambiar tu propio rol."
                }), 400

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute(
                "SELECT id_user FROM Usuarios WHERE id_user = %s",
                (id_user,)
            )
            usuario_existente = cursor.fetchone()

            if not usuario_existente:
                return jsonify({"message": "El usuario no existe."}), 404

            cursor.execute(
                """
                SELECT id_user
                FROM Usuarios
                WHERE username = %s AND id_user <> %s
                """,
                (username, id_user)
            )

            if cursor.fetchone():
                return jsonify({
                    "message": "Ese nombre de usuario ya está registrado."
                }), 409

            cursor.execute(
                "SELECT id_rol FROM Roles WHERE nombre_rol = %s",
                (nombre_rol,)
            )
            rol = cursor.fetchone()

            if not rol:
                return jsonify({"message": "El rol seleccionado no existe."}), 400

            cursor.execute(
                """
                UPDATE Usuarios
                SET username = %s, id_rol = %s, estado = %s
                WHERE id_user = %s
                """,
                (username, rol["id_rol"], estado, id_user)
            )

            conexion.commit()

            return jsonify({
                "message": "Usuario actualizado correctamente.",
                "usuario": {
                    "id_user": id_user,
                    "username": username,
                    "rol": nombre_rol,
                    "estado": estado
                }
            }), 200

        except Exception:
            if conexion:
                conexion.rollback()

            app.logger.exception("Error al modificar usuario.")
            return jsonify({"message": "No fue posible modificar el usuario."}), 500

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    return app