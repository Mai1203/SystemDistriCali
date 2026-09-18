from .session import SessionLocal, Base, session_scope
from .manager import db_manager


def __getattr__(name):
    """Lazy alias para 'engine' — solo se crea cuando se accede por primera vez."""
    if name == "engine":
        return db_manager.get_engine()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
