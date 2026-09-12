from typing import Optional
from sqlalchemy import create_engine, Engine
from app.database.config import load_config, DatabaseConfig
from app.utils.logger import logger

_current_engine: Optional[Engine] = None


def get_engine_for_config(config: DatabaseConfig) -> Engine:
    """Crea un nuevo SQLAlchemy Engine configurado para el motor especificado."""
    url = config.get_connection_url()
    
    if config.mode == "local" or config.engine_type == "sqlite":
        logger.info(f"Inicializando Engine SQLite en: {url}")
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        logger.info(f"Inicializando Engine PostgreSQL: host={config.host}, port={config.port}, db={config.database}")
        return create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verifica liveness de la conexión antes de entregarla
            pool_recycle=1800,   # Recicla conexiones tras 30 min
            connect_args={"connect_timeout": 5},
            echo=False
        )


def get_engine() -> Engine:
    """Obtiene el engine singleton actual o lo inicializa si aún no existe."""
    global _current_engine
    if _current_engine is None:
        config = load_config()
        _current_engine = get_engine_for_config(config)
    return _current_engine


def close_engine():
    """Cierra y libera el engine actual sin recrear uno nuevo inmediatamente."""
    global _current_engine
    if _current_engine is not None:
        try:
            _current_engine.dispose()
            logger.info("Engine liberado exitosamente.")
        except Exception as e:
            logger.warning(f"Error al liberar engine: {e}")
        _current_engine = None


def reset_engine(new_config: Optional[DatabaseConfig] = None) -> Engine:
    """Cierra el engine actual y crea uno nuevo (útil al cambiar de servidor/configuración)."""
    close_engine()
    config = new_config or load_config()
    _current_engine = get_engine_for_config(config)
    return _current_engine
