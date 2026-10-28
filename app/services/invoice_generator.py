"""Generador de PDFs de Factura de Venta y Recibo de Abono para Distri Magik.

Soporta hojas tamaño Carta y Oficio Colombia de manera responsive/adaptable,
con paginación dinámica 'Página X de Y', encabezado de continuación y diseño fiel
a la plantilla comercial institucional.
"""

from datetime import date, datetime
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.printer_config import PAPER_CARTA, PAPER_OFICIO
from app.utils.logger import logger

# Rutas y constantes


def _resource_path(relative_path: str) -> Path:
    """Devuelve la ruta absoluta a un recurso embalado o del árbol de fuentes.

    Funciona tanto en modo desarrollo como en la instalación empaquetada
    con PyInstaller (mismo orden de búsqueda que printing_service).
    """
    candidates = []

    # 1. Bundle de PyInstaller en modo congelado.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / relative_path)

    # 2. Recurso copiado junto al ejecutable por el instalador.
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / relative_path)

    # 3. Modo desarrollo: relativa al archivo de fuentes.
    candidates.append(Path(__file__).resolve().parents[2] / relative_path)

    for candidato in candidates:
        if candidato.is_file():
            return candidato

    return candidates[-1]


_LOGO_PATH = _resource_path("assets/LogoDistriMagik.png")
_LOGO_GRAYSCALE_PATH = _resource_path("assets/LogoDistriMagik_grayscale.png")
_COMPANY_NAME = "Distri Magik"
_COMPANY_PHONE = "315-038-66-18"
_COMPANY_ADDRESS = "Cali, Colombia"


def _get_grayscale_logo_path() -> Path:
    """Devuelve la ruta al logo de Distri Magik con filtro de escala de grises aplicado."""
    if not _LOGO_PATH.is_file():
        return _LOGO_PATH
    if not _LOGO_GRAYSCALE_PATH.is_file():
        try:
            from PIL import Image as PILImage
            img = PILImage.open(_LOGO_PATH)
            if img.mode == "RGBA":
                r, g, b, a = img.split()
                gray = PILImage.merge("RGB", (r, g, b)).convert("L")
                gray_rgba = PILImage.merge("RGBA", (gray, gray, gray, a))
                gray_rgba.save(_LOGO_GRAYSCALE_PATH)
            else:
                img.convert("L").save(_LOGO_GRAYSCALE_PATH)
        except Exception as e:
            logger.warning(f"No se pudo generar logo en escala de grises: {e}")
            return _LOGO_PATH
    return _LOGO_GRAYSCALE_PATH


# La impresión comercial se maneja únicamente en blanco y negro.  Mantener la
# paleta centralizada evita que un valor destacado (por ejemplo, un abono)
# vuelva a salir en color al modificar una plantilla.
_COLOR_NAVY = colors.black
_COLOR_NAVY_LIGHT = colors.black
_COLOR_DARK = colors.black
_COLOR_BG_CARD = colors.white
# Grises neutros para que las tablas se lean sin crear una cuadrícula pesada
# al imprimir en blanco y negro.
_COLOR_BORDER = colors.HexColor("#E0E0E0")
_COLOR_BORDER_STRONG = colors.HexColor("#C7C7C7")
_COLOR_TEXT_MAIN = colors.black
_COLOR_TEXT_MUTED = colors.black
_COLOR_DISCOUNT = colors.black

# Dimensiones en mm convertidas a puntos
PAGE_DIMENSIONS = {
    PAPER_CARTA: (215.9 * mm, 279.4 * mm),
    PAPER_OFICIO: (215.9 * mm, 330.2 * mm),  # Oficio Colombia
}


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas que calcula el total de páginas y dibuja

    los pies de página ('Página X de Y'), membrete institucional y
    encabezados de continuación en páginas subsiguientes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.invoice_number_str = ""

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        page_w, page_h = self._pagesize
        margin_x = 18 * mm
        margin_b = 15 * mm

        # 1. Encabezado de continuación en páginas subsiguientes (página >= 2)
        if self._pageNumber > 1 and self.invoice_number_str:
            self.setFont("Helvetica-Bold", 8.5)
            self.setFillColor(_COLOR_NAVY)
            text_cont = f"Continuación Factura N.º {self.invoice_number_str}"
            self.drawRightString(page_w - margin_x, page_h - 10 * mm, text_cont)

        # 2. Pie de página institucional
        self.setFont("Helvetica", 8)
        self.setFillColor(_COLOR_TEXT_MUTED)

        # Izquierda: Distri Magik - Factura de Venta Comercial
        self.drawString(
            margin_x,
            margin_b,
            f"{_COMPANY_NAME} - Factura de Venta Comercial",
        )

        # Derecha: Página X de Y
        page_str = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(page_w - margin_x, margin_b, page_str)

        self.restoreState()


