"""Pruebas unitarias para el sistema modernizado de impresión (Carta / Oficio)."""

from datetime import datetime
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

from PyPDF2 import PdfReader
from PyQt6.QtGui import QPageSize

from app.services.invoice_generator import (
    generate_credit_receipt_pdf,
    generate_invoice_pdf,
)
from app.services.printer_config import (
    PAPER_CARTA,
    PAPER_OFICIO,
    load_printer_config,
    save_printer_config,
    validate_printer_ready,
)
from app.services.printing_service import (
    _resolve_page_size,
    open_printer_settings,
    print_credit_receipt,
    print_invoice,
)


def test_printer_config_save_and_load(tmp_path):
    config_file = tmp_path / "printer_config.json"
    with patch("app.services.printer_config.PRINTER_CONFIG_FILE", config_file):
        # Inicialmente vacío
        default_cfg = load_printer_config()
        assert default_cfg["configured"] is False
        assert default_cfg["paper_type"] == PAPER_CARTA

        # Guardar configuración con Oficio Colombia
        success = save_printer_config("Impresora_Test_HP", PAPER_OFICIO, auto_silent_print=True)
        assert success is True

        # Cargar y verificar
        loaded = load_printer_config()
        assert loaded["configured"] is True
        assert loaded["printer_name"] == "Impresora_Test_HP"
        assert loaded["paper_type"] == PAPER_OFICIO
        assert loaded["auto_silent_print"] is True


def test_validate_printer_ready_detects_missing_printer():
    # Caso 1: Sin configurar
    ready, reason, p_info = validate_printer_ready({"configured": False})
    assert ready is False
    assert "no ha sido configurada" in reason

    # Caso 2: Configurada pero no existente en Windows
    with patch("app.services.printer_config.get_available_printers", return_value=[]):
        ready, reason, p_info = validate_printer_ready({
            "configured": True,
            "printer_name": "Impresora_Inexistente",
        })
        assert ready is False
        assert "no detecta ninguna impresora" in reason


def test_invoice_pdf_generation_carta_and_oficio():
    invoice_sample = {
        "Factura": {
            "ID_Factura": 1492,
            "Fecha_Factura": datetime(2026, 10, 20, 17, 30),
            "Descuento": 77000,
            "MetodoPago": "Transferencia Bancaria (Bancolombia)",
        },
        "Cliente": {
            "ID_Cliente": "1.061.789.432",
            "Nombre": "María Camila",
            "Apellido": "Restrepo",
            "Teléfono": "312-765-4321",
            "Direccion": "Calle 15 # 5-23, Barrio San Bosco",
        },
        "Detalles": [
            {
                "Producto": f"Producto de prueba {i:02d}",
                "Cantidad": 2,
                "Precio_Unitario": 12500,
                "Subtotal": 25000,
            }
            for i in range(1, 10)
        ],
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_carta = os.path.join(tmp_dir, "factura_carta.pdf")
        pdf_oficio = os.path.join(tmp_dir, "factura_oficio.pdf")

        generate_invoice_pdf(invoice_sample, pdf_carta, PAPER_CARTA)
        generate_invoice_pdf(invoice_sample, pdf_oficio, PAPER_OFICIO)

        assert os.path.exists(pdf_carta)
        assert os.path.exists(pdf_oficio)

        reader_carta = PdfReader(pdf_carta)
        reader_oficio = PdfReader(pdf_oficio)

        assert len(reader_carta.pages) == 1
        assert len(reader_oficio.pages) == 1

        # Verificar que incluya los textos institucionales
        text_carta = reader_carta.pages[0].extract_text()
        assert "FACTURA DE VENTA" in text_carta
        assert "00001492" in text_carta
        assert "María Camila Restrepo" in text_carta
        assert "1.061.789.432" in text_carta
        assert "Distri Magik - Factura de Venta Comercial" in text_carta
        assert "Página 1 de 1" in text_carta


def test_responsive_layout_carta_vs_oficio():
    """Valida que una venta de tamaño medio (26 productos) requiere 2 páginas en

    Carta pero cabe en 1 sola página en Oficio Colombia.
    """
    invoice_medium = {
        "Factura": {
            "ID_Factura": 1493,
            "Fecha_Factura": datetime(2026, 10, 20, 17, 30),
            "Descuento": 0,
            "MetodoPago": "Efectivo",
        },
        "Cliente": {
            "ID_Cliente": "123",
            "Nombre": "Cliente Prueba",
            "Apellido": "",
            "Teléfono": "3000000",
            "Direccion": "Cali",
        },
        "Detalles": [
            {
                "Producto": f"Producto {i:02d}",
                "Cantidad": 1,
                "Precio_Unitario": 10000,
                "Subtotal": 10000,
            }
            for i in range(1, 27)
        ],
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_carta = os.path.join(tmp_dir, "med_carta.pdf")
        pdf_oficio = os.path.join(tmp_dir, "med_oficio.pdf")

        generate_invoice_pdf(invoice_medium, pdf_carta, PAPER_CARTA)
        generate_invoice_pdf(invoice_medium, pdf_oficio, PAPER_OFICIO)

        reader_carta = PdfReader(pdf_carta)
        reader_oficio = PdfReader(pdf_oficio)

        # En Carta salta a 2 páginas por altura limitada
        assert len(reader_carta.pages) == 2
        # En Oficio aprovecha los 50.8 mm extra y cabe en 1 sola página
        assert len(reader_oficio.pages) == 1

        # En la página 2 de Carta debe estar el encabezado de continuación
        text_p2 = reader_carta.pages[1].extract_text()
        assert "Continuación Factura N.º 00001493" in text_p2
        assert "Página 2 de 2" in text_p2


def test_credit_receipt_pdf_generation():
    class DummyVenta:
        Total_Deuda = 500000
        Saldo_Pendiente = 200000
        Fecha_Limite = datetime(2026, 11, 30)

    class DummyPago:
        Fecha_Registro = datetime(2026, 10, 23)
        Monto = 50000
        metodopago = "Transferencia"
        tipopago = "Abono Parcial"

    factura_data = {
        "Factura": {"ID_Factura": 888},
        "Cliente": {"ID_Cliente": "999888", "Nombre": "Laura", "Apellido": "Gómez"},
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_recibo = os.path.join(tmp_dir, "recibo.pdf")
        generate_credit_receipt_pdf(
            factura_data,
            DummyVenta(),
            [DummyPago()],
            abono=50000,
            output_path=pdf_recibo,
            paper_type=PAPER_OFICIO,
        )

        assert os.path.exists(pdf_recibo)
        reader = PdfReader(pdf_recibo)
        assert len(reader.pages) == 1
        text = reader.pages[0].extract_text()
        assert "RECIBO DE ABONO" in text
        assert "00000888" in text
        assert "Laura Gómez" in text
        assert "HISTORIAL DE ABONOS REGISTRADOS" in text
