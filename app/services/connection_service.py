from typing import Tuple
from sqlalchemy import create_engine, text
from app.database.config import DatabaseConfig
from app.utils.logger import logger


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
            logger.error(f"Error probando conexión SQLite: {e}")
            return False, f"Error al abrir la base de datos local: {str(e)}"
    
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
        error_msg = str(e)
        logger.error(f"Fallo de conexión a PostgreSQL ({config.host}:{config.port}): {error_msg}")
        
        # Mensajes amigables de diagnóstico
        if "timeout expired" in error_msg.lower() or "could not connect to server" in error_msg.lower():
            return False, (
                f"No se pudo contactar al servidor en {config.host}:{config.port}.\n\n"
                "Compruebe:\n"
                "1. Que el PC Servidor esté encendido y conectado a la misma red.\n"
                "2. Que el servicio de PostgreSQL esté en ejecución en el servidor.\n"
                "3. Que el Firewall de Windows en el servidor permita conexiones en el puerto 5432."
            )
        elif "password authentication failed" in error_msg.lower():
            return False, "Usuario o contraseña de PostgreSQL incorrectos."
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            return False, f"La base de datos '{config.database}' no existe en el servidor."
        else:
            return False, f"Error al conectar con el servidor: {error_msg}"
