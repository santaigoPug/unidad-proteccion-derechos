
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv(
            "DB_NAME",
            "unidad_proteccion_derechos"
        ),
        "user": os.getenv("DB_USER", "app_user"),
        "password": os.getenv("DB_PASSWORD", ""),

    }
    SECRET_KEY = os.getenv("SECRET_KEY")

  