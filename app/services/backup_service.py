"""
backup_service.py
=================
Servicio unificado de respaldos para SystemDistriCali.

Solo soporta PostgreSQL (todos los modos: local, server, terminal).
  - PostgreSQL → volcado SQL con pg_dump / restauración con psql
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from app.database.config import load_config, DatabaseConfig
from app.utils.logger import logger

# ─────────────────────────────────────────────────────────────────────────────
# Constante: ventana oculta en Windows
# ─────────────────────────────────────────────────────────────────────────────
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _run_hidden(cmd, **kwargs) -> subprocess.CompletedProcess:
    """Ejecuta un subproceso sin mostrar ventana de consola en Windows y desactiva stdin interactivo."""
    flags = kwargs.pop("creationflags", 0) | _CREATE_NO_WINDOW
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    return subprocess.run(cmd, creationflags=flags, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# Búsqueda de binarios de PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────

def _find_pg_bin(binary: str) -> Optional[str]:
    """
    Busca un binario de PostgreSQL (pg_dump, psql) en:
    1. C:\\Program Files\\PostgreSQL\\{versión}\\bin\\
    2. PATH del sistema
    Retorna la ruta completa o None si no se encuentra.
    """
    rutas_base = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "PostgreSQL",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "PostgreSQL",
    ]
    for base in rutas_base:
        if base.exists():
            subdirs = sorted(
                [d for d in base.iterdir() if d.is_dir()],
                reverse=True,
            )
            for version_dir in subdirs:
                candidate = version_dir / "bin" / binary
                if candidate.exists():
                    logger.info(f"Binario '{binary}' encontrado en: {candidate}")
                    return str(candidate)

    # Intentar desde el PATH
    try:
        name_only = binary.replace(".exe", "")
        res = _run_hidden(
            [name_only, "--version"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0:
            logger.info(f"Binario '{binary}' disponible en PATH.")
            return name_only
    except Exception:
        pass

    logger.warning(f"Binario '{binary}' no encontrado.")
    return None


def find_pg_dump() -> Optional[str]:
    """Localiza el ejecutable pg_dump en el sistema."""
    return _find_pg_bin("pg_dump.exe" if os.name == "nt" else "pg_dump")


def find_psql() -> Optional[str]:
    """Localiza el ejecutable psql en el sistema."""
    return _find_pg_bin("psql.exe" if os.name == "nt" else "psql")


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de formato
# ─────────────────────────────────────────────────────────────────────────────

def get_extension_respaldo(config: Optional[DatabaseConfig] = None) -> str:
    """Retorna '.sql' para PostgreSQL."""
    return ".sql"


def get_filtro_dialogo(config: Optional[DatabaseConfig] = None) -> str:
    """Retorna el filtro de extensión para QFileDialog (PostgreSQL)."""
    return "Respaldo SQL (*.sql)"


def nombre_respaldo_automatico(
    config: Optional[DatabaseConfig] = None,
    fecha: Optional[str] = None,
) -> str:
    """
    Genera el nombre de archivo para el respaldo automático del día.
    Ejemplo: Backup_2026-09-12.sql
    """
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")
    ext = get_extension_respaldo(config)
    return f"Backup_{fecha}{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# RESPALDO — Crear
# ─────────────────────────────────────────────────────────────────────────────

def crear_respaldo(
    ruta_destino: str,
    config: Optional[DatabaseConfig] = None,
) -> Tuple[bool, str]:
    """
    Crea un respaldo de la base de datos PostgreSQL en *ruta_destino*.

    - PostgreSQL → pg_dump --file=ruta_destino --format=plain (.sql)

    Retorna (éxito: bool, mensaje: str).
    """
    if config is None:
        config = load_config()

    return _backup_postgresql(config, ruta_destino)


def _backup_postgresql(config: DatabaseConfig, ruta_destino: str) -> Tuple[bool, str]:
    """Respaldo PostgreSQL: genera un volcado SQL plano con pg_dump."""
    pg_dump = find_pg_dump()
    if not pg_dump:
        msg = (
            "No se encontró 'pg_dump'. Asegúrate de que PostgreSQL esté instalado "
            "y que la carpeta bin esté en el PATH del sistema."
        )
        logger.error(msg)
        return False, msg

    cmd = [
        pg_dump,
        "--host", config.host,
        "--port", str(config.port),
        "--username", config.user,
        "--dbname", config.database,
        "--file", ruta_destino,
        "--format", "plain",   # SQL plano (.sql): portable y legible
        "--encoding", "UTF8",
        "--clean",             # Incluye DROP TABLE IF EXISTS antes de CREATE/INSERT
        "--if-exists",         # Evita errores si la tabla no existe al hacer DROP
        "--no-owner",          # No incluir comandos ALTER OWNER TO (evita rol postgres)
        "--no-privileges",     # No incluir GRANT / REVOKE
        "--no-password",       # Contraseña via PGPASSWORD
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = config.password or ""
    env["PGCLIENTENCODING"] = "utf-8"

    try:
        logger.info(
            f"Ejecutando pg_dump: host={config.host}:{config.port} "
            f"db={config.database} → {ruta_destino}"
        )
        resultado = _run_hidden(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minutos máximo
        )

        if resultado.returncode == 0:
            logger.info(f"Respaldo PostgreSQL creado: {ruta_destino}")
            return True, f"Respaldo creado correctamente en:\n{ruta_destino}"
        else:
            error_detalle = resultado.stderr.strip() or resultado.stdout.strip()
            logger.error(f"pg_dump falló (código {resultado.returncode}): {error_detalle}")
            return False, f"Error en pg_dump:\n{error_detalle}"

    except subprocess.TimeoutExpired:
        msg = "El proceso pg_dump tardó demasiado y fue cancelado (timeout 5 min)."
        logger.error(msg)
        return False, msg
    except Exception as e:
        logger.error(f"Excepción al ejecutar pg_dump: {e}")
        return False, f"Error al ejecutar pg_dump: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# RESTAURAR — Importar
# ─────────────────────────────────────────────────────────────────────────────

def restaurar_respaldo(ruta_origen: str, config: Optional[DatabaseConfig] = None) -> Tuple[bool, str]:
    """
    Restaura la base de datos PostgreSQL desde un archivo .sql.
    - Limpia el esquema 'public' (DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO PUBLIC;).
    - Ejecuta el script .sql mediante psql.
    Retorna (éxito: bool, mensaje: str).
    """
    if config is None:
        config = load_config()

    if not os.path.exists(ruta_origen):
        return False, f"El archivo de respaldo no existe: {ruta_origen}"

    # Liberar el pool de conexiones de SQLAlchemy para evitar que bloquee la base de datos
    try:
        from app.database.engine import close_engine
        close_engine()
    except Exception as e:
        logger.warning(f"Aviso al liberar engine antes de la restauración: {e}")

    res, msg = _restaurar_postgresql(config, ruta_origen)

    # Re-inicializar / verificar el engine y la BD tras la restauración
    try:
        from app.database.engine import reset_engine
        from app.database.database import init_db
        reset_engine(config)
        init_db()
    except Exception as e:
        logger.warning(f"Aviso al re-inicializar BD tras restauración: {e}")

    return res, msg


def _restaurar_postgresql(config: DatabaseConfig, ruta_origen: str) -> Tuple[bool, str]:
    """
    Restauración PostgreSQL en segundo plano con psql (sin ventana de consola emergente).
    1. Limpia el esquema 'public' (DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO PUBLIC;).
    2. Ejecuta el script SQL mediante psql.
    """
    psql = find_psql()
    if not psql:
        msg = (
            "No se encontró 'psql'. Asegúrate de que PostgreSQL esté instalado "
            "y que la carpeta bin esté en el PATH del sistema."
        )
        logger.error(msg)
        return False, msg

    env = os.environ.copy()
    env["PGPASSWORD"] = config.password or ""
    env["PGCLIENTENCODING"] = "utf-8"
    env["PGCONNECT_TIMEOUT"] = "10"

    # Paso 1: Liberar conexiones activas de la BD para evitar que psql quede bloqueado en lock wait
    cmd_terminate = [
        psql,
        "--host", config.host,
        "--port", str(config.port),
        "--username", config.user,
        "--dbname", config.database,
        "--no-password",
        "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{config.database}' AND pid <> pg_backend_pid();",
    ]
    try:
        _run_hidden(cmd_terminate, capture_output=True, text=True, env=env, timeout=10)
    except Exception as e:
        logger.warning(f"No se pudieron terminar conexiones previas: {e}")

    # Paso 2: Limpiar el esquema public previo para eliminar todas las tablas antes de reinsertar
    cmd_clean = [
        psql,
        "--host", config.host,
        "--port", str(config.port),
        "--username", config.user,
        "--dbname", config.database,
        "--no-password",
        "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO PUBLIC;",
    ]

    try:
        logger.info(f"Limpiando esquema public en PostgreSQL ({config.database})...")
        res_clean = _run_hidden(cmd_clean, capture_output=True, text=True, env=env, timeout=30)
        if res_clean.returncode != 0:
            logger.warning(f"Aviso al limpiar esquema public: {res_clean.stderr or res_clean.stdout}")
    except Exception as e:
        logger.warning(f"No se pudo limpiar el esquema public antes de la importación: {e}")

    # Paso 3: Ejecutar el archivo de respaldo .sql
    cmd = [
        psql,
        "--host", config.host,
        "--port", str(config.port),
        "--username", config.user,
        "--dbname", config.database,
        "--file", ruta_origen,
        "--no-password",
        "--single-transaction",
    ]

    try:
        logger.info(
            f"Restaurando desde {ruta_origen} → "
            f"host={config.host}:{config.port} db={config.database}"
        )
        resultado = _run_hidden(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minutos máximo
        )

        stderr = resultado.stderr.strip()
        stdout = resultado.stdout.strip()
        detalle = stderr or stdout

        if resultado.returncode == 0 or "ERROR:" not in detalle.upper():
            logger.info("Restauración PostgreSQL completada con éxito.")
            return True, "Datos restaurados correctamente desde el respaldo."

        if "must be member of role" in detalle:
            logger.info("Restauración PostgreSQL completada (omitiendo asignación de rol owner 'postgres').")
            return True, "Datos restaurados correctamente desde el respaldo."

        logger.error(f"psql falló (código {resultado.returncode}): {detalle[:400]}")
        return False, f"Error al restaurar la base de datos:\n{detalle[:400]}"

    except subprocess.TimeoutExpired:
        msg = "El proceso psql tardó demasiado y fue cancelado (timeout 5 min)."
        logger.error(msg)
        return False, msg
    except Exception as e:
        logger.error(f"Excepción al ejecutar psql: {e}")
        return False, f"Error al ejecutar psql: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# Verificación de herramientas
# ─────────────────────────────────────────────────────────────────────────────

def verificar_herramientas_postgres() -> Tuple[bool, str]:
    """
    Verifica que pg_dump y psql estén disponibles para las operaciones de respaldo.
    Retorna (disponible: bool, mensaje: str).
    """
    pg_dump = find_pg_dump()
    psql = find_psql()
    if pg_dump and psql:
        return True, "pg_dump y psql disponibles."
    faltantes = []
    if not pg_dump:
        faltantes.append("pg_dump")
    if not psql:
        faltantes.append("psql")
    msg = (
        f"Herramientas no encontradas: {', '.join(faltantes)}. "
        "Instala PostgreSQL o agrega la carpeta 'bin' al PATH del sistema."
    )
    return False, msg