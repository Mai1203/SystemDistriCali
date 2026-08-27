from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
from pathlib import Path
import os

# Obtener la carpeta segura para almacenar la base de datos
app_data_dir = Path(os.getenv("APPDATA") or os.path.expanduser("~/.local/share")) / "SystemDistriCali"
app_data_dir.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe

# Nueva ruta para la base de datos
DATABASE_PATH = app_data_dir / "systemdistricali.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"  # Formato correcto para SQLAlchemy

# Crear el motor de conexión
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base para los modelos
Base = declarative_base()

# Crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa la base de datos (crea tablas si no existen)."""
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
    )  # Importar los modelos

    try:
        configure_mappers()  # Configura todos los mapeos
    except Exception as e:
        print(f"Error al configurar los mappers: {e}")

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        columnas = {columna["name"] for columna in inspect(engine).get_columns("USUARIOS")}
        if "Permisos" not in columnas:
            connection.execute(text(
                'ALTER TABLE "USUARIOS" ADD COLUMN "Permisos" VARCHAR(500) NOT NULL DEFAULT \'\''
            ))
    migrar_esquema()


def migrar_esquema():
    """Añade los PV nuevos y actualiza los tipos de factura sin perder datos."""
    inspector = inspect(engine)

    with engine.begin() as connection:
        columnas = {columna["name"] for columna in inspector.get_columns("PRODUCTOS")}
        for columna in ("Precio_venta_1", "Precio_venta_2", "Precio_venta_3", "Precio_venta_4"):
            if columna not in columnas:
                connection.execute(text(
                    f'ALTER TABLE "PRODUCTOS" ADD COLUMN "{columna}" REAL NOT NULL DEFAULT 0'
                ))

        connection.execute(text(
            'UPDATE "PRODUCTOS" SET "Precio_venta_1" = "Precio_venta_normal" '
            'WHERE "Precio_venta_1" = 0'
        ))
        connection.execute(text(
            'UPDATE "PRODUCTOS" SET "Precio_venta_2" = "Precio_venta_mayor" '
            'WHERE "Precio_venta_2" = 0'
        ))
        connection.execute(text(
            'UPDATE "PRODUCTOS" SET "Precio_venta_3" = "Precio_venta_1" '
            'WHERE "Precio_venta_3" = 0'
        ))
        connection.execute(text(
            'UPDATE "PRODUCTOS" SET "Precio_venta_4" = "Precio_venta_2" '
            'WHERE "Precio_venta_4" = 0'
        ))

        connection.execute(text("PRAGMA ignore_check_constraints = ON"))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'FAC-01\' WHERE "Nombre" IN (\'Factura A\', \'F-01\')'
        ))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'FAC-02\' WHERE "Nombre" IN (\'Factura B\', \'F-02\')'
        ))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'FAC-03\' WHERE "Nombre" = \'F-03\''
        ))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'FAC-04\' WHERE "Nombre" = \'F-04\''
        ))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'FAC-CREDITO\' WHERE "Nombre" = \'Credito\''
        ))
        for identificador, nombre in ((1, "FAC-01"), (2, "FAC-02"), (3, "FAC-03"), (4, "FAC-04")):
            connection.execute(
                text(
                    'INSERT OR IGNORE INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") '
                    'VALUES (:identificador, :nombre)'
                ),
                {"identificador": identificador, "nombre": nombre},
            )

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
