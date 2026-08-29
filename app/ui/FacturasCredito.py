# UI de FacturasCredito — Escrita a mano siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry, tarjetas con sombra, inputs focus, tabla plum, botones SVG, responsiva)
#
# Reglas aplicadas del design_system_login.txt:
#  · Colores semánticos con prefijo _
#  · Tarjetas flotantes (border-radius + QGraphicsDropShadowEffect)
#  · Input búsqueda con borde 1.5px, foco 2px _PRIMARY, ícono search
#  · Tabla con header plum, selección tinte berry, hover suave
#  · Botones: primario plum (Abono/Ticket), secundario outline (Editar), danger (Eliminar)
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

_CTRL_MIN_H = 44
_BTN_MIN_H  = 46


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
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 0px 12px 0px 38px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
    }}
    QLineEdit:focus {{
        border: 2px solid {_PRIMARY};
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
        border-radius: 10px;
        font-size: 14px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 10px 16px;
        letter-spacing: 0.4px;
        min-height: {_BTN_MIN_H}px;
    }}
    QToolButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QToolButton:pressed {{
        background-color: {_PRIMARY_P};
        padding-top: 12px;
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
        border: 1.5px solid {_PRIMARY};
        border-radius: 10px;
        font-size: 14px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 10px 16px;
        letter-spacing: 0.4px;
        min-height: {_BTN_MIN_H}px;
    }}
    QToolButton:hover {{
        background-color: #FBEFF7;
        border: 2px solid {_PRIMARY};
    }}
    QToolButton:pressed {{
        background-color: #F3E6EF;
    }}
"""

_DANGER_BTN_QSS = f"""
    QToolButton {{
        background-color: {_DANGER};
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 10px 16px;
        letter-spacing: 0.4px;
        min-height: {_BTN_MIN_H}px;
    }}
    QToolButton:hover {{
        background-color: {_DANGER_H};
    }}
    QToolButton:pressed {{
        background-color: {_DANGER_P};
        padding-top: 12px;
    }}
