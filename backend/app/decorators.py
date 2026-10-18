from functools import wraps

from flask import jsonify, session


def login_required(view):
    """Requiere una sesión autenticada para ejecutar la vista."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "id_user" not in session:
            return jsonify({"message": "Debes iniciar sesión."}), 401
        return view(*args, **kwargs)
    return wrapped


def role_required(rol):
    """Restringe una vista al rol indicado y exige una sesión válida."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "id_user" not in session:
                return jsonify({"message": "Debes iniciar sesión."}), 401
            if session.get("rol") != rol:
                return jsonify({"message": "No tienes permisos para realizar esta acción."}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator
