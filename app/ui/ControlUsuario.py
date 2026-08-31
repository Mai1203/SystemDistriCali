from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
#  SystemDistriCali — Lady Nail SHOP
#  Módulo:  Control de Usuarios
#  Basado en: docs/design_system_login.txt (v2.0)
#  Patrón:   Facturas.py (cards con sombra, QToolButton, tabla plum)
# ═══════════════════════════════════════════════════════════════════

# ── Paleta de colores ──────────────────────────────────────────────
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


# ── Helpers ────────────────────────────────────────────────────────
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


# ── QSS ────────────────────────────────────────────────────────────
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


_QSS_COMBO = f"""
    QComboBox {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
        min-height: {_CTRL_MIN_H}px;
    }}
    QComboBox:focus {{
        border: 2px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QComboBox:hover {{
        border-color: {_BORDER_H};
    }}
    QComboBox::drop-down {{
        border: none;
        background: {_BG};
        width: 32px;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }}
    QComboBox::drop-down:hover {{
        background: {_DIVIDER};
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid none;
        border-right: 5px solid none;
        border-top: 6px solid {_MUTED};
        margin-right: 10px;
    }}
    QComboBox::down-arrow:hover {{
        border-top: 6px solid {_PRIMARY};
    }}
    QComboBox QLineEdit {{
        background-color: transparent;
        border: none;
        color: {_TEXT};
        font-family: {_FONT};
        font-size: 13px;
        padding: 0px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 10px;
        selection-background-color: #F3E6EF;
        selection-color: {_PRIMARY};
        outline: none;
        padding: 4px;
    }}
    QComboBox QAbstractItemView::item {{
        background-color: {_CARD_BG};
        color: {_TEXT};
        font-family: {_FONT};
        font-size: 13px;
        padding: 8px 12px 8px 32px;
        border-radius: 6px;
        margin: 2px 4px;
        min-height: 32px;
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: #F3E6EF;
        color: {_PRIMARY};
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: #F7EFF4;
    }}
    QComboBox QAbstractItemView::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1.5px solid {_BORDER};
        background: {_CARD_BG};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView::indicator:checked {{
        background: {_PRIMARY};
        border-color: {_PRIMARY};
        image: none;
    }}
"""


class Ui_ControlUsuario(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        # Íconos en runtime
        icon_search = qta.icon("fa5s.search", color=_PRIMARY).pixmap(20, 20)
        icon_id     = qta.icon("fa5s.id-badge", color=_PRIMARY).pixmap(20, 20)
        icon_user   = qta.icon("fa5s.user", color=_PRIMARY).pixmap(20, 20)
        icon_lock   = qta.icon("fa5s.lock", color=_PRIMARY).pixmap(20, 20)
        icon_rol    = qta.icon("fa5s.user-tag", color=_PRIMARY).pixmap(20, 20)
        icon_trash  = qta.icon("fa5s.trash-alt", color="#FFFFFF").pixmap(20, 20)

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

        # ── Tarjeta: Formulario ─────────────────────────────────────
        self.widget_3 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setStyleSheet(f"""
            QWidget#widget_3 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
            {_QSS_COMBO}
        """)
        _card_shadow(self.widget_3)
        sp3 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.widget_3.setSizePolicy(sp3)

        self.gridLayout = QtWidgets.QGridLayout(self.widget_3)
        self.gridLayout.setContentsMargins(28, 22, 28, 22)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setVerticalSpacing(18)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(12)
        self.gridLayout_2.setVerticalSpacing(14)

        # Título
        self.LabelVentasA = QtWidgets.QLabel(parent=self.widget_3)
        self.LabelVentasA.setObjectName("LabelVentasA")
        self.LabelVentasA.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        self.gridLayout_2.addWidget(self.LabelVentasA, 0, 0, 1, 1)

        # Spacer
        self.label_30 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_30.setText("")
        self.label_30.setObjectName("label_30")
        self.gridLayout_2.addWidget(self.label_30, 1, 0, 1, 1)

        # Labels fila 2
        self.label_3 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_5 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 2, 1, 1, 1)

        self.label_7 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 2, 2, 1, 1)

        self.label = QtWidgets.QLabel(parent=self.widget_3)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 3, 1, 1)

        # Inputs fila 3
        self.InputIdUser = self._make_input("InputIdUser", icon_id)
        self.gridLayout_2.addWidget(self.InputIdUser, 3, 0, 1, 1)

        self.InputNombreUser = self._make_input("InputNombreUser", icon_user)
        self.gridLayout_2.addWidget(self.InputNombreUser, 3, 1, 1, 1)

        self.InputUser = self._make_input("InputUser", icon_user)
        self.gridLayout_2.addWidget(self.InputUser, 3, 2, 1, 1)

        self.InputPasswordUser = self._make_input("InputPasswordUser", icon_lock)
        self.InputPasswordUser.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )
        self.gridLayout_2.addWidget(self.InputPasswordUser, 3, 3, 1, 1)

        # Fila 4: Label Rol (placeholder para comboPermisos dinámico)
        self.label_6 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 4, 0, 1, 1)

        # Fila 5: Botones
        self.BtnRolUser = self._make_btn(
            "BtnRolUser", "Asesor Comercial", _SECONDARY_BTN_QSS, icon_rol
        )
        self.gridLayout_2.addWidget(self.BtnRolUser, 5, 0, 1, 1)

        self.BtnRegistrarUser = self._make_btn(
            "BtnRegistrarUser", "Registrar Usuario", _PRIMARY_BTN_QSS, icon_user
        )
        self.gridLayout_2.addWidget(self.BtnRegistrarUser, 5, 2, 1, 1)

        self.BtnEliminar = self._make_btn(
            "BtnEliminar", "Eliminar Usuario", _DANGER_BTN_QSS, icon_trash
        )
        self.gridLayout_2.addWidget(self.BtnEliminar, 5, 3, 1, 1)

        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.widget_3, 0)

        # ── Buscador ────────────────────────────────────────────────
        self.widget_2 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet("background: transparent;")
        _sp_hfix(self.widget_2)
        self.widget_2.setMinimumHeight(48)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setSpacing(10)

        self.label_2 = QtWidgets.QLabel(parent=self.widget_2)
        self.label_2.setObjectName("label_2")
        self.label_2.setFixedSize(24, 24)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setPixmap(icon_search)
        self.label_2.setScaledContents(True)
        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEdit = QtWidgets.QLineEdit(parent=self.widget_2)
        self.lineEdit.setObjectName("lineEdit")
        _sp_hfix(self.lineEdit)
        self.lineEdit.setMinimumHeight(_CTRL_MIN_H)
        self.lineEdit.setStyleSheet(_SEARCH_QSS)
        self.horizontalLayout_3.addWidget(self.lineEdit)

        self.verticalLayout_2.addWidget(self.widget_2, 0)

        # ── Tabla ───────────────────────────────────────────────────
        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("background: transparent;")
        _sp_expand(self.widget)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setSpacing(0)

        self.TablaUser = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaUser.setObjectName("TablaUser")
        _sp_expand(self.TablaUser)
        self.TablaUser.setMinimumHeight(280)
        self.TablaUser.setStyleSheet(_TABLE_QSS)
        self.TablaUser.setColumnCount(6)
        self.TablaUser.setRowCount(16)
        self.TablaUser.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaUser.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        self.TablaUser.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.TablaUser.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaUser.verticalHeader().setVisible(False)
        self.TablaUser.setShowGrid(False)
        _card_shadow(self.TablaUser)

        for row_idx in range(16):
            item = QtWidgets.QTableWidgetItem()
            self.TablaUser.setVerticalHeaderItem(row_idx, item)

        for col_idx in range(6):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignCenter
            )
            self.TablaUser.setHorizontalHeaderItem(col_idx, item)

        self.verticalLayout_3.addWidget(self.TablaUser)

        self.verticalLayout_2.addWidget(self.widget, 1)

        # ── Placeholder inferior ────────────────────────────────────
        self.widget_4 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setStyleSheet("background: transparent;")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_2.addWidget(self.widget_4, 0)

        self.Contenido.addWidget(self.ContenidoPage1)
        self.horizontalLayout_2.addWidget(self.Contenido)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ── Helpers de creación ────────────────────────────────────────
    def _make_input(self, name: str, icon_pix) -> QtWidgets.QLineEdit:
        le = QtWidgets.QLineEdit(parent=self.widget_3)
        le.setObjectName(name)
        _sp_hfix(le)
        le.setMinimumSize(QtCore.QSize(220, _CTRL_MIN_H))
        le.setStyleSheet(_INPUT_QSS)
        le.addAction(
            QtGui.QIcon(icon_pix),
            QtWidgets.QLineEdit.ActionPosition.LeadingPosition,
        )
        return le

    def _make_btn(self, name: str, text: str, style: str, icon_pix) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton(parent=self.widget_3)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        _sp_hfix(btn)
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setStyleSheet(style)
        btn.setIcon(QtGui.QIcon(icon_pix))
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        btn.setText(text)
        return btn

    # ── Responsividad dinámica ─────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        ctrl_h = max(42, min(52, int(height * 0.058)))
        self.lineEdit.setMinimumHeight(ctrl_h)
        for name in (
            "InputIdUser", "InputNombreUser", "InputUser", "InputPasswordUser"
        ):
            getattr(self, name).setMinimumHeight(ctrl_h)

        btn_h = max(44, min(54, int(height * 0.062)))
        for name in ("BtnRolUser", "BtnRegistrarUser", "BtnEliminar"):
            getattr(self, name).setMinimumHeight(btn_h)

    # ── Textos ─────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Control de Usuarios"))
        self.label_3.setText(_translate("Form", "ID:"))
        self.label_5.setText(_translate("Form", "Nombre:"))
        self.label_7.setText(_translate("Form", "Usuario:"))
        self.label.setText(_translate("Form", "Contraseña:"))
        self.label_6.setText(_translate("Form", "Rol"))
        self.LabelVentasA.setText(_translate("Form", "Usuarios"))
        self.BtnRolUser.setText(_translate("Form", "Asesor Comercial"))
        self.BtnRegistrarUser.setText(_translate("Form", "Registrar Usuario"))
        self.BtnEliminar.setText(_translate("Form", "Eliminar Usuario"))

        for row_idx in range(16):
            item = self.TablaUser.verticalHeaderItem(row_idx)
            if item is not None:
                if row_idx < 14:
                    item.setText(_translate("Form", "Nueva fila"))
                else:
                    item.setText(_translate("Form", "New Row"))

        headers = [
            "ID ",
            "Nombre",
            "Usuario",
            "Contraseña",
            "Rol",
            "Estado",
        ]
        for col_idx, header_text in enumerate(headers):
            item = self.TablaUser.horizontalHeaderItem(col_idx)
            if item is not None:
                item.setText(_translate("Form", header_text))
