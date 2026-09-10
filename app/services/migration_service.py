import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Callable, Optional
from sqlalchemy import create_engine, text, inspect
from app.database.config import DatabaseConfig, APP_DATA_DIR
from app.utils.logger import logger


ORDERED_TABLES = [
    ("MARCAS", "ID_Marca"),
    ("CATEGORIAS", "ID_Categoria"),
    ("METODO_PAGO", "ID_Metodo_Pago"),
    ("TIPO_FACTURA", "ID_Tipo_Factura"),
    ("TIPO_PAGO", "ID_Tipo_Pago"),
    ("USUARIOS", "ID_Usuario"),
    ("CLIENTES", "ID_Cliente"),
    ("PRODUCTOS", "ID_Producto"),
    ("LOTES_PRODUCTO", "ID_Lote"),
    ("FACTURA", "ID_Factura"),
    ("DETALLE_FACTURAS", "ID_Detalle_Factura"),
    ("VENTA_CREDITO", "ID_Venta_Credito"),
    ("PAGO_CREDITO", "ID_Pago_Credito"),
    ("TIPO_INGRESO", "ID_Tipo_Ingreso"),
    ("CAJA", "ID_Caja"),
    ("EGRESOS", "ID_Egreso"),
    ("ANALISIS_FINANCIERO", "ID_Analisis_Financiero"),
    ("REPORTE", "ID_Reporte"),
    ("HISTORIAL_INICIO", "ID_Historial_Inicio"),
    ("HISTORIAL_MODIFICACION", "ID_Historial_Modificacion"),
]


def backup_sqlite_file(sqlite_path: str) -> Optional[str]:
    """Crea una copia de seguridad segura de la base de datos SQLite antes de la migración."""
    src = Path(sqlite_path)
    if not src.exists():
        return None

    backup_dir = APP_DATA_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backup_dir / f"sqlite_backup_pre_migration_{timestamp}.db"
    
    try:
        shutil.copy2(src, dst)
        logger.info(f"Respaldo SQLite generado exitosamente en: {dst}")
        return str(dst)
    except Exception as e:
        logger.error(f"Error al respaldar archivo SQLite: {e}")
        return None


def migrate_sqlite_to_postgres(
    sqlite_path: str,
    target_config: DatabaseConfig,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> Tuple[bool, str]:
    """
    Migra datos existentes desde SQLite hacia PostgreSQL preservando integridad y actualizando secuencias.
    """
    if not os.path.exists(sqlite_path):
        return False, f"El archivo SQLite no existe en: {sqlite_path}"

    # 1. Respaldo previo
    backup_path = backup_sqlite_file(sqlite_path)
    logger.info(f"Iniciando proceso de migración. Respaldo de seguridad en: {backup_path}")

    # 2. Conectar a ambas bases
    sqlite_url = f"sqlite:///{Path(sqlite_path).as_posix()}"
    pg_url = target_config.get_connection_url()

    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    pg_engine = create_engine(pg_url)

    try:
        # Asegurar tablas en destino
        from app.database.database import init_db
        init_db()

        inspector_sqlite = inspect(sqlite_engine)
        inspector_pg = inspect(pg_engine)

        sqlite_tables = set(inspector_sqlite.get_table_names())
        pg_tables = set(inspector_pg.get_table_names())

        total_steps = len(ORDERED_TABLES)

        with sqlite_engine.connect() as sqlite_conn, pg_engine.begin() as pg_conn:
            for idx, (table_name, pk_name) in enumerate(ORDERED_TABLES, start=1):
                if table_name not in sqlite_tables or table_name not in pg_tables:
                    logger.info(f"Omitiendo tabla '{table_name}' (no presente en ambos esquemas).")
                    continue

                if progress_callback:
                    progress_callback(f"Migrando tabla {table_name}...", idx, total_steps)

                # Obtener columnas comunes
                sqlite_cols = [c["name"] for c in inspector_sqlite.get_columns(table_name)]
                pg_cols = [c["name"] for c in inspector_pg.get_columns(table_name)]
                common_cols = [c for c in sqlite_cols if c in pg_cols]

                if not common_cols:
                    continue

                # Leer datos de SQLite
                cols_str = ", ".join([f'"{c}"' for c in common_cols])
                rows = sqlite_conn.execute(text(f'SELECT {cols_str} FROM "{table_name}"')).mappings().all()

                if rows:
                    # Inserción en bloques
                    params_str = ", ".join([f":{c}" for c in common_cols])
                    insert_sql = text(
                        f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({params_str}) '
                        f'ON CONFLICT ("{pk_name}") DO NOTHING'
                    )
                    pg_conn.execute(insert_sql, [dict(r) for r in rows])
                    logger.info(f"Tabla '{table_name}': {len(rows)} registros procesados.")

                # Actualizar secuencia SERIAL de PostgreSQL
                if pk_name:
                    try:
                        seq_sql = text(
                            f"SELECT setval(pg_get_serial_sequence('\"{table_name}\"', '{pk_name}'), "
                            f"COALESCE((SELECT MAX(\"{pk_name}\") FROM \"{table_name}\"), 1), "
                            f"(SELECT COUNT(*) FROM \"{table_name}\") > 0)"
                        )
                        pg_conn.execute(seq_sql)
                    except Exception as seq_err:
                        logger.warning(f"Aviso actualizando secuencia para {table_name}.{pk_name}: {seq_err}")

        sqlite_engine.dispose()
        pg_engine.dispose()

        logger.info("Migración de datos de SQLite a PostgreSQL completada con éxito.")
        return True, "Migración completada con éxito. Todos los datos fueron transferidos."

    except Exception as e:
        logger.error(f"Error crítico durante la migración: {e}")
        return False, f"Error durante la migración: {str(e)}"
