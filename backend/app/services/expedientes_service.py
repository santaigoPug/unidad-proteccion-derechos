from app.repositories import expedientes_repository as repository
from app.services import personas_service
from app.services.personas_service import PersonaNoEncontrada  
ESTADOS_VALIDOS = (
    "recibido",
    "en revisión",
    "en seguimiento",
    "cerrado",
)

TRANSICIONES_ESTADO = {
    "recibido": "en revisión",
    "en revisión": "en seguimiento",
    "en seguimiento": "cerrado",
    "cerrado": None,
}


class ErrorValidacion(ValueError):
    pass


class ExpedienteNoEncontrado(Exception):
    pass


def validar_transicion_estado(estado_actual, estado_nuevo):
    if estado_actual not in ESTADOS_VALIDOS:
        raise ErrorValidacion(
            f"El expediente tiene un estado no reconocido: {estado_actual}."
        )

    if estado_nuevo not in ESTADOS_VALIDOS:
        raise ErrorValidacion(
            f"El estado solicitado no es válido: {estado_nuevo}."
        )

    siguiente_estado = TRANSICIONES_ESTADO[estado_actual]

    if siguiente_estado is None:
        raise ErrorValidacion(
            "El expediente está cerrado y no puede reabrirse."
        )

    if estado_nuevo != siguiente_estado:
        raise ErrorValidacion(
            f"Transición no permitida. Desde '{estado_actual}' "
            f"solo puedes avanzar a '{siguiente_estado}'."
        )

    return True
def _validar_texto(datos, campo, maximo=None):
    valor = datos.get(campo)

    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(
            f"El campo {campo} es obligatorio y debe ser texto."
        )

    valor = valor.strip()

    if maximo is not None and len(valor) > maximo:
        raise ErrorValidacion(
            f"El campo {campo} no puede superar "
            f"{maximo} caracteres."
        )

    return valor


def listar_expedientes():
    return repository.listar_expedientes()


def obtener_expediente(id_expediente):
    expediente = repository.obtener_expediente(id_expediente)

    if not expediente:
        raise ExpedienteNoEncontrado(
            "El expediente solicitado no existe."
        )

    if expediente.get("fecha_apertura"):
        expediente["fecha_apertura"] = (
            expediente["fecha_apertura"].isoformat(sep=" ")
        )

    return expediente


def crear_expediente(datos, id_responsable):
    if not isinstance(datos, dict):
        raise ErrorValidacion(
            "Debes enviar un objeto JSON válido."
        )

    motivo = _validar_texto(
        datos,
        "motivo_atencion",
        maximo=255,
    )

    descripcion = _validar_texto(
        datos,
        "descripcion",
    )

    if not isinstance(id_responsable, int) or id_responsable <= 0:
        raise ErrorValidacion(
            "No se pudo identificar al usuario responsable."
        )

    expediente = repository.crear_expediente(
        motivo_atencion=motivo,
        descripcion=descripcion,
        id_responsable=id_responsable,
    )

    return expediente
def listar_personas_para_expediente(busqueda=""):
    if not isinstance(busqueda, str):
        raise ErrorValidacion(
            "El parámetro de búsqueda debe ser texto."
        )

    busqueda = busqueda.strip().casefold()

    personas = personas_service.listar_personas()
    resultado = []

    for persona in personas:
        nombre = persona["nombre_completo"]
        municipio = persona.get("nombre_municipio") or ""

        if busqueda and (
            busqueda not in nombre.casefold()
            and busqueda not in municipio.casefold()
        ):
            continue

        resultado.append({
            "id_persona": persona["id_persona"],
            "nombre_completo": nombre,
            "f_nacimiento": persona["f_nacimiento"],
            "nombre_municipio": municipio,
        })
    return resultado



def vincular_persona_a_expediente(
    id_expediente,
    id_persona,
    rol_en_caso,
):
    # Validar el rol.
    if not isinstance(rol_en_caso, str) or not rol_en_caso.strip():
        raise ErrorValidacion("El rol en el caso es obligatorio.")

    rol_en_caso = rol_en_caso.strip()

    if len(rol_en_caso) > 100:
        raise ErrorValidacion(
            "El rol en el caso no puede superar los 100 caracteres."
        )

    # Validar los identificadores.
    try:
        id_expediente = int(id_expediente)
        id_persona = int(id_persona)
    except (TypeError, ValueError):
        raise ErrorValidacion(
            "Los identificadores deben ser números enteros."
        )

    if id_expediente <= 0 or id_persona <= 0:
        raise ErrorValidacion(
            "Los identificadores deben ser mayores que cero."
        )

    # Comprobar que el expediente existe.
    expediente = repository.obtener_expediente(id_expediente)

    if not expediente:
        raise ExpedienteNoEncontrado("El expediente no existe.")

    # Comprobar que la persona existe.
    try:
        personas_service.obtener_persona(id_persona)
    except PersonaNoEncontrada as error:
        raise ErrorValidacion("La persona no existe.") from error

    # Guardar la relación.
    try:
        repository.vincular_persona(
            id_expediente,
            id_persona,
            rol_en_caso,
        )
    except Exception as error:
        raise ErrorValidacion(
            "No fue posible vincular la persona. "
            "Puede que ya esté vinculada a este expediente."
        ) from error

    return {
        "id_expediente": id_expediente,
        "id_persona": id_persona,
        "rol_en_caso": rol_en_caso,
    }

def listar_personas_vinculadas(id_expediente):
    try:
        id_expediente = int(id_expediente)
    except (TypeError, ValueError):
        raise ErrorValidacion(
            "El identificador del expediente debe ser un entero."
        )

    if id_expediente <= 0:
        raise ErrorValidacion(
            "El identificador del expediente debe ser mayor que cero."
        )

    expediente = repository.obtener_expediente(id_expediente)

    if not expediente:
        raise ExpedienteNoEncontrado("El expediente no existe.")

    relaciones = repository.listar_personas_de_expediente(
        id_expediente
    )

    personas = []

    for relacion in relaciones:
        try:
            persona = personas_service.obtener_persona(
                relacion["id_persona"]
            )
        except PersonaNoEncontrada:
            continue

        personas.append({
            "id_persona": persona["id_persona"],
            "nombre_completo": persona["nombre_completo"],
            "f_nacimiento": persona["f_nacimiento"],
            "nombre_municipio": persona.get("nombre_municipio"),
            "rol_en_caso": relacion["rol_en_caso"],
        })

    return personas

def cambiar_estado_expediente(
    id_expediente,
    id_usuario,
    estado_nuevo,
    descripcion,
):
    if not isinstance(descripcion, str) or not descripcion.strip():
        raise ErrorValidacion(
            "La descripción del cambio de estado es obligatoria."
        )

    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ErrorValidacion(
            "No se pudo identificar al usuario responsable."
        )

    expediente = obtener_expediente(id_expediente)
    estado_actual = expediente["estado"]

    validar_transicion_estado(estado_actual, estado_nuevo)

    return repository.cambiar_estado_expediente(
        id_expediente=id_expediente,
        id_usuario=id_usuario,
        estado_nuevo=estado_nuevo,
        descripcion=descripcion.strip(),
        estado_esperado=estado_actual,
    )

def listar_historial_expediente(id_expediente):
    expediente = obtener_expediente(id_expediente)

    return repository.listar_historial_expediente(
        id_expediente
    )

