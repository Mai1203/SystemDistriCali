# UI de PagoCredito — Escrita a mano siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry, tarjetas compactas, inputs focus, tabla plum, botones SVG, responsiva)
#
# Reglas aplicadas del design_system_login.txt:
#  · Colores semánticos con prefijo _
#  · Tarjetas con sombra (border-radius + QGraphicsDropShadowEffect)
#  · Inputs con borde 1px, foco 1.5px _PRIMARY, border-radius 8px
#  · Tabla con header plum, selección tinte berry
#  · Botones compactos: primario plum, secundario outline
#  · Íconos SVG (qtawesome) creados en tiempo de ejecución
#  · resizeEvent → adapt_to_size recalcula márgenes y alturas
#  · PointingHandCursor en controles interactivos

from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta


# ─────────────────────────────────────────────────────────────────
#  Paleta semántica (Sistema de Diseño Lady Nail)
# ─────────────────────────────────────────────────────────────────
_PRIMARY     = "#862D6D"
_PRIMARY_H   = "#6E2259"
_PRIMARY_P   = "#551443"
_BG          = "#F5F0F4"
_CARD_BG     = "#FFFFFF"
_BORDER      = "#D8C8D5"
_BORDER_H    = "#A97099"
_TEXT        = "#201A24"
_MUTED       = "#7B737F"
_FOCUS_BG    = "#FFFAFE"
_DIVIDER     = "#E2DAE1"
_CARD_BORDER = "#EAE0E8"

_DANGER      = "#C0392B"
_DANGER_H    = "#A93226"
_DANGER_P    = "#7B241C"

_FONT = "'Segoe UI', Arial, sans-serif"

_CTRL_MIN_H = 38
_BTN_MIN_H  = 32


def _sp_expand(w: QtWidgets.QWidget):
    w.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    return w


# ─────────────────────────────────────────────────────────────────
#  Hojas de estilo (QSS)
# ─────────────────────────────────────────────────────────────────
_INPUT_QSS = f"""
    QLineEdit, QComboBox {{
        background-color: {_CARD_BG};
        border: 1px solid {_BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1.5px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QLineEdit:hover, QComboBox:hover {{
        border-color: {_BORDER_H};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: 1px solid {_DIVIDER};
    }}
    QComboBox QAbstractItemView {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        selection-background-color: #FDF0F6;
        selection-color: {_PRIMARY};
        border-radius: 4px;
        padding: 4px;
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 28px;
        padding-left: 8px;
    }}
"""

_PRIMARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 4px 12px;
        letter-spacing: 0.3px;
        min-height: {_BTN_MIN_H}px;
    }}
    QPushButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QPushButton:pressed {{
        background-color: {_PRIMARY_P};
        padding-top: 10px;
    }}
    QPushButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_SECONDARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {_CARD_BG};
        color: {_PRIMARY};
        border: 1px solid {_PRIMARY};
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 8px 16px;
        letter-spacing: 0.3px;
        min-height: {_BTN_MIN_H}px;
    }}
    QPushButton:hover {{
        background-color: #FBEFF7;
        border: 1.5px solid {_PRIMARY};
    }}
    QPushButton:pressed {{
        background-color: #F3E6EF;
    }}
"""

_DANGER_BTN_QSS = f"""
    QPushButton {{
        background-color: {_DANGER};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 8px 16px;
        letter-spacing: 0.3px;
        min-height: {_BTN_MIN_H}px;
    }}
    QPushButton:hover {{
        background-color: {_DANGER_H};
    }}
    QPushButton:pressed {{
        background-color: {_DANGER_P};
        padding-top: 10px;
    }}
"""

_TABLE_QSS = f"""
    QTableWidget {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 10px;
        gridline-color: {_DIVIDER};
        font-size: 12px;
        color: {_TEXT};
        font-family: {_FONT};
        selection-background-color: #F3E6EF;
    }}
    QTableWidget::item {{
        background-color: {_CARD_BG};
        border: none;
        padding: 6px 8px;
    }}
    QTableWidget::item:selected {{
        background-color: #F3E6EF;
        color: {_TEXT};
    }}
    QTableWidget::item:hover {{
        background-color: #F7EFF4;
    }}
    QHeaderView::section {{
        background-color: #FBEFF7;
        color: {_PRIMARY};
        border: none;
        border-bottom: 1px solid {_PRIMARY};
        font-weight: 600;
        font-size: 12px;
        padding: 8px;
        font-family: {_FONT};
    }}
    QHeaderView::section:horizontal {{
        border-right: 1px solid {_DIVIDER};
    }}
    QTableWidget::verticalHeader {{
        background-color: #FBEFF7;
        color: {_MUTED};
        border: none;
        font-family: {_FONT};
    }}
    QTableCornerButton::section {{
        background-color: #FBEFF7;
        border: none;
    }}
