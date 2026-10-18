
# En este archivo se registrarán las extensiones
# compartidas de la aplicación cuando sean necesarias.

import mysql.connector
from backend.app.config import Config


def get_db_connection():
    """Crea y devuelve una conexión nueva a MySQL."""
    return mysql.connector.connect(**Config.DB_CONFIG)
