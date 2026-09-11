from sqlalchemy import inspect, text
from sqlalchemy.orm import configure_mappers
from pathlib import Path
import os

from app.database.config import load_config, APP_DATA_DIR, DEFAULT_SQLITE_PATH
from app.database.engine import get_engine, reset_engine
from app.database.session import Base, SessionLocal, session_scope
from app.utils.logger import logger

# Variables compatibles hacia atrás
app_data_dir = APP_DATA_DIR
DATABASE_PATH = Path(DEFAULT_SQLITE_PATH)
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Proxy/instancia de engine global
engine = get_engine()


def init_db():
    """Inicializa la base de datos (crea tablas y esquemas según el motor configurado)."""
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

    current_engine = get_engine()

    try:
        configure_mappers()
    except Exception as e:
        logger.warning(f"Aviso al configurar mappers: {e}")

    try:
        logger.info(f"Creando tablas en el motor: {current_engine.dialect.name}")
        Base.metadata.create_all(bind=current_engine)
        logger.info("Tablas creadas/verificadas exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear tablas en Base.metadata.create_all: {e}")
        raise

    try:
        with current_engine.begin() as connection:
            inspector = inspect(current_engine)
            if "USUARIOS" in inspector.get_table_names():
                columnas = {columna["name"] for columna in inspector.get_columns("USUARIOS")}
                if "Permisos" not in columnas:
                    logger.info("Añadiendo columna 'Permisos' a USUARIOS...")
                    connection.execute(text(
                        'ALTER TABLE "USUARIOS" ADD COLUMN "Permisos" VARCHAR(500) NOT NULL DEFAULT \'\''
                    ))
    except Exception as e:
        logger.error(f"Error al verificar columna Permisos: {e}")

    # Ejecutar migración de esquema si aplica
    migrar_esquema(current_engine)

    # Poblar datos iniciales indispensables (roles, métodos de pago, usuario admin, etc.)
    poblar_datos_iniciales(current_engine)


