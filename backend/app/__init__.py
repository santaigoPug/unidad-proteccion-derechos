
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.routes.auth_routes import auth_bp
from app.routes.usuarios_routes import usuarios_bp
from app.routes.personas_routes import personas_bp
from app.routes.expedientes_routes import expedientes_bp
from app.routes.municipios_routes import municipios_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                ]
            }
        },
        supports_credentials=True,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(expedientes_bp)
    app.register_blueprint(municipios_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "message": "La aplicación Flask está funcionando",
        }), 200

    return app
