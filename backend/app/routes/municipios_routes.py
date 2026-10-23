from flask import Blueprint, jsonify

from app.common.decorators import login_required
from app.services.municipios_service import listar_municipios


municipios_bp = Blueprint("municipios", __name__)


@municipios_bp.route("/municipios", methods=["GET"])
@login_required
def obtener_municipios_route():
    try:
        municipios = listar_municipios()

        return jsonify({
            "municipios": municipios
        }), 200

    except Exception:
        return jsonify({
            "message": "Ocurrió un error al consultar los municipios."
        }), 500