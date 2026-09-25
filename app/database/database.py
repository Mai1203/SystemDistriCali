from sqlalchemy import inspect, text
from sqlalchemy.orm import configure_mappers

from app.database.manager import db_manager
from app.database.session import Base, SessionLocal, session_scope  # Re-export para compatibilidad
from app.database.seeds.seeder_manager import DatabaseSeeder
from app.utils.logger import logger


def init_db():
    """Inicializa la base de datos (crea tablas y esquemas PostgreSQL)."""
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
    )  # Importar todos los modelos para registro en Base.metadata
    
    import app.database.events  # Registrar eventos automáticos de SQLAlchemy

    current_engine = db_manager.get_engine()

    try:
        configure_mappers()
    except Exception as e:
        logger.warning(f"Aviso al configurar mappers: {e}")

    try:
        print("[DEBUG] Creando tablas...", flush=True)
        Base.metadata.create_all(bind=current_engine)
        print("[DEBUG] Tablas creadas.", flush=True)
    except Exception as e:
        logger.error(f"Error al crear tablas en Base.metadata.create_all: {e}")
        raise

    print("[DEBUG] Verificando esquemas...", flush=True)
    try:
        with current_engine.begin() as connection:
            inspector = inspect(current_engine)
            if "USUARIOS" in inspector.get_table_names():
                columnas = {columna["name"] for columna in inspector.get_columns("USUARIOS")}
                if "Permisos" not in columnas:
                    connection.execute(text('ALTER TABLE "USUARIOS" ADD COLUMN "Permisos" VARCHAR(500) NOT NULL DEFAULT \'\''))
            if "DETALLE_FACTURAS" in inspector.get_table_names():
                columnas_df = {columna["name"] for columna in inspector.get_columns("DETALLE_FACTURAS")}
                if "ID_Lote" not in columnas_df:
                    connection.execute(text('ALTER TABLE "DETALLE_FACTURAS" ADD COLUMN "ID_Lote" INTEGER REFERENCES "LOTES_PRODUCTO"("ID_Lote")'))
    except Exception as e:
        logger.error(f"Error al verificar/migrar esquemas básicos: {e}")

    print("[DEBUG] Ejecutando DatabaseSeeder.run_all_seeds()...", flush=True)
    DatabaseSeeder.run_all_seeds()
    print("[DEBUG] run_all_seeds() completado.", flush=True)

    print("[DEBUG] Instalando triggers...", flush=True)
    from app.database.triggers import instalar_triggers_postgresql
    instalar_triggers_postgresql(current_engine)
    print("[DEBUG] init_db() FINISHED.", flush=True)