-- Tablas de la app "control" (auditoría y metas de ventas) para MySQL.
--
-- Opción recomendada (crea las tablas y registra la migración):
--     python manage.py migrate control
--
-- Opción manual: ejecutar este script en la base de datos del proyecto (por ejemplo `ranfit`).
-- Si luego quieres usar migrate, hazlo así para que Django no intente crearlas otra vez:
--     python manage.py migrate control --fake-initial
--
-- No modifica ninguna tabla existente.

CREATE TABLE IF NOT EXISTS `control_registroauditoria` (
    `id`             BIGINT       NOT NULL AUTO_INCREMENT,
    `fecha`          DATETIME(6)  NOT NULL,
    `usuario_nombre` VARCHAR(80)  NOT NULL,
    `usuario_correo` VARCHAR(120) NOT NULL,
    `rol_id`         INT          NULL,
    `ip`             VARCHAR(45)  NOT NULL,
    `accion`         VARCHAR(30)  NOT NULL,
    `modulo`         VARCHAR(30)  NOT NULL,
    `objeto`         VARCHAR(60)  NOT NULL,
    `objeto_id`      VARCHAR(40)  NOT NULL,
    `descripcion`    VARCHAR(300) NOT NULL,
    `cambios`        LONGTEXT     NOT NULL,
    PRIMARY KEY (`id`),
    KEY `control_registroauditoria_fecha_idx` (`fecha`),
    KEY `control_registroauditoria_usuario_correo_idx` (`usuario_correo`),
    KEY `control_registroauditoria_accion_idx` (`accion`),
    KEY `control_registroauditoria_modulo_idx` (`modulo`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `control_metaventas` (
    `id`            BIGINT        NOT NULL AUTO_INCREMENT,
    `anio`          SMALLINT UNSIGNED NOT NULL,
    `mes`           SMALLINT UNSIGNED NOT NULL,
    `valor`         BIGINT        NOT NULL,
    `definida_por`  VARCHAR(120)  NOT NULL,
    `actualizada`   DATETIME(6)   NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `control_metaventas_anio_mes_uniq` (`anio`, `mes`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
