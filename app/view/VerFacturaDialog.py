"""
Diálogo modal para visualizar el detalle completo de facturas y credifacturas.
Incluye área scrollable para facturas con múltiples productos, vista estructurada
y vista previa de impresión, con diseño alineado al sistema Lady Nail.
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QTextBrowser,
    QTabWidget,
    QMessageBox,
)
import qtawesome as qta

from ..utils.formateador import formatear_numero
from ..services.printing_service import build_invoice_html


# ─────────────────────────────────────────────────────────────────
#  Paleta semántica (Sistema de Diseño Lady Nail)
# ─────────────────────────────────────────────────────────────────
_PRIMARY        = "#862D6D"
_PRIMARY_HOVER  = "#6E2259"
_PRIMARY_ACTIVE = "#551443"
_BG             = "#F5F0F4"
_CARD_BG        = "#FFFFFF"
_BORDER         = "#D8C8D5"
_BORDER_HOVER   = "#A97099"
_TEXT           = "#201A24"
_MUTED          = "#7B737F"
_DIVIDER        = "#E2DAE1"
_CARD_BORDER    = "#EAE0E8"

_SUCCESS_BG     = "#E8F8F0"
_SUCCESS_TEXT   = "#1E824C"
_SUCCESS_BORDER = "#A3E4D7"

_WARNING_BG     = "#FEF5E7"
_WARNING_TEXT   = "#D35400"
_WARNING_BORDER = "#FAD7A0"

_INFO_BG        = "#F8EDF5"
_INFO_TEXT      = "#862D6D"
_INFO_BORDER    = "#E8C5DE"

_FONT = "'Segoe UI', Arial, sans-serif"


# ─────────────────────────────────────────────────────────────────
#  Estilo general del diálogo
# ─────────────────────────────────────────────────────────────────
_DIALOG_STYLESHEET = f"""
QDialog {{
    background-color: {_BG};
    font-family: {_FONT};
    color: {_TEXT};
}}
QFrame#HeaderCard {{
    background-color: {_CARD_BG};
    border-bottom: 1px solid {_DIVIDER};
    padding: 12px 18px;
}}
QFrame#Card {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 8px;
}}
QFrame#BottomBar {{
    background-color: {_CARD_BG};
    border-top: 1px solid {_DIVIDER};
    padding: 10px 18px;
}}
QLabel {{
    font-family: {_FONT};
    color: {_TEXT};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: {_DIVIDER};
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {_BORDER_HOVER};
    border-radius: 4px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_PRIMARY};
}}
QScrollBar::handle:vertical:pressed {{
    background: {_PRIMARY_ACTIVE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background: {_DIVIDER};
    height: 8px;
    border-radius: 4px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {_BORDER_HOVER};
    border-radius: 4px;
    min-width: 32px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {_PRIMARY};
}}
QScrollBar::handle:horizontal:pressed {{
    background: {_PRIMARY_ACTIVE};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
    background: none;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}
QTabWidget::pane {{
    border: none;
    background: transparent;
}}
QTabBar::tab {{
    background: #EAE0E8;
    color: {_MUTED};
    font-weight: 600;
    font-size: 12px;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background: {_CARD_BG};
    color: {_PRIMARY};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background: #F0E6EE;
    color: {_TEXT};
}}
QTableWidget {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 6px;
    gridline-color: #F0EAF0;
    font-family: {_FONT};
    font-size: 12px;
    color: {_TEXT};
    selection-background-color: #F2E4EE;
    selection-color: {_PRIMARY};
}}
QHeaderView::section {{
    background-color: #EDE3EB;
    color: {_PRIMARY};
    font-family: {_FONT};
    font-size: 11px;
    font-weight: 700;
    border: none;
    padding: 7px 6px;
}}
"""


class ScrollIgnoredTableWidget(QTableWidget):
    """
    Tabla que delega el wheelEvent al QScrollArea contenedor para que
    el usuario pueda desplazarse suavemente por todo el documento
    sin quedar atrapado en el scroll interno de la tabla.
    """
    def wheelEvent(self, event):
        event.ignore()


class VerFacturaDialog(QDialog):
    """
    Diálogo para visualizar una factura con soporte total de scroll,
    evitando que facturas con muchos productos se corten o queden fuera de pantalla.
    """

    def __init__(
        self,
        factura_completa: dict,
        credito: dict = None,
        pagos: list = None,
        titulo: str = None,
        parent = None,
    ):
        super().__init__(parent)
        self.factura_completa = factura_completa or {}
        self.credito = credito
        self.pagos = pagos or []

        self._factura = self.factura_completa.get("Factura", {})
        self._cliente = self.factura_completa.get("Cliente", {})
        self._detalles = self.factura_completa.get("Detalles", [])

        id_factura = self._factura.get("ID_Factura", "")
        if titulo:
            self.setWindowTitle(titulo)
        elif self.credito:
            self.setWindowTitle(f"Factura de venta a crédito #{id_factura}")
        else:
            self.setWindowTitle(f"Factura de venta #{id_factura}")

        self.resize(800, 680)
        self.setMinimumSize(680, 520)
        self.setStyleSheet(_DIALOG_STYLESHEET)

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 1. Encabezado Fijo Superior ────────────────────────────
        header_frame = self._build_header()
        root_layout.addWidget(header_frame, 0)

        # ── 2. Contenedor de pestañas (detalle y vista de impresión) ─
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setContentsMargins(16, 10, 16, 6)

        tab_detalle = self._build_tab_detalle()
        tab_impresion = self._build_tab_impresion()

        icon_detalle = qta.icon("fa5s.list-alt", color=_PRIMARY)
        icon_impresion = qta.icon("fa5s.file-invoice", color=_PRIMARY)

        self.tab_widget.addTab(tab_detalle, icon_detalle, " Detalle de Factura")
        self.tab_widget.addTab(tab_impresion, icon_impresion, " Vista de impresión")

        root_layout.addWidget(self.tab_widget, 1)

        # ── 3. Barra de Acciones Inferior Fija ──────────────────────
        bottom_bar = self._build_bottom_bar()
        root_layout.addWidget(bottom_bar, 0)

    # ─────────────────────────────────────────────────────────────
    #  Encabezado
    # ─────────────────────────────────────────────────────────────
    def _build_header(self) -> QFrame:
        header_frame = QFrame()
        header_frame.setObjectName("HeaderCard")

        layout = QHBoxLayout(header_frame)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        # Ícono
        lbl_icon = QLabel()
        icon_name = "fa5s.file-invoice-dollar"
        lbl_icon.setPixmap(qta.icon(icon_name, color=_PRIMARY).pixmap(32, 32))
        layout.addWidget(lbl_icon)

        # Título y subtítulo
        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        id_factura = self._factura.get("ID_Factura", "-")
        tipo_factura = self._factura.get("TipoFactura", "Venta")

        lbl_title = QLabel(f"FACTURA DE VENTA #{id_factura}")
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {_PRIMARY};")
        title_box.addWidget(lbl_title)

        fecha = self._factura.get("Fecha_Factura", "")
        if hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
        else:
            fecha_str = str(fecha) if fecha else "Fecha no registrada"

        lbl_sub = QLabel(f"Fecha: {fecha_str}  •  Tipo: {tipo_factura}")
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {_MUTED};")
        title_box.addWidget(lbl_sub)

        layout.addLayout(title_box)
        layout.addStretch()

        # Badges de Estado y Crédito
        estado = self._factura.get("Estado", False)
        is_pagada = bool(estado) if not isinstance(estado, str) else estado.lower() in ("pagada", "true", "1")

        if is_pagada:
            lbl_estado = QLabel("PAGADA")
            lbl_estado.setStyleSheet(
                f"background-color: {_SUCCESS_BG}; color: {_SUCCESS_TEXT}; "
                f"border: 1px solid {_SUCCESS_BORDER}; border-radius: 12px; "
                f"padding: 4px 12px; font-size: 11px; font-weight: 700;"
            )
        else:
            lbl_estado = QLabel("PENDIENTE")
            lbl_estado.setStyleSheet(
                f"background-color: {_WARNING_BG}; color: {_WARNING_TEXT}; "
                f"border: 1px solid {_WARNING_BORDER}; border-radius: 12px; "
                f"padding: 4px 12px; font-size: 11px; font-weight: 700;"
            )
        layout.addWidget(lbl_estado)

        if self.credito:
            lbl_cred_badge = QLabel("CRÉDITO")
            lbl_cred_badge.setStyleSheet(
                f"background-color: {_INFO_BG}; color: {_INFO_TEXT}; "
                f"border: 1px solid {_INFO_BORDER}; border-radius: 12px; "
                f"padding: 4px 12px; font-size: 11px; font-weight: 700;"
            )
            layout.addWidget(lbl_cred_badge)

        return header_frame

    # ─────────────────────────────────────────────────────────────
    #  Pestaña 1: Detalle de Factura (Área Scrollable)
    # ─────────────────────────────────────────────────────────────
    def _build_tab_detalle(self) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(0)

        # ScrollArea principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(12, 12, 12, 16)
        content_layout.setSpacing(14)

        # 1. Tarjeta de Cliente y Datos de Venta
        card_info = self._build_info_card()
        content_layout.addWidget(card_info)

        # 2. Tarjeta de Productos (Tabla de Artículos con auto-expansión)
        card_productos = self._build_productos_card()
        content_layout.addWidget(card_productos)

        # 3. Tarjeta de Totales
        card_totales = self._build_totales_card()
        content_layout.addWidget(card_totales)

        # 4. Tarjeta de Crédito y Abonos (si aplica)
        if self.credito:
            card_credito = self._build_credito_card()
            content_layout.addWidget(card_credito)

        content_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        container_layout.addWidget(scroll_area)

        return container

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Información de Cliente y Pago
    # ─────────────────────────────────────────────────────────────
    def _build_info_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Título de la tarjeta
        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon("fa5s.user-circle", color=_PRIMARY).pixmap(18, 18))
        header.addWidget(lbl_icon)

        lbl_title = QLabel("Información del Cliente y Venta")
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {_PRIMARY};")
        header.addWidget(lbl_title)
        header.addStretch()
        layout.addLayout(header)

        # Separador fino
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {_DIVIDER}; max-height: 1px;")
        layout.addWidget(divider)

        # Datos en grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)

        nombre = f"{self._cliente.get('Nombre', '')} {self._cliente.get('Apellido', '')}".strip() or "Consumidor Final"
        identificacion = str(self._cliente.get("ID_Cliente") or "No registrada")
        telefono = str(self._cliente.get("Teléfono") or self._cliente.get("telefono") or "No registrado")
        direccion = str(self._cliente.get("Direccion") or self._cliente.get("direccion") or "No registrada")
        metodo_pago = self._factura.get("MetodoPago", "No especificado")

        campos = [
            ("Cliente:", nombre, 0, 0),
            ("Identificación:", identificacion, 0, 1),
            ("Teléfono:", telefono, 1, 0),
            ("Dirección:", direccion, 1, 1),
            ("Método de Pago:", metodo_pago, 2, 0),
        ]

        # Si hubo desglose de pagos en efectivo o transferencia
        m_efectivo = float(self._factura.get("Monto_efectivo", 0) or 0)
        m_transaccion = float(self._factura.get("Monto_TRANSACCION", 0) or 0)
        if m_efectivo > 0 and m_transaccion > 0:
            desglose = f"Efectivo: ${formatear_numero(m_efectivo)} | Transf: ${formatear_numero(m_transaccion)}"
            campos.append(("Desglose:", desglose, 2, 1))

        for etiqueta, valor, row, col in campos:
            box = QHBoxLayout()
            box.setSpacing(6)
            lbl_k = QLabel(etiqueta)
            lbl_k.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {_MUTED}; min-width: 95px;")
            lbl_v = QLabel(valor)
            lbl_v.setStyleSheet(f"font-size: 12px; font-weight: 500; color: {_TEXT};")
            lbl_v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            box.addWidget(lbl_k)
            box.addWidget(lbl_v, 1)
            grid.addLayout(box, row, col)

        layout.addLayout(grid)
        return card

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Productos Facturados
    # ─────────────────────────────────────────────────────────────
    def _build_productos_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Título y contador
        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon("fa5s.box-open", color=_PRIMARY).pixmap(18, 18))
        header.addWidget(lbl_icon)

        lbl_title = QLabel("Productos / Artículos")
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {_PRIMARY};")
        header.addWidget(lbl_title)

        num_items = len(self._detalles)
        lbl_count = QLabel(f"{num_items} {'artículo' if num_items == 1 else 'artículos'}")
        lbl_count.setStyleSheet(
            f"background-color: #F8EDF5; color: {_PRIMARY}; border-radius: 10px; "
            f"padding: 2px 10px; font-size: 11px; font-weight: 600;"
        )
        header.addWidget(lbl_count)
        header.addStretch()
        layout.addLayout(header)

        # Separador fino
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {_DIVIDER}; max-height: 1px;")
        layout.addWidget(divider)

        # Comprobar si hay algún lote registrado
        tiene_lotes = any(bool(d.get("Lote") and d.get("Lote") != "LOTE") for d in self._detalles)

        if tiene_lotes:
            columnas = ["#", "Producto", "Lote", "Cant.", "Precio Unit.", "Subtotal"]
        else:
            columnas = ["#", "Producto", "Cant.", "Precio Unit.", "Subtotal"]

        table = ScrollIgnoredTableWidget()
        table.setColumnCount(len(columnas))
        table.setHorizontalHeaderLabels(columnas)
        table.setRowCount(len(self._detalles))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Configurar anchos de columna
        h_header = table.horizontalHeader()
        h_header.setHighlightSections(False)
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 36)

        col_prod = 1
        h_header.setSectionResizeMode(col_prod, QHeaderView.ResizeMode.Stretch)

        idx = 2
        if tiene_lotes:
            h_header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(idx, 90)
            idx += 1

        h_header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(idx, 60)   # Cantidad
        idx += 1

        h_header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(idx, 115)  # Precio Unitario
        idx += 1

        h_header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(idx, 125)  # Subtotal

        # Llenar datos
        for row, det in enumerate(self._detalles):
            table.setRowHeight(row, 30)

            # 0. Num
            it_num = QTableWidgetItem(str(row + 1))
            it_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_num.setForeground(QtGui.QColor(_MUTED))
            table.setItem(row, 0, it_num)

            # 1. Producto
            nombre_prod = det.get("Producto", "-")
            marca = det.get("Marca")
            if marca and marca != "Sin Marca":
                nombre_prod = f"{nombre_prod} ({marca})"
            it_prod = QTableWidgetItem(nombre_prod)
            it_prod.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 1, it_prod)

            cur_col = 2
            if tiene_lotes:
                lote_val = det.get("Lote") or "-"
                it_lote = QTableWidgetItem(str(lote_val))
                it_lote.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, cur_col, it_lote)
                cur_col += 1

            # Cantidad
            cant = det.get("Cantidad", 0)
            cant_str = str(int(cant)) if (isinstance(cant, (int, float)) and cant % 1 == 0) else f"{cant}"
            it_cant = QTableWidgetItem(cant_str)
            it_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_cant = it_cant.font()
            font_cant.setBold(True)
            it_cant.setFont(font_cant)
            table.setItem(row, cur_col, it_cant)
            cur_col += 1

            # Precio Unitario
            precio = float(det.get("Precio_Unitario", 0) or 0)
            it_precio = QTableWidgetItem(f"${formatear_numero(precio)}")
            it_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, cur_col, it_precio)
            cur_col += 1

            # Subtotal
            subt = float(det.get("Subtotal", 0) or 0)
            it_subt = QTableWidgetItem(f"${formatear_numero(subt)}")
            it_subt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font_subt = it_subt.font()
            font_subt.setBold(True)
            it_subt.setFont(font_subt)
            it_subt.setForeground(QtGui.QColor(_PRIMARY))
            table.setItem(row, cur_col, it_subt)

        # Altura fija para que expanda todos los productos y el QScrollArea maneje el scroll fluido
        header_height = h_header.height() or 32
        row_heights = sum(table.rowHeight(r) for r in range(table.rowCount()))
        total_table_height = max(80, header_height + row_heights + 6)
        table.setFixedHeight(total_table_height)

        layout.addWidget(table)
        return card

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Resumen de Totales
    # ─────────────────────────────────────────────────────────────
    def _build_totales_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        subtotal = sum(float(d.get("Subtotal", 0) or 0) for d in self._detalles)
        descuento = float(self._factura.get("Descuento", 0) or 0)
        total = subtotal - descuento

        # Subtotal
        box_sub = QHBoxLayout()
        box_sub.addStretch()
        lbl_sub_k = QLabel("Subtotal:")
        lbl_sub_k.setStyleSheet(f"font-size: 13px; color: {_MUTED};")
        lbl_sub_v = QLabel(f"${formatear_numero(subtotal)}")
        lbl_sub_v.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {_TEXT}; min-width: 120px; text-align: right;")
        lbl_sub_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        box_sub.addWidget(lbl_sub_k)
        box_sub.addWidget(lbl_sub_v)
        layout.addLayout(box_sub)

        # Descuento (si existe)
        if descuento > 0:
            box_desc = QHBoxLayout()
            box_desc.addStretch()
            lbl_desc_k = QLabel("Descuento:")
            lbl_desc_k.setStyleSheet(f"font-size: 13px; color: #C0392B;")
            lbl_desc_v = QLabel(f"-${formatear_numero(descuento)}")
            lbl_desc_v.setStyleSheet(f"font-size: 13px; font-weight: 600; color: #C0392B; min-width: 120px; text-align: right;")
            lbl_desc_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            box_desc.addWidget(lbl_desc_k)
            box_desc.addWidget(lbl_desc_v)
            layout.addLayout(box_desc)

        # Separador fino
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {_DIVIDER}; max-height: 1px;")
        layout.addWidget(divider)

        # Total General
        box_tot = QHBoxLayout()
        box_tot.addStretch()
        lbl_tot_k = QLabel("TOTAL:")
        lbl_tot_k.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {_PRIMARY};")
        lbl_tot_v = QLabel(f"${formatear_numero(total)}")
        lbl_tot_v.setStyleSheet(
            f"font-size: 18px; font-weight: 800; color: {_PRIMARY}; "
            f"min-width: 130px; text-align: right;"
        )
        lbl_tot_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        box_tot.addWidget(lbl_tot_k)
        box_tot.addWidget(lbl_tot_v)
        layout.addLayout(box_tot)

        return card

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Crédito y Abonos (para Credifacturas)
    # ─────────────────────────────────────────────────────────────
    def _build_credito_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Encabezado
        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon("fa5s.hand-holding-usd", color=_PRIMARY).pixmap(18, 18))
        header.addWidget(lbl_icon)

        lbl_title = QLabel("Detalle de Crédito y Abonos")
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {_PRIMARY};")
        header.addWidget(lbl_title)
        header.addStretch()
        layout.addLayout(header)

        # Separador fino
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {_DIVIDER}; max-height: 1px;")
        layout.addWidget(divider)

        # Cajas métricas: Deuda, Saldo, Fecha Límite
        box_metrics = QHBoxLayout()
        box_metrics.setSpacing(12)

        total_deuda = float(self.credito.get("Total_Deuda", 0) or 0)
        saldo_pendiente = float(self.credito.get("Saldo_Pendiente", 0) or 0)
        fecha_limite = self.credito.get("Fecha_Limite", "-")
        if hasattr(fecha_limite, "strftime"):
            fecha_limite_str = fecha_limite.strftime("%d/%m/%Y")
        else:
            fecha_limite_str = str(fecha_limite)

        metrics = [
            ("TOTAL DEUDA", f"${formatear_numero(total_deuda)}", _TEXT, _CARD_BG, _CARD_BORDER),
            ("SALDO PENDIENTE", f"${formatear_numero(saldo_pendiente)}", 
             _WARNING_TEXT if saldo_pendiente > 0 else _SUCCESS_TEXT, 
             _WARNING_BG if saldo_pendiente > 0 else _SUCCESS_BG, 
             _WARNING_BORDER if saldo_pendiente > 0 else _SUCCESS_BORDER),
            ("FECHA LÍMITE", fecha_limite_str, _TEXT, _CARD_BG, _CARD_BORDER),
        ]

        for tit, val, color, bg, border in metrics:
            m_frame = QFrame()
            m_frame.setStyleSheet(
                f"background-color: {bg}; border: 1px solid {border}; "
                f"border-radius: 6px; padding: 6px 10px;"
            )
            m_layout = QVBoxLayout(m_frame)
            m_layout.setContentsMargins(4, 4, 4, 4)
            m_layout.setSpacing(2)

            lbl_t = QLabel(tit)
            lbl_t.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {_MUTED};")
            lbl_v = QLabel(val)
            lbl_v.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {color};")
            m_layout.addWidget(lbl_t)
            m_layout.addWidget(lbl_v)
            box_metrics.addWidget(m_frame)

        layout.addLayout(box_metrics)

        # Tabla de Abonos
        lbl_abonos_tit = QLabel("Historial de Abonos")
        lbl_abonos_tit.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {_MUTED}; margin-top: 4px;")
        layout.addWidget(lbl_abonos_tit)

        if self.pagos:
            table_pagos = ScrollIgnoredTableWidget()
            table_pagos.setColumnCount(4)
            table_pagos.setHorizontalHeaderLabels(["Fecha Abono", "Monto", "Método", "Tipo Pago"])
            table_pagos.setRowCount(len(self.pagos))
            table_pagos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table_pagos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table_pagos.verticalHeader().setVisible(False)
            table_pagos.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            p_header = table_pagos.horizontalHeader()
            p_header.setHighlightSections(False)
            p_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            p_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            table_pagos.setColumnWidth(1, 120)
            p_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            table_pagos.setColumnWidth(2, 110)
            p_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            table_pagos.setColumnWidth(3, 110)

            for r, pago in enumerate(self.pagos):
                table_pagos.setRowHeight(r, 28)

                # Fecha
                f_pago = getattr(pago, "Fecha_Registro", pago.get("Fecha_Registro") if isinstance(pago, dict) else "")
                if hasattr(f_pago, "strftime"):
                    f_str = f_pago.strftime("%d/%m/%Y %H:%M")
                else:
                    f_str = str(f_pago)
                it_f = QTableWidgetItem(f_str)
                it_f.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                table_pagos.setItem(r, 0, it_f)

                # Monto
                monto = getattr(pago, "Monto", pago.get("Monto") if isinstance(pago, dict) else 0)
                it_m = QTableWidgetItem(f"${formatear_numero(monto)}")
                it_m.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                font_m = it_m.font()
                font_m.setBold(True)
                it_m.setFont(font_m)
                it_m.setForeground(QtGui.QColor(_SUCCESS_TEXT))
                table_pagos.setItem(r, 1, it_m)

                # Método
                metodo = getattr(pago, "metodopago", pago.get("metodopago") if isinstance(pago, dict) else "-")
                it_met = QTableWidgetItem(str(metodo))
                it_met.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_pagos.setItem(r, 2, it_met)

                # Tipo
                tipo = getattr(pago, "tipopago", pago.get("tipopago") if isinstance(pago, dict) else "-")
                it_tip = QTableWidgetItem(str(tipo))
                it_tip.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_pagos.setItem(r, 3, it_tip)

            p_h_height = p_header.height() or 28
            p_row_heights = sum(table_pagos.rowHeight(r) for r in range(table_pagos.rowCount()))
            table_pagos.setFixedHeight(max(70, p_h_height + p_row_heights + 6))
            layout.addWidget(table_pagos)
        else:
            lbl_no_pagos = QLabel("No se registran abonos realizados para esta factura de crédito.")
            lbl_no_pagos.setStyleSheet(f"font-size: 12px; color: {_MUTED}; font-style: italic; padding: 4px 0px;")
            layout.addWidget(lbl_no_pagos)

        return card

    # ─────────────────────────────────────────────────────────────
    #  Pestaña 2: Vista previa del documento impreso
    # ─────────────────────────────────────────────────────────────
    def _build_tab_impresion(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        lbl_desc = QLabel("Vista previa de la factura comercial de página completa:")
        lbl_desc.setStyleSheet(f"font-size: 12px; color: {_MUTED};")
        layout.addWidget(lbl_desc)

        preview = QTextBrowser()
        preview.setHtml(build_invoice_html(self.factura_completa, self.credito, self.pagos))
        preview.setOpenExternalLinks(False)
        layout.addWidget(preview)

        return container

    # ─────────────────────────────────────────────────────────────
    #  Barra Inferior de Acciones
    # ─────────────────────────────────────────────────────────────
    def _build_bottom_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("BottomBar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(10)

        # Resumen rápido del total a la izquierda
        subtotal = sum(float(d.get("Subtotal", 0) or 0) for d in self._detalles)
        descuento = float(self._factura.get("Descuento", 0) or 0)
        total = subtotal - descuento

        resumen_box = QHBoxLayout()
        resumen_box.setSpacing(8)

        lbl_total = QLabel(f"Total: ${formatear_numero(total)}")
        lbl_total.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {_PRIMARY};")
        resumen_box.addWidget(lbl_total)

        if self.credito:
            saldo = float(self.credito.get("Saldo_Pendiente", 0) or 0)
            lbl_saldo = QLabel(f"•  Saldo: ${formatear_numero(saldo)}")
            color_saldo = _WARNING_TEXT if saldo > 0 else _SUCCESS_TEXT
            lbl_saldo.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color_saldo};")
            resumen_box.addWidget(lbl_saldo)

        layout.addLayout(resumen_box)
        layout.addStretch()

        # Botón de cierre
        btn_cerrar = QPushButton(" Cerrar")
        btn_cerrar.setIcon(qta.icon("fa5s.times", color="#FFFFFF"))
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-family: {_FONT};
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {_PRIMARY_ACTIVE};
            }}
        """)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)

        return bar