def migrar_esquema(target_engine=None):
    """Añade los PV nuevos, lotes y actualiza los tipos de factura de forma segura según el motor."""
    current_engine = target_engine or get_engine()
    inspector = inspect(current_engine)
    dialect = current_engine.dialect.name

    try:
        with current_engine.begin() as connection:
            tables = inspector.get_table_names()

            # 1. Migración de columnas en DETALLE_FACTURAS
            if "DETALLE_FACTURAS" in tables:
                columnas_df = {columna["name"] for columna in inspector.get_columns("DETALLE_FACTURAS")}
                if "ID_Lote" not in columnas_df:
                    connection.execute(text(
                        'ALTER TABLE "DETALLE_FACTURAS" ADD COLUMN "ID_Lote" INTEGER REFERENCES "LOTES_PRODUCTO"("ID_Lote")'
                    ))

            # 2. Migración de productos existentes a lotes si no tienen ninguno
            if "LOTES_PRODUCTO" in tables and "PRODUCTOS" in tables:
                connection.execute(text('''
                    INSERT INTO "LOTES_PRODUCTO" (
                        "ID_Producto", "Numero_Lote", "Fecha_Entrada", "Fecha_Vencimiento",
                        "Stock_inicial", "Stock_actual", "Precio_costo",
                        "Precio_venta_1", "Precio_venta_2", "Precio_venta_3", "Precio_venta_4",
                        "Ganancia_1", "Ganancia_2", "Ganancia_3", "Ganancia_4",
                        "Estado", "Proveedor", "Notas"
                    )
                    SELECT 
                        p."ID_Producto",
                        'LOTE-INICIAL',
                        CURRENT_TIMESTAMP,
                        NULL,
                        p."Stock_actual",
                        p."Stock_actual",
                        p."Precio_costo",
                        p."Precio_venta_1",
                        p."Precio_venta_2",
                        p."Precio_venta_3",
                        p."Precio_venta_4",
                        p."Ganancia_1",
                        p."Ganancia_2",
                        p."Ganancia_3",
                        p."Ganancia_4",
                        TRUE,
                        'Inventario Inicial',
                        'Lote generado automáticamente por migración'
                    FROM "PRODUCTOS" p
                    WHERE NOT EXISTS (
                        SELECT 1 FROM "LOTES_PRODUCTO" l WHERE l."ID_Producto" = p."ID_Producto"
                    )
                '''))

            # 3. Columnas de precios en PRODUCTOS
            if "PRODUCTOS" in tables:
                columnas = {columna["name"] for columna in inspector.get_columns("PRODUCTOS")}
                for columna in ("Precio_venta_1", "Precio_venta_2", "Precio_venta_3", "Precio_venta_4"):
                    if columna not in columnas:
                        connection.execute(text(
                            f'ALTER TABLE "PRODUCTOS" ADD COLUMN "{columna}" REAL NOT NULL DEFAULT 0'
                        ))

            # 4. Tipos de factura estándar
            if "TIPO_FACTURA" in tables:
                for identificador, nombre in ((1, "FAC-01"), (2, "FAC-02"), (3, "FAC-03"), (4, "FAC-04")):
                    if dialect == "sqlite":
                        connection.execute(
                            text(
                                'INSERT OR IGNORE INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") '
                                'VALUES (:identificador, :nombre)'
                            ),
                            {"identificador": identificador, "nombre": nombre},
                        )
                    else:  # PostgreSQL
                        connection.execute(
                            text(
                                'INSERT INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") '
                                'VALUES (:identificador, :nombre) '
                                'ON CONFLICT ("ID_Tipo_Factura") DO NOTHING'
                            ),
                            {"identificador": identificador, "nombre": nombre},
                        )

            # 5. Migraciones específicas de SQLite legado
            if dialect == "sqlite" and "TIPO_INGRESO" in tables:
                sql_tipo_ingreso = connection.execute(text(
                    "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'TIPO_INGRESO'"
                )).scalar() or ""
                if (
                    "Venta FAC-01" not in sql_tipo_ingreso
                    or "Venta FAC-CREDITO" not in sql_tipo_ingreso
                    or "FAC-ABONO" not in sql_tipo_ingreso
                ):
                    connection.execute(text("PRAGMA foreign_keys = OFF"))
                    connection.execute(text('ALTER TABLE "TIPO_INGRESO" RENAME TO "TIPO_INGRESO_OLD"'))
                    connection.execute(text(
                        '''CREATE TABLE "TIPO_INGRESO" (
                            "ID_Tipo_Ingreso" INTEGER PRIMARY KEY AUTOINCREMENT,
                            "Tipo_Ingreso" VARCHAR NOT NULL,
                            "ID_Pago_Credito" INTEGER,
                            "ID_Factura" INTEGER,
                            CHECK ("Tipo_Ingreso" IN ('Venta FAC-01', 'Venta FAC-02', 'Venta FAC-03', 'Venta FAC-04', 'Venta FAC-CREDITO', 'FAC-ABONO')),
                            FOREIGN KEY ("ID_Pago_Credito") REFERENCES "PAGO_CREDITO" ("ID_Pago_Credito"),
                            FOREIGN KEY ("ID_Factura") REFERENCES "FACTURA" ("ID_Factura")
                        )'''
                    ))
                    connection.execute(text(
                        '''INSERT INTO "TIPO_INGRESO" (
                            "ID_Tipo_Ingreso", "Tipo_Ingreso", "ID_Pago_Credito", "ID_Factura"
                        )
                        SELECT old."ID_Tipo_Ingreso",
                            CASE
                                WHEN old."Tipo_Ingreso" = 'Venta' AND old."ID_Factura" IS NOT NULL
                                THEN 'Venta ' || factura_tipo."Nombre"
                                WHEN old."Tipo_Ingreso" = 'Abono'
                                THEN 'FAC-ABONO'
                                ELSE old."Tipo_Ingreso"
                            END,
                            old."ID_Pago_Credito", old."ID_Factura"
                        FROM "TIPO_INGRESO_OLD" old
                        LEFT JOIN "FACTURA" factura ON factura."ID_Factura" = old."ID_Factura"
                        LEFT JOIN "TIPO_FACTURA" factura_tipo
                            ON factura_tipo."ID_Tipo_Factura" = factura."ID_Tipo_Factura"'''
                    ))
                    connection.execute(text('DROP TABLE "TIPO_INGRESO_OLD"'))
                    connection.execute(text('PRAGMA foreign_keys = ON'))
    except Exception as e:
        logger.warning(f"Aviso durante la migración de esquema: {e}")


