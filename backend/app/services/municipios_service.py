from app.repositories.municipios_repository import obtener_municipios


def listar_municipios():
    """Devuelve la lista de municipios disponibles."""
    return obtener_municipios()