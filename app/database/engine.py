from typing import Optional
from sqlalchemy import create_engine, Engine
from app.database.config import load_config, DatabaseConfig
from app.utils.logger import logger

_current_engine: Optional[Engine] = None


def get_engine_for_config(config: DatabaseConfig) -> Engine:
    """Crea o reutiliza el engine gestionado por DatabaseManager."""
    from app.database.manager import db_manager

    return db_manager.initialize(config)


def get_engine() -> Engine:
    """Obtiene el engine singleton gestionado por DatabaseManager."""
    from app.database.manager import db_manager

    return db_manager.get_engine()


def close_engine():
    """Cierra y libera el engine gestionado por DatabaseManager."""
    from app.database.manager import db_manager

    db_manager.close()


def reset_engine(new_config: Optional[DatabaseConfig] = None) -> Engine:
    """Cierra el engine actual y crea uno nuevo con la configuración indicada."""
    from app.database.manager import db_manager
    from app.database.config import load_config

    config = new_config or load_config()
    return db_manager.initialize(config)
