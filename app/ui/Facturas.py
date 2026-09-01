# UI de Facturas — Diseño basado en FacturasCredito
# (paleta plum/berry, tarjetas compactas, inputs focus, tabla plum, botones SVG, responsiva)

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

_CTRL_MIN_H = 34
_BTN_MIN_H  = 34


def _sp_expand(w: QtWidgets.QWidget):
    w.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    return w


def _sp_hfix(w: QtWidgets.QWidget):
    w.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    return w


# ─────────────────────────────────────────────────────────────────
#  Hojas de estilo (QSS)
# ─────────────────────────────────────────────────────────────────
_INPUT_QSS = f"""
    QLineEdit {{
        background-color: {_CARD_BG};
        border: 1px solid {_BORDER};
        border-radius: 8px;
        padding: 0px 12px 0px 36px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
    }}
    QLineEdit:focus {{
        border: 1.5px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QLineEdit:hover {{
        border-color: {_BORDER_H};
    }}
"""

_PRIMARY_BTN_QSS = f"""
    QToolButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        font-family: {_FONT};
        padding: 4px 8px;
        letter-spacing: 0.2px;
        min-height: {_BTN_MIN_H}px;
    }}
    QToolButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QToolButton:pressed {{
        background-color: {_PRIMARY_P};
        padding-top: 6px;
    }}
    QToolButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_SECONDARY_BTN_QSS = f"""
    QToolButton {{
        background-color: {_CARD_BG};
        color: {_PRIMARY};
        border: 1px solid {_PRIMARY};
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        font-family: {_FONT};
        padding: 4px 8px;
        letter-spacing: 0.2px;
        min-height: {_BTN_MIN_H}px;
        cursor: pointer;
    }}
    QToolButton:hover {{
        background-color: #FBEFF7;
        border: 1.5px solid {_PRIMARY};
    }}
    QToolButton:pressed {{
        background-color: #F3E6EF;
    }}