def poblar_datos_iniciales(target_engine=None):
    """Inserta datos base requeridos (roles, métodos de pago, tipos de factura, usuario admin, cliente default)."""
    current_engine = target_engine or get_engine()
    inspector = inspect(current_engine)
    dialect = current_engine.dialect.name
    tables = inspector.get_table_names()

    try:
        with current_engine.begin() as conn:
            # 1. ROLES
            if "ROL" in tables:
                roles = [(1, "ADMINISTRADOR"), (2, "ASESOR")]
                for id_rol, nombre in roles:
                    if dialect == "sqlite":
                        conn.execute(
                            text('INSERT OR IGNORE INTO "ROL" ("ID_Rol", "Nombre") VALUES (:id, :nom)'),
                            {"id": id_rol, "nom": nombre}
                        )
                    else:
                        conn.execute(
                            text('INSERT INTO "ROL" ("ID_Rol", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Rol") DO NOTHING'),
                            {"id": id_rol, "nom": nombre}
                        )
                if dialect == "postgresql":
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"ROL\"', 'ID_Rol'), COALESCE((SELECT MAX(\"ID_Rol\") FROM \"ROL\"), 1))"))
                    except Exception:
                        pass

            # 2. METODO_PAGO
            if "METODO_PAGO" in tables:
                metodos = [(1, "Transferencia"), (2, "Efectivo"), (3, "Mixto")]
                for id_met, nombre in metodos:
                    if dialect == "sqlite":
                        conn.execute(
                            text('INSERT OR IGNORE INTO "METODO_PAGO" ("ID_Metodo_Pago", "Nombre") VALUES (:id, :nom)'),
                            {"id": id_met, "nom": nombre}
                        )
                    else:
                        conn.execute(
                            text('INSERT INTO "METODO_PAGO" ("ID_Metodo_Pago", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Metodo_Pago") DO NOTHING'),
                            {"id": id_met, "nom": nombre}
                        )
                if dialect == "postgresql":
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"METODO_PAGO\"', 'ID_Metodo_Pago'), COALESCE((SELECT MAX(\"ID_Metodo_Pago\") FROM \"METODO_PAGO\"), 1))"))
                    except Exception:
                        pass

            # 3. TIPO_PAGO
            if "TIPO_PAGO" in tables:
                tipos_pago = [(1, "Abono"), (2, "Pago Total")]
                for id_tp, nombre in tipos_pago:
                    if dialect == "sqlite":
                        conn.execute(
                            text('INSERT OR IGNORE INTO "TIPO_PAGO" ("ID_Tipo_Pago", "Nombre") VALUES (:id, :nom)'),
                            {"id": id_tp, "nom": nombre}
                        )
                    else:
                        conn.execute(
                            text('INSERT INTO "TIPO_PAGO" ("ID_Tipo_Pago", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Tipo_Pago") DO NOTHING'),
                            {"id": id_tp, "nom": nombre}
                        )
                if dialect == "postgresql":
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"TIPO_PAGO\"', 'ID_Tipo_Pago'), COALESCE((SELECT MAX(\"ID_Tipo_Pago\") FROM \"TIPO_PAGO\"), 1))"))
                    except Exception:
                        pass

            # 4. TIPO_FACTURA
            if "TIPO_FACTURA" in tables:
                tipos_fac = [(1, "FAC-01"), (2, "FAC-02"), (3, "FAC-03"), (4, "FAC-04"), (5, "FAC-CREDITO")]
                for id_tf, nombre in tipos_fac:
                    if dialect == "sqlite":
                        conn.execute(
                            text('INSERT OR IGNORE INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") VALUES (:id, :nom)'),
                            {"id": id_tf, "nom": nombre}
                        )
                    else:
                        conn.execute(
                            text('INSERT INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Tipo_Factura") DO NOTHING'),
                            {"id": id_tf, "nom": nombre}
                        )
                if dialect == "postgresql":
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"TIPO_FACTURA\"', 'ID_Tipo_Factura'), COALESCE((SELECT MAX(\"ID_Tipo_Factura\") FROM \"TIPO_FACTURA\"), 1))"))
                    except Exception:
                        pass

            # 5. CLIENTE DEFAULT (Consumidor Final)
            if "CLIENTES" in tables:
                if dialect == "sqlite":
                    conn.execute(
                        text('INSERT OR IGNORE INTO "CLIENTES" ("ID_Cliente", "Nombre", "Apellido", "Direccion", "Teléfono") VALUES (:id, :nom, :ape, :dir, :tel)'),
                        {"id": "111", "nom": "Consumidor", "ape": "Final", "dir": "-", "tel": "2222222222"}
                    )
                else:
                    conn.execute(
                        text('INSERT INTO "CLIENTES" ("ID_Cliente", "Nombre", "Apellido", "Direccion", "Teléfono") VALUES (:id, :nom, :ape, :dir, :tel) ON CONFLICT ("ID_Cliente") DO NOTHING'),
                        {"id": "111", "nom": "Consumidor", "ape": "Final", "dir": "-", "tel": "2222222222"}
                    )

            # 6. USUARIO ADMIN DEFAULT (Si no existe ningún usuario)
            if "USUARIOS" in tables:
                count_users = conn.execute(text('SELECT COUNT(*) FROM "USUARIOS"')).scalar() or 0
                if count_users == 0:
                    logger.info("Creando usuario administrador por defecto (admin)...")
                    if dialect == "sqlite":
                        conn.execute(
                            text('INSERT OR IGNORE INTO "USUARIOS" ("ID_Usuario", "Nombre", "Usuario", "Contrasena", "Estado", "ID_Rol", "Permisos") VALUES (:id, :nom, :usr, :pwd, :est, :rol, :perm)'),
                            {
                                "id": "12345678",
                                "nom": "Administrador",
                                "usr": "admin",
                                "pwd": "admin",
                                "est": True,
                                "rol": 1,
                                "perm": "dashboard,ventas,clientes,productos,egresos,reportes,configuracion"
                            }
                        )
                    else:
                        conn.execute(
                            text('INSERT INTO "USUARIOS" ("ID_Usuario", "Nombre", "Usuario", "Contrasena", "Estado", "ID_Rol", "Permisos") VALUES (:id, :nom, :usr, :pwd, :est, :rol, :perm) ON CONFLICT ("ID_Usuario") DO NOTHING'),
                            {
                                "id": "12345678",
                                "nom": "Administrador",
                                "usr": "admin",
                                "pwd": "admin",
                                "est": True,
                                "rol": 1,
                                "perm": "dashboard,ventas,clientes,productos,egresos,reportes,configuracion"
                            }
                        )

            # 7. MARCA Y CATEGORIA DEFAULT
            if "MARCAS" in tables:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "MARCAS" ("ID_Marca", "Nombre") VALUES (1, \'Distri Magik\')'))
                else:
                    conn.execute(text('INSERT INTO "MARCAS" ("ID_Marca", "Nombre") VALUES (1, \'Distri Magik\') ON CONFLICT ("ID_Marca") DO NOTHING'))
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"MARCAS\"', 'ID_Marca'), COALESCE((SELECT MAX(\"ID_Marca\") FROM \"MARCAS\"), 1))"))
                    except Exception:
                        pass

            if "CATEGORIAS" in tables:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "CATEGORIAS" ("ID_Categoria", "Nombre") VALUES (1, \'General\')'))
                else:
                    conn.execute(text('INSERT INTO "CATEGORIAS" ("ID_Categoria", "Nombre") VALUES (1, \'General\') ON CONFLICT ("ID_Categoria") DO NOTHING'))
                    try:
                        conn.execute(text("SELECT setval(pg_get_serial_sequence('\"CATEGORIAS\"', 'ID_Categoria'), COALESCE((SELECT MAX(\"ID_Categoria\") FROM \"CATEGORIAS\"), 1))"))
                    except Exception:
                        pass

            # 8. PRODUCTOS INICIALES — gestionado fuera con ORM (ver bloque siguiente)

        logger.info("Datos iniciales requeridos verificados/poblados con éxito.")
    except Exception as e:
        logger.error(f"Error al poblar datos iniciales: {e}")

    # 8. PRODUCTOS INICIALES — usando ORM fuera del bloque with conn
    try:
        inspector2 = inspect(current_engine)
        if "PRODUCTOS" in inspector2.get_table_names():
            with current_engine.connect() as chk:
                count_prod = chk.execute(text('SELECT COUNT(*) FROM "PRODUCTOS"')).scalar() or 0
            if count_prod == 0:
                logger.info("Insertando 20 productos iniciales con ORM...")
                from app.controllers.producto_crud import crear_producto
                productos_seed = [
                    (1,  "Esmalte rojo",          2500,  6500),
                    (2,  "Esmalte nude",           2500,  6500),
                    (3,  "Esmalte base",           2800,  7000),
                    (4,  "Esmalte brillo",         2800,  7000),
                    (5,  "Removedor de esmalte",   4000,  9000),
                    (6,  "Algodon paquete",        3000,  7000),
                    (7,  "Lima de unas",           1200,  3500),
                    (8,  "Lima pulidora",          1800,  4500),
                    (9,  "Cortaunas",              3500,  8000),
                    (10, "Empujador de cuticula",  2500,  6000),
                    (11, "Aceite de cuticula",     5000, 11000),
                    (12, "Crema para manos",       6500, 14000),
                    (13, "Guantes desechables",    4500,  9500),
                    (14, "Tapabocas paquete",      5000, 11000),
                    (15, "Toallas desechables",    3500,  8000),
                    (16, "Gel constructor",       12000, 25000),
                    (17, "Primer para unas",       7000, 15000),
                    (18, "Lampara UV",            45000, 85000),
                    (19, "Brocha para gel",        3000,  7500),
                    (20, "Decoracion para unas",   4000, 10000),
                ]
                db_seed = SessionLocal()
                try:
                    for (id_p, nombre, costo, pv1) in productos_seed:
                        pv2 = round(pv1 * 0.9)
                        pv3 = round(pv1 * 0.85)
                        pv4 = round(pv1 * 0.8)
                        try:
                            crear_producto(
                                db=db_seed,
                                id_producto=id_p,
                                nombre=nombre,
                                precio_costo=costo,
                                stock_actual=20,
                                stock_min=5,
                                precio_venta_1=pv1,
                                precio_venta_2=pv2,
                                precio_venta_3=pv3,
                                precio_venta_4=pv4,
                                id_marca=1,
                                id_categoria=1,
                            )
                        except Exception as ep:
                            logger.warning(f"Producto {id_p} ({nombre}) omitido: {ep}")
                            db_seed.rollback()
                    logger.info("20 productos iniciales insertados exitosamente.")
                finally:
                    db_seed.close()
    except Exception as e:
        logger.error(f"Error al insertar productos iniciales: {e}")

