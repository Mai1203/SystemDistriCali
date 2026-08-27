from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
from pathlib import Path
import os

# Obtener la carpeta segura para almacenar la base de datos
app_data_dir = Path(os.getenv("APPDATA") or os.path.expanduser("~/.local/share")) / "Systock"
app_data_dir.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe

# Nueva ruta para la base de datos
DATABASE_PATH = app_data_dir / "ladynails-cali.db"
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
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'F-01\' WHERE "Nombre" = \'Factura A\''
        ))
        connection.execute(text(
            'UPDATE "TIPO_FACTURA" SET "Nombre" = \'F-02\' WHERE "Nombre" = \'Factura B\''
        ))
        for identificador, nombre in ((1, "F-01"), (2, "F-02"), (3, "F-03"), (4, "F-04")):
            connection.execute(
                text(
                    'INSERT OR IGNORE INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") '
                    'VALUES (:identificador, :nombre)'
                ),
                {"identificador": identificador, "nombre": nombre},
            )
