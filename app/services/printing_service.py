"""Servicio de impresión de facturas y recibos de abono para SystemDistriCali.

Soporta reconocimiento automático de impresoras, configuración persistente,
papel Carta y Oficio Colombia, y reproducción fiel de la plantilla comercial.
"""

from datetime import date, datetime
from html import escape
import os
from pathlib import Path
import tempfile
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt6.QtCore import QMarginsF, QPointF, QRectF, QSize, QSizeF
from PyQt6.QtGui import QImage, QPainter, QPageLayout, QPageSize, QTextDocument
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.services.invoice_generator import (
    generate_credit_receipt_pdf,
    generate_invoice_pdf,
)
from app.services.printer_config import (
    PAPER_CARTA,
    PAPER_DIMENSIONS_MM,
    PAPER_OFICIO,
    ConfigurarImpresoraDialog,
    find_printer_info,
    get_available_printers,
    load_printer_config,
    save_printer_config,
    validate_printer_ready,
)
from app.utils.logger import logger

_PAPER_SIZES_MM = {
    "Carta": (215.9, 279.4),
    "Oficio": (215.9, 330.2),
}
_COMPANY_ADDRESS = "Cali, Colombia"
_COMPANY_PHONE = "315-038-66-18"
_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "LogoDistriMagik.png"


def _supported_paper_sizes(printer_info):
    """Mantiene compatibilidad con utilidades y tests existentes."""
    options = {}
    if not printer_info:
        return options
    for page_size in printer_info.supportedPageSizes():
        width, height = page_size.size(QPageSize.Unit.Millimeter).width(), page_size.size(
            QPageSize.Unit.Millimeter
        ).height()
        for label, (target_width, target_height) in _PAPER_SIZES_MM.items():
            if abs(width - target_width) <= 1.5 and abs(height - target_height) <= 1.5:
                options[label] = page_size
    return options


