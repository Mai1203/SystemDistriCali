"""Shared Windows printing for full-page invoices and credit receipts."""

from datetime import date, datetime
from html import escape
from pathlib import Path

from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QPageLayout, QPageSize, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)


_PAPER_SIZES_MM = {
    "Carta": (215.9, 279.4),
    "Oficio": (215.9, 330.2),
}
_COMPANY_ADDRESS = "Cali, Colombia"
_COMPANY_PHONE = "315-038-66-18"
_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "LogoDistriMagik.png"


def _supported_paper_sizes(printer_info):
    options = {}
    for page_size in printer_info.supportedPageSizes():
        width, height = page_size.size(QPageSize.Unit.Millimeter).width(), page_size.size(
            QPageSize.Unit.Millimeter
        ).height()
        for label, (target_width, target_height) in _PAPER_SIZES_MM.items():
            if abs(width - target_width) <= 1.5 and abs(height - target_height) <= 1.5:
                options[label] = page_size
    return options


class _PrintSettingsDialog(QDialog):
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

        default_name = QPrinterInfo.defaultPrinter().printerName()
        for printer_info in printers:
            name = printer_info.printerName()
            label = f"{name} (predeterminada)" if name == default_name else name
            self.printer_combo.addItem(
                label, printer_info
            )

        for index in range(self.printer_combo.count()):
            printer_info = self.printer_combo.itemData(index)
            if printer_info.printerName() == default_name:
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


def _print_html(parent, document_html, title):
    printers = QPrinterInfo.availablePrinters()
    if not printers:
        QMessageBox.warning(
            parent,
            "Impresión no disponible",
            "Windows no detecta impresoras instaladas. Conecte o configure una impresora e intente nuevamente.",
        )
        return False

    dialog = _PrintSettingsDialog(printers, parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return False

    printer_info, page_size = dialog.selection()
    if printer_info is None or page_size is None:
        QMessageBox.warning(
            parent,
            "Configuración incompleta",
            "Seleccione una impresora y un tamaño de papel compatible.",
        )
        return False

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPrinterName(printer_info.printerName())
    printer.setResolution(300)
    layout = QPageLayout(
        page_size,
        QPageLayout.Orientation.Portrait,
        QMarginsF(12, 12, 12, 12),
        QPageLayout.Unit.Millimeter,
    )
    if not printer.setPageLayout(layout):
        QMessageBox.warning(
            parent,
            "Configuración no disponible",
            f"No se pudo aplicar el tamaño de papel seleccionado en {printer_info.printerName()}.",
        )
        return False

    document = QTextDocument()
    document.setHtml(document_html)
    document.setPageSize(printer.pageLayout().paintRect(QPageLayout.Unit.Point).size())
    document.print(printer)
    if printer.error() != QPrinter.PrinterError.NoError:
        QMessageBox.critical(
            parent,
            "Error de impresión",
            f"No se pudo enviar «{title}» a {printer_info.printerName()}. "
            "Revise que la impresora esté conectada y que el controlador funcione.",
        )
        return False
    return True


def print_invoice(parent, factura_completa, credito=None):
    return _print_html(
        parent,
        build_invoice_html(factura_completa, credito),
        "Factura de venta",
    )


def print_credit_receipt(parent, factura_completa, venta, pagos, abono):
    return _print_html(
        parent,
        build_credit_receipt_html(factura_completa, venta, pagos, abono),
        "Recibo de abono",
    )