def _format_currency(value: Any) -> str:
    """Formatea valores numéricos a formato moneda de Colombia ($ 1.250.000,00)."""
    try:
        val = float(value or 0)
    except (ValueError, TypeError):
        val = 0.0

    formatted = f"{abs(val):,.2f}".replace(",", "\0").replace(".", ",").replace("\0", ".")
    sign = "-" if val < 0 else ""
    return f"{sign}${formatted}"


def _format_datetime(value: Any) -> str:
    """Formatea objetos datetime o date a formato dd/mm/aaaa hh:mm:ss."""
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return str(value or "No registrada")


def generate_invoice_pdf(
    factura_completa: Dict[str, Any],
    output_path: str,
    paper_type: str = PAPER_CARTA,
    credito: Optional[Dict[str, Any]] = None,
    pagos: Optional[List[Any]] = None,
) -> str:
    """Genera el PDF de la factura adaptado a Carta u Oficio Colombia con el diseño comercial."""
    if pagos is None and credito and isinstance(credito, dict):
        pagos = credito.get("pagos")

    page_w, page_h = PAGE_DIMENSIONS.get(paper_type, PAGE_DIMENSIONS[PAPER_CARTA])
    # Mantiene el contenido, especialmente la tabla de productos, separado
    # del borde físico tanto en Carta como en Oficio.
    margin_lr = 18 * mm
    margin_tb = 14 * mm
    printable_w = page_w - (2 * margin_lr)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_w, page_h),
        leftMargin=margin_lr,
        rightMargin=margin_lr,
        topMargin=margin_tb,
        bottomMargin=32 * mm,  # Espacio para el pie de página (15mm) + margen generoso como en la plantilla
    )

    factura = factura_completa.get("Factura", {})
    cliente = factura_completa.get("Cliente", {})
    detalles = factura_completa.get("Detalles", [])
    raw_id = factura.get("ID_Factura", "")
    try:
        invoice_number_str = f"{int(raw_id):08d}"
    except (ValueError, TypeError):
        invoice_number_str = str(raw_id or "00000000")

    subtotal = sum(float(item.get("Subtotal", 0) or 0) for item in detalles)
    descuento = float(factura.get("Descuento", 0) or 0)
    total = (
        float(credito.get("Total_Deuda", subtotal - descuento) or 0)
        if credito
        else subtotal - descuento
    )
    fecha_emision = _format_datetime(factura.get("Fecha_Factura") or datetime.now())
    metodo_pago = "Crédito" if credito else factura.get("MetodoPago", "Efectivo")

    nombre_cliente = " ".join(
        p for p in (cliente.get("Nombre"), cliente.get("Apellido")) if p
    ) or "Consumidor Final"
    cedula_cliente = str(cliente.get("ID_Cliente") or "No registrada")
    contacto_cliente = str(cliente.get("Teléfono") or cliente.get("Telefono") or "No registrado")
    direccion_cliente = str(cliente.get("Direccion") or cliente.get("Dirección") or "No registrada")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvoiceTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=_COLOR_NAVY,
        alignment=2,  # Derecha
    )
    badge_label_style = ParagraphStyle(
        "BadgeLabel",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=_COLOR_TEXT_MUTED,
        alignment=1,  # Centrado
    )
    badge_value_style = ParagraphStyle(
        "BadgeValue",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=_COLOR_NAVY,
        alignment=1,  # Centrado
    )
    meta_style = ParagraphStyle(
        "MetaText",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=_COLOR_TEXT_MAIN,
    )
    meta_right_style = ParagraphStyle(
        "MetaRightText",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=_COLOR_TEXT_MAIN,
        alignment=2,
    )
    header_navy_bar_style = ParagraphStyle(
        "HeaderNavyBar",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )
    client_label_style = ParagraphStyle(
        "ClientLabel",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=_COLOR_NAVY,
    )
    client_value_style = ParagraphStyle(
        "ClientValue",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=_COLOR_TEXT_MAIN,
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10.5,
        textColor=colors.white,
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=_COLOR_TEXT_MAIN,
    )
    table_cell_center_style = ParagraphStyle(
        "TableCellCenter",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=_COLOR_TEXT_MAIN,
        alignment=1,
    )
    table_cell_right_style = ParagraphStyle(
        "TableCellRight",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=_COLOR_TEXT_MAIN,
        alignment=2,
    )

    story = []

    # ─────────────────────────────────────────────────────────────
    # 1. ENCABEZADO SUPERIOR: Logo + Contacto vs Título + Número + Fecha
    # ─────────────────────────────────────────────────────────────
    # Bloque Izquierdo: Logo y teléfono
    left_elements = []
    logo_file = _get_grayscale_logo_path()
    if logo_file.is_file():
        # Escalar manteniendo aspecto
        logo_img = Image(str(logo_file), width=42 * mm, height=18 * mm)
        logo_img.hAlign = "LEFT"
        left_elements.append(logo_img)
    else:
        left_elements.append(
            Paragraph(f"<b>{_COMPANY_NAME}</b>", title_style)
        )
    left_elements.append(Spacer(1, 2 * mm))
    left_elements.append(
        Paragraph(f"<b>Teléfono:</b> {_COMPANY_PHONE}", meta_style)
    )
    left_elements.append(
        Paragraph(f"<b>Ubicación:</b> {_COMPANY_ADDRESS}", meta_style)
    )

    # Bloque Derecho: Título, Caja de Factura N.° y Fecha
    right_elements = []
    right_elements.append(Paragraph("FACTURA DE VENTA", title_style))
    right_elements.append(Spacer(1, 2 * mm))

    badge_data = [
        [Paragraph("FACTURA N.º", badge_label_style)],
        [Paragraph(invoice_number_str, badge_value_style)],
    ]
    badge_w = 56 * mm
    badge_table = Table(badge_data, colWidths=[badge_w])
    badge_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER_STRONG),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )
    col_r_w = printable_w * 0.48
    badge_outer = Table(
        [["", badge_table]],
        colWidths=[max(0, col_r_w - badge_w), badge_w],
    )
    badge_outer.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    right_elements.append(badge_outer)
    right_elements.append(Spacer(1, 2 * mm))
    right_elements.append(
        Paragraph(f"<b>Fecha de Emisión:</b><br/>{fecha_emision}", meta_right_style)
    )

    header_table_data = [[left_elements, right_elements]]
    header_table = Table(
        header_table_data,
        colWidths=[printable_w * 0.52, printable_w * 0.48],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 4 * mm))

    # ─────────────────────────────────────────────────────────────
    # 2. SECCIÓN FACTURAR A (Tarjeta de Cliente con Barra Oscura)
    # ─────────────────────────────────────────────────────────────
    customer_navy_bar = Table(
        [[Paragraph("FACTURAR A", header_navy_bar_style)]],
        colWidths=[printable_w],
    )
    customer_navy_bar.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_DARK),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    # 2 columnas y 2 filas espaciosas
    col_w = printable_w * 0.50
    customer_grid_data = [
        [
            [
                Paragraph("NOMBRE DEL CLIENTE", client_label_style),
                Paragraph(nombre_cliente, client_value_style),
            ],
            [
                Paragraph("CÉDULA / NIT", client_label_style),
                Paragraph(cedula_cliente, client_value_style),
            ],
        ],
        [
            [
                Paragraph("CONTACTO", client_label_style),
                Paragraph(contacto_cliente, client_value_style),
            ],
            [
                Paragraph("DIRECCIÓN", client_label_style),
                Paragraph(direccion_cliente, client_value_style),
            ],
        ],
    ]
    customer_grid = Table(customer_grid_data, colWidths=[col_w, col_w])
    customer_grid.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, _COLOR_BORDER),
        ])
    )

    story.append(customer_navy_bar)
    story.append(customer_grid)
    story.append(Spacer(1, 4 * mm))

    # ─────────────────────────────────────────────────────────────
    # 3. TABLA DE PRODUCTOS
    # ─────────────────────────────────────────────────────────────
    # Columnas proporcionales: Descripción (54%), Cantidad (12%), P. Unit (17%), Total (17%)
    col_desc_w = printable_w * 0.54
    col_cant_w = printable_w * 0.12
    col_unit_w = printable_w * 0.17
    col_tot_w = printable_w * 0.17

    products_data = [
        [
            Paragraph("DESCRIPCIÓN DEL PRODUCTO", table_header_style),
            Paragraph("CANT.", table_header_style),
            Paragraph("P. UNITARIO", ParagraphStyle("TH_R", parent=table_header_style, alignment=2)),
            Paragraph("TOTAL", ParagraphStyle("TH_R2", parent=table_header_style, alignment=2)),
        ]
    ]

    for item in detalles:
        prod_name = str(item.get("Producto") or "Producto sin nombre")
        cant = item.get("Cantidad", 0)
        p_unit = item.get("Precio_Unitario", 0)
        p_subtotal = item.get("Subtotal", 0)

        products_data.append([
            Paragraph(prod_name, table_cell_style),
            Paragraph(str(cant), table_cell_center_style),
            Paragraph(_format_currency(p_unit), table_cell_right_style),
            Paragraph(_format_currency(p_subtotal), table_cell_right_style),
        ])

    if len(products_data) == 1:
        products_data.append([
            Paragraph("No hay productos registrados en esta factura.", table_cell_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("$ 0,00", table_cell_right_style),
            Paragraph("$ 0,00", table_cell_right_style),
        ])

    products_table = Table(
        products_data,
        colWidths=[col_desc_w, col_cant_w, col_unit_w, col_tot_w],
        repeatRows=1,  # Repite cabecera navy si salta de página
    )
    products_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
            ("TOPPADDING", (0, 1), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            # Líneas divisorias horizontales sutiles entre filas
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, _COLOR_BORDER),
        ])
    )
    story.append(products_table)
    story.append(Spacer(1, 3 * mm))

    # ─────────────────────────────────────────────────────────────
    # 4. TOTALES, FORMA DE PAGO Y MENSAJE FINAL (KeepTogether)
    # ─────────────────────────────────────────────────────────────
    footer_block = []

    # Bloque de Totales alineado a la derecha
    summary_w = printable_w * 0.46
    lbl_tot_style = ParagraphStyle(
        "LblTot", fontName="Helvetica-Bold", fontSize=9, textColor=_COLOR_TEXT_MAIN, alignment=2
    )
    val_tot_style = ParagraphStyle(
        "ValTot", fontName="Helvetica", fontSize=9, textColor=_COLOR_TEXT_MAIN, alignment=2
    )
    val_desc_style = ParagraphStyle(
        "ValDesc", fontName="Helvetica", fontSize=9, textColor=_COLOR_DISCOUNT, alignment=2
    )

    tot_banner_lbl = ParagraphStyle(
        "TotBannerLbl", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white
    )
    tot_banner_val = ParagraphStyle(
        "TotBannerVal", fontName="Helvetica-Bold", fontSize=12, textColor=colors.white, alignment=2
    )

    descuento_str = f"-{_format_currency(descuento)}" if descuento > 0 else "$0,00"

    summary_rows = [
        [Paragraph("SUBTOTAL", lbl_tot_style), Paragraph(_format_currency(subtotal), val_tot_style)],
        [Paragraph("DESCUENTO", lbl_tot_style), Paragraph(descuento_str, val_desc_style if descuento > 0 else val_tot_style)],
        [Paragraph("TOTAL A PAGAR", tot_banner_lbl), Paragraph(_format_currency(total), tot_banner_val)],
    ]

    summary_table = Table(summary_rows, colWidths=[summary_w * 0.48, summary_w * 0.52])
    summary_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, 1), 2),
            # Fila de TOTAL A PAGAR con fondo Navy
            ("BACKGROUND", (0, 2), (-1, 2), _COLOR_NAVY),
            ("TOPPADDING", (0, 2), (-1, 2), 6),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 6),
            ("LEFTPADDING", (0, 2), (-1, 2), 8),
            ("RIGHTPADDING", (0, 2), (-1, 2), 8),
        ])
    )
    summary_table.hAlign = "RIGHT"
    footer_block.append(summary_table)
    footer_block.append(Spacer(1, 4 * mm))

    # Tarjeta de FORMA DE PAGO
    payment_title_style = ParagraphStyle(
        "PaymentTitle", fontName="Helvetica-Bold", fontSize=8.5, textColor=_COLOR_NAVY
    )
    payment_desc_style = ParagraphStyle(
        "PaymentDesc", fontName="Helvetica", fontSize=8.5, textColor=_COLOR_TEXT_MAIN
    )

    payment_lines = [
        Paragraph("<b>FORMA DE PAGO</b>", payment_title_style),
        Paragraph(f"Método: {metodo_pago}", payment_desc_style),
    ]
    if credito:
        saldo_pend = float(credito.get("Saldo_Pendiente", 0) or 0)
        limite = _format_datetime(credito.get("Fecha_Limite"))
        payment_lines.append(
            Paragraph(
                f"<b>Saldo pendiente:</b> {_format_currency(saldo_pend)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Fecha límite:</b> {limite}",
                payment_desc_style,
            )
        )

    payment_card = Table([[payment_lines]], colWidths=[printable_w])
    payment_card.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER),
            ("LINEBEFORE", (0, 0), (0, -1), 1, _COLOR_BORDER_STRONG),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    footer_block.append(payment_card)
    footer_block.append(Spacer(1, 3 * mm))

    # Historial de Pagos (si la factura incluye pagos o es crédito)
    if pagos is not None:
        history_section_title_style = ParagraphStyle(
            "HistTitle", fontName="Helvetica-Bold", fontSize=9, textColor=_COLOR_NAVY
        )
        footer_block.append(Paragraph("HISTORIAL DE PAGOS", history_section_title_style))
        footer_block.append(Spacer(1, 2 * mm))

        history_data = [
            [
                Paragraph("FECHA", table_header_style),
                Paragraph("MONTO", ParagraphStyle("TH_R3", parent=table_header_style, alignment=2)),
                Paragraph("MÉTODO", table_header_style),
                Paragraph("TIPO", table_header_style),
            ]
        ]

        for p in pagos:
            f_reg = _format_datetime(
                getattr(p, "Fecha_Registro", None)
                if not isinstance(p, dict)
                else p.get("Fecha_Registro")
            )
            monto = float(
                getattr(p, "Monto", 0)
                if not isinstance(p, dict)
                else p.get("Monto", 0) or 0
            )
            metodo = str(
                (
                    getattr(p, "metodopago", "")
                    if not isinstance(p, dict)
                    else p.get("metodopago", "")
                )
                or "Efectivo"
            )
            tipo = str(
                (
                    getattr(p, "tipopago", "")
                    if not isinstance(p, dict)
                    else p.get("tipopago", "")
                )
                or "Abono"
            )

            history_data.append([
                Paragraph(f_reg, table_cell_style),
                Paragraph(_format_currency(monto), table_cell_right_style),
                Paragraph(metodo, table_cell_style),
                Paragraph(tipo, table_cell_style),
            ])

        if len(history_data) == 1:
            history_data.append([
                Paragraph("No hay pagos registrados.", table_cell_style),
                Paragraph("$ 0,00", table_cell_right_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
            ])

        w_f = printable_w * 0.32
        w_m = printable_w * 0.24
        w_met = printable_w * 0.24
        w_t = printable_w * 0.20
        history_table = Table(history_data, colWidths=[w_f, w_m, w_met, w_t])
        history_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), _COLOR_NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, _COLOR_BORDER),
            ])
        )
        footer_block.append(history_table)
        footer_block.append(Spacer(1, 3 * mm))

    # Frase de agradecimiento
    thanks_style = ParagraphStyle(
        "Thanks",
        fontName="Helvetica",
        fontSize=8,
        textColor=_COLOR_TEXT_MUTED,
        alignment=1,
    )
    footer_block.append(
        Paragraph(
            "Gracias por su compra. Si tiene alguna inquietud respecto a esta factura, por favor contáctenos.",
            thanks_style,
        )
    )

    if pagos is not None:
        story.append(KeepTogether(footer_block[:3]))
        story.extend(footer_block[3:])
    else:
        story.append(KeepTogether(footer_block))

    # Construir PDF con NumberedCanvas
    def _canvas_factory(*args, **kwargs):
        c = NumberedCanvas(*args, **kwargs)
        c.invoice_number_str = invoice_number_str
        return c

    doc.build(story, canvasmaker=_canvas_factory)
    return output_path


