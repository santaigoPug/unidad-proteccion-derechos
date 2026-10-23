from flask import Blueprint, jsonify, request
from mysql.connector import IntegrityError

from app.common.decorators import login_required
from app.services import personas_service as service


personas_bp = Blueprint("personas", __name__)


@personas_bp.route("/api/personas", methods=["POST"])
@login_required
def crear_persona():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "message": "Debes enviar un objeto JSON válido."
        }), 400

    try:
        persona = service.crear_persona(datos)

        return jsonify({
            "message": "Persona registrada correctamente.",
            "persona": persona,
        }), 201

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except service.IdentidadDuplicada as error:
        return jsonify({"message": str(error)}), 409

    except IntegrityError:
        return jsonify({
            "message": "No se pudo guardar la persona. "
                       "Verifica que el CURP no esté duplicado "
                       "y que el municipio sea válido."
        }), 409

    except Exception:
        from flask import current_app

        current_app.logger.exception(
            "Error al registrar una persona."
        )

        return jsonify({
            "message": "Ocurrió un error al registrar la persona."
        }), 500


@personas_bp.route("/api/personas", methods=["GET"])
@login_required
def listar_personas():
    busqueda = request.args.get("q", "")

    try:
        personas = service.listar_personas(busqueda)

        return jsonify({
            "personas": personas,
            "total": len(personas),
        }), 200

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        from flask import current_app

        current_app.logger.exception(
            "Error al consultar personas."
        )

        return jsonify({
            "message": "No fue posible consultar las personas."
        }), 500


@personas_bp.route(
    "/api/personas/<int:id_persona>",
    methods=["GET"],
)
@login_required
def obtener_persona(id_persona):
    try:
        persona = service.obtener_persona(id_persona)

        return jsonify({"persona": persona}), 200

    except service.PersonaNoEncontrada as error:
        return jsonify({"message": str(error)}), 404

    except Exception:
        from flask import current_app

        current_app.logger.exception(
            "Error al consultar una persona."
        )

        return jsonify({
            "message": "No fue posible consultar la persona."
        }), 500


@personas_bp.route(
    "/api/personas/<int:id_persona>",
    methods=["PUT"],
)
@login_required
def actualizar_persona(id_persona):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "message": "Debes enviar un objeto JSON válido."
        }), 400

    try:
        persona = service.actualizar_persona(
            id_persona,
            datos,
        )

        return jsonify({
            "message": "Persona actualizada correctamente.",
            "persona": persona,
        }), 200

    except service.ErrorValidacion as error:
        return jsonify({"message": str(error)}), 400

    except service.PersonaNoEncontrada as error:
        return jsonify({"message": str(error)}), 404

    except service.IdentidadDuplicada as error:
        return jsonify({"message": str(error)}), 409

    except IntegrityError:
        return jsonify({
            "message": "No se pudo actualizar la persona. "
                       "Verifica el CURP y el municipio."
        }), 409

    except Exception:
        from flask import current_app

        current_app.logger.exception(
            "Error al actualizar una persona."
        )

        return jsonify({
            "message": "No fue posible actualizar la persona."
        }), 500