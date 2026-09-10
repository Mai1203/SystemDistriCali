# Diálogo de selección de lote al agregar producto en ventas
# Se muestra cuando un producto tiene lotes activos registrados.

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QSpinBox,
)
from PyQt6.QtCore import Qt
import qtawesome as qta

# ─────────────────────────────────────────────────────────────────
#  Paleta (misma que el resto del sistema)
# ─────────────────────────────────────────────────────────────────
_PRIMARY       = "#862D6D"
_PRIMARY_H     = "#6E2259"
_PRIMARY_P     = "#551443"
_BG            = "#F5F0F4"
_CARD_BG       = "#FFFFFF"
_BORDER        = "#D8C8D5"
_BORDER_FOCUS  = "#862D6D"
_TEXT          = "#201A24"
_MUTED         = "#7B737F"
_CARD_BORDER   = "#EAE0E8"
_DIVIDER       = "#E2DAE1"

_DIALOG_QSS = f"""
QDialog {{
    background-color: {_BG};
    border-radius: 16px;
}}
QFrame#CardFrame {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 14px;
}}
QLabel#TitleLabel {{
    font-family: 'Segoe UI';
    font-size: 16px;
    font-weight: 700;
    color: {_TEXT};
    background: transparent;
}}
QLabel#ProductoLabel {{
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {_MUTED};
    background: transparent;
}}
QLabel#FieldLabel {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 600;
    color: {_MUTED};
    background: transparent;
}}
QComboBox {{
    background-color: {_CARD_BG};
    border: 1.5px solid {_BORDER};
    border-radius: 7px;
    padding: 6px 10px;
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {_TEXT};
    min-height: 32px;
}}
QComboBox:focus {{
    border-color: {_BORDER_FOCUS};
    background-color: #FFFAFE;
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {_CARD_BG};
    border: 1px solid {_BORDER};
    border-radius: 6px;
    selection-background-color: #F3E6EF;
    selection-color: {_TEXT};
    font-family: 'Segoe UI';
    font-size: 12px;
    padding: 4px;
}}
QSpinBox {{
    background-color: {_CARD_BG};
    border: 1.5px solid {_BORDER};
    border-radius: 7px;
    padding: 6px 10px;
    font-family: 'Segoe UI';
    font-size: 13px;
    font-weight: 600;
    color: {_TEXT};
    min-height: 32px;
}}
QSpinBox:focus {{
    border-color: {_BORDER_FOCUS};
    background-color: #FFFAFE;
}}
QPushButton#BtnConfirmar {{
    background-color: {_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 8px 20px;
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
}}
QPushButton#BtnConfirmar:hover {{
    background-color: {_PRIMARY_H};
}}
QPushButton#BtnConfirmar:pressed {{
    background-color: {_PRIMARY_P};
}}
QPushButton#BtnCancelar {{
    background-color: transparent;
    color: {_PRIMARY};
    border: 1.5px solid {_PRIMARY};
    border-radius: 7px;
    padding: 8px 20px;
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
}}
QPushButton#BtnCancelar:hover {{
    background-color: #FBEFF7;
}}
QPushButton#BtnCancelar:pressed {{
    background-color: #F3E6EF;
}}
"""


def _shadow(widget: QtWidgets.QWidget):
    effect = QtWidgets.QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(32)
    effect.setXOffset(0)
    effect.setYOffset(8)
    effect.setColor(QtGui.QColor(100, 30, 80, 40))
    widget.setGraphicsEffect(effect)


