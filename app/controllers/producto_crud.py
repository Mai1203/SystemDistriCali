from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import or_
from app.models.productos import Productos
from app.models.productos import Marcas
from app.models.productos import Categorias
from app.models.facturas import Facturas
from app.models.detalle_facturas import DetalleFacturas


def redondear_a_cientos(numero):
    """
    Redondea el número hacia el siguiente múltiplo de 100.
    Siempre redondea hacia arriba.
    """
    if numero is None:  # Comprobar si el número es None
        raise ValueError("El valor de 'numero' no puede ser None")

    if not isinstance(numero, (int, float)):  # Verifica que el número sea int o float
        raise TypeError("El valor debe ser un número entero o flotante")

    if numero % 100 == 0:
        return numero  # Ya es múltiplo de 100

    return ((numero // 100) + 1) * 100


def calcular_ganancia(precio_venta, precio_costo):
    return precio_venta - precio_costo


def calcular_precio(precio_costo, porcentaje):
    return redondear_a_cientos(precio_costo + (precio_costo * porcentaje))


def cambiar_estado(stock_actual):
    if stock_actual > 0:
        return True
    else:
        return False


# Crear un producto
def crear_producto(
    db: Session,
    id_producto: int,
    nombre: str,
    precio_costo: float,
    stock_actual: int,
    stock_min: int,
    precio_venta_1: float,
    precio_venta_2: float,
    id_marca: int,
    id_categoria: int,
    precio_venta_3: float = 0,
    precio_venta_4: float = 0,
):
    """
    Crea un nuevo producto.
    """
    estado = cambiar_estado(stock_actual)

    ganancia_1 = calcular_ganancia(precio_venta_1, precio_costo)
    ganancia_2 = calcular_ganancia(precio_venta_2, precio_costo)
    ganancia_3 = calcular_ganancia(precio_venta_3, precio_costo)
    ganancia_4 = calcular_ganancia(precio_venta_4, precio_costo)

    nuevo_producto = Productos(
        ID_Producto=id_producto,
        Nombre=nombre,
        Precio_costo=precio_costo,
        Precio_venta_1=precio_venta_1,
        Precio_venta_2=precio_venta_2,
        Precio_venta_3=precio_venta_3,
        Precio_venta_4=precio_venta_4,
        Ganancia_1=ganancia_1,
        Ganancia_2=ganancia_2,
        Ganancia_3=ganancia_3,
        Ganancia_4=ganancia_4,
        Stock_actual=stock_actual,
        Stock_min=stock_min,
        ID_Marca=id_marca,
        ID_Categoria=id_categoria,
        Estado=estado,
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

def obtener_productos_mas_vendidos(db: Session, limite=20):
    resultados = (
        db.query(
            Productos.ID_Producto,
            Productos.Nombre,
            func.sum(DetalleFacturas.Cantidad).label("Total_Unidades_Vendidas"),
            func.sum(DetalleFacturas.Subtotal).label("Total_Ganado"),
        )
        .join(DetalleFacturas, Productos.ID_Producto == DetalleFacturas.ID_Producto)
        .group_by(Productos.ID_Producto, Productos.Nombre)
        .order_by(func.sum(DetalleFacturas.Cantidad).desc())
        .limit(limite)
        .all()
    )

    return resultados

# Obtener todos los productos
def obtener_productos(db: Session):
    """
    Obtiene los productos junto con el nombre de la marca y la categoría.
    """
    productos = (
        db.query(
            Productos.ID_Producto,
            Productos.Nombre,
            Productos.Precio_costo,
            Productos.Precio_venta_1,
            Productos.Precio_venta_2,
            Productos.Precio_venta_3,
            Productos.Precio_venta_4,
            Productos.Ganancia_1,
            Productos.Ganancia_2,
            Productos.Ganancia_3,
            Productos.Ganancia_4,
            Productos.Stock_actual,
            Productos.Stock_min,
            Productos.Estado,
            Marcas.Nombre.label("marcas"),
            Categorias.Nombre.label("categorias"),
        )
        .join(Marcas, Productos.ID_Marca == Marcas.ID_Marca)
        .join(Categorias, Productos.ID_Categoria == Categorias.ID_Categoria)
        .all()
    )
    return productos


# Obtener un producto por ID
def obtener_producto_por_id(db: Session, id_producto: int):
    productos = (
        db.query(
            Productos.ID_Producto,
            Productos.Nombre,
            Productos.Precio_costo,
            Productos.Precio_venta_1,
            Productos.Precio_venta_2,
            Productos.Precio_venta_3,
            Productos.Precio_venta_4,
            Productos.Ganancia_1,
            Productos.Ganancia_2,
            Productos.Ganancia_3,
            Productos.Ganancia_4,
            Productos.Stock_actual,
            Productos.Stock_min,
            Marcas.Nombre.label("marcas"),
            Categorias.Nombre.label("categorias"),
        )
        .join(Marcas, Productos.ID_Marca == Marcas.ID_Marca)
        .join(Categorias, Productos.ID_Categoria == Categorias.ID_Categoria)
        .filter(Productos.ID_Producto == id_producto)
        .all()
    )
    return productos


def buscar_productos(db: Session, busqueda: str):
    """
    Busca productos por código, nombre, marca o categoría.
    """
    if not busqueda:
        return None

    productos = (
        db.query(
            Productos.ID_Producto,
            Productos.Nombre,
            Productos.Precio_costo,
            Productos.Precio_venta_1,
            Productos.Precio_venta_2,
            Productos.Precio_venta_3,
            Productos.Precio_venta_4,
            Productos.Ganancia_1,
            Productos.Ganancia_2,
            Productos.Ganancia_3,
            Productos.Ganancia_4,
            Productos.Stock_actual,
            Productos.Stock_min,
            Productos.Estado,
            Marcas.Nombre.label("marcas"),
            Categorias.Nombre.label("categorias"),
        )
        .join(Marcas, Productos.ID_Marca == Marcas.ID_Marca)
        .join(Categorias, Productos.ID_Categoria == Categorias.ID_Categoria)
        .filter(
            or_(
                Productos.Nombre.like(f"%{busqueda}%"),
                Productos.ID_Producto.like(f"%{busqueda}%"),
                Marcas.Nombre.like(f"%{busqueda}%"),
                Categorias.Nombre.like(f"%{busqueda}%"),
            )
        )
        .all()
    )
    return productos


# Actualizar un producto
def actualizar_producto(
    db: Session,
    id_producto: int,
    nombre: str = None,
    precio_costo: float = None,
    precio_venta_1: float = None,
    precio_venta_2: float = None,
    precio_venta_3: float = None,
    precio_venta_4: float = None,
    stock_actual: int = None,
    stock_min: int = None,
    id_marca: int = None,
    id_categoria: int = None,
):
    """
    Actualiza un producto existente.
    """
    producto_existente = (
        db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
    )
    if not producto_existente:
        return None

    # Actualizar valores si se proporcionan
    if nombre:
        producto_existente.Nombre = nombre
    if precio_costo:
        producto_existente.Precio_costo = precio_costo

    if precio_venta_1 is not None:
        producto_existente.Precio_venta_1 = precio_venta_1
    if precio_venta_2 is not None:
        producto_existente.Precio_venta_2 = precio_venta_2
    if precio_venta_3 is not None:
        producto_existente.Precio_venta_3 = precio_venta_3
    if precio_venta_4 is not None:
        producto_existente.Precio_venta_4 = precio_venta_4

    # Recalcular ganancias si precio_costo o precios de venta fueron actualizados
    if precio_costo or precio_venta_1 is not None:
        producto_existente.Ganancia_1 = calcular_ganancia(
            producto_existente.Precio_venta_1, producto_existente.Precio_costo
        )
        
    if precio_costo or precio_venta_2 is not None:
        producto_existente.Ganancia_2 = calcular_ganancia(
            producto_existente.Precio_venta_2, producto_existente.Precio_costo
        )

    if precio_costo or precio_venta_3 is not None:
        producto_existente.Ganancia_3 = calcular_ganancia(
            producto_existente.Precio_venta_3, producto_existente.Precio_costo
        )
        
    if precio_costo or precio_venta_4 is not None:
        producto_existente.Ganancia_4 = calcular_ganancia(
            producto_existente.Precio_venta_4, producto_existente.Precio_costo
        )

    if stock_actual is not None:
        producto_existente.Stock_actual = stock_actual
        # Actualizar estado según el nuevo stock_actual
        producto_existente.Estado = cambiar_estado(stock_actual)
    if stock_min is not None:
        producto_existente.Stock_min = stock_min

    if id_marca:
        producto_existente.ID_Marca = id_marca
    if id_categoria:
        producto_existente.ID_Categoria = id_categoria

    db.commit()
    db.refresh(producto_existente)
    return producto_existente


# Eliminar un producto
def eliminar_producto(db: Session, id_producto: int):
    """
    Elimina un producto por su ID.
    """
    producto_existente = (
        db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
    )
    if not producto_existente:
        return False

    db.delete(producto_existente)
    db.commit()
    return True


# Verificar el stock de un producto
def verificar_stock(db: Session, id_producto: int):
    """
    Verifica si el stock de un producto está por debajo del mínimo.
    """
    producto = db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
    if producto:
        if producto.Stock_actual < producto.Stock_min:
            return f"Advertencia: El stock del producto '{producto.Nombre}' está por debajo del mínimo permitido."
        return f"El stock del producto '{producto.Nombre}' está dentro del rango permitido."
    return "Producto no encontrado."
