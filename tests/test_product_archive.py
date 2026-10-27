import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.controllers.clientes_crud import crear_cliente
from app.controllers.detalle_factura_crud import crear_detalle_factura
from app.controllers.facturas_crud import crear_factura, obtener_factura_completa
from app.controllers.producto_crud import (
    crear_producto,
    eliminar_producto,
)
from app.database.session import Base
from app.models.facturas import MetodoPago, TipoFactura
from app.models.productos import Categorias, Marcas, Productos


class ProductDeletionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add_all(
            [
                Marcas(ID_Marca=1, Nombre="Marca"),
                Categorias(ID_Categoria=1, Nombre="Categoría"),
                MetodoPago(ID_Metodo_Pago=1, Nombre="Efectivo"),
                TipoFactura(ID_Tipo_Factura=1, Nombre="FAC-01"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _crear_producto(self, nombre):
        return crear_producto(
            self.db,
            1,
            nombre,
            100,
            5,
            1,
            150,
            140,
            1,
            1,
            130,
            120,
        )

    def test_sold_product_cannot_be_deleted(self):
        crear_cliente(
            self.db,
            "123456",
            "Ana",
            "Prueba",
            "Calle 1",
            "3000000000",
        )
        producto = self._crear_producto("Producto vendido")
        factura = crear_factura(
            self.db,
            150,
            0,
            0,
            True,
            1,
            1,
            "123456",
            None,
            False,
        )
        crear_detalle_factura(
            self.db,
            1,
            150,
            150,
            producto.ID_Producto,
            factura.ID_Factura,
        )

        self.assertFalse(eliminar_producto(self.db, producto.ID_Producto))
        self.assertIsNotNone(
            self.db.query(Productos)
            .filter(Productos.ID_Producto == producto.ID_Producto)
            .one_or_none()
        )
        detalle = obtener_factura_completa(self.db, factura.ID_Factura)["Detalles"][0]
        self.assertEqual(detalle["Producto"], "Producto vendido")


if __name__ == "__main__":
    unittest.main()
