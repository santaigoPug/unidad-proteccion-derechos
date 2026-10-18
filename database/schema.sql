-- =============================================================================
-- BORRADOR DE ESQUEMA SQL
-- Proyecto: Unidad de Protección de Derechos Vulnerados
-- Fuente principal: Proyecto Mau.pdf, diccionario de datos (pp. 21-25)
--
-- IMPORTANTE:
-- 1. Este archivo es un BORRADOR. No ha sido ejecutado en MySQL.
-- 2. Algunos tipos/decisiones se infieren porque el PDF los presenta como
--    sugeridos o ambiguos. Se anotan en comentarios para revisión.
-- 3. Revisar las notas al final antes de utilizar este esquema.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS unidad_proteccion_derechos
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE unidad_proteccion_derechos;

-- -----------------------------------------------------------------------------
-- 1. Roles
-- PDF: id_rol (PK), nombre_rol (UNIQUE), descripcion (VARCHAR/TEXT).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Roles (
    id_rol INT NOT NULL AUTO_INCREMENT,
    nombre_rol VARCHAR(50) NOT NULL,
    descripcion TEXT NULL,
    PRIMARY KEY (id_rol),
    UNIQUE KEY uq_roles_nombre_rol (nombre_rol)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. Usuarios
-- PDF usa el nombre id_user como PK; se conserva para respetar el diccionario.
-- "estado" aparece como VARCHAR/BOOLEAN: aquí se propone BOOLEAN.
-- "password" se conserva como nombre del campo del PDF, pero debe almacenar
-- únicamente un hash seguro de contraseña, nunca texto plano.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Usuarios (
    id_user INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    f_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id_user),
    UNIQUE KEY uq_usuarios_username (username),
    CONSTRAINT fk_usuarios_roles
        FOREIGN KEY (id_rol) REFERENCES Roles (id_rol)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. Municipios
-- El PDF marca departamento_estado como UNIQUE. Se conserva literalmente en
-- este borrador, aunque conviene confirmar si la intención era una restricción
-- UNIQUE compuesta (nombre_municipio, departamento_estado).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Municipios (
    id_municipio INT NOT NULL AUTO_INCREMENT,
    nombre_municipio VARCHAR(100) NOT NULL,
    departamento_estado VARCHAR(100) NULL,
    PRIMARY KEY (id_municipio),
    UNIQUE KEY uq_municipios_departamento_estado (departamento_estado)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. Personas
-- Se omite id_nacimiento provisionalmente, según la decisión del proyecto,
-- hasta confirmar su significado en el documento original.
-- datos_cifrados se mantiene como TEXT conforme al diccionario.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Personas (
    id_persona INT NOT NULL AUTO_INCREMENT,
    f_nacimiento DATE NULL,
    id_municipio INT NULL,
    datos_cifrados TEXT NULL,
    hash_identidad VARCHAR(255) NULL,
    PRIMARY KEY (id_persona),
    UNIQUE KEY uq_personas_hash_identidad (hash_identidad),
    CONSTRAINT fk_personas_municipios
        FOREIGN KEY (id_municipio) REFERENCES Municipios (id_municipio)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. Derechos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Derechos (
    id_derecho INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NULL,
    clasificacion VARCHAR(100) NULL,
    PRIMARY KEY (id_derecho),
    UNIQUE KEY uq_derechos_nombre (nombre)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. Expedientes
-- PDF: id_expediente (PK), codigo_unico (UNIQUE), fecha_apertura,
-- estado e id_responsable (FK a usuario).
--
-- Se agrega seguimiento TEXT como decisión provisional para cumplir la
-- preferencia del proyecto de mantener el seguimiento dentro de Expedientes.
-- El campo no aparece expresamente en la tabla de Expedientes del diccionario.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Expedientes (
    id_expediente INT NOT NULL AUTO_INCREMENT,
    codigo_unico VARCHAR(100) NOT NULL,
    fecha_apertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) NOT NULL,
    id_responsable INT NULL,
    seguimiento TEXT NULL,
    PRIMARY KEY (id_expediente),
    UNIQUE KEY uq_expedientes_codigo_unico (codigo_unico),
    CONSTRAINT fk_expedientes_responsable
        FOREIGN KEY (id_responsable) REFERENCES Usuarios (id_user)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. Expediente_Persona
-- Tabla intermedia con PK compuesta, conforme a los campos marcados PK/FK.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Expediente_Persona (
    id_expediente INT NOT NULL,
    id_persona INT NOT NULL,
    rol_en_caso VARCHAR(100) NULL,
    PRIMARY KEY (id_expediente, id_persona),
    CONSTRAINT fk_expediente_persona_expediente
        FOREIGN KEY (id_expediente) REFERENCES Expedientes (id_expediente)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_expediente_persona_persona
        FOREIGN KEY (id_persona) REFERENCES Personas (id_persona)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. Expediente_Derecho
-- El PDF identifica id_expediente e id_derecho como FK, pero no aclara
-- explícitamente una PK. Se propone una PK compuesta para evitar duplicados
-- del mismo derecho en un mismo expediente.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Expediente_Derecho (
    id_expediente INT NOT NULL,
    id_derecho INT NOT NULL,
    nivel_gravedad VARCHAR(50) NULL,
    observaciones TEXT NULL,
    PRIMARY KEY (id_expediente, id_derecho),
    CONSTRAINT fk_expediente_derecho_expediente
        FOREIGN KEY (id_expediente) REFERENCES Expedientes (id_expediente)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_expediente_derecho_derecho
        FOREIGN KEY (id_derecho) REFERENCES Derechos (id_derecho)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 9. Logs
-- El diccionario usa id_usuario para la FK, mientras que Usuarios usa id_user.
-- Se conserva id_usuario en Logs y se referencia a Usuarios.id_user.
-- registro_id se deja sin FK porque puede referirse a registros de distintas
-- tablas; tabla_afectada indica cuál sería la tabla de origen.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Logs (
    id_log INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    registro_id INT NULL,
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100) NULL,
    detalles TEXT NULL,
    `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_log),
    CONSTRAINT fk_logs_usuarios
        FOREIGN KEY (id_usuario) REFERENCES Usuarios (id_user)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =============================================================================
-- DECISIONES INFERIDAS / PENDIENTES DE VALIDACIÓN
-- 1. Tipos DATETIME para f_creacion y fecha_apertura, porque el PDF indica
--    DATE/DATETIME.
-- 2. Usuarios.estado se definió BOOLEAN; el PDF indica VARCHAR/BOOLEAN.
-- 3. Se usa AUTO_INCREMENT para las PK enteras; el PDF indica INT y PK.
-- 4. Se agregó seguimiento TEXT a Expedientes por decisión del proyecto.
--    Esto permite notas acumuladas, pero no conserva por separado fecha,
--    autor y cada actualización. Si se requiere historial cronológico real,
--    una tabla de seguimiento sería más adecuada; no se crea aquí porque se
--    decidió mantenerlo dentro de Expedientes.
-- 5. Municipios.departamento_estado se marcó UNIQUE porque así aparece en el
--    diccionario. Confirmar si debe ser UNIQUE compuesto con nombre_municipio.
-- 6. hash_identidad se dejó NULL para permitir registros aún no completados;
--    revisar si debe ser obligatorio.
-- 7. nombre en Derechos se marcó UNIQUE como medida propuesta; el diccionario
--    no indica explícitamente UNIQUE para ese campo.
-- 8. Se omitió Personas.id_nacimiento provisionalmente, según lo acordado.
-- 9. No se añadieron columnas adicionales de motivo o descripción de caso,
--    porque no están descritas en el fragmento del diccionario de Expedientes.
-- 10. No se incluyen datos iniciales (INSERT) ni se ejecuta este archivo.
-- =============================================================================