"""

_CANCEL_BTN_QSS = f"""
    QToolButton {{
        background-color: {_CARD_BG};
        color: {_DANGER};
        border: 1px solid {_DANGER};
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        font-family: {_FONT};
        padding: 4px 8px;
        letter-spacing: 0.2px;
        min-height: {_BTN_MIN_H}px;
        cursor: pointer;
    }}
    QToolButton:hover {{
        background-color: #FDEDEC;
        border: 1.5px solid {_DANGER};
    }}
    QToolButton:pressed {{
        background-color: #FADBD8;
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


class Ui_Facturas(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        # Íconos
        icon_search = qta.icon("fa5s.search", color=_PRIMARY).pixmap(16, 16)
        icon_view = qta.icon("fa5s.eye", color=_PRIMARY).pixmap(16, 16)
        icon_edit = qta.icon("fa5s.edit", color=_PRIMARY).pixmap(16, 16)
        icon_check = qta.icon("fa5s.check-circle", color="#FFFFFF").pixmap(16, 16)
        icon_cancel = qta.icon("fa5s.times-circle", color=_DANGER).pixmap(16, 16)

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

        # ── Encabezado: título + buscador ─────────────────────────
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
        header_layout.setHorizontalSpacing(12)
        header_layout.setVerticalSpacing(8)
        header_layout.setObjectName("header_layout")

        self.LabelProductos = QtWidgets.QLabel(parent=self.frame_header)
        self.LabelProductos.setObjectName("LabelProductos")
        self.LabelProductos.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        header_layout.addWidget(self.LabelProductos, 0, 0, 1, 1)

        searchRow = QtWidgets.QHBoxLayout()
        searchRow.setSpacing(8)
        self.label_search = QtWidgets.QLabel(parent=self.frame_header)
        self.label_search.setObjectName("label_search")
        self.label_search.setFixedSize(20, 20)
        self.label_search.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_search.setPixmap(icon_search)
        self.label_search.setScaledContents(True)
        searchRow.addWidget(self.label_search)

        self.InputBuscador = QtWidgets.QLineEdit(parent=self.frame_header)
        self.InputBuscador.setObjectName("InputBuscador")
        _sp_hfix(self.InputBuscador)
        self.InputBuscador.setMinimumHeight(_CTRL_MIN_H)
        self.InputBuscador.setStyleSheet(_INPUT_QSS)
        self.InputBuscador.setClearButtonEnabled(True)
        searchRow.addWidget(self.InputBuscador, 1)

        header_layout.addLayout(searchRow, 1, 0, 1, 1)

        self.verticalLayout_3.addWidget(self.frame_header, 0)

        # ── Tabla ─────────────────────────────────────────────────
        self.TablaFacturas = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaFacturas.setObjectName("TablaFacturas")
        _sp_expand(self.TablaFacturas)
        self.TablaFacturas.setMinimumHeight(280)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.TablaFacturas.setFont(font)
        self.TablaFacturas.setStyleSheet(_TABLE_QSS)
        self.TablaFacturas.setColumnCount(11)
        self.TablaFacturas.setRowCount(0)
        self.TablaFacturas.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaFacturas.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaFacturas.verticalHeader().setVisible(False)
        self.TablaFacturas.setShowGrid(False)
        _card_shadow(self.TablaFacturas)
        self.verticalLayout_3.addWidget(self.TablaFacturas, 1)

        # ── Barra de acciones inferior ────────────────────────────
        self.frame_actions = QtWidgets.QFrame(parent=self.widget)
        self.frame_actions.setObjectName("frame_actions")
        self.frame_actions.setStyleSheet(f"""
            QFrame#frame_actions {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 10px;
            }}
        """)
        self.frame_actions.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        _card_shadow(self.frame_actions)
        
        actions_layout = QtWidgets.QHBoxLayout(self.frame_actions)
        actions_layout.setContentsMargins(12, 10, 12, 10)
        actions_layout.setSpacing(10)
        
        self.BtnFacturaPagada = self._make_btn(
            "BtnFacturaPagada", "Factura Pagada", _PRIMARY_BTN_QSS, icon_check
        )
        self.BtnVerFactura = self._make_btn(
            "BtnVerFactura", "Ver Factura", _SECONDARY_BTN_QSS, icon_view
        )
        self.BtnEditarFactura = self._make_btn(
            "BtnEditarFactura", "Editar Factura", _SECONDARY_BTN_QSS, icon_edit
        )
        self.BtnVerCancelarVenta = self._make_btn(
            "BtnVerCancelarVenta", "Cancelar Venta", _CANCEL_BTN_QSS, icon_cancel
        )
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.BtnFacturaPagada)
        actions_layout.addWidget(self.BtnVerFactura)
        actions_layout.addWidget(self.BtnEditarFactura)
        actions_layout.addWidget(self.BtnVerCancelarVenta)
        actions_layout.addStretch()
        
        self.verticalLayout_3.addWidget(self.frame_actions, 0)
        self.verticalLayout_2.addWidget(self.widget, 1)

        self.Contenido.addWidget(self.ContenidoPage1)
        self.horizontalLayout_2.addWidget(self.Contenido)
        self.gridLayout_2.addWidget(self.Contenedor, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def _make_btn(self, name, text, style, icon_pix):
        btn = QtWidgets.QToolButton(parent=self.frame_actions)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setStyleSheet(style)
        btn.setIcon(QtGui.QIcon(icon_pix))
        btn.setIconSize(QtCore.QSize(14, 14))
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setText(text)
        return btn

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(12, min(48, int(width * 0.04)))
        v_margin = max(12, min(40, int(height * 0.035)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        ctrl_h = max(36, min(44, int(height * 0.048)))
        self.InputBuscador.setMinimumHeight(ctrl_h)

        btn_h = max(30, min(38, int(height * 0.042)))
        for btn in (self.BtnFacturaPagada, self.BtnVerFactura, self.BtnEditarFactura, self.BtnVerCancelarVenta):
            btn.setMinimumHeight(btn_h)

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Facturas · Lady Nail"))
        self.LabelProductos.setText(_translate("Form", "Facturas"))
        headers = [
            "Id", "Usuario", "MedPago", "Cliente", "TipoFac", "Fecha",
            "F.Modif", "Efectivo", "Transferencia", "M.Total", "Estado",
        ]
        for col, text in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(_translate("Form", text))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaFacturas.setHorizontalHeaderItem(col, item)
        self.BtnFacturaPagada.setText(_translate("Form", "Factura Pagada"))
        self.BtnVerFactura.setText(_translate("Form", "Ver Factura"))
        self.BtnEditarFactura.setText(_translate("Form", "Editar Factura"))
        self.BtnVerCancelarVenta.setText(_translate("Form", "Cancelar Venta"))
