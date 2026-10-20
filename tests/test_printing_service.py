from datetime import datetime

from app.services.printing_service import (
    _supported_paper_sizes,
    build_invoice_html,
)


class _FakeSize:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def width(self):
        return self._width

    def height(self):
        return self._height


class _FakePageSize:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def size(self, _unit):
        return _FakeSize(self.width, self.height)


class _FakePrinterInfo:
    def __init__(self, sizes):
        self._sizes = sizes

    def supportedPageSizes(self):
        return self._sizes


def test_paper_options_only_include_formats_reported_by_printer():
    letter = _FakePageSize(215.9, 279.4)
    oficio = _FakePageSize(215.9, 330.2)
    legal = _FakePageSize(215.9, 355.6)

    options = _supported_paper_sizes(_FakePrinterInfo([letter, oficio, legal]))

    assert options == {"Carta": letter, "Oficio": oficio}
    assert _supported_paper_sizes(_FakePrinterInfo([legal])) == {}


def test_invoice_html_includes_commercial_data_and_preserves_long_text():
    product_name = "Esmalte & tratamiento <profesional> " + ("nombre largo " * 12)
    long_address = "Calle 15 # 5-23, " + ("sector residencial " * 8)
    long_name = "María Camila " + ("Restrepo " * 8)
    invoice = {
        "Factura": {
            "ID_Factura": 1492,
            "Fecha_Factura": datetime(2026, 10, 20, 17, 30),
            "Descuento": 1000,
            "MetodoPago": "Transferencia",
        },
        "Cliente": {
            "ID_Cliente": "1.061.789.432",
            "Nombre": long_name,
            "Apellido": "",
            "Teléfono": "312-765-4321",
            "Direccion": long_address,
        },
        "Detalles": [
            {
                "Producto": product_name,
                "Cantidad": 2,
                "Precio_Unitario": 12500,
                "Subtotal": 25000,
            }
        ],
    }

    rendered = build_invoice_html(invoice)

    assert "FACTURA DE VENTA" in rendered
    assert "electrónica" not in rendered
    assert "20/10/2026 17:30:00" in rendered
    assert "312-765-4321" in rendered
    assert long_name in rendered
    assert long_address in rendered
    assert "&lt;profesional&gt;" in rendered
    assert "N.º 00001492" in rendered
    assert "$ 25.000,00" in rendered
    assert "$ 24.000,00" in rendered
    assert "Esmalte &amp; tratamiento " in rendered
    assert "nombre largo " * 12 in rendered


def test_invoice_html_keeps_every_product_for_long_sales():
    details = [
        {
            "Producto": f"Producto de prueba {index:02d}",
            "Cantidad": index,
            "Precio_Unitario": index * 100,
            "Subtotal": index * index * 100,
        }
        for index in range(1, 51)
    ]
    invoice = {
        "Factura": {"ID_Factura": 90, "Descuento": 0},
        "Cliente": {},
        "Detalles": details,
    }

    rendered = build_invoice_html(invoice)

    assert all(f"Producto de prueba {index:02d}" in rendered for index in range(1, 51))


def test_credit_invoice_uses_saved_debt_total():
    invoice = {
        "Factura": {"ID_Factura": 42, "Descuento": 50},
        "Cliente": {},
        "Detalles": [{"Producto": "Producto", "Cantidad": 1, "Subtotal": 100}],
    }

    rendered = build_invoice_html(invoice, {"Total_Deuda": 80})

    assert "TOTAL A PAGAR: $ 80,00" in rendered
