from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class DetalleFacturas(Base):
    __tablename__ = "DETALLE_FACTURAS"

    ID_Detalle_Factura = Column(Integer, primary_key=True, autoincrement=True)
    Cantidad = Column(Integer, nullable=False)
    Precio_unitario = Column(Numeric(12, 2, asdecimal=False), nullable=False)
    Subtotal = Column(Numeric(12, 2, asdecimal=False), nullable=False)

    ID_Producto = Column(Integer, ForeignKey("PRODUCTOS.ID_Producto"))
    ID_Factura = Column(Integer, ForeignKey("FACTURA.ID_Factura"))
    ID_Lote = Column(Integer, ForeignKey("LOTES_PRODUCTO.ID_Lote"), nullable=True)

    # Relaciones
    productos = relationship("Productos", back_populates="detallefacturas")
    facturas = relationship("Facturas", back_populates="detallefacturas")
    lote = relationship("LoteProducto", back_populates="detallefacturas")
