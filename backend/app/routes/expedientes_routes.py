
from re import error

from flask import Blueprint, current_app, jsonify, request
from app.db import get_db_connection
from app.common.decorators import login_required
from app.services import expedientes_service as service
from app.repositories import expedientes_repository as repository

expedientes_bp = Blueprint("expedientes", __name__)


@expedientes_bp.route("/api/expedientes", methods=["GET"])
@login_required
def listar_expedientes():
    try:
        expedientes = service.listar_expedientes()

        # Convertir las fechas para que jsonify pueda serializarlas.
        for expediente in expedientes:
            fecha = expediente.get("fecha_apertura")
            if fecha:
                expediente["fecha_apertura"] = fecha.isoformat(sep=" ")

        return jsonify({
            "expedientes": expedientes,
            "total": len(expedientes),
        }), 200

    except Exception:
        current_app.logger.exception(
            "Error al consultar expedientes."
        )
        return jsonify({
            "message": "No fue posible consultar los expedientes."
        }), 500


@expedientes_bp.route(
    "/api/expedientes/<int:id_expediente>",
    methods=["GET"],
)
@login_required
def obtener_expediente(id_expediente):
    try:
        expediente = service.obtener_expediente(id_expediente)

        return jsonify({
            "expediente": expediente,
        }), 200

    except service.ExpedienteNoEncontrado as error:
        return jsonify({"message": str(error)}), 404

    except Exception:
        current_app.logger.exception(
            "Error al consultar un expediente."
        )
        return jsonify({
            "message": "No fue posible consultar el expediente."
        }), 500


@expedientes_bp.route("/api/expedientes", methods=["POST"])
@login_required
def crear_expediente():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "message": "Debes enviar un objeto JSON válido."
        }), 400

    try:
        id_responsable = session_user_id()
        expediente = service.crear_expediente(
            datos,
            id_responsable,
        )

        return jsonify({
            "message": "Expediente registrado correctamente.",
            "expediente": expediente,
        }), 201

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Error al registrar un expediente."
        )
        return jsonify({
            "message": "No fue posible registrar el expediente."
        }), 500


def session_user_id():
    from flask import session
    return session.get("id_user")
@expedientes_bp.route(
    "/api/expedientes/personas",
    methods=["GET"],
)
@login_required
def listar_personas_para_expediente():
    busqueda = request.args.get("q", "")

    try:
        personas = service.listar_personas_para_expediente(
            busqueda
        )

        return jsonify({
            "personas": personas,
            "total": len(personas),
        }), 200

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Error al consultar personas para expedientes."
        )

        return jsonify({
            "message": "No fue posible consultar las personas."
        }), 500

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

@expedientes_bp.route(
    "/api/expedientes/<int:id_expediente>/personas",
    methods=["POST"],
)
@login_required
def vincular_persona_a_expediente(id_expediente):
    datos = request.get_json(silent=True) or {}

    id_persona = datos.get("id_persona")
    rol_en_caso = datos.get("rol_en_caso")

    try:
        resultado = service.vincular_persona_a_expediente(
            id_expediente,
            id_persona,
            rol_en_caso,
        )

        return jsonify({
            "message": "Persona vinculada al expediente correctamente.",
            "vinculacion": resultado,
        }), 201

    except service.ExpedienteNoEncontrado as error:
        return jsonify({"message": str(error)}), 404

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Error al vincular persona con expediente."
        )
        return jsonify({
            "message": "No fue posible vincular la persona al expediente."
        }), 500

@expedientes_bp.route(
    "/api/expedientes/<int:id_expediente>/personas",
    methods=["GET"],
)
@login_required
def obtener_personas_vinculadas(id_expediente):
    try:
        personas = service.listar_personas_vinculadas(
            id_expediente
        )

        return jsonify({
            "personas": personas,
            "total": len(personas),
        }), 200

    except service.ExpedienteNoEncontrado as error:
        return jsonify({"message": str(error)}), 404

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        current_app.logger.exception(
            "Error al consultar personas vinculadas al expediente."
        )
        return jsonify({
            "message": "No fue posible consultar las personas vinculadas."
        }), 500

@expedientes_bp.route(
    "/api/expedientes/<int:id_expediente>/estado",
    methods=["PATCH"],
)
@login_required
def cambiar_estado_expediente(id_expediente):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "message": "Debes enviar un objeto JSON válido."
        }), 400

    estado_nuevo = datos.get("estado")
    descripcion = datos.get("descripcion")

    try:
        resultado = service.cambiar_estado_expediente(
            id_expediente=id_expediente,
            id_usuario=session_user_id(),
            estado_nuevo=estado_nuevo,
            descripcion=descripcion,
        )

        return jsonify({
            "message": "Estado actualizado correctamente.",
            "expediente": resultado,
        }), 200

    except service.ExpedienteNoEncontrado as error:
        return jsonify({"message": str(error)}), 404

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except repository.ConflictoEstado as error:
        return jsonify({"message": str(error)}), 409

    except LookupError as error:
        return jsonify({"message": str(error)}), 404
    except Exception:
        current_app.logger.exception(
            "Error al cambiar el estado del expediente."
        )
        return jsonify({
            "message": "No fue posible cambiar el estado del expediente."
        }), 500


@expedientes_bp.route(
    "/api/expedientes/<int:id_expediente>/historial",
    methods=["GET"],
)
@login_required
def obtener_historial_expediente(id_expediente):
    try:
        historial = service.listar_historial_expediente(
            id_expediente
        )

        for registro in historial:
            fecha = registro.get("fecha")
            if fecha:
                registro["fecha"] = fecha.isoformat(sep=" ")

        return jsonify({
            "historial": historial,
            "total": len(historial),
        }), 200

    except service.ExpedienteNoEncontrado as error:
        return jsonify({"message": str(error)}), 404

    except Exception:
        current_app.logger.exception(
            "Error al consultar el historial del expediente."
        )
        return jsonify({
            "message": "No fue posible consultar el historial."
        }), 500
