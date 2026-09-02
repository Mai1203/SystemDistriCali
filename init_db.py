from app.database.database import init_db, SessionLocal
from app.controllers.usuario_crud import *
from app.controllers.rol_crud import *
from app.controllers.producto_crud import *
from app.controllers.marca_crud import *
from app.controllers.categorias_crud import *
from app.controllers.metodo_pago_crud import *
from app.controllers.tipo_factura_crud import *
from app.controllers.clientes_crud import *
from app.controllers.tipo_pago_crud import *
from app.controllers.tipo_ingreso_crud import *
from app.controllers.ingresos_crud import *
from app.configuracion import TIPOS_VENTA
from app.models.productos import Productos


def conectar_base():
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

def inicializar_db():
    try:
        init_db()
        print("Base de datos Inicializada")
        
    except Exception as e:
        print(f"Error al inicializar base de datos: {e}")
    
    poblar_datos_prueba()

def poblar_datos_prueba():
    db = SessionLocal()
    # Crear usuarios de prueba
    try:
        print("creando cliente default")
        crear_cliente(
            db, 111, "Predeterminado", "Predeterminado", "Predeterminado", "1234567890"
        )
        print("cliente default creado exitosamente.")
    except Exception as e:
        print(f"Error al crear cliente: {e}")
        
    try:
        print("Crear Tipo Pago")
        crear_tipo_pago(db, "Abono")
        crear_tipo_pago(db, "Pago Total")
        print("Tipo Pago creado exitosamente.")
    except Exception as e:
        print(f"Error al crear Tipo Pago: {e}")

    def crear_productos_iniciales(db):
        if db.query(Productos).count() > 0:
            return

        productos = [
            ("Esmalte rojo", "Belleza", 2500, 6500),
            ("Esmalte nude", "Belleza", 2500, 6500),
            ("Esmalte base", "Belleza", 2800, 7000),
            ("Esmalte brillo", "Belleza", 2800, 7000),
            ("Removedor de esmalte", "Cuidado", 4000, 9000),
            ("Algodon paquete", "Cuidado", 3000, 7000),
            ("Lima de unas", "Herramientas", 1200, 3500),
            ("Lima pulidora", "Herramientas", 1800, 4500),
            ("Cortaunas", "Herramientas", 3500, 8000),
            ("Empujador de cuticula", "Herramientas", 2500, 6000),
            ("Aceite de cuticula", "Cuidado", 5000, 11000),
            ("Crema para manos", "Cuidado", 6500, 14000),
            ("Guantes desechables", "Desechables", 4500, 9500),
            ("Tapabocas paquete", "Desechables", 5000, 11000),
            ("Toallas desechables", "Desechables", 3500, 8000),
            ("Gel constructor", "Unas", 12000, 25000),
            ("Primer para unas", "Unas", 7000, 15000),
            ("Lampara UV", "Equipos", 45000, 85000),
            ("Brocha para gel", "Herramientas", 3000, 7500),
            ("Decoracion para unas", "Decoracion", 4000, 10000),
        ]

        for indice, (nombre, categoria, costo, precio) in enumerate(productos, start=1):
            id_marca = obtener_o_crear_marca(db, "Lady Nail")
            id_categoria = obtener_o_crear_categoria(db, categoria)
            crear_producto(
                db=db,
                id_producto=indice,
                nombre=nombre,
                precio_costo=costo,
                stock_actual=20,
                stock_min=5,
                precio_venta_1=precio,
                precio_venta_2=precio * 0.9,
                precio_venta_3=precio * 0.85,
                precio_venta_4=precio * 0.8,
                id_marca=id_marca,
                id_categoria=id_categoria,
            )

        print("20 productos iniciales creados exitosamente.")

    try:
        crear_productos_iniciales(db)
    except Exception as e:
        print(f"Error al crear productos iniciales: {e}")

    try:
        print("creando Tipo Facturas")
        for tipo in TIPOS_VENTA.values():
            crear_tipo_factura(db, tipo["factura"])
        crear_tipo_factura(db, "FAC-CREDITO")
        print("Tipo Facturas creados exitosamente.")
    except Exception as e:
        print(f"Error al crear Tipo Facturas: {e}")

    try:
        print("Creando rols de prueba...")
        crear_rol(db, "ADMINISTRADOR")
        crear_rol(db, "ASESOR")
        print("Rols de prueba creados exitosamente.")
    except Exception as e:
        print(f"Error al poblar datos: {e}")

    try:
        print("Creando usuarios de prueba...")
        '''crear_usuario(db, 87068087, "John Jairo Uribe", "Super_admin25", "John$Adm!n_32", True, 1)'''
        crear_usuario(db, 12345678, "Administrador", "admin", "admin", True, 1)
        print("usuarios de prueba creados exitosamente.")
    except Exception as e:
        print(f"Error al poblar datos: {e}")

    try:
        print("Creando metodos de pago ...")
        
        crear_metodo_pago(db, "Transferencia")
        crear_metodo_pago(db, "Efectivo")
        crear_metodo_pago(db, "Mixto")
    except Exception as e:
        print(f"Error al poblar datos: {e}")
    db.close()

    
