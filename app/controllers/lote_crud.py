from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.lotes import LoteProducto
from app.models.productos import Productos
from app.models.detalle_facturas import DetalleFacturas


def calcular_ganancia(precio_venta, precio_costo):
    return (precio_venta or 0) - (precio_costo or 0)


def sincronizar_producto_con_lotes(db: Session, id_producto: int):
    """
    Recalcula el Stock_actual del producto como la suma del Stock_actual de todos sus lotes,
    y actualiza los precios del producto con los del lote más reciente activo (o el último creado).
    """
    producto = db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
    if not producto:
        return None

    # Suma de stock de todos los lotes
    total_stock = (
        db.query(func.coalesce(func.sum(LoteProducto.Stock_actual), 0))
        .filter(LoteProducto.ID_Producto == id_producto)
        .scalar()
    )
    producto.Stock_actual = total_stock
    producto.Estado = total_stock > 0

    # Obtener el lote más reciente (preferiblemente con stock, o el último registrado)
    ultimo_lote = (
        db.query(LoteProducto)
        .filter(LoteProducto.ID_Producto == id_producto, LoteProducto.Stock_actual > 0)
        .order_by(desc(LoteProducto.ID_Lote))
        .first()
    )
    if not ultimo_lote:
        ultimo_lote = (
            db.query(LoteProducto)
            .filter(LoteProducto.ID_Producto == id_producto)
            .order_by(desc(LoteProducto.ID_Lote))
            .first()
        )

    if ultimo_lote:
        producto.Precio_costo = ultimo_lote.Precio_costo
        producto.Precio_venta_1 = ultimo_lote.Precio_venta_1
        producto.Precio_venta_2 = ultimo_lote.Precio_venta_2
        producto.Precio_venta_3 = ultimo_lote.Precio_venta_3
        producto.Precio_venta_4 = ultimo_lote.Precio_venta_4
        producto.Ganancia_1 = ultimo_lote.Ganancia_1
        producto.Ganancia_2 = ultimo_lote.Ganancia_2
        producto.Ganancia_3 = ultimo_lote.Ganancia_3
        producto.Ganancia_4 = ultimo_lote.Ganancia_4

    db.commit()
    db.refresh(producto)
    return producto


def crear_lote(
    db: Session,
    id_producto: int,
    numero_lote: str,
    precio_costo: float,
    stock_inicial: int,
    precio_venta_1: float,
    precio_venta_2: float,
    precio_venta_3: float = 0.0,
    precio_venta_4: float = 0.0,
    fecha_vencimiento: str = None,
    proveedor: str = None,
    notas: str = None,
):
    """
    Crea un nuevo lote para un producto y sincroniza el stock/precios del producto.
    """
    ganancia_1 = calcular_ganancia(precio_venta_1, precio_costo)
    ganancia_2 = calcular_ganancia(precio_venta_2, precio_costo)
    ganancia_3 = calcular_ganancia(precio_venta_3, precio_costo)
    ganancia_4 = calcular_ganancia(precio_venta_4, precio_costo)
    estado = stock_inicial > 0

    nuevo_lote = LoteProducto(
        ID_Producto=id_producto,
        Numero_Lote=numero_lote,
        Fecha_Vencimiento=fecha_vencimiento,
        Stock_inicial=stock_inicial,
        Stock_actual=stock_inicial,
        Precio_costo=precio_costo,
        Precio_venta_1=precio_venta_1,
        Precio_venta_2=precio_venta_2,
        Precio_venta_3=precio_venta_3,
        Precio_venta_4=precio_venta_4,
        Ganancia_1=ganancia_1,
        Ganancia_2=ganancia_2,
        Ganancia_3=ganancia_3,
        Ganancia_4=ganancia_4,
        Estado=estado,
        Proveedor=proveedor,
        Notas=notas,
    )
    db.add(nuevo_lote)
    db.commit()
    db.refresh(nuevo_lote)

    # Sincronizar producto
    sincronizar_producto_con_lotes(db, id_producto)

    return nuevo_lote


def obtener_lotes_por_producto(db: Session, id_producto: int, solo_disponibles: bool = False):
    """
    Devuelve los lotes de un producto. Si solo_disponibles=True, solo los que tienen Stock_actual > 0.
    """
    query = db.query(LoteProducto).filter(LoteProducto.ID_Producto == id_producto)
    if solo_disponibles:
        query = query.filter(LoteProducto.Stock_actual > 0, LoteProducto.Estado == True)
    return query.order_by(desc(LoteProducto.ID_Lote)).all()