class _PrintSettingsDialog(QDialog):
    """Diálogo retrocompatible con la versión previa para pruebas unitarias."""

    def __init__(self, printers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de impresión")
        self.setMinimumWidth(430)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.printer_combo = QComboBox(self)
        self.paper_combo = QComboBox(self)
        self.paper_status = QLabel(self)
        self.paper_status.setWordWrap(True)
        form.addRow("Impresora:", self.printer_combo)
        form.addRow("Tamaño de papel:", self.paper_combo)
        layout.addLayout(form)
        layout.addWidget(self.paper_status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Print
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self.print_button = buttons.button(QDialogButtonBox.StandardButton.Print)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        default_name = ""
        try:
            default_name = QPrinterInfo.defaultPrinter().printerName()
        except Exception:
            pass

        for printer_info in printers:
            name = printer_info.printerName()
            label = f"{name} (predeterminada)" if name == default_name else name
            self.printer_combo.addItem(label, printer_info)

        for index in range(self.printer_combo.count()):
            printer_info = self.printer_combo.itemData(index)
            if printer_info and printer_info.printerName() == default_name:
                self.printer_combo.setCurrentIndex(index)
                break

        self.printer_combo.currentIndexChanged.connect(self._refresh_paper_sizes)
        self._refresh_paper_sizes()

    def _refresh_paper_sizes(self):
        self.paper_combo.clear()
        printer_info = self.printer_combo.currentData()
        if printer_info is None:
            self.paper_status.setText("Seleccione una impresora disponible.")
            self.print_button.setEnabled(False)
            return

        paper_sizes = _supported_paper_sizes(printer_info)
        for label in _PAPER_SIZES_MM:
            page_size = paper_sizes.get(label)
            if page_size is not None:
                dimensions = "215,9 × 279,4 mm" if label == "Carta" else "215,9 × 330,2 mm"
                self.paper_combo.addItem(f"{label} ({dimensions})", page_size)

        if self.paper_combo.count():
            self.paper_status.setText("")
            self.print_button.setEnabled(True)
        else:
            self.paper_status.setText(
                "La impresora no informa compatibilidad con Carta (215,9 × 279,4 mm) "
                "ni Oficio Colombia (215,9 × 330,2 mm). Revise el controlador o la "
                "configuración de papel de Windows."
            )
            self.print_button.setEnabled(False)

    def selection(self):
        return self.printer_combo.currentData(), self.paper_combo.currentData()


def _escape(value):
    return escape("" if value is None else str(value), quote=True)


def _currency(value):
    formatted = f"{float(value or 0):,.2f}"
    return "$ " + formatted.replace(",", "\0").replace(".", ",").replace("\0", ".")


def _format_date(value):
    if isinstance(value, (datetime, date)):
        return value.strftime(
            "%d/%m/%Y %H:%M:%S" if isinstance(value, datetime) else "%d/%m/%Y"
        )
    return str(value or "No registrada")


def _document_shell(body):
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; color: #111; font-size: 9pt; }}
      .header {{ width: 100%; border-bottom: 2px solid #555; padding-bottom: 10px; }}
      .logo {{ width: 115px; height: auto; }}
      .title {{ font-size: 22pt; font-weight: bold; text-align: right; }}
      .meta {{ color: #333; font-size: 9pt; }}
      .total-banner {{ background-color: #e5e5e5; padding: 9px; text-align: center;
                       font-size: 15pt; font-weight: bold; margin: 14px 0; }}
      .section-title {{ font-size: 10pt; font-weight: bold; margin: 10px 0 5px; }}
      table {{ border-collapse: collapse; width: 100%; }}
      .customer td {{ vertical-align: top; padding: 3px 8px 8px 0; }}
      .products {{ margin-top: 12px; }}
      .products th {{ text-align: left; border-top: 2px solid #777;
                      border-bottom: 1px solid #777; padding: 5px 4px; }}
      .products td {{ border-bottom: 1px solid #bbb; padding: 5px 4px;
                      vertical-align: top; }}
      .number {{ text-align: right; white-space: nowrap; }}
      .product-name {{ width: 52%; word-wrap: break-word; }}
      .summary {{ width: 56%; margin: 12px 0 0 auto; }}
      .summary td {{ padding: 4px; }}
      .summary .grand-total td {{ border-top: 2px solid #555; font-size: 12pt;
                                 font-weight: bold; padding-top: 8px; }}
      .payment {{ border-top: 2px solid #888; border-bottom: 2px solid #888;
                  margin-top: 14px; padding: 8px 0; }}
      .footer {{ margin-top: 14px; color: #333; }}
      .small {{ font-size: 8pt; color: #444; }}
    </style></head><body>{body}</body></html>
    """


def build_invoice_html(factura_completa, credito=None):
    """Mantiene compatibilidad con tests unitarios existentes."""
    factura = factura_completa.get("Factura", {})
    cliente = factura_completa.get("Cliente", {})
    detalles = factura_completa.get("Detalles", [])
    invoice_id = factura.get("ID_Factura", "")

    subtotal = sum(float(item.get("Subtotal", 0) or 0) for item in detalles)
    descuento = float(factura.get("Descuento", 0) or 0)
    total = (
        float(credito.get("Total_Deuda", subtotal - descuento) or 0)
        if credito
        else subtotal - descuento
    )
    logo = (
        f'<img class="logo" src="{_escape(_LOGO_PATH.as_uri())}" alt="Distri Magik">'
        if _LOGO_PATH.is_file()
        else '<strong>Distri Magik</strong>'
    )
    nombre_cliente = " ".join(
        part for part in (cliente.get("Nombre"), cliente.get("Apellido")) if part
    )
    metodo_pago = "Crédito" if credito else factura.get("MetodoPago", "No especificado")

    rows = "".join(
        "<tr>"
        f'<td class="product-name">{_escape(detalle.get("Producto", ""))}</td>'
        f'<td class="number">{_escape(detalle.get("Cantidad", ""))}</td>'
        f'<td class="number">{_currency(detalle.get("Precio_Unitario", 0))}</td>'
        f'<td class="number">{_currency(detalle.get("Subtotal", 0))}</td>'
        "</tr>"
        for detalle in detalles
    )
    if not rows:
        rows = '<tr><td colspan="4">No hay productos registrados.</td></tr>'

    credit_details = ""
    if credito:
        credit_details = (
            '<p class="small">Saldo pendiente: '
            f"{_currency(credito.get('Saldo_Pendiente', 0))}"
            " &nbsp;|&nbsp; Fecha límite: "
            f"{_escape(_format_date(credito.get('Fecha_Limite')))}</p>"
        )

    body = f"""
    <table class="header"><tr>
      <td>{logo}<br><span class="meta">{_COMPANY_ADDRESS} · Tel. {_COMPANY_PHONE}</span></td>
      <td class="title">FACTURA DE VENTA<br>
        <span class="meta">N.º {_escape(f"0000{invoice_id}")}</span>
      </td>
    </tr></table>
    <table class="customer"><tr>
      <td><b>FACTURA A:</b></td>
      <td><b>NOMBRE</b><br>{_escape(nombre_cliente or "Consumidor Final")}<br>
          <b>CÉDULA</b><br>{_escape(cliente.get("ID_Cliente", "No registrada"))}</td>
      <td><b>CONTACTO</b><br>{_escape(cliente.get("Teléfono") or "No registrado")}</td>
      <td><b>DIRECCIÓN</b><br>{_escape(cliente.get("Direccion") or "No registrada")}</td>
    </tr></table>
    <table><tr><td class="meta">FECHA DE LA FACTURA<br>
      {_escape(_format_date(factura.get("Fecha_Factura")))}</td>
      <td class="meta">MÉTODO DE PAGO<br>{_escape(metodo_pago)}</td></tr></table>
    <div class="total-banner">TOTAL A PAGAR: {_currency(total)}</div>
    <table class="products">
      <thead><tr><th>PRODUCTO</th><th class="number">CANT.</th>
        <th class="number">P. UNIT</th><th class="number">TOTAL</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <table class="summary" align="right">
      <tr><td>SUBTOTAL</td><td class="number">{_currency(subtotal)}</td></tr>
      <tr><td>DESCUENTO</td><td class="number">{_currency(descuento)}</td></tr>
      <tr class="grand-total"><td>TOTAL A PAGAR</td><td class="number">{_currency(total)}</td></tr>
    </table>
    {credit_details}
    <div class="payment"><b>FORMA DE PAGO</b><br>
      Método de Pago: {_escape(metodo_pago)}
    </div>
    <p class="footer"><b>¡Gracias por tu compra!</b></p>
    """
    return _document_shell(body)


def build_credit_receipt_html(factura_completa, venta, pagos, abono):
    """Mantiene compatibilidad con tests unitarios existentes."""
    cliente = factura_completa.get("Cliente", {})
    invoice = factura_completa.get("Factura", {})
    nombre_cliente = " ".join(
        part for part in (cliente.get("Nombre"), cliente.get("Apellido")) if part
    )
    saldo = max(0, float(venta.Saldo_Pendiente) - float(abono))

    payment_rows = "".join(
        "<tr>"
        f"<td>{_escape(_format_date(getattr(pago, 'Fecha_Registro', '')))}</td>"
        f"<td>{_currency(getattr(pago, 'Monto', 0))}</td>"
        f"<td>{_escape(getattr(pago, 'metodopago', ''))}</td>"
        f"<td>{_escape(getattr(pago, 'tipopago', ''))}</td>"
        "</tr>"
        for pago in pagos
    )
    if not payment_rows:
        payment_rows = '<tr><td colspan="4">No hay abonos registrados.</td></tr>'

    body = f"""
    <table class="header"><tr>
      <td><strong>Distri Magik</strong><br>
        <span class="meta">{_COMPANY_ADDRESS} · Tel. {_COMPANY_PHONE}</span></td>
      <td class="title">RECIBO DE ABONO<br>
        <span class="meta">Factura N.º {_escape(invoice.get('ID_Factura', ''))}</span>
      </td>
    </tr></table>
    <p><b>CLIENTE:</b> {_escape(nombre_cliente)}<br>
       <b>CÉDULA:</b> {_escape(cliente.get('ID_Cliente', ''))}</p>
    <table class="summary" align="right">
      <tr><td>DEUDA TOTAL</td><td class="number">{_currency(venta.Total_Deuda)}</td></tr>
      <tr><td>ABONO ACTUAL</td><td class="number">{_currency(abono)}</td></tr>
      <tr class="grand-total"><td>SALDO PENDIENTE</td><td class="number">{_currency(saldo)}</td></tr>
    </table>
    <p>Fecha límite: {_escape(_format_date(venta.Fecha_Limite))}</p>
    <p class="section-title">HISTORIAL DE ABONOS</p>
    <table class="products"><thead><tr><th>FECHA</th><th class="number">MONTO</th>
      <th>MÉTODO</th><th>TIPO</th></tr></thead><tbody>{payment_rows}</tbody></table>
    <p class="footer"><b>¡Gracias por tu compra!</b></p>
    """
    return _document_shell(body)


def open_printer_settings(parent=None) -> bool:
    """Abre el diálogo de configuración de impresora de forma voluntaria desde la UI.

    Retorna True si el usuario guardó los cambios.
    """
    dialog = ConfigurarImpresoraDialog(parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


def _resolve_page_size(printer_info: QPrinterInfo, paper_type: str) -> QPageSize:
    """Determina el QPageSize adecuado según la configuración y el driver de la impresora."""
    target_w, target_h = PAPER_DIMENSIONS_MM.get(paper_type, PAPER_DIMENSIONS_MM[PAPER_CARTA])

    # Buscar coincidencia exacta en las páginas reportadas por la impresora
    for supported in printer_info.supportedPageSizes():
        w = supported.size(QPageSize.Unit.Millimeter).width()
        h = supported.size(QPageSize.Unit.Millimeter).height()
        if abs(w - target_w) <= 2.0 and abs(h - target_h) <= 2.0:
            return supported

    # Si es Oficio y la impresora no lo tiene por nombre, buscar Carta o tamaño personalizado
    if paper_type == PAPER_OFICIO:
        return QPageSize(
            QSizeF(target_w, target_h),
            QPageSize.Unit.Millimeter,
            "Oficio Colombia",
        )

    return QPageSize(QPageSize.PageSizeId.Letter)


def _send_pdf_to_printer(
    pdf_path: str, printer_info: QPrinterInfo, paper_type: str, document_title: str
) -> bool:
    """Renderiza e imprime un PDF directamente a través de QPdfDocument y QPainter sobre QPrinter."""
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPrinterName(printer_info.printerName())
    printer.setDocName(document_title)
    printer.setResolution(300)

    page_size = _resolve_page_size(printer_info, paper_type)
    layout = QPageLayout(
        page_size,
        QPageLayout.Orientation.Portrait,
        QMarginsF(0, 0, 0, 0),  # Los márgenes ya están calculados dentro del PDF
        QPageLayout.Unit.Millimeter,
    )
    printer.setPageLayout(layout)

    pdf_doc = QPdfDocument(None)
    pdf_doc.load(pdf_path)
    page_count = pdf_doc.pageCount()

    if page_count == 0:
        pdf_doc.close()
        raise RuntimeError("El archivo de factura generado está vacío.")

    painter = QPainter()
    if not painter.begin(printer):
        pdf_doc.close()
        raise RuntimeError(
            f"No se pudo iniciar el trabajo de impresión en «{printer_info.printerName()}». "
            "Verifique que la impresora esté conectada y en línea."
        )

    try:
        paint_rect = printer.pageLayout().paintRectPixels(printer.resolution())
        for page_idx in range(page_count):
            if page_idx > 0:
                printer.newPage()

            pts = pdf_doc.pagePointSize(page_idx)
            # Calcular tamaño de rasterizado óptimo a 300 DPI
            dpi_factor = printer.resolution() / 72.0
            raster_size = QSize(
                int(pts.width() * dpi_factor),
                int(pts.height() * dpi_factor),
            )
            qimage = pdf_doc.render(page_idx, raster_size)

            if not qimage.isNull():
                target_rect = QRectF(
                    paint_rect.x(),
                    paint_rect.y(),
                    paint_rect.width(),
                    paint_rect.height(),
                )
                painter.drawImage(target_rect, qimage)
    finally:
        painter.end()
        pdf_doc.close()

    if printer.error() != QPrinter.PrinterError.NoError:
        raise RuntimeError(f"Error devuelto por la impresora: {printer.error().name}")

    return True


def _handle_printing_error(
    parent,
    pdf_path: str,
    error_msg: str,
    pdf_generator_fn: Callable[[str, str], str],
    document_title: str,
) -> bool:
    """Manejo de errores asistido con opciones de: Reintentar, Cambiar Impresora o Guardar PDF."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Error de Impresión")
    msg_box.setText(f"Ocurrió un inconveniente al imprimir «{document_title}»:")
    msg_box.setInformativeText(f"{error_msg}\n\n¿Cómo desea proceder?")

    btn_reintentar = msg_box.addButton("Reintentar", QMessageBox.ButtonRole.ActionRole)
    btn_cambiar = msg_box.addButton("Cambiar Impresora", QMessageBox.ButtonRole.ActionRole)
    btn_guardar_pdf = msg_box.addButton("Guardar como PDF", QMessageBox.ButtonRole.ActionRole)
    btn_cancelar = msg_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)

    msg_box.exec()
    clicked = msg_box.clickedButton()

    if clicked == btn_reintentar:
        return _execute_print_pipeline(parent, pdf_generator_fn, document_title)

    if clicked == btn_cambiar:
        if open_printer_settings(parent):
            return _execute_print_pipeline(parent, pdf_generator_fn, document_title)
        return False

    if clicked == btn_guardar_pdf:
        save_path, _ = QFileDialog.getSaveFileName(
            parent,
            f"Guardar {document_title}",
            f"{document_title.replace(' ', '_')}.pdf",
            "Archivos PDF (*.pdf)",
        )
        if save_path:
            try:
                import shutil
                shutil.copyfile(pdf_path, save_path)
                QMessageBox.information(
                    parent,
                    "Archivo Guardado",
                    f"El documento se guardó exitosamente en:\n{save_path}",
                )
                return True
            except Exception as e:
                QMessageBox.critical(
                    parent, "Error", f"No se pudo guardar el archivo PDF: {e}"
                )
        return False

    return False


def _execute_print_pipeline(
    parent,
    pdf_generator_fn: Callable[[str, str], str],
    document_title: str,
) -> bool:
    """Ejecuta el flujo completo de verificación, generación y envío a la impresora."""
    config = load_printer_config()

    # 1. Comprobar si está configurada
    if not config.get("configured") or not config.get("printer_name"):
        dialog = ConfigurarImpresoraDialog(
            parent,
            reason_message="Configure la impresora y tamaño de papel por primera vez.",
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        config = load_printer_config()

    # 2. Validar que la impresora configurada exista y esté disponible
    is_ready, reason, printer_info = validate_printer_ready(config)
    if not is_ready:
        dialog = ConfigurarImpresoraDialog(
            parent,
            reason_message=f"{reason}\nPor favor seleccione una impresora disponible para continuar.",
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        config = load_printer_config()
        printer_info = find_printer_info(config.get("printer_name", ""))
        if not printer_info:
            QMessageBox.warning(
                parent,
                "Impresión no disponible",
                "No se pudo inicializar la impresora seleccionada.",
            )
            return False

    paper_type = config.get("paper_type", PAPER_CARTA)

    # 3. Generar PDF temporal adaptado a la hoja configurada
    temp_fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf", prefix="factura_distri_")
    os.close(temp_fd)

    try:
        pdf_generator_fn(temp_pdf_path, paper_type)

        # 4. Enviar directamente a la impresora (silencioso y automático)
        _send_pdf_to_printer(temp_pdf_path, printer_info, paper_type, document_title)
        logger.info(
            f"Documento «{document_title}» enviado exitosamente a {printer_info.printerName()} ({paper_type})."
        )
        return True
    except Exception as exc:
        logger.error(f"Fallo al imprimir {document_title}: {exc}")
        return _handle_printing_error(
            parent, temp_pdf_path, str(exc), pdf_generator_fn, document_title
        )
    finally:
        try:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
        except Exception:
            pass


def print_invoice(
    parent, factura_completa: Dict[str, Any], credito: Optional[Dict[str, Any]] = None
) -> bool:
    """Imprime automáticamente una factura comercial en hoja Carta u Oficio Colombia.

    Reconoce la impresora preconfigurada e imprime en segundo plano sin interrupciones.
    Si la impresora no está configurada o se desconecta, asiste al usuario para reconfigurarla.
    """
    def _generate(out_path: str, paper_type: str) -> str:
        return generate_invoice_pdf(factura_completa, out_path, paper_type, credito)

    raw_id = factura_completa.get("Factura", {}).get("ID_Factura", "")
    title = f"Factura N.º {raw_id}" if raw_id else "Factura de venta"
    return _execute_print_pipeline(parent, _generate, title)


def print_credit_receipt(
    parent, factura_completa: Dict[str, Any], venta: Any, pagos: List[Any], abono: float
) -> bool:
    """Imprime automáticamente un recibo de abono para créditos en hoja Carta u Oficio Colombia."""
    def _generate(out_path: str, paper_type: str) -> str:
        return generate_credit_receipt_pdf(
            factura_completa, venta, pagos, abono, out_path, paper_type
        )

    raw_id = factura_completa.get("Factura", {}).get("ID_Factura", "")
    title = f"Recibo de Abono Factura N.º {raw_id}" if raw_id else "Recibo de abono"
    return _execute_print_pipeline(parent, _generate, title)
