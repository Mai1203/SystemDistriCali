from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, func
from app.models.lotes import LoteProducto
from app.models.productos import Productos

def sync_stock_producto(mapper, connection, target):
    """
    Recalcula y actualiza el Stock_actual de Productos cada vez que un Lote cambia.
    """
    # Usamos connection.execute para actualizar directamente en la BD
    # sin interferir con la sesión actual
    stmt = (
        Productos.__table__.update()
        .where(Productos.__table__.c.ID_Producto == target.ID_Producto)
        .values(
            Stock_actual=select(func.coalesce(func.sum(LoteProducto.Stock_actual), 0))
            .where(LoteProducto.ID_Producto == target.ID_Producto)
            .scalar_subquery(),
            # Actualizamos también el estado: True si hay stock, False si es 0
            Estado=select(func.coalesce(func.sum(LoteProducto.Stock_actual), 0) > 0)
            .where(LoteProducto.ID_Producto == target.ID_Producto)
            .scalar_subquery()
        )
    )
    connection.execute(stmt)

# Conectamos el evento a INSERT, UPDATE y DELETE del LoteProducto
@event.listens_for(LoteProducto, 'after_insert')
def after_insert_lote(mapper, connection, target):
    sync_stock_producto(mapper, connection, target)

@event.listens_for(LoteProducto, 'after_update')
def after_update_lote(mapper, connection, target):
    sync_stock_producto(mapper, connection, target)

@event.listens_for(LoteProducto, 'after_delete')
def after_delete_lote(mapper, connection, target):
    sync_stock_producto(mapper, connection, target)
