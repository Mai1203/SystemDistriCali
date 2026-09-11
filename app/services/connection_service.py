from typing import Tuple
from sqlalchemy import create_engine, text
from app.database.config import DatabaseConfig
from app.utils.logger import logger


def _safe_error_message(e: Exception) -> str:
    """Extrae el mensaje de error de forma segura evitando fallos de codificación utf-8/latin-1."""
    try:
        return str(e)
    except UnicodeDecodeError:
        pass
    except Exception:
        pass

    try:
        # Intentar extraer args como bytes o representaciones
        parts = []
        for arg in getattr(e, "args", []):
            if isinstance(arg, bytes):
                parts.append(arg.decode("latin-1", errors="replace"))
            elif isinstance(arg, str):
                parts.append(arg)
            else:
                parts.append(repr(arg))
        if parts:
            return " ".join(parts)
    except Exception:
        pass

    return repr(e)


def test_connection(config: DatabaseConfig, timeout_seconds: int = 4) -> Tuple[bool, str]:
    """
    Prueba la conexión a la base de datos según la configuración provista.
    Retorna (éxito: bool, mensaje: str).
    """
    url = config.get_connection_url()
    
    if config.mode == "local" or config.engine_type == "sqlite":
        try:
            test_engine = create_engine(url, connect_args={"check_same_thread": False})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            test_engine.dispose()
            return True, "Conexión a SQLite local verificada correctamente."
        except Exception as e:
            err_str = _safe_error_message(e)
            logger.error(f"Error probando conexión SQLite: {err_str}")
            return False, f"Error al abrir la base de datos local: {err_str}"
    
    # PostgreSQL
    try:
        test_engine = create_engine(
            url,
            connect_args={"connect_timeout": timeout_seconds},
            pool_pre_ping=True
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
        return True, "¡Conexión exitosa con el servidor PostgreSQL!"
    except Exception as e:
        error_msg = _safe_error_message(e)
        logger.error(f"Fallo de conexión a PostgreSQL ({config.host}:{config.port}): {error_msg}")
        
        lower_msg = error_msg.lower()

        # Diagnósticos amigables
        if "timeout" in lower_msg or "could not connect" in lower_msg or "no se pudo conectar" in lower_msg:
            return False, (
                f"No se pudo contactar al servidor en {config.host}:{config.port}.\n\n"
                "Compruebe:\n"
                "1. Que el PC Servidor esté encendido y conectado a la misma red.\n"
                "2. Que el servicio de PostgreSQL esté en ejecución en el servidor.\n"
                "3. Que el Firewall de Windows en el servidor tenga abierto el puerto 5432."
            )
        elif "pg_hba.conf" in lower_msg or "no hay una línea en pg_hba" in lower_msg:
            return False, (
                "El servidor PostgreSQL rechazó la conexión por reglas de acceso (pg_hba.conf).\n"
                "Por favor ejecute 'Configurar / Inicializar Servidor' en el PC Servidor para autorizar la red."
            )
        elif "password authentication failed" in lower_msg or "autenticaci" in lower_msg or "autentificaci" in lower_msg:
            return False, "Usuario o contraseña de PostgreSQL incorrectos."
        elif "database" in lower_msg and ("does not exist" in lower_msg or "no existe" in lower_msg):
            return False, f"La base de datos '{config.database}' no existe en el servidor."
        else:
            return False, f"Error al conectar con el servidor: {error_msg}"