"""

_TABLE_QSS = f"""
    QTableWidget {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 14px;
        gridline-color: {_DIVIDER};
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
        selection-background-color: #F3E6EF;
    }}
    QTableWidget::item {{
        background-color: {_CARD_BG};
        border: none;
        padding: 8px 10px;
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
        border-bottom: 2px solid {_PRIMARY};
        font-weight: 600;
        font-size: 13px;
        padding: 10px;
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


class Ui_FacturasCredito(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        # Íconos creados en tiempo de ejecución (requieren QApplication activa)
        icon_search = qta.icon("fa5s.search", color=_PRIMARY).pixmap(20, 20)
        icon_edit = qta.icon("fa5s.edit", color=_PRIMARY).pixmap(20, 20)
        icon_trash = qta.icon("fa5s.trash-alt", color="#FFFFFF").pixmap(20, 20)
        icon_check = qta.icon("fa5s.check-circle", color="#FFFFFF").pixmap(20, 20)
        icon_pdf = qta.icon("fa5s.file-pdf", color="#FFFFFF").pixmap(20, 20)

        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.Contenedor = QtWidgets.QWidget(parent=Form)
        self.Contenedor.setObjectName("Contenedor")
        self.Contenedor.setStyleSheet("background-color: transparent;")
        _sp_expand(self.Contenedor)
        self.gridLayout_2.addWidget(self.Contenedor, 0, 0, 1, 1)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Contenedor)
        self.horizontalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.horizontalLayout_2.setSpacing(24)
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
        self.verticalLayout_2.setSpacing(24)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("background: transparent;")
        _sp_expand(self.widget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(24)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # ── Encabezado: título + buscador ─────────────────────────
        self.frame_2 = QtWidgets.QFrame(parent=self.widget)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setStyleSheet(f"""
            QFrame#frame_2 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        self.frame_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.frame_2)
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setContentsMargins(28, 22, 28, 22)
        self.gridLayout_3.setHorizontalSpacing(12)
        self.gridLayout_3.setVerticalSpacing(14)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.LabelProductos = QtWidgets.QLabel(parent=self.frame_2)
        self.LabelProductos.setObjectName("LabelProductos")
        self.LabelProductos.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        self.gridLayout_3.addWidget(self.LabelProductos, 0, 0, 1, 1)

        searchRow = QtWidgets.QHBoxLayout()
        searchRow.setSpacing(10)
        self.label_11 = QtWidgets.QLabel(parent=self.frame_2)
        self.label_11.setObjectName("label_11")
        self.label_11.setFixedSize(24, 24)
        self.label_11.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_11.setPixmap(icon_search)
        self.label_11.setScaledContents(True)
        searchRow.addWidget(self.label_11)

        self.InputBuscador = QtWidgets.QLineEdit(parent=self.frame_2)
        self.InputBuscador.setObjectName("InputBuscador")
        _sp_hfix(self.InputBuscador)
        self.InputBuscador.setMinimumHeight(_CTRL_MIN_H)
        self.InputBuscador.setStyleSheet(_INPUT_QSS)
        self.InputBuscador.setClearButtonEnabled(True)
        searchRow.addWidget(self.InputBuscador, 1)
        self.gridLayout_3.addLayout(searchRow, 1, 0, 1, 1)

        self.verticalLayout_3.addWidget(self.frame_2, 0)

        # ── Tabla ─────────────────────────────────────────────────
        self.TablaFacturasCredito = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaFacturasCredito.setObjectName("TablaFacturasCredito")
        _sp_expand(self.TablaFacturasCredito)
        self.TablaFacturasCredito.setMinimumHeight(280)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.TablaFacturasCredito.setFont(font)
        self.TablaFacturasCredito.setStyleSheet(_TABLE_QSS)
        self.TablaFacturasCredito.setColumnCount(9)
        self.TablaFacturasCredito.setRowCount(0)
        self.TablaFacturasCredito.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaFacturasCredito.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaFacturasCredito.verticalHeader().setVisible(False)
        self.TablaFacturasCredito.setShowGrid(False)
        _card_shadow(self.TablaFacturasCredito)
        self.verticalLayout_3.addWidget(self.TablaFacturasCredito, 1)

        # ── Barra de botones ──────────────────────────────────────
        self.widget_2 = QtWidgets.QWidget(parent=self.widget)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet("background: transparent;")
        self.widget_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.gridLayout = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 1)

        self.BtnAgregarAbono = self._make_btn(
            "BtnAgregarAbono", "   Agregar Abono", _PRIMARY_BTN_QSS, icon_check
        )
        self.BtnEditarFactura = self._make_btn(
            "BtnEditarFactura", "   Editar Factura", _SECONDARY_BTN_QSS, icon_edit
        )
        self.BtnGenerarTicket = self._make_btn(
            "BtnGenerarTicket", "   Generar Ticket", _PRIMARY_BTN_QSS, icon_pdf
        )
        self.BtnEliminarFactura = self._make_btn(
            "BtnEliminarFactura", "   Eliminar Factura", _DANGER_BTN_QSS, icon_trash
        )
        self.gridLayout.addWidget(self.BtnAgregarAbono, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.BtnEditarFactura, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.BtnGenerarTicket, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.BtnEliminarFactura, 0, 3, 1, 1)

        self.verticalLayout_3.addWidget(self.widget_2, 0)
        self.verticalLayout_2.addWidget(self.widget, 1)

        self.Contenido.addWidget(self.ContenidoPage1)
        self.horizontalLayout_2.addWidget(self.Contenido)
        self.gridLayout_2.addWidget(self.Contenedor, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def _make_btn(self, name, text, style, icon_pix):
        btn = QtWidgets.QToolButton(parent=self.widget_2)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        _sp_hfix(btn)
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setStyleSheet(style)
        btn.setIcon(QtGui.QIcon(icon_pix))
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setText(text)
        return btn

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        ctrl_h = max(42, min(52, int(height * 0.058)))
        self.InputBuscador.setMinimumHeight(ctrl_h)

        btn_h = max(44, min(54, int(height * 0.062)))
        for btn in (self.BtnAgregarAbono, self.BtnEditarFactura,
                    self.BtnGenerarTicket, self.BtnEliminarFactura):
            btn.setMinimumHeight(btn_h)

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Facturas a Crédito · Lady Nail"))
        self.LabelProductos.setText(_translate("Form", "Facturas Con Credito"))
        headers = [
            "Id", "Usuario", "Id Factura", "Cliente", "F.Registro",
            "F.Limite", "T.Deuda", "Pendiente", "Estado",
        ]
        for col, text in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(_translate("Form", text))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaFacturasCredito.setHorizontalHeaderItem(col, item)
        self.BtnEditarFactura.setText(_translate("Form", "   Editar Factura"))
        self.BtnEliminarFactura.setText(_translate("Form", "   Eliminar Factura"))
        self.BtnAgregarAbono.setText(_translate("Form", "   Agregar Abono"))
        self.BtnGenerarTicket.setText(_translate("Form", "   Generar Ticket"))
