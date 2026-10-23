import hashlib
import json
import re
from datetime import date

from cryptography.fernet import Fernet, InvalidToken

from app.config import Config
from app.repositories import personas_repository as repository


class ErrorValidacion(ValueError):
    pass


class PersonaNoEncontrada(Exception):
    pass


class IdentidadDuplicada(Exception):
    pass


def _fernet():
    clave = Config.ENCRYPTION_KEY

    if not clave:
        raise RuntimeError(
            "No está configurada la variable ENCRYPTION_KEY."
        )

    try:
        return Fernet(clave.encode("utf-8"))
    except (ValueError, TypeError):
        raise RuntimeError(
            "ENCRYPTION_KEY no contiene una clave Fernet válida."
        )


def _normalizar_curp(curp):
    if not isinstance(curp, str):
        raise ErrorValidacion("El CURP es obligatorio.")

    curp = curp.strip().upper()

    if not re.fullmatch(r"[A-Z0-9]{18}", curp):
        raise ErrorValidacion(
            "El CURP debe contener exactamente 18 caracteres "
            "alfanuméricos."
        )

    return curp


def _validar_texto(datos, campo, obligatorio=True):
    valor = datos.get(campo)

    if valor is None:
        if obligatorio:
            raise ErrorValidacion(
                f"El campo {campo} es obligatorio."
            )

        return ""

    if not isinstance(valor, str):
        raise ErrorValidacion(
            f"El campo {campo} debe ser texto."
        )

    valor = valor.strip()

    if obligatorio and not valor:
        raise ErrorValidacion(
            f"El campo {campo} es obligatorio."
        )

    return valor


def _normalizar_fecha(valor):
    if valor in (None, ""):
        return None

    if not isinstance(valor, str):
        raise ErrorValidacion(
            "La fecha de nacimiento debe usar el formato YYYY-MM-DD."
        )

    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ErrorValidacion(
            "La fecha de nacimiento no es válida. "
            "Usa el formato YYYY-MM-DD."
        )


def _normalizar_municipio(valor):
    if valor in (None, ""):
        return None

    if isinstance(valor, bool):
        raise ErrorValidacion("El municipio no es válido.")

    try:
        municipio = int(valor)
    except (ValueError, TypeError):
        raise ErrorValidacion(
            "id_municipio debe ser un identificador numérico."
        )

    if municipio <= 0:
        raise ErrorValidacion("El municipio no es válido.")

    if not repository.municipio_existe(municipio):
        raise ErrorValidacion(
            "El municipio seleccionado no existe."
        )

    return municipio


def _cifrar_datos(datos_sensibles):
    contenido = json.dumps(
        datos_sensibles,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    return _fernet().encrypt(contenido).decode("utf-8")


def _descifrar_datos(datos_cifrados):
    try:
        contenido = _fernet().decrypt(
            datos_cifrados.encode("utf-8")
        )

        datos = json.loads(contenido.decode("utf-8"))

    except (InvalidToken, ValueError, TypeError, UnicodeDecodeError):
        raise RuntimeError(
            "No fue posible descifrar los datos de una persona."
        )

    if not isinstance(datos, dict):
        raise RuntimeError(
            "Los datos cifrados de una persona no tienen un formato válido."
        )

    return datos


def _preparar_datos(datos):
    if not isinstance(datos, dict):
        raise ErrorValidacion(
            "El cuerpo de la solicitud debe ser un objeto JSON."
        )

    nombre = _validar_texto(datos, "nombre_completo")
    curp = _normalizar_curp(datos.get("curp"))
    telefono = _validar_texto(datos, "telefono")
    direccion = _validar_texto(datos, "direccion")

    if len(nombre) > 200:
        raise ErrorValidacion(
            "El nombre completo no puede superar 200 caracteres."
        )

    if len(telefono) > 30:
        raise ErrorValidacion(
            "El teléfono no puede superar 30 caracteres."
        )

    if len(direccion) > 1000:
        raise ErrorValidacion(
            "La dirección no puede superar 1000 caracteres."
        )

    f_nacimiento = _normalizar_fecha(
        datos.get("f_nacimiento")
    )

    id_municipio = _normalizar_municipio(
        datos.get("id_municipio")
    )

    hoy = date.today()

    if f_nacimiento and f_nacimiento > hoy:
        raise ErrorValidacion(
            "La fecha de nacimiento no puede estar en el futuro."
        )

    datos_sensibles = {
        "nombre_completo": nombre,
        "curp": curp,
        "telefono": telefono,
        "direccion": direccion,
    }

    hash_identidad = hashlib.sha256(
        curp.encode("utf-8")
    ).hexdigest()

    datos_cifrados = _cifrar_datos(datos_sensibles)

    return {
        "f_nacimiento": f_nacimiento,
        "id_municipio": id_municipio,
        "datos_cifrados": datos_cifrados,
        "hash_identidad": hash_identidad,
    }


def _serializar_persona(registro):
    datos_sensibles = _descifrar_datos(
        registro["datos_cifrados"]
    )

    f_nacimiento = registro["f_nacimiento"]

    return {
        "id_persona": registro["id_persona"],
        "nombre_completo": datos_sensibles["nombre_completo"],
        "curp": datos_sensibles["curp"],
        "telefono": datos_sensibles["telefono"],
        "direccion": datos_sensibles["direccion"],
        "f_nacimiento": (
            f_nacimiento.isoformat()
            if f_nacimiento
            else None
        ),
        "id_municipio": registro["id_municipio"],
        "nombre_municipio": registro["nombre_municipio"],
    }


def crear_persona(datos):
    persona = _preparar_datos(datos)

    existente = repository.obtener_por_hash(
        persona["hash_identidad"]
    )

    if existente:
        raise IdentidadDuplicada(
            "Ya existe una persona registrada con ese CURP."
        )

    id_persona = repository.crear_persona(**persona)

    registro = repository.obtener_persona(id_persona)

    return _serializar_persona(registro)


def listar_personas(busqueda=""):
    if not isinstance(busqueda, str):
        raise ErrorValidacion(
            "El parámetro de búsqueda debe ser texto."
        )

    busqueda = busqueda.strip().casefold()

    registros = repository.listar_personas()
    personas = []

    for registro in registros:
        persona = _serializar_persona(registro)

        if not busqueda:
            personas.append(persona)
            continue

        valores = (
            persona["nombre_completo"],
            persona["curp"],
            persona["telefono"],
            persona["direccion"],
            persona["nombre_municipio"] or "",
        )

        if any(
            busqueda in valor.casefold()
            for valor in valores
        ):
            personas.append(persona)

    return personas


def obtener_persona(id_persona):
    registro = repository.obtener_persona(id_persona)

    if not registro:
        raise PersonaNoEncontrada(
            "La persona solicitada no existe."
        )

    return _serializar_persona(registro)


def actualizar_persona(id_persona, datos):
    actual = repository.obtener_persona(id_persona)

    if not actual:
        raise PersonaNoEncontrada(
            "La persona solicitada no existe."
        )

    persona = _preparar_datos(datos)

    existente = repository.obtener_por_hash(
        persona["hash_identidad"],
        excluir_id=id_persona,
    )

    if existente:
        raise IdentidadDuplicada(
            "Otra persona ya está registrada con ese CURP."
        )

    repository.actualizar_persona(
        id_persona=id_persona,
        **persona,
    )

    registro = repository.obtener_persona(id_persona)

    return _serializar_persona(registro)