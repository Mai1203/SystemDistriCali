from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session, declarative_base
from app.database.manager import db_manager
from app.utils.logger import logger

Base = declarative_base()


def SessionLocal() -> Session:
    """Instancia una nueva sesión vinculada al engine activo a través del DatabaseManager."""
    return db_manager.get_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager transaccional seguro.
    Ejecuta commit si no hay excepciones y rollback automático si ocurre cualquier error.
    Siempre cierra la sesión al finalizar.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error en bloque transaccional: {e}")
        raise
    finally:
        session.close()
        db_manager.remove_session()