class LoteSeleccionDialog(QDialog):
    """
    Diálogo modal para seleccionar el lote y la cantidad
    de un producto antes de agregarlo a la tabla de venta.

    Parámetros
    ----------
    lotes : list
        Lista de objetos LoteProducto con stock disponible.
    nombre_producto : str
        Nombre del producto para mostrar como referencia.
    tipo_venta : int
        Índice de tipo de venta (0-3) para mostrar el precio correcto.
    obtener_precio_fn : callable
        Función ``obtener_precio_lote(lote, tipo_venta)`` del módulo configuracion.
    parent : QWidget, optional
    """

    def __init__(self, lotes, nombre_producto: str, tipo_venta: int,
                 obtener_precio_fn, parent=None):
        super().__init__(parent)
        self._lotes = lotes
        self._nombre_producto = nombre_producto
        self._tipo_venta = tipo_venta
        self._obtener_precio = obtener_precio_fn

        # Resultado expuesto tras accept()
        self.lote_seleccionado = None   # objeto LoteProducto
        self.cantidad_seleccionada = 1

        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle("Seleccionar Lote")
        self.setMinimumWidth(420)
        self.setMaximumWidth(520)
        self.setSizeGripEnabled(False)
        self.setModal(True)
        self.setStyleSheet(_DIALOG_QSS)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Layout raíz (margen para que la sombra sea visible)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(0)

        # Tarjeta
        card = QFrame()
        card.setObjectName("CardFrame")
        _shadow(card)
        root.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        # ── Encabezado ────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.layer-group", color=_PRIMARY).pixmap(18, 18))
        icon_lbl.setFixedSize(22, 22)
        icon_lbl.setScaledContents(True)
        header_row.addWidget(icon_lbl)

        title = QLabel("Seleccionar Lote")
        title.setObjectName("TitleLabel")
        header_row.addWidget(title, 1)

        # Botón cerrar
        btn_x = QPushButton()
        btn_x.setFixedSize(26, 26)
        btn_x.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        btn_x.setIcon(qta.icon("fa5s.times", color=_MUTED))
        btn_x.setIconSize(QtCore.QSize(10, 10))
        btn_x.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 13px; }
            QPushButton:hover { background-color: #F3E6EF; }
        """)
        btn_x.clicked.connect(self.reject)
        header_row.addWidget(btn_x)
        card_layout.addLayout(header_row)

        # Nombre del producto
        prod_lbl = QLabel(f"Producto: <b>{self._nombre_producto}</b>")
        prod_lbl.setObjectName("ProductoLabel")
        card_layout.addWidget(prod_lbl)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {_DIVIDER}; max-height: 1px; border: none;")
        card_layout.addWidget(sep)

        # ── Selector de lote ──────────────────────────────────────
        lbl_lote = QLabel("Lote disponible")
        lbl_lote.setObjectName("FieldLabel")
        card_layout.addWidget(lbl_lote)

        self._combo_lote = QComboBox()
        self._combo_lote.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        for lote in self._lotes:
            nom = lote.Numero_Lote or f"LOTE-{lote.ID_Lote}"
            pv = self._obtener_precio(lote, self._tipo_venta)
            self._combo_lote.addItem(
                f"{nom}   ·   Stock: {lote.Stock_actual}   ·   ${pv:,.0f}",
                lote,
            )
        self._combo_lote.currentIndexChanged.connect(self._on_lote_cambiado)
        card_layout.addWidget(self._combo_lote)

        # Stock disponible (info dinámica)
        self._stock_info = QLabel()
        self._stock_info.setObjectName("FieldLabel")
        self._stock_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(self._stock_info)

        # ── Cantidad ──────────────────────────────────────────────
        lbl_cant = QLabel("Cantidad")
        lbl_cant.setObjectName("FieldLabel")
        card_layout.addWidget(lbl_cant)

        self._spin_cantidad = QSpinBox()
        self._spin_cantidad.setMinimum(1)
        self._spin_cantidad.setValue(1)
        self._spin_cantidad.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        card_layout.addWidget(self._spin_cantidad)

        # Sincronizar stock info con el lote inicial
        self._on_lote_cambiado(0)

        # ── Botones ───────────────────────────────────────────────
        card_layout.addSpacing(4)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("BtnCancelar")
        btn_cancelar.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancelar.clicked.connect(self.reject)

        btn_confirmar = QPushButton("  Confirmar")
        btn_confirmar.setObjectName("BtnConfirmar")
        btn_confirmar.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        btn_confirmar.setIcon(qta.icon("fa5s.check", color="#FFFFFF"))
        btn_confirmar.setIconSize(QtCore.QSize(11, 11))
        btn_confirmar.clicked.connect(self._confirmar)

        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(btn_confirmar)
        card_layout.addLayout(btn_row)

        self.adjustSize()

    # ─────────────────────────────────────────────────────────────
    def _on_lote_cambiado(self, _index: int):
        lote = self._combo_lote.currentData()
        if lote is None:
            return
        stock = lote.Stock_actual
        self._stock_info.setText(
            f"<span style='color:{_PRIMARY};font-weight:600;'>{stock}</span>"
            f"&nbsp;<span style='color:{_MUTED};'>unidades disponibles</span>"
        )
        self._spin_cantidad.setMaximum(stock)
        if self._spin_cantidad.value() > stock:
            self._spin_cantidad.setValue(stock)

    # ─────────────────────────────────────────────────────────────
    def _confirmar(self):
        lote = self._combo_lote.currentData()
        cantidad = self._spin_cantidad.value()
        if lote is None or cantidad < 1:
            return
        if cantidad > lote.Stock_actual:
            QtWidgets.QMessageBox.warning(
                self, "Stock insuficiente",
                f"Solo hay {lote.Stock_actual} unidades disponibles en este lote."
            )
            return
        self.lote_seleccionado = lote
        self.cantidad_seleccionada = cantidad
        self.accept()

    # ─────────────────────────────────────────────────────────────
    # Centrar respecto al padre al mostrarse
    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            geo = self.parent().geometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + (geo.height() - self.height()) // 2
            self.move(x, y)
