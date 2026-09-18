from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from app.database.manager import db_manager
from app.utils.logger import logger

class DatabaseSeeder:
    """Clase responsable de inyectar datos iniciales y por defecto de la aplicación."""

    @staticmethod
    def _seed_basic_tables(conn, dialect: str, tables: list):
        # 1. ROLES
        if "ROL" in tables:
            roles = [(1, "ADMINISTRADOR"), (2, "ASESOR")]
            for id_rol, nombre in roles:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "ROL" ("ID_Rol", "Nombre") VALUES (:id, :nom)'), {"id": id_rol, "nom": nombre})
                else:
                    conn.execute(text('INSERT INTO "ROL" ("ID_Rol", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Rol") DO NOTHING'), {"id": id_rol, "nom": nombre})
            if dialect == "postgresql":
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"ROL\"', 'ID_Rol'), COALESCE((SELECT MAX(\"ID_Rol\") FROM \"ROL\"), 1))"))
                except:
                    pass

        # 2. METODO_PAGO
        if "METODO_PAGO" in tables:
            metodos = [(1, "Transferencia"), (2, "Efectivo"), (3, "Mixto")]
            for id_met, nombre in metodos:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "METODO_PAGO" ("ID_Metodo_Pago", "Nombre") VALUES (:id, :nom)'), {"id": id_met, "nom": nombre})
                else:
                    conn.execute(text('INSERT INTO "METODO_PAGO" ("ID_Metodo_Pago", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Metodo_Pago") DO NOTHING'), {"id": id_met, "nom": nombre})
            if dialect == "postgresql":
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"METODO_PAGO\"', 'ID_Metodo_Pago'), COALESCE((SELECT MAX(\"ID_Metodo_Pago\") FROM \"METODO_PAGO\"), 1))"))
                except:
                    pass

        # 3. TIPO_PAGO
        if "TIPO_PAGO" in tables:
            tipos_pago = [(1, "Abono"), (2, "Pago Total")]
            for id_tp, nombre in tipos_pago:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "TIPO_PAGO" ("ID_Tipo_Pago", "Nombre") VALUES (:id, :nom)'), {"id": id_tp, "nom": nombre})
                else:
                    conn.execute(text('INSERT INTO "TIPO_PAGO" ("ID_Tipo_Pago", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Tipo_Pago") DO NOTHING'), {"id": id_tp, "nom": nombre})
            if dialect == "postgresql":
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"TIPO_PAGO\"', 'ID_Tipo_Pago'), COALESCE((SELECT MAX(\"ID_Tipo_Pago\") FROM \"TIPO_PAGO\"), 1))"))
                except:
                    pass

        # 4. TIPO_FACTURA
        if "TIPO_FACTURA" in tables:
            tipos_fac = [(1, "FAC-01"), (2, "FAC-02"), (3, "FAC-03"), (4, "FAC-04"), (5, "FAC-CREDITO")]
            for id_tf, nombre in tipos_fac:
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") VALUES (:id, :nom)'), {"id": id_tf, "nom": nombre})
                else:
                    conn.execute(text('INSERT INTO "TIPO_FACTURA" ("ID_Tipo_Factura", "Nombre") VALUES (:id, :nom) ON CONFLICT ("ID_Tipo_Factura") DO NOTHING'), {"id": id_tf, "nom": nombre})
            if dialect == "postgresql":
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"TIPO_FACTURA\"', 'ID_Tipo_Factura'), COALESCE((SELECT MAX(\"ID_Tipo_Factura\") FROM \"TIPO_FACTURA\"), 1))"))
                except:
                    pass

        # 5. CLIENTE DEFAULT (Consumidor Final)
        if "CLIENTES" in tables:
            if dialect == "sqlite":
                conn.execute(text('INSERT OR IGNORE INTO "CLIENTES" ("ID_Cliente", "Nombre", "Apellido", "Direccion", "Teléfono") VALUES (:id, :nom, :ape, :dir, :tel)'), {"id": "111", "nom": "Consumidor", "ape": "Final", "dir": "-", "tel": "2222222222"})
            else:
                conn.execute(text('INSERT INTO "CLIENTES" ("ID_Cliente", "Nombre", "Apellido", "Direccion", "Teléfono") VALUES (:id, :nom, :ape, :dir, :tel) ON CONFLICT ("ID_Cliente") DO NOTHING'), {"id": "111", "nom": "Consumidor", "ape": "Final", "dir": "-", "tel": "2222222222"})

        # 6. USUARIO ADMIN DEFAULT
        if "USUARIOS" in tables:
            count_users = conn.execute(text('SELECT COUNT(*) FROM "USUARIOS"')).scalar() or 0
            if count_users == 0:
                logger.info("Creando usuario administrador por defecto (admin)...")
                admin_data = {
                    "id": "12345678",
                    "nom": "Administrador",
                    "usr": "admin",
                    "pwd": "admin",
                    "est": True,
                    "rol": 1,
                    "perm": "dashboard,ventas,clientes,productos,egresos,reportes,configuracion"
                }
                if dialect == "sqlite":
                    conn.execute(text('INSERT OR IGNORE INTO "USUARIOS" ("ID_Usuario", "Nombre", "Usuario", "Contrasena", "Estado", "ID_Rol", "Permisos") VALUES (:id, :nom, :usr, :pwd, :est, :rol, :perm)'), admin_data)
                else:
                    conn.execute(text('INSERT INTO "USUARIOS" ("ID_Usuario", "Nombre", "Usuario", "Contrasena", "Estado", "ID_Rol", "Permisos") VALUES (:id, :nom, :usr, :pwd, :est, :rol, :perm) ON CONFLICT ("ID_Usuario") DO NOTHING'), admin_data)

        # 7. MARCA Y CATEGORIA DEFAULT
        if "MARCAS" in tables:
            if dialect == "sqlite":
                conn.execute(text('INSERT OR IGNORE INTO "MARCAS" ("ID_Marca", "Nombre") VALUES (1, \'Distri Magik\')'))
            else:
                conn.execute(text('INSERT INTO "MARCAS" ("ID_Marca", "Nombre") VALUES (1, \'Distri Magik\') ON CONFLICT ("ID_Marca") DO NOTHING'))
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"MARCAS\"', 'ID_Marca'), COALESCE((SELECT MAX(\"ID_Marca\") FROM \"MARCAS\"), 1))"))
                except:
                    pass

        if "CATEGORIAS" in tables:
            if dialect == "sqlite":
                conn.execute(text('INSERT OR IGNORE INTO "CATEGORIAS" ("ID_Categoria", "Nombre") VALUES (1, \'General\')'))
            else:
                conn.execute(text('INSERT INTO "CATEGORIAS" ("ID_Categoria", "Nombre") VALUES (1, \'General\') ON CONFLICT ("ID_Categoria") DO NOTHING'))
                try:
                    conn.execute(text("SELECT setval(pg_get_serial_sequence('\"CATEGORIAS\"', 'ID_Categoria'), COALESCE((SELECT MAX(\"ID_Categoria\") FROM \"CATEGORIAS\"), 1))"))
                except:
                    pass

    @staticmethod
    def _seed_products():
        engine = db_manager.get_engine()
        inspector2 = inspect(engine)
        if not inspector2.has_table("PRODUCTOS"):
            return

        with engine.connect() as chk:
            count_prod = chk.execute(text('SELECT COUNT(*) FROM "PRODUCTOS"')).scalar() or 0

        if count_prod > 0:
            return

        logger.info("Insertando 20 productos iniciales con ORM...")
        from app.models.lotes import LoteProducto
        from app.models.productos import Productos

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

        print("[DEBUG] Iniciando transacción para productos...", flush=True)
        with Session(bind=engine) as db_seed:
            for id_producto, nombre, costo, pv1 in productos_seed:
                pv2 = round(pv1 * 0.9)
                pv3 = round(pv1 * 0.85)
                pv4 = round(pv1 * 0.8)
                estado = True
                ganancia_1 = pv1 - costo
                ganancia_2 = pv2 - costo
                ganancia_3 = pv3 - costo
                ganancia_4 = pv4 - costo

                db_seed.add(Productos(
                    ID_Producto=id_producto,
                    Nombre=nombre,
                    Precio_costo=costo,
                    Precio_venta_1=pv1,
                    Precio_venta_2=pv2,
                    Precio_venta_3=pv3,
                    Precio_venta_4=pv4,
                    Ganancia_1=ganancia_1,
                    Ganancia_2=ganancia_2,
                    Ganancia_3=ganancia_3,
                    Ganancia_4=ganancia_4,
                    Stock_actual=20,
                    Stock_min=5,
                    ID_Marca=1,
                    ID_Categoria=1,
                    Estado=estado,
                ))
                db_seed.add(LoteProducto(
                    ID_Producto=id_producto,
                    Numero_Lote="LOTE-001",
                    Stock_inicial=20,
                    Stock_actual=20,
                    Precio_costo=costo,
                    Precio_venta_1=pv1,
                    Precio_venta_2=pv2,
                    Precio_venta_3=pv3,
                    Precio_venta_4=pv4,
                    Ganancia_1=ganancia_1,
                    Ganancia_2=ganancia_2,
                    Ganancia_3=ganancia_3,
                    Ganancia_4=ganancia_4,
                    Estado=estado,
                    Proveedor="Inventario Inicial",
                    Notas="Lote inicial al crear el producto",
                ))
                print(f"[DEBUG] Producto preparado: {nombre}", flush=True)

            db_seed.commit()
            print("[DEBUG] Commit de productos completado.", flush=True)
        logger.info("20 productos iniciales procesados exitosamente.")

    @classmethod
    def run_all_seeds(cls):
        """Ejecuta todos los seeds si las tablas están vacías."""
        engine = db_manager.get_engine()
        inspector = inspect(engine)
        dialect = engine.dialect.name
        tables = inspector.get_table_names()

        try:
            with engine.begin() as conn:
                print("[DEBUG] cls._seed_basic_tables() empezando...", flush=True)
                cls._seed_basic_tables(conn, dialect, tables)
                print("[DEBUG] cls._seed_basic_tables() completado.", flush=True)
            logger.info("Datos básicos verificados/poblados con éxito.")
        except Exception as e:
            logger.error(f"Error al poblar datos iniciales básicos: {e}")

        try:
            print("[DEBUG] cls._seed_products() empezando...", flush=True)
            cls._seed_products()
            print("[DEBUG] cls._seed_products() completado.", flush=True)
        except Exception as e:
            logger.error(f"Error al poblar productos iniciales: {e}")