"""


def _card_shadow(widget: QtWidgets.QWidget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(40)
    shadow.setXOffset(0)
    shadow.setYOffset(12)
    shadow.setColor(QtGui.QColor(100, 30, 80, 45))
    widget.setGraphicsEffect(shadow)


class Ui_PagoCredito(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        # Íconos
        icon_search = qta.icon("fa5s.search", color=_PRIMARY).pixmap(16, 16)
        icon_dollar = qta.icon("fa5s.dollar-sign", color="#28A745").pixmap(16, 16)
        icon_edit = qta.icon("fa5s.edit", color=_PRIMARY).pixmap(16, 16)
        icon_back = qta.icon("fa5s.arrow-left", color=_PRIMARY).pixmap(16, 16)

        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.Contenedor = QtWidgets.QWidget(parent=Form)
        self.Contenedor.setObjectName("Contenedor")
        self.Contenedor.setStyleSheet("background-color: transparent;")
        _sp_expand(self.Contenedor)
        self.gridLayout_2.addWidget(self.Contenedor, 0, 0, 1, 1)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Contenedor)
        self.horizontalLayout_2.setContentsMargins(16, 16, 16, 16)
        self.horizontalLayout_2.setSpacing(16)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.Contenido = QtWidgets.QStackedWidget(parent=self.Contenedor)
        self.Contenido.setObjectName("Contenido")
        self.Contenido.setStyleSheet("background: transparent; border: none;")
        _sp_expand(self.Contenido)
        self.horizontalLayout_2.addWidget(self.Contenido)

        self.ContenidoPage1 = QtWidgets.QWidget()
        self.ContenidoPage1.setObjectName("ContenidoPage1")
        self.Contenido.addWidget(self.ContenidoPage1)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.ContenidoPage1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(16)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("background: transparent;")
        _sp_expand(self.widget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(16)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # ── Encabezado: título + info deuda ────────────────────────
        self.frame_header = QtWidgets.QFrame(parent=self.widget)
        self.frame_header.setObjectName("frame_header")
        self.frame_header.setStyleSheet(f"""
            QFrame#frame_header {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 12px;
            }}
        """)
        self.frame_header.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.frame_header)
        
        header_layout = QtWidgets.QGridLayout(self.frame_header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setHorizontalSpacing(16)
        header_layout.setVerticalSpacing(8)
        header_layout.setObjectName("header_layout")

        # ── Fila 0: botón atrás + título
        title_row = QtWidgets.QHBoxLayout()
        title_row.setSpacing(8)

        self.BtnAtras = QtWidgets.QToolButton(parent=self.frame_header)
        self.BtnAtras.setObjectName("BtnAtras")
        self.BtnAtras.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnAtras.setIcon(QtGui.QIcon(icon_back))
        self.BtnAtras.setIconSize(QtCore.QSize(14, 14))
        self.BtnAtras.setFixedSize(32, 32)
        self.BtnAtras.setToolTip("Volver")
        self.BtnAtras.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: 1px solid {_BORDER};
                border-radius: 6px;
            }}
            QToolButton:hover {{
                background-color: #FBEFF7;
                border-color: {_PRIMARY};
            }}
            QToolButton:pressed {{
                background-color: #F3E6EF;
            }}
        """)
        title_row.addWidget(self.BtnAtras)

        self.LabelPago = QtWidgets.QLabel(parent=self.frame_header)
        self.LabelPago.setObjectName("LabelPago")
        self.LabelPago.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        title_row.addWidget(self.LabelPago)
        title_row.addStretch()
        header_layout.addLayout(title_row, 0, 0, 1, 4)

        self.LabelDeuda = QtWidgets.QLabel("Total Deuda: $0", parent=self.frame_header)
        self.LabelDeuda.setObjectName("LabelDeuda")
        self.LabelDeuda.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {_TEXT};"
            f" font-family: {_FONT}; background: transparent;"
        )
        header_layout.addWidget(self.LabelDeuda, 0, 1, 1, 1)

        self.LabelPendiente = QtWidgets.QLabel("Pendiente: $0", parent=self.frame_header)
        self.LabelPendiente.setObjectName("LabelPendiente")
        self.LabelPendiente.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {_DANGER};"
            f" font-family: {_FONT}; background: transparent;"
        )
        header_layout.addWidget(self.LabelPendiente, 0, 2, 1, 1)

        self.LabelEstado = QtWidgets.QLabel("Pendiente", parent=self.frame_header)
        self.LabelEstado.setObjectName("LabelEstado")
        self.LabelEstado.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {_DANGER};"
            f" font-family: {_FONT}; background: transparent;"
        )
        header_layout.addWidget(self.LabelEstado, 0, 3, 1, 1)

        self.verticalLayout_3.addWidget(self.frame_header, 0)

        # ── Tabla de pagos ─────────────────────────────────────────
        self.TablaPagoCredito = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaPagoCredito.setObjectName("TablaPagoCredito")
        _sp_expand(self.TablaPagoCredito)
        self.TablaPagoCredito.setMinimumHeight(280)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.TablaPagoCredito.setFont(font)
        self.TablaPagoCredito.setStyleSheet(_TABLE_QSS)
        self.TablaPagoCredito.setColumnCount(7)
        self.TablaPagoCredito.setRowCount(0)
        self.TablaPagoCredito.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaPagoCredito.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaPagoCredito.verticalHeader().setVisible(False)
        self.TablaPagoCredito.setShowGrid(False)
        _card_shadow(self.TablaPagoCredito)
        self.verticalLayout_3.addWidget(self.TablaPagoCredito, 1)

        # ── Card inferior: método de pago + abonar ─────────────────
        self.frame_footer = QtWidgets.QFrame(parent=self.widget)
        self.frame_footer.setObjectName("frame_footer")
        self.frame_footer.setStyleSheet(f"""
            QFrame#frame_footer {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 10px;
            }}
        """)
        self.frame_footer.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        _card_shadow(self.frame_footer)
        
        footer_layout = QtWidgets.QHBoxLayout(self.frame_footer)
        footer_layout.setContentsMargins(12, 10, 12, 10)
        footer_layout.setSpacing(4)

        self.label_metodo = QtWidgets.QLabel("Método de Pago:", parent=self.frame_footer)
        self.label_metodo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.label_metodo.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {_MUTED};"
            f" font-family: {_FONT}; background: transparent;"
        )
        footer_layout.addWidget(self.label_metodo)

        self.MetodoPagoBox = QtWidgets.QComboBox(parent=self.frame_footer)
        self.MetodoPagoBox.setObjectName("MetodoPagoBox")
        self.MetodoPagoBox.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.MetodoPagoBox.setFixedWidth(170)
        self.MetodoPagoBox.setMinimumHeight(_CTRL_MIN_H)
        self.MetodoPagoBox.setStyleSheet(_INPUT_QSS)
        footer_layout.addWidget(self.MetodoPagoBox)

        self.label_monto = QtWidgets.QLabel("Monto a pagar:", parent=self.frame_footer)
        self.label_monto.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.label_monto.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {_MUTED};"
            f" font-family: {_FONT}; background: transparent;"
        )
        footer_layout.addWidget(self.label_monto)

        self.InputPago = QtWidgets.QLineEdit(parent=self.frame_footer)
        self.InputPago.setObjectName("InputPago")
        self.InputPago.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.InputPago.setFixedWidth(150)
        self.InputPago.setMinimumHeight(_CTRL_MIN_H)
        self.InputPago.setStyleSheet(_INPUT_QSS)
        self.InputPago.setPlaceholderText("$")
        footer_layout.addWidget(self.InputPago)

        self.BtnAbonar = QtWidgets.QPushButton("Abonar", parent=self.frame_footer)
        self.BtnAbonar.setObjectName("BtnAbonar")
        self.BtnAbonar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnAbonar.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.BtnAbonar.setFixedWidth(110)
        self.BtnAbonar.setMinimumHeight(_BTN_MIN_H)
        self.BtnAbonar.setStyleSheet(_PRIMARY_BTN_QSS)
        self.BtnAbonar.setIcon(qta.icon('fa5s.dollar-sign', color='white'))
        self.BtnAbonar.setIconSize(QtCore.QSize(16, 16))
        footer_layout.addWidget(self.BtnAbonar)
        
        self.verticalLayout_3.addWidget(self.frame_footer, 0)
        self.verticalLayout_2.addWidget(self.widget, 1)

        self.Contenido.addWidget(self.ContenidoPage1)
        self.horizontalLayout_2.addWidget(self.Contenido)
        self.gridLayout_2.addWidget(self.Contenedor, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Pago de Crédito · Lady Nail"))
        self.LabelPago.setText(_translate("Form", "Pago de Crédito"))
        headers = [
            "Id", "Nombre", "F.Registro", "Venta Crédito",
            "Método Pago", "Tipo Pago", "Monto",
        ]
        for col, text in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(_translate("Form", text))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaPagoCredito.setHorizontalHeaderItem(col, item)
