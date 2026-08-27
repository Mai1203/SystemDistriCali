from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base


class TipoIngreso(Base):
    __tablename__ = "TIPO_INGRESO"

    ID_Tipo_Ingreso = Column(Integer, primary_key=True, autoincrement=True)
    Tipo_Ingreso = Column(String, nullable=False)

    __table_args__ = (CheckConstraint(
        "Tipo_Ingreso IN ('Venta FAC-01', 'Venta FAC-02', 'Venta FAC-03', 'Venta FAC-04', 'Venta FAC-CREDITO', 'FAC-ABONO')"
    ),)

    ID_Pago_Credito = Column(Integer, ForeignKey("PAGO_CREDITO.ID_Pago_Credito"))
    ID_Factura = Column(Integer, ForeignKey("FACTURA.ID_Factura"))

    # Relaciones
    pagocredito = relationship("PagoCredito", back_populates="tipoingreso")
    facturas = relationship("Facturas", back_populates="tipoingreso")
    ingresos = relationship("Ingresos", back_populates="tipoingreso")
    analisisfinanciero = relationship(
        "AnalisisFinanciero", back_populates="tipoingreso"
    )
