from sqlalchemy import text, inspect
from app.utils.logger import logger

# Tablas que tendrán disparadores de notificación en tiempo real
# Excluidas deliberadamente: DETALLE_FACTURAS y LOTES_PRODUCTO
REALTIME_TABLES = [
    "FACTURA",
    "PRODUCTOS",
    "VENTA_CREDITO",
    "PAGO_CREDITO",
    "CAJA",
    "EGRESOS",
    "CLIENTES",
]

NOTIFICATION_CHANNEL = "distri_realtime_events"

PG_NOTIFY_FUNCTION_SQL = f"""
CREATE OR REPLACE FUNCTION notify_db_event() RETURNS trigger AS $$
DECLARE
    payload JSON;
    record_data JSON;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        record_data = row_to_json(OLD);
    ELSE
        record_data = row_to_json(NEW);
    END IF;

    payload = json_build_object(
        'table', TG_TABLE_NAME,
        'action', TG_OP,
        'data', record_data
    );

    PERFORM pg_notify('{NOTIFICATION_CHANNEL}', payload::text);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""


def instalar_triggers_postgresql(engine):
    """
    Instala la función de notificación y los triggers para PostgreSQL.
    Es seguro e idempotente (reemplaza función y recrea triggers).
    """
    if engine.dialect.name != "postgresql":
        logger.debug(f"Motor {engine.dialect.name} no requiere triggers de PostgreSQL.")
        return

    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        with engine.begin() as conn:
            # 1. Crear o reemplazar la función de notificación
            logger.info("Instalando función de notificación PostgreSQL: notify_db_event()")
            conn.execute(text(PG_NOTIFY_FUNCTION_SQL))

            # 2. Crear triggers para las tablas existentes
            for table_name in REALTIME_TABLES:
                if table_name in existing_tables:
                    trigger_name = f"trg_notify_{table_name.lower()}"
                    
                    # Eliminar trigger previo si existe para evitar conflictos
                    conn.execute(text(f'DROP TRIGGER IF EXISTS "{trigger_name}" ON "{table_name}";'))
                    
                    # Crear nuevo trigger AFTER INSERT OR UPDATE OR DELETE
                    conn.execute(text(f"""
                        CREATE TRIGGER "{trigger_name}"
                        AFTER INSERT OR UPDATE OR DELETE ON "{table_name}"
                        FOR EACH ROW EXECUTE FUNCTION notify_db_event();
                    """))
                    logger.info(f"Trigger {trigger_name} instalado en tabla {table_name}")
                else:
                    logger.debug(f"Tabla {table_name} no encontrada en la base de datos al instalar triggers.")

        logger.info("Triggers de tiempo real en PostgreSQL instalados exitosamente.")
    except Exception as e:
        logger.error(f"Error al instalar triggers de PostgreSQL: {e}")