def generate_credit_receipt_pdf(
    factura_completa: Dict[str, Any],
    venta: Any,
    pagos: List[Any],
    abono: float,
    output_path: str,
    paper_type: str = PAPER_CARTA,
) -> str:
    """Genera el PDF del Recibo de Abono con la misma estructura visual de la factura de venta.

    Incluye: encabezado con logo, seccion FACTURAR A (2x2), tabla completa de productos,
    resumen de credito (Deuda Total / Abono Actual / Saldo Pendiente) e historial de abonos.
    """
    page_w, page_h = PAGE_DIMENSIONS.get(paper_type, PAGE_DIMENSIONS[PAPER_CARTA])
    # Mantiene el contenido, especialmente la tabla de productos, separado
    # del borde físico tanto en Carta como en Oficio.
    margin_lr = 18 * mm
    margin_tb = 14 * mm
    printable_w = page_w - (2 * margin_lr)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_w, page_h),
        leftMargin=margin_lr,
        rightMargin=margin_lr,
        topMargin=margin_tb,
        bottomMargin=32 * mm,  # Espacio para el pie de página (15mm) + margen generoso como en la plantilla
    )

    factura = factura_completa.get("Factura", {})
    cliente = factura_completa.get("Cliente", {})
    detalles = factura_completa.get("Detalles", [])

    raw_id = factura.get("ID_Factura", "")
    try:
        invoice_number_str = f"{int(raw_id):08d}"
    except (ValueError, TypeError):
        invoice_number_str = str(raw_id or "00000000")

    nombre_cliente   = " ".join(
        p for p in (cliente.get("Nombre"), cliente.get("Apellido")) if p
    ) or "Consumidor Final"
    cedula_cliente    = str(cliente.get("ID_Cliente") or "No registrada")
    contacto_cliente  = str(cliente.get("Telefono") or cliente.get("Telefono") or "No registrado")
    direccion_cliente = str(cliente.get("Direccion") or cliente.get("Direccion") or "No registrada")
    metodo_pago       = factura.get("MetodoPago", "Credito")
    fecha_emision     = _format_datetime(factura.get("Fecha_Factura") or datetime.now())

    total_deuda    = float(getattr(venta, "Total_Deuda", 0) or 0)
    saldo_anterior = float(getattr(venta, "Saldo_Pendiente", 0) or 0)
    nuevo_saldo    = max(0.0, saldo_anterior - float(abono or 0))
    fecha_limite   = _format_datetime(getattr(venta, "Fecha_Limite", None))

    # Estilos identicos a generate_invoice_pdf
    title_style = ParagraphStyle(
        "ReceiptTitle", fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=_COLOR_NAVY, alignment=2,
    )
    badge_label_style = ParagraphStyle(
        "BadgeLabel", fontName="Helvetica", fontSize=8, leading=10,
        textColor=_COLOR_TEXT_MUTED, alignment=1,
    )
    badge_value_style = ParagraphStyle(
        "BadgeValue", fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=_COLOR_NAVY, alignment=1,
    )
    meta_style = ParagraphStyle(
        "MetaText", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=_COLOR_TEXT_MAIN,
    )
    meta_right_style = ParagraphStyle(
        "MetaRightText", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=_COLOR_TEXT_MAIN, alignment=2,
    )
    header_navy_bar_style = ParagraphStyle(
        "HeaderNavyBar", fontName="Helvetica-Bold", fontSize=9, leading=11,
        textColor=colors.white,
    )
    client_label_style = ParagraphStyle(
        "ClientLabel", fontName="Helvetica-Bold", fontSize=7.5, leading=9.5,
        textColor=_COLOR_NAVY,
    )
    client_value_style = ParagraphStyle(
        "ClientValue", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=_COLOR_TEXT_MAIN,
    )
    table_header_style = ParagraphStyle(
        "TableHeader", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5,
        textColor=colors.white,
    )
    table_cell_style = ParagraphStyle(
        "TableCell", fontName="Helvetica", fontSize=8, leading=10,
        textColor=_COLOR_TEXT_MAIN,
    )
    table_cell_center_style = ParagraphStyle(
        "TableCellCenter", fontName="Helvetica", fontSize=8, leading=10,
        textColor=_COLOR_TEXT_MAIN, alignment=1,
    )
    table_cell_right_style = ParagraphStyle(
        "TableCellRight", fontName="Helvetica", fontSize=8, leading=10,
        textColor=_COLOR_TEXT_MAIN, alignment=2,
    )

    story = []

    # 1. ENCABEZADO: Logo + Contacto vs Titulo + Numero + Fecha
    left_elements = []
    logo_file = _get_grayscale_logo_path()
    if logo_file.is_file():
        logo_img = Image(str(logo_file), width=42 * mm, height=18 * mm)
        logo_img.hAlign = "LEFT"
        left_elements.append(logo_img)
    else:
        left_elements.append(Paragraph(f"<b>{_COMPANY_NAME}</b>", title_style))
    left_elements.append(Spacer(1, 2 * mm))
    left_elements.append(Paragraph(f"<b>Telefono:</b> {_COMPANY_PHONE}", meta_style))
    left_elements.append(Paragraph(f"<b>Ubicacion:</b> {_COMPANY_ADDRESS}", meta_style))

    right_elements = []
    right_elements.append(Paragraph("RECIBO DE ABONO", title_style))
    right_elements.append(Spacer(1, 2 * mm))

    badge_data = [
        [Paragraph("FACTURA N.", badge_label_style)],
        [Paragraph(invoice_number_str, badge_value_style)],
    ]
    badge_w = 56 * mm
    badge_table = Table(badge_data, colWidths=[badge_w])
    badge_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER_STRONG),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )
    col_r_w = printable_w * 0.48
    badge_outer = Table(
        [["", badge_table]],
        colWidths=[max(0, col_r_w - badge_w), badge_w],
    )
    badge_outer.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    right_elements.append(badge_outer)
    right_elements.append(Spacer(1, 2 * mm))
    right_elements.append(
        Paragraph(f"<b>Fecha de Emision:</b><br/>{fecha_emision}", meta_right_style)
    )

    header_table_data = [[left_elements, right_elements]]
    header_table = Table(
        header_table_data,
        colWidths=[printable_w * 0.52, printable_w * 0.48],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 4 * mm))

    # 2. SECCION FACTURAR A (2 columnas x 2 filas)
    customer_navy_bar = Table(
        [[Paragraph("FACTURAR A", header_navy_bar_style)]],
        colWidths=[printable_w],
    )
    customer_navy_bar.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_DARK),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    col_w = printable_w * 0.50
    customer_grid_data = [
        [
            [
                Paragraph("NOMBRE DEL CLIENTE", client_label_style),
                Paragraph(nombre_cliente, client_value_style),
            ],
            [
                Paragraph("CEDULA / NIT", client_label_style),
                Paragraph(cedula_cliente, client_value_style),
            ],
        ],
        [
            [
                Paragraph("CONTACTO", client_label_style),
                Paragraph(contacto_cliente, client_value_style),
            ],
            [
                Paragraph("DIRECCION", client_label_style),
                Paragraph(direccion_cliente, client_value_style),
            ],
        ],
    ]
    customer_grid = Table(customer_grid_data, colWidths=[col_w, col_w])
    customer_grid.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, _COLOR_BORDER),
        ])
    )

    story.append(customer_navy_bar)
    story.append(customer_grid)
    story.append(Spacer(1, 3 * mm))

    # 3. TABLA DE PRODUCTOS (identica a la factura de venta)
    col_desc_w = printable_w * 0.54
    col_cant_w = printable_w * 0.12
    col_unit_w = printable_w * 0.17
    col_tot_w  = printable_w * 0.17

    products_data = [
        [
            Paragraph("DESCRIPCION DEL PRODUCTO", table_header_style),
            Paragraph("CANT.", table_header_style),
            Paragraph("P. UNITARIO", ParagraphStyle("TH_R", parent=table_header_style, alignment=2)),
            Paragraph("TOTAL", ParagraphStyle("TH_R2", parent=table_header_style, alignment=2)),
        ]
    ]

    for item in detalles:
        prod_name  = str(item.get("Producto") or "Producto sin nombre")
        cant       = item.get("Cantidad", 0)
        p_unit     = item.get("Precio_Unitario", 0)
        p_subtotal = item.get("Subtotal", 0)

        products_data.append([
            Paragraph(prod_name, table_cell_style),
            Paragraph(str(cant), table_cell_center_style),
            Paragraph(_format_currency(p_unit), table_cell_right_style),
            Paragraph(_format_currency(p_subtotal), table_cell_right_style),
        ])

    if len(products_data) == 1:
        products_data.append([
            Paragraph("No hay productos registrados en esta factura.", table_cell_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("$ 0,00", table_cell_right_style),
            Paragraph("$ 0,00", table_cell_right_style),
        ])

    products_table = Table(
        products_data,
        colWidths=[col_desc_w, col_cant_w, col_unit_w, col_tot_w],
        repeatRows=1,
    )
    products_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
            ("TOPPADDING", (0, 1), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, _COLOR_BORDER),
        ])
    )
    story.append(products_table)
    story.append(Spacer(1, 3 * mm))

    # 4. RESUMEN DE CREDITO + FORMA DE PAGO + HISTORIAL (KeepTogether)
    footer_block = []

    # Deuda Total / Abono Actual / Saldo Pendiente
    summary_w = printable_w * 0.46
    lbl_tot_style = ParagraphStyle(
        "LblTot", fontName="Helvetica-Bold", fontSize=9, textColor=_COLOR_TEXT_MAIN, alignment=2
    )
    val_tot_style = ParagraphStyle(
        "ValTot", fontName="Helvetica", fontSize=9, textColor=_COLOR_TEXT_MAIN, alignment=2
    )
    val_abono_style = ParagraphStyle(
        "ValAbono", fontName="Helvetica", fontSize=9, textColor=_COLOR_TEXT_MAIN, alignment=2
    )
    tot_banner_lbl = ParagraphStyle(
        "TotBannerLbl", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white
    )
    tot_banner_val = ParagraphStyle(
        "TotBannerVal", fontName="Helvetica-Bold", fontSize=12, textColor=colors.white, alignment=2
    )

    credit_summary_rows = [
        [Paragraph("DEUDA TOTAL",    lbl_tot_style), Paragraph(_format_currency(total_deuda), val_tot_style)],
        [Paragraph("ABONO ACTUAL",   lbl_tot_style), Paragraph(_format_currency(abono), val_abono_style)],
        [Paragraph("SALDO PENDIENTE", tot_banner_lbl), Paragraph(_format_currency(nuevo_saldo), tot_banner_val)],
    ]

    credit_summary_table = Table(
        credit_summary_rows,
        colWidths=[summary_w * 0.48, summary_w * 0.52],
    )
    credit_summary_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, 1), 2),
            ("BACKGROUND", (0, 2), (-1, 2), _COLOR_NAVY),
            ("TOPPADDING", (0, 2), (-1, 2), 6),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 6),
            ("LEFTPADDING", (0, 2), (-1, 2), 8),
            ("RIGHTPADDING", (0, 2), (-1, 2), 8),
        ])
    )
    credit_summary_table.hAlign = "RIGHT"
    footer_block.append(credit_summary_table)
    footer_block.append(Spacer(1, 4 * mm))

    # Tarjeta de Forma de Pago
    payment_title_style = ParagraphStyle(
        "PaymentTitle", fontName="Helvetica-Bold", fontSize=8.5, textColor=_COLOR_NAVY
    )
    payment_desc_style = ParagraphStyle(
        "PaymentDesc", fontName="Helvetica", fontSize=8.5, textColor=_COLOR_TEXT_MAIN
    )

    payment_card = Table(
        [[
            [
                Paragraph("<b>FORMA DE PAGO</b>", payment_title_style),
                Paragraph(f"Metodo: {metodo_pago}", payment_desc_style),
                Paragraph(
                    f"<b>Saldo pendiente:</b> {_format_currency(nuevo_saldo)}"
                    f"    |    <b>Fecha limite:</b> {fecha_limite}",
                    payment_desc_style,
                ),
            ]
        ]],
        colWidths=[printable_w],
    )
    payment_card.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG_CARD),
            ("BOX", (0, 0), (-1, -1), 1, _COLOR_BORDER),
            ("LINEBEFORE", (0, 0), (0, -1), 1, _COLOR_BORDER_STRONG),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    footer_block.append(payment_card)
    footer_block.append(Spacer(1, 4 * mm))

    # Historial de Abonos Registrados
    history_section_title_style = ParagraphStyle(
        "HistTitle", fontName="Helvetica-Bold", fontSize=9, textColor=_COLOR_NAVY
    )
    footer_block.append(Paragraph("HISTORIAL DE ABONOS REGISTRADOS", history_section_title_style))
    footer_block.append(Spacer(1, 2 * mm))

    history_data = [
        [
            Paragraph("FECHA", table_header_style),
            Paragraph("MONTO", ParagraphStyle("TH_R3", parent=table_header_style, alignment=2)),
            Paragraph("METODO", table_header_style),
            Paragraph("TIPO", table_header_style),
        ]
    ]

    for p in pagos:
        f_reg  = _format_datetime(getattr(p, "Fecha_Registro", None))
        monto  = float(getattr(p, "Monto", 0) or 0)
        metodo = str(getattr(p, "metodopago", "") or "Efectivo")
        tipo   = str(getattr(p, "tipopago", "") or "Abono")

        history_data.append([
            Paragraph(f_reg, table_cell_style),
            Paragraph(_format_currency(monto), table_cell_right_style),
            Paragraph(metodo, table_cell_style),
            Paragraph(tipo, table_cell_style),
        ])

    if len(history_data) == 1:
        history_data.append([
            Paragraph("No hay abonos previos registrados.", table_cell_style),
            Paragraph("$ 0,00", table_cell_right_style),
            Paragraph("-", table_cell_style),
            Paragraph("-", table_cell_style),
        ])

    w_f   = printable_w * 0.32
    w_m   = printable_w * 0.24
    w_met = printable_w * 0.24
    w_t   = printable_w * 0.20
    history_table = Table(history_data, colWidths=[w_f, w_m, w_met, w_t])
    history_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _COLOR_NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, _COLOR_BORDER),
        ])
    )
    footer_block.append(history_table)
    footer_block.append(Spacer(1, 4 * mm))

    thanks_style = ParagraphStyle(
        "Thanks", fontName="Helvetica", fontSize=8, textColor=_COLOR_TEXT_MUTED, alignment=1
    )
    footer_block.append(
        Paragraph(
            "Gracias por su pago. Conserve este recibo para cualquier reclamacion.",
            thanks_style,
        )
    )

    # El historial puede crecer con cada abono.  Solo mantenemos juntos el
    # resumen y la forma de pago; el historial queda libre para continuar en
    # otra página del formato configurado en vez de sobrepasar el borde inferior.
    story.append(KeepTogether(footer_block[:3]))
    story.extend(footer_block[3:])

    def _canvas_factory(*args, **kwargs):
        c = NumberedCanvas(*args, **kwargs)
        c.invoice_number_str = invoice_number_str
        return c

    doc.build(story, canvasmaker=_canvas_factory)
    return output_path

