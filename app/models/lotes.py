from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from pytz import timezone


def get_local_time():
    try:
        local_tz = timezone("America/Bogota")
        now = datetime.now(local_tz)
        return now.replace(microsecond=0)
    except Exception:
        return datetime.now().replace(microsecond=0)


class LoteProducto(Base):
    __tablename__ = "LOTES_PRODUCTO"

    ID_Lote = Column(Integer, primary_key=True, autoincrement=True)
    ID_Producto = Column(Integer, ForeignKey("PRODUCTOS.ID_Producto"), nullable=False, index=True)
    Numero_Lote = Column(String, nullable=True)
    Fecha_Entrada = Column(DateTime(timezone=True), default=get_local_time)
    Fecha_Vencimiento = Column(String, nullable=True)
    Stock_inicial = Column(Integer, nullable=False, default=0)
    Stock_actual = Column(Integer, nullable=False, default=0)
    Precio_costo = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Precio_venta_1 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Precio_venta_2 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Precio_venta_3 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Precio_venta_4 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Ganancia_1 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Ganancia_2 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Ganancia_3 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Ganancia_4 = Column(Numeric(12, 2, asdecimal=False), nullable=False, default=0.0)
    Estado = Column(Boolean, nullable=False, default=True)
    Proveedor = Column(String, nullable=True)
    Notas = Column(String, nullable=True)

    # Relaciones
    producto = relationship("Productos", back_populates="lotes")
    detallefacturas = relationship("DetalleFacturas", back_populates="lote")
