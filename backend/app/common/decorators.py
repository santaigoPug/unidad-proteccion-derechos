from functools import wraps

from flask import jsonify, session


def login_required(view):
    """Devuelve 401 si no hay una sesión iniciada."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "id_user" not in session:
            return jsonify({"message": "Debes iniciar sesión."}), 401
        return view(*args, **kwargs)
    return wrapped


def role_required(rol):
    """Devuelve 401 sin sesión y 403 si el rol no coincide."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "id_user" not in session:
                return jsonify({"message": "Debes iniciar sesión."}), 401
            if session.get("rol") != rol:
                return jsonify({
                    "message": "No tienes permisos para realizar esta acción."
                }), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator