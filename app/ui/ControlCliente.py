from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

# ═══════════════════════════════════════════════════════════════════
# SystemDistriCali — Lady Nail SHOP
# Módulo: Control de Clientes
# Diseño alineado visualmente con Control de Usuarios
# ═══════════════════════════════════════════════════════════════════

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
_FONT        = "'Segoe UI', Arial, sans-serif"

_CTRL_MIN_H = 44
_BTN_MIN_H  = 40


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


def _card_shadow(widget: QtWidgets.QWidget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(40)
    shadow.setXOffset(0)
    shadow.setYOffset(12)
    shadow.setColor(QtGui.QColor(100, 30, 80, 45))
    widget.setGraphicsEffect(shadow)


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
QLineEdit:disabled {{
    color: {_MUTED};
    background-color: #FBF7FA;
}}
"""

_SEARCH_QSS = f"""
QLineEdit {{
    border: none;
    border-bottom: 1.5px solid {_BORDER};
    background: transparent;
    padding: 6px 4px;
    font-size: 13px;
    color: {_TEXT};
    font-family: {_FONT};
}}
QLineEdit:focus {{
    border-bottom: 2px solid {_PRIMARY};
}}
"""

_PRIMARY_BTN_QSS = f"""
QPushButton {{
    background-color: {_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    font-family: {_FONT};
    padding: 0 16px;
    letter-spacing: 0.4px;
    min-height: {_BTN_MIN_H}px;
    max-height: {_BTN_MIN_H}px;
}}
QPushButton:hover {{ background-color: {_PRIMARY_H}; }}
QPushButton:pressed {{ background-color: {_PRIMARY_P}; }}
QPushButton:disabled {{ background-color: #C4A8BF; color: #F0E8EF; }}
"""

_DANGER_BTN_QSS = f"""
QPushButton {{
    background-color: {_DANGER};
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    font-family: {_FONT};
    padding: 0 16px;
    letter-spacing: 0.4px;
    min-height: {_BTN_MIN_H}px;
    max-height: {_BTN_MIN_H}px;
}}
QPushButton:hover {{ background-color: {_DANGER_H}; }}
QPushButton:pressed {{ background-color: {_DANGER_P}; }}
QPushButton:disabled {{ background-color: #D9B8B4; color: #F7EEEE; }}
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
QTableWidget::item:hover {{ background-color: #F7EFF4; }}
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
QHeaderView::section:horizontal {{ border-right: 1px solid {_DIVIDER}; }}
QTableWidget::verticalHeader {{
    background-color: #FBEFF7;
    color: {_MUTED};
    border: none;
    font-family: {_FONT};
}}
QTableCornerButton::section {{ background-color: #FBEFF7; border: none; }}
QScrollBar:vertical {{
    border: none; background: {_BG}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {_BORDER}; min-height: 20px; border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{ background: {_BORDER_H}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none; background: {_BG}; height: 0px;
}}
QScrollBar:horizontal {{
    border: none; background: {_BG}; height: 8px; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {_BORDER}; min-width: 20px; border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{ background: {_BORDER_H}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none; background: {_BG}; width: 0px;
}}
"""


class Ui_ControlCliente(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        # Íconos en runtime
        icon_search   = qta.icon("fa5s.search", color=_PRIMARY).pixmap(20, 20)
        icon_id       = qta.icon("fa5s.id-card", color=_PRIMARY).pixmap(20, 20)
        icon_user     = qta.icon("fa5s.user", color=_PRIMARY).pixmap(20, 20)
        icon_phone    = qta.icon("fa5s.phone", color=_PRIMARY).pixmap(20, 20)
        icon_address  = qta.icon("fa5s.map-marker-alt", color=_PRIMARY).pixmap(20, 20)
        icon_trash    = qta.icon("fa5s.trash-alt", color="#FFFFFF").pixmap(16, 16)
        icon_register = qta.icon("fa5s.user-plus", color="#FFFFFF").pixmap(16, 16)

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

        # ── Tarjeta: formulario ─────────────────────────────────────
        self.widget_3 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setStyleSheet(f"""
            QWidget#widget_3 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        _card_shadow(self.widget_3)
        self.widget_3.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )

        self.gridLayout = QtWidgets.QGridLayout(self.widget_3)
        self.gridLayout.setContentsMargins(28, 22, 28, 22)
        self.gridLayout.setHorizontalSpacing(14)
        self.gridLayout.setVerticalSpacing(14)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayout_Cliente = QtWidgets.QGridLayout()
        self.gridLayout_Cliente.setHorizontalSpacing(12)
        self.gridLayout_Cliente.setVerticalSpacing(12)
        self.gridLayout_Cliente.setObjectName("gridLayout_Cliente")
        for col in range(5):
            self.gridLayout_Cliente.setColumnStretch(col, 1)

        # Título
        self.LabelVentasA = QtWidgets.QLabel(parent=self.widget_3)
        self.LabelVentasA.setObjectName("LabelVentasA")
        self.LabelVentasA.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {_PRIMARY}; "
            f"font-family: {_FONT}; background: transparent;"
        )
        self.gridLayout_Cliente.addWidget(self.LabelVentasA, 0, 0, 1, 5)

        self.label_30 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_30.setText("")
        self.label_30.setObjectName("label_30")
        self.gridLayout_Cliente.addWidget(self.label_30, 1, 0, 1, 5)

        # Labels
        labels = [
            ("label_3", "Cédula:", 2, 0),
            ("label_5", "Nombre:", 2, 1),
            ("label_7", "Apellido:", 2, 2),
            ("label", "Teléfono:", 2, 3),
            ("label_4", "Dirección:", 2, 4),
        ]
        for name, text, row, col in labels:
            lbl = QtWidgets.QLabel(parent=self.widget_3)
            lbl.setObjectName(name)
            lbl.setStyleSheet(
                f"font-size: 13px; font-weight: 600; color: {_TEXT}; "
                f"font-family: {_FONT}; background: transparent; padding: 0px;"
            )
            lbl.setText(text)
            self.gridLayout_Cliente.addWidget(lbl, row, col)
            setattr(self, name, lbl)

        # Inputs: se conservan exactamente los objectName originales.
        self.InputCedula = self._make_input("InputCedula", icon_id)
        self.gridLayout_Cliente.addWidget(self.InputCedula, 3, 0)

        self.InputNombre = self._make_input("InputNombre", icon_user)
        self.gridLayout_Cliente.addWidget(self.InputNombre, 3, 1)

        self.InputApellido = self._make_input("InputApellido", icon_user)
        self.gridLayout_Cliente.addWidget(self.InputApellido, 3, 2)

        self.InputTelefono = self._make_input("InputTelefono", icon_phone)
        self.gridLayout_Cliente.addWidget(self.InputTelefono, 3, 3)

        self.InputDireccion = self._make_input("InputDireccion", icon_address)
        self.gridLayout_Cliente.addWidget(self.InputDireccion, 3, 4)

        # Botones: misma jerarquía visual que Usuarios.
        self.BtnRegistrar = self._make_button(
            "BtnRegistrar", "Registrar Cliente", _PRIMARY_BTN_QSS, icon_register
        )
        self.BtnRegistrar.setFixedWidth(215)
        self.gridLayout_Cliente.addWidget(
            self.BtnRegistrar, 4, 3, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight
        )

        self.BtnEliminar = self._make_button(
            "BtnEliminar", "Eliminar Cliente", _DANGER_BTN_QSS, icon_trash
        )
        self.BtnEliminar.setFixedWidth(215)
        self.gridLayout_Cliente.addWidget(
            self.BtnEliminar, 4, 4, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight
        )

        self.gridLayout.addLayout(self.gridLayout_Cliente, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.widget_3, 0)

        # ── Buscador ─────────────────────────────────────────────────
        self.widget_2 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet("background: transparent;")
        _sp_hfix(self.widget_2)
        self.widget_2.setMinimumHeight(48)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.label_2 = QtWidgets.QLabel(parent=self.widget_2)
        self.label_2.setObjectName("label_2")
        self.label_2.setFixedSize(24, 24)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setPixmap(icon_search)
        self.label_2.setScaledContents(True)
        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEditBuscador = QtWidgets.QLineEdit(parent=self.widget_2)
        self.lineEditBuscador.setObjectName("lineEditBuscador")
        _sp_hfix(self.lineEditBuscador)
        self.lineEditBuscador.setMinimumHeight(_CTRL_MIN_H)
        self.lineEditBuscador.setStyleSheet(_SEARCH_QSS)
        self.horizontalLayout_3.addWidget(self.lineEditBuscador)
        self.verticalLayout_2.addWidget(self.widget_2, 0)

        # ── Tabla ────────────────────────────────────────────────────
        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("background: transparent;")
        _sp_expand(self.widget)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.TablaClientes = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaClientes.setObjectName("TablaClientes")
        _sp_expand(self.TablaClientes)
        self.TablaClientes.setMinimumHeight(280)
        self.TablaClientes.setStyleSheet(_TABLE_QSS)
        self.TablaClientes.setColumnCount(5)
        self.TablaClientes.setRowCount(16)
        self.TablaClientes.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaClientes.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        self.TablaClientes.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.TablaClientes.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaClientes.verticalHeader().setVisible(False)
        self.TablaClientes.setShowGrid(False)
        _card_shadow(self.TablaClientes)

        for row_idx in range(16):
            item = QtWidgets.QTableWidgetItem()
            self.TablaClientes.setVerticalHeaderItem(row_idx, item)

        headers = ["Cédula", "Nombre", "Apellido", "Teléfono", "Dirección"]
        for col_idx, header_text in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header_text)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaClientes.setHorizontalHeaderItem(col_idx, item)

        self.verticalLayout_3.addWidget(self.TablaClientes)
        self.verticalLayout_2.addWidget(self.widget, 1)

        # Placeholder inferior conservado para compatibilidad.
        self.widget_4 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setStyleSheet("background: transparent;")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_2.addWidget(self.widget_4, 0)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def _make_input(self, name: str, icon_pix) -> QtWidgets.QLineEdit:
        le = QtWidgets.QLineEdit(parent=self.widget_3)
        le.setObjectName(name)
        _sp_hfix(le)
        le.setMinimumSize(QtCore.QSize(180, _CTRL_MIN_H))
        le.setStyleSheet(_INPUT_QSS)
        le.addAction(
            QtGui.QIcon(icon_pix),
            QtWidgets.QLineEdit.ActionPosition.LeadingPosition,
        )
        return le

    def _make_button(self, name: str, text: str, style: str, icon_pix):
        btn = QtWidgets.QPushButton(parent=self.widget_3)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setMinimumWidth(170)
        btn.setStyleSheet(style)
        btn.setIcon(QtGui.QIcon(icon_pix))
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setText(text)
        return btn

    def adapt_to_size(self, width: int, height: int):
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        ctrl_h = max(42, min(52, int(height * 0.058)))
        self.lineEditBuscador.setMinimumHeight(ctrl_h)
        for name in (
            "InputCedula", "InputNombre", "InputApellido",
            "InputTelefono", "InputDireccion"
        ):
            getattr(self, name).setMinimumHeight(ctrl_h)

        for name in ("BtnRegistrar", "BtnEliminar"):
            getattr(self, name).setMinimumHeight(_BTN_MIN_H)
            getattr(self, name).setMaximumHeight(_BTN_MIN_H)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Control de Clientes"))
        self.label_3.setText(_translate("Form", "Cédula:"))
        self.label_5.setText(_translate("Form", "Nombre:"))
        self.label_7.setText(_translate("Form", "Apellido:"))
        self.label.setText(_translate("Form", "Teléfono:"))
        self.label_4.setText(_translate("Form", "Dirección:"))
        self.LabelVentasA.setText(_translate("Form", "Clientes"))
        self.BtnEliminar.setText(_translate("Form", "Eliminar Cliente"))
        self.BtnRegistrar.setText(_translate("Form", "Registrar Cliente"))

        for row_idx in range(16):
            item = self.TablaClientes.verticalHeaderItem(row_idx)
            if item is not None:
                item.setText(_translate("Form", "Nueva fila" if row_idx < 14 else "New Row"))