def obtener_lote_por_id(db: Session, id_lote: int):
    """
    Obtiene un lote por su ID.
    """
    return db.query(LoteProducto).filter(LoteProducto.ID_Lote == id_lote).first()


def actualizar_lote(
    db: Session,
    id_lote: int,
    numero_lote: str = None,
    precio_costo: float = None,
    precio_venta_1: float = None,
    precio_venta_2: float = None,
    precio_venta_3: float = None,
    precio_venta_4: float = None,
    stock_actual: int = None,
    fecha_vencimiento: str = None,
    proveedor: str = None,
    notas: str = None,
):
    """
    Actualiza los datos de un lote y sincroniza el producto.
    """
    lote = db.query(LoteProducto).filter(LoteProducto.ID_Lote == id_lote).first()
    if not lote:
        return None

    if numero_lote is not None:
        lote.Numero_Lote = numero_lote
    if precio_costo is not None:
        lote.Precio_costo = precio_costo
    if precio_venta_1 is not None:
        lote.Precio_venta_1 = precio_venta_1
    if precio_venta_2 is not None:
        lote.Precio_venta_2 = precio_venta_2
    if precio_venta_3 is not None:
        lote.Precio_venta_3 = precio_venta_3
    if precio_venta_4 is not None:
        lote.Precio_venta_4 = precio_venta_4

    # Recalcular ganancias
    lote.Ganancia_1 = calcular_ganancia(lote.Precio_venta_1, lote.Precio_costo)
    lote.Ganancia_2 = calcular_ganancia(lote.Precio_venta_2, lote.Precio_costo)
    lote.Ganancia_3 = calcular_ganancia(lote.Precio_venta_3, lote.Precio_costo)
    lote.Ganancia_4 = calcular_ganancia(lote.Precio_venta_4, lote.Precio_costo)

    if stock_actual is not None:
        lote.Stock_actual = stock_actual
        lote.Estado = stock_actual > 0

    if fecha_vencimiento is not None:
        lote.Fecha_Vencimiento = fecha_vencimiento
    if proveedor is not None:
        lote.Proveedor = proveedor
    if notas is not None:
        lote.Notas = notas

    db.commit()
    db.refresh(lote)

    # Sincronizar producto
    sincronizar_producto_con_lotes(db, lote.ID_Producto)

    return lote


def eliminar_lote(db: Session, id_lote: int):
    """
    Elimina un lote si no tiene facturas asociadas.
    """
    lote = db.query(LoteProducto).filter(LoteProducto.ID_Lote == id_lote).first()
    if not lote:
        return False, "Lote no encontrado."

    detalles = db.query(DetalleFacturas).filter(DetalleFacturas.ID_Lote == id_lote).first()
    if detalles:
        return False, "No se puede eliminar el lote porque ya tiene ventas registradas. Puede cambiar su stock a 0."

    id_producto = lote.ID_Producto
    db.delete(lote)
    db.commit()

    # Sincronizar producto
    sincronizar_producto_con_lotes(db, id_producto)
    return True, "Lote eliminado correctamente."


def descontar_stock_lote(db: Session, id_lote: int, cantidad: int):
    """
    Descuenta stock de un lote específico y sincroniza el producto.
    """
    lote = db.query(LoteProducto).filter(LoteProducto.ID_Lote == id_lote).first()
    if not lote:
        return False, "Lote no encontrado."

    if lote.Stock_actual < cantidad:
        return False, f"Stock insuficiente en el lote {lote.Numero_Lote or lote.ID_Lote}. Disponible: {lote.Stock_actual}"

    lote.Stock_actual -= cantidad
    lote.Estado = lote.Stock_actual > 0
    db.commit()

    # Sincronizar stock total del producto
    sincronizar_producto_con_lotes(db, lote.ID_Producto)
    return True, lote


def restaurar_stock_lote(db: Session, id_lote: int, cantidad: int):
    """
    Restaura stock a un lote (por ejemplo al anular o eliminar una venta).
    """
    lote = db.query(LoteProducto).filter(LoteProducto.ID_Lote == id_lote).first()
    if not lote:
        return False, "Lote no encontrado."

    lote.Stock_actual += cantidad
    lote.Estado = lote.Stock_actual > 0
    db.commit()

    sincronizar_producto_con_lotes(db, lote.ID_Producto)
    return True, lote
