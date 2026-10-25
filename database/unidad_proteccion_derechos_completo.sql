-- =============================================================================
-- ESQUEMA UNIFICADO DE BASE DE DATOS
-- Proyecto: Unidad de Protección de Derechos Vulnerados
-- Motor: MySQL / MariaDB (InnoDB)
--
-- Incluye todas las tablas del esquema y la migración 002 en un único archivo.
-- Diseñado para una instalación nueva; CREATE TABLE IF NOT EXISTS no modifica
-- automáticamente tablas existentes. Para una base ya creada, haga respaldo
-- y revise/aplique migraciones por separado antes de usar este archivo.
-- No incluye datos de demostración (INSERT).
-- =============================================================================

CREATE DATABASE IF NOT EXISTS unidad_proteccion_derechos
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE unidad_proteccion_derechos;

-- 1. Roles
CREATE TABLE IF NOT EXISTS roles (
  id_rol INT(11) NOT NULL AUTO_INCREMENT,
  nombre_rol VARCHAR(50) NOT NULL,
  descripcion TEXT NULL,
  PRIMARY KEY (id_rol),
  UNIQUE KEY uq_roles_nombre_rol (nombre_rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id_user INT(11) NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL COMMENT 'Guardar únicamente hash seguro de contraseña',
  id_rol INT(11) NOT NULL,
  f_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_user),
  UNIQUE KEY uq_usuarios_username (username),
  KEY idx_usuarios_rol (id_rol),
  CONSTRAINT fk_usuarios_roles FOREIGN KEY (id_rol)
    REFERENCES roles (id_rol) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Municipios: unicidad por nombre y departamento/estado
CREATE TABLE IF NOT EXISTS municipios (
  id_municipio INT(11) NOT NULL AUTO_INCREMENT,
  nombre_municipio VARCHAR(100) NOT NULL,
  departamento_estado VARCHAR(100) NULL,
  PRIMARY KEY (id_municipio),
  UNIQUE KEY uq_municipios_nombre_departamento (nombre_municipio, departamento_estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Personas
CREATE TABLE IF NOT EXISTS personas (
  id_persona INT(11) NOT NULL AUTO_INCREMENT,
  f_nacimiento DATE NULL,
  id_municipio INT(11) NULL,
  datos_cifrados TEXT NOT NULL,
  hash_identidad VARCHAR(255) NOT NULL,
  PRIMARY KEY (id_persona),
  UNIQUE KEY uq_personas_hash_identidad (hash_identidad),
  KEY idx_personas_municipio (id_municipio),
  CONSTRAINT fk_personas_municipios FOREIGN KEY (id_municipio)
    REFERENCES municipios (id_municipio) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Derechos
CREATE TABLE IF NOT EXISTS derechos (
  id_derecho INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(150) NOT NULL,
  descripcion TEXT NULL,
  clasificacion VARCHAR(100) NULL,
  PRIMARY KEY (id_derecho),
  UNIQUE KEY uq_derechos_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Expedientes
CREATE TABLE IF NOT EXISTS expedientes (
  id_expediente INT(11) NOT NULL AUTO_INCREMENT,
  codigo_unico VARCHAR(100) NOT NULL,
  fecha_apertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  motivo_atencion VARCHAR(255) NOT NULL,
  descripcion TEXT NOT NULL,
  estado VARCHAR(30) NOT NULL DEFAULT 'recibido',
  id_responsable INT(11) NOT NULL,
  PRIMARY KEY (id_expediente),
  UNIQUE KEY uq_expedientes_codigo_unico (codigo_unico),
  KEY idx_expedientes_estado (estado),
  KEY idx_expedientes_fecha_apertura (fecha_apertura),
  KEY idx_expedientes_responsable (id_responsable),
  CONSTRAINT fk_expedientes_responsable FOREIGN KEY (id_responsable)
    REFERENCES usuarios (id_user) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Contador anual para generar folios únicos
CREATE TABLE IF NOT EXISTS contadores_folio (
  anio SMALLINT(4) NOT NULL,
  ultimo_numero INT(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (anio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Relación Expediente-Persona
CREATE TABLE IF NOT EXISTS expediente_persona (
  id_expediente INT(11) NOT NULL,
  id_persona INT(11) NOT NULL,
  rol_en_caso VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_expediente, id_persona),
  KEY idx_expediente_persona_persona (id_persona),
  CONSTRAINT fk_expediente_persona_expediente FOREIGN KEY (id_expediente)
    REFERENCES expedientes (id_expediente) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_expediente_persona_persona FOREIGN KEY (id_persona)
    REFERENCES personas (id_persona) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Relación Expediente-Derecho
CREATE TABLE IF NOT EXISTS expediente_derecho (
  id_expediente INT(11) NOT NULL,
  id_derecho INT(11) NOT NULL,
  nivel_gravedad VARCHAR(20) NOT NULL,
  observaciones TEXT NULL,
  PRIMARY KEY (id_expediente, id_derecho),
  KEY idx_expediente_derecho_derecho (id_derecho),
  CONSTRAINT fk_expediente_derecho_expediente FOREIGN KEY (id_expediente)
    REFERENCES expedientes (id_expediente) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_expediente_derecho_derecho FOREIGN KEY (id_derecho)
    REFERENCES derechos (id_derecho) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Historial de seguimiento
CREATE TABLE IF NOT EXISTS seguimiento (
  id_seguimiento INT(11) NOT NULL AUTO_INCREMENT,
  id_expediente INT(11) NOT NULL,
  id_usuario INT(11) NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  descripcion TEXT NOT NULL,
  estado_nuevo VARCHAR(30) NULL,
  PRIMARY KEY (id_seguimiento),
  KEY idx_seguimiento_expediente_fecha (id_expediente, fecha),
  KEY idx_seguimiento_usuario (id_usuario),
  CONSTRAINT fk_seguimiento_expediente FOREIGN KEY (id_expediente)
    REFERENCES expedientes (id_expediente) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_seguimiento_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios (id_user) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Logs de auditoría
-- registro_id es polimórfico, por lo que no tiene una FK directa.
CREATE TABLE IF NOT EXISTS logs (
  id_log INT(11) NOT NULL AUTO_INCREMENT,
  id_usuario INT(11) NULL,
  registro_id INT(11) NULL,
  accion VARCHAR(100) NOT NULL,
  tabla_afectada VARCHAR(100) NOT NULL,
  detalles TEXT NULL,
  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_log),
  KEY idx_logs_usuario (id_usuario),
  KEY idx_logs_tabla_fecha (tabla_afectada, `timestamp`),
  KEY idx_logs_fecha (`timestamp`),
  CONSTRAINT fk_logs_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios (id_user) ON UPDATE RESTRICT ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verificación: deben aparecer las 11 tablas del esquema.
SHOW TABLES;
