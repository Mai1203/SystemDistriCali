class PrecioVentaStrategy:
    def __init__(self, atributo):
        self.atributo = atributo

    def obtener(self, producto):
        return getattr(producto, self.atributo)


TIPOS_VENTA = {
    0: {"nombre": "FAC-01", "factura": "FAC-01", "precio": PrecioVentaStrategy("Precio_venta_1")},
    1: {"nombre": "FAC-02", "factura": "FAC-02", "precio": PrecioVentaStrategy("Precio_venta_2")},
    2: {"nombre": "FAC-03", "factura": "FAC-03", "precio": PrecioVentaStrategy("Precio_venta_3")},
    3: {"nombre": "FAC-04", "factura": "FAC-04", "precio": PrecioVentaStrategy("Precio_venta_4")},
}

PERMISOS_VISTAS = (
    "Ventas",
    "Caja",
    "Credito",
    "Egreso",
    "Respaldo",
    "Productos",
    "CrediFactura",
    "Facturas",
    "Reportes",
    "ControlUsuario",
    "Clientes",
)


def obtener_tipo_venta(indice):
    return TIPOS_VENTA.get(indice, TIPOS_VENTA[0])


def obtener_precio_producto(producto, indice):
    tipo_venta = obtener_tipo_venta(indice)
    return tipo_venta["precio"].obtener(producto)
