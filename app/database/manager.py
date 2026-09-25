import threading
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.config import load_config, DatabaseConfig
from app.utils.logger import logger

class DatabaseManager:
    """
    Singleton Thread-Safe que gestiona el ciclo de vida del Engine y la Sesión.
    Garantiza que siempre haya una sola fuente de verdad para la conexión a BD.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._engine = None
                cls._instance._session_factory = None
        return cls._instance

    def initialize(self, config: Optional[DatabaseConfig] = None) -> Engine:
        """Inicializa o reinicializa el motor con una nueva configuración (PostgreSQL)."""
        with self._lock:
            self._close_engine()
            
            cfg = config or load_config()
            url = cfg.get_connection_url()
            
            logger.info(f"Inicializando Engine PostgreSQL: host={cfg.host}, port={cfg.port}, db={cfg.database}")
            self._engine = create_engine(
                url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=15,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={
                    "connect_timeout": 5,
                    "options": "-c lock_timeout=5s -c statement_timeout=0",
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 3,
                },
                echo=False
            )
            
            self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            
            return self._engine

    def get_engine(self) -> Engine:
        """Obtiene el engine actual. Si no existe, lo inicializa."""
        if self._engine is None:
            self.initialize()
        return self._engine

    def get_session(self) -> Session:
        """Obtiene una nueva sesión para consultas ORM."""
        if self._session_factory is None:
            self.initialize()
        return self._session_factory()

    def remove_session(self):
        """Las sesiones se gestionan individualmente y se cierran con close()."""
        return None

    def _close_engine(self):
        """Cierra el engine actual internamente."""
        if self._engine is not None:
            try:
                self.remove_session()
                self._engine.dispose()
                logger.info("Engine liberado exitosamente.")
            except Exception as e:
                logger.warning(f"Error al liberar engine: {e}")
            self._engine = None
            self._session_factory = None

    def close(self):
        """Cierra el engine público."""
        with self._lock:
            self._close_engine()

# Instancia global exportable
db_manager = DatabaseManager()