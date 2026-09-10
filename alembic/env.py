from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Añadir raíz del proyecto al sys.path
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from app.database.engine import get_engine
from app.database.session import Base
from app.models import (
    usuarios,
    productos,
    facturas,
    detalle_facturas,
    venta_credito,
    clientes,
    pago_credito,
    tipo_ingresos,
    ingresos,
    caja,
    egresos,
    analisis_financiero,
    reporte,
    historial,
    lotes,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline."""
    engine = get_engine()
    url = engine.url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online usando el engine dinámico."""
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
