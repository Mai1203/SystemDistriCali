from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.database.engine import get_engine
from app.utils.logger import logger

Base = declarative_base()


def get_session_factory():
    """Genera una fábrica de sesiones vinculada al engine actual."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def SessionLocal() -> Session:
    """Instancia una nueva sesión vinculada al engine activo."""
    factory = get_session_factory()
    return factory()


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
