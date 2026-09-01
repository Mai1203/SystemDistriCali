from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
# SystemDistriCali — Lady Nail SHOP
# Módulo: Control de Usuarios
# ═══════════════════════════════════════════════════════════════════


# ── Paleta ─────────────────────────────────────────────────────────

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


# Alturas
_CTRL_MIN_H = 44
_BTN_MIN_H  = 34


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

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

    shadow.setColor(
        QtGui.QColor(100, 30, 80, 45)
    )

    widget.setGraphicsEffect(shadow)


# ═══════════════════════════════════════════════════════════════════
# INPUTS
# ═══════════════════════════════════════════════════════════════════

_INPUT_QSS = f"""
    QLineEdit {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;

        padding: 0px 12px 0px 38px;

        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};

        min-height: {_CTRL_MIN_H}px;
    }}

    QLineEdit:focus {{
        border: 2px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}

    QLineEdit:hover {{
        border-color: {_BORDER_H};
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# BUSCADOR
# ═══════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════
# BOTÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

_PRIMARY_BTN_QSS = f"""
    QToolButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;

        border: none;
        border-radius: 9px;

        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};

        padding: 0 14px;

        min-height: {_BTN_MIN_H}px;
        max-height: {_BTN_MIN_H}px;
    }}

    QToolButton:hover {{
        background-color: {_PRIMARY_H};
    }}

    QToolButton:pressed {{
        background-color: {_PRIMARY_P};
    }}

    QToolButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# BOTÓN ROL
# ═══════════════════════════════════════════════════════════════════

_SECONDARY_BTN_QSS = f"""
    QToolButton {{
        background-color: {_CARD_BG};

        color: {_PRIMARY};

        border: 1.5px solid {_PRIMARY};
        border-radius: 10px;

        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};

        padding: 0 12px;

        min-height: {_CTRL_MIN_H}px;
        max-height: {_CTRL_MIN_H}px;
    }}

    QToolButton:hover {{
        background-color: #FBEFF7;
        border: 2px solid {_PRIMARY};
    }}

    QToolButton:pressed {{
        background-color: #F3E6EF;
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# BOTÓN ELIMINAR
# ═══════════════════════════════════════════════════════════════════

_DANGER_BTN_QSS = f"""
    QToolButton {{
        background-color: {_DANGER};
        color: #FFFFFF;

        border: none;
        border-radius: 9px;

        font-size: 13px;
        font-weight: 600;
        font-family: {_FONT};

        padding: 0 14px;

        min-height: {_BTN_MIN_H}px;
        max-height: {_BTN_MIN_H}px;
    }}

    QToolButton:hover {{
        background-color: {_DANGER_H};
    }}

    QToolButton:pressed {{
        background-color: {_DANGER_P};
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# TABLA
# ═══════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════
# COMBOBOX
# ═══════════════════════════════════════════════════════════════════

_QSS_COMBO = f"""
    QComboBox {{
        background-color: {_CARD_BG};

        border: 1.5px solid {_BORDER};
        border-radius: 10px;

        padding: 8px 12px;

        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};

        min-height: 28px;
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

        border-left: 5px solid transparent;
        border-right: 5px solid transparent;

        border-top: 6px solid {_MUTED};

        margin-right: 10px;
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
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════

class Ui_ControlUsuario(object):

    def setupUi(self, Form):

        Form.setObjectName("Form")

        Form.setMinimumSize(
            QtCore.QSize(900, 600)
        )

        Form.setStyleSheet(
            f"background-color: {_BG};"
        )


        # ═══════════════════════════════════════════════════════════
        # ICONOS
        # ═══════════════════════════════════════════════════════════

        icon_search = qta.icon(
            "fa5s.search",
            color=_PRIMARY
        ).pixmap(20, 20)

        icon_id = qta.icon(
            "fa5s.id-badge",
            color=_PRIMARY
        ).pixmap(20, 20)

        icon_user = qta.icon(
            "fa5s.user",
            color=_PRIMARY
        ).pixmap(20, 20)

        icon_lock = qta.icon(
            "fa5s.lock",
            color=_PRIMARY
        ).pixmap(20, 20)

        icon_rol = qta.icon(
            "fa5s.user-tag",
            color=_PRIMARY
        ).pixmap(20, 20)

        icon_trash = qta.icon(
            "fa5s.trash-alt",
            color="#FFFFFF"
        ).pixmap(16, 16)

        icon_register = qta.icon(
            "fa5s.user-plus",
            color="#FFFFFF"
        ).pixmap(16, 16)


        # ═══════════════════════════════════════════════════════════
        # CONTENEDOR PRINCIPAL
        # ═══════════════════════════════════════════════════════════

        self.gridLayoutPrincipal = QtWidgets.QGridLayout(Form)

        self.gridLayoutPrincipal.setContentsMargins(
            0, 0, 0, 0
        )

        self.Contenedor = QtWidgets.QWidget(
            parent=Form
        )

        self.Contenedor.setObjectName(
            "Contenedor"
        )

        self.Contenedor.setStyleSheet(
            "background-color: transparent;"
        )

        _sp_expand(self.Contenedor)

        self.gridLayoutPrincipal.addWidget(
            self.Contenedor,
            0,
            0,
            1,
            1
        )


        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(
            self.Contenedor
        )

        self.horizontalLayout_2.setContentsMargins(
            24, 24, 24, 24
        )

        self.horizontalLayout_2.setSpacing(24)


        self.Contenido = QtWidgets.QStackedWidget(
            parent=self.Contenedor
        )

        self.Contenido.setObjectName(
            "Contenido"
        )

        self.Contenido.setStyleSheet(
            "background: transparent; border: none;"
        )

        _sp_expand(self.Contenido)

        self.horizontalLayout_2.addWidget(
            self.Contenido
        )


        # ═══════════════════════════════════════════════════════════
        # PÁGINA
        # ═══════════════════════════════════════════════════════════

        self.ContenidoPage1 = QtWidgets.QWidget()

        self.ContenidoPage1.setObjectName(
            "ContenidoPage1"
        )

        self.Contenido.addWidget(
            self.ContenidoPage1
        )


        self.verticalLayout_2 = QtWidgets.QVBoxLayout(
            self.ContenidoPage1
        )

        self.verticalLayout_2.setContentsMargins(
            0, 0, 0, 0
        )

        self.verticalLayout_2.setSpacing(24)


        # ═══════════════════════════════════════════════════════════
        # TARJETA FORMULARIO
        # ═══════════════════════════════════════════════════════════

        self.widget_3 = QtWidgets.QWidget(
            parent=self.ContenidoPage1
        )

        self.widget_3.setObjectName(
            "widget_3"
        )

        self.widget_3.setStyleSheet(
            f"""
            QWidget#widget_3 {{
                background-color: {_CARD_BG};

                border: 1px solid {_CARD_BORDER};

                border-radius: 22px;
            }}

            {_QSS_COMBO}
            """
        )

        _card_shadow(
            self.widget_3
        )


        self.gridLayout = QtWidgets.QGridLayout(
            self.widget_3
        )

        self.gridLayout.setContentsMargins(
            28, 22, 28, 22
        )

        self.gridLayout.setHorizontalSpacing(
            12
        )

        self.gridLayout.setVerticalSpacing(
            12
        )


        # ═══════════════════════════════════════════════════════════
        # GRID DEL FORMULARIO
        #
        # COLUMNAS
        #
        # 0 = ID / Rol
        # 1 = Nombre / Permisos
        # 2 = Usuario
        # 3 = Contraseña / Registrar
        # 4 = Eliminar
        #
        # ═══════════════════════════════════════════════════════════

        self.gridFormulario = QtWidgets.QGridLayout()

        self.gridFormulario.setHorizontalSpacing(
            12
        )

        self.gridFormulario.setVerticalSpacing(
            8
        )


        # ═══════════════════════════════════════════════════════════
        # TÍTULO
        # ═══════════════════════════════════════════════════════════

        self.LabelVentasA = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.LabelVentasA.setObjectName(
            "LabelVentasA"
        )

        self.LabelVentasA.setStyleSheet(
            f"""
            font-size: 28px;
            font-weight: 700;
            color: {_PRIMARY};
            font-family: {_FONT};
            background: transparent;
            """
        )

        self.gridFormulario.addWidget(
            self.LabelVentasA,
            0,
            0,
            1,
            5
        )


        # ═══════════════════════════════════════════════════════════
        # ESPACIO
        # ═══════════════════════════════════════════════════════════

        self.label_30 = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label_30.setText("")

        self.gridFormulario.addWidget(
            self.label_30,
            1,
            0,
            1,
            5
        )


        # ═══════════════════════════════════════════════════════════
        # PRIMERA FILA
        #
        # ID
        # NOMBRE
        # USUARIO
        # CONTRASEÑA
        #
        # ═══════════════════════════════════════════════════════════

        self.label_3 = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label_3.setObjectName(
            "label_3"
        )

        self.gridFormulario.addWidget(
            self.label_3,
            2,
            0
        )


        self.label_5 = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label_5.setObjectName(
            "label_5"
        )

        self.gridFormulario.addWidget(
            self.label_5,
            2,
            1
        )


        self.label_7 = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label_7.setObjectName(
            "label_7"
        )

        self.gridFormulario.addWidget(
            self.label_7,
            2,
            2
        )


        self.label = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label.setObjectName(
            "label"
        )

        self.gridFormulario.addWidget(
            self.label,
            2,
            3
        )


        # ═══════════════════════════════════════════════════════════
        # INPUTS
        # ═══════════════════════════════════════════════════════════

        self.InputIdUser = self._make_input(
            "InputIdUser",
            icon_id
        )

        self.gridFormulario.addWidget(
            self.InputIdUser,
            3,
            0
        )


        self.InputNombreUser = self._make_input(
            "InputNombreUser",
            icon_user
        )

        self.gridFormulario.addWidget(
            self.InputNombreUser,
            3,
            1
        )


        self.InputUser = self._make_input(
            "InputUser",
            icon_user
        )

        self.gridFormulario.addWidget(
            self.InputUser,
            3,
            2
        )


        self.InputPasswordUser = self._make_input(
            "InputPasswordUser",
            icon_lock
        )

        self.InputPasswordUser.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )

        self.gridFormulario.addWidget(
            self.InputPasswordUser,
            3,
            3
        )


        # ═══════════════════════════════════════════════════════════
        # SEGUNDA FILA
        #
        # ROL COMIENZA DESDE LA IZQUIERDA
        # PERMISOS AL LADO
        # BOTONES A LA DERECHA
        #
        # ═══════════════════════════════════════════════════════════

        self.label_6 = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.label_6.setObjectName(
            "label_6"
        )

        self.gridFormulario.addWidget(
            self.label_6,
            4,
            0
        )


        # Label de permisos.
        #
        # El ComboBox real se crea en el VIEW.
        #
        self.labelPermisosPlaceholder = QtWidgets.QLabel(
            parent=self.widget_3
        )

        self.labelPermisosPlaceholder.setObjectName(
            "labelPermisosPlaceholder"
        )

        self.labelPermisosPlaceholder.setText(
            "Permisos"
        )

        self.gridFormulario.addWidget(
            self.labelPermisosPlaceholder,
            4,
            1
        )


        # ═══════════════════════════════════════════════════════════
        # ROL
        # ═══════════════════════════════════════════════════════════

        self.BtnRolUser = self._make_btn(
            "BtnRolUser",
            "ASESOR",
            _SECONDARY_BTN_QSS,
            icon_rol,

            min_h=_CTRL_MIN_H,
            icon_size=20
        )

        self.gridFormulario.addWidget(
            self.BtnRolUser,
            5,
            0
        )


        # ═══════════════════════════════════════════════════════════
        # BOTONES
        #
        # IMPORTANTE:
        # Se colocan en columnas 3 y 4.
        # Por eso quedan completamente a la derecha.
        # ═══════════════════════════════════════════════════════════

        self.BtnRegistrarUser = self._make_btn(
            "BtnRegistrarUser",
            "Registrar Usuario",
            _PRIMARY_BTN_QSS,
            icon_register,

            min_h=_BTN_MIN_H,
            icon_size=16
        )

        self.gridFormulario.addWidget(
            self.BtnRegistrarUser,
            5,
            3
        )


        self.BtnEliminar = self._make_btn(
            "BtnEliminar",
            "Eliminar Usuario",
            _DANGER_BTN_QSS,
            icon_trash,

            min_h=_BTN_MIN_H,
            icon_size=16
        )

        self.gridFormulario.addWidget(
            self.BtnEliminar,
            5,
            4
        )


        # ═══════════════════════════════════════════════════════════
        # AÑADIR GRID
        # ═══════════════════════════════════════════════════════════

        self.gridLayout.addLayout(
            self.gridFormulario,
            0,
            0
        )

        self.verticalLayout_2.addWidget(
            self.widget_3,
            0
        )


        # ═══════════════════════════════════════════════════════════
        # BUSCADOR
        # ═══════════════════════════════════════════════════════════

        self.widget_2 = QtWidgets.QWidget(
            parent=self.ContenidoPage1
        )

        self.widget_2.setObjectName(
            "widget_2"
        )

        self.widget_2.setStyleSheet(
            "background: transparent;"
        )

        _sp_hfix(
            self.widget_2
        )

        self.widget_2.setMinimumHeight(
            48
        )


        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(
            self.widget_2
        )

        self.horizontalLayout_3.setSpacing(
            10
        )


        self.label_2 = QtWidgets.QLabel(
            parent=self.widget_2
        )

        self.label_2.setObjectName(
            "label_2"
        )

        self.label_2.setFixedSize(
            24,
            24
        )

        self.label_2.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter
        )

        self.label_2.setPixmap(
            icon_search
        )

        self.label_2.setScaledContents(
            True
        )

        self.horizontalLayout_3.addWidget(
            self.label_2
        )


        self.lineEdit = QtWidgets.QLineEdit(
            parent=self.widget_2
        )

        self.lineEdit.setObjectName(
            "lineEdit"
        )

        _sp_hfix(
            self.lineEdit
        )

        self.lineEdit.setMinimumHeight(
            _CTRL_MIN_H
        )

        self.lineEdit.setStyleSheet(
            _SEARCH_QSS
        )

        self.horizontalLayout_3.addWidget(
            self.lineEdit
        )


        self.verticalLayout_2.addWidget(
            self.widget_2,
            0
        )


        # ═══════════════════════════════════════════════════════════
        # TABLA
        # ═══════════════════════════════════════════════════════════

        self.widget = QtWidgets.QWidget(
            parent=self.ContenidoPage1
        )

        self.widget.setObjectName(
            "widget"
        )

        self.widget.setStyleSheet(
            "background: transparent;"
        )

        _sp_expand(
            self.widget
        )


        self.verticalLayout_3 = QtWidgets.QVBoxLayout(
            self.widget
        )

        self.verticalLayout_3.setSpacing(
            0
        )


        self.TablaUser = QtWidgets.QTableWidget(
            parent=self.widget
        )

        self.TablaUser.setObjectName(
            "TablaUser"
        )

        _sp_expand(
            self.TablaUser
        )

        self.TablaUser.setMinimumHeight(
            280
        )

        self.TablaUser.setStyleSheet(
            _TABLE_QSS
        )

        self.TablaUser.setColumnCount(
            6
        )

        self.TablaUser.setRowCount(
            16
        )


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

        self.TablaUser.verticalHeader().setVisible(
            False
        )

        self.TablaUser.setShowGrid(
            False
        )


        _card_shadow(
            self.TablaUser
        )


        for row_idx in range(16):

            item = QtWidgets.QTableWidgetItem()

            self.TablaUser.setVerticalHeaderItem(
                row_idx,
                item
            )


        for col_idx in range(6):

            item = QtWidgets.QTableWidgetItem()

            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignCenter
            )

            self.TablaUser.setHorizontalHeaderItem(
                col_idx,
                item
            )


        self.verticalLayout_3.addWidget(
            self.TablaUser
        )


        self.verticalLayout_2.addWidget(
            self.widget,
            1
        )


        # ═══════════════════════════════════════════════════════════
        # PLACEHOLDER INFERIOR
        # ═══════════════════════════════════════════════════════════

        self.widget_4 = QtWidgets.QWidget(
            parent=self.ContenidoPage1
        )

        self.widget_4.setObjectName(
            "widget_4"
        )

        self.widget_4.setStyleSheet(
            "background: transparent;"
        )

        self.verticalLayout_2.addWidget(
            self.widget_4,
            0
        )


        self.retranslateUi(
            Form
        )

        QtCore.QMetaObject.connectSlotsByName(
            Form
        )


    # ═══════════════════════════════════════════════════════════════
    # CREAR INPUT
    # ═══════════════════════════════════════════════════════════════

    def _make_input(
        self,
        name: str,
        icon_pix
    ):

        le = QtWidgets.QLineEdit(
            parent=self.widget_3
        )

        le.setObjectName(
            name
        )

        _sp_hfix(
            le
        )

        le.setMinimumHeight(
            _CTRL_MIN_H
        )

        le.setStyleSheet(
            _INPUT_QSS
        )

        le.addAction(
            QtGui.QIcon(icon_pix),
            QtWidgets.QLineEdit.ActionPosition.LeadingPosition
        )

        return le


    # ═══════════════════════════════════════════════════════════════
    # CREAR BOTÓN
    # ═══════════════════════════════════════════════════════════════

    def _make_btn(
        self,
        name: str,
        text: str,
        style: str,
        icon_pix,
        min_h: int = _BTN_MIN_H,
        icon_size: int = 16
    ):

        btn = QtWidgets.QToolButton(
            parent=self.widget_3
        )

        btn.setObjectName(
            name
        )

        btn.setCursor(
            QtGui.QCursor(
                QtCore.Qt.CursorShape.PointingHandCursor
            )
        )

        _sp_hfix(
            btn
        )

        btn.setMinimumHeight(
            min_h
        )

        btn.setMaximumHeight(
            min_h
        )

        btn.setStyleSheet(
            style
        )

        btn.setIcon(
            QtGui.QIcon(icon_pix)
        )

        btn.setIconSize(
            QtCore.QSize(
                icon_size,
                icon_size
            )
        )

        btn.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )

        btn.setText(
            text
        )

        return btn


    # ═══════════════════════════════════════════════════════════════
    # RESPONSIVIDAD
    # ═══════════════════════════════════════════════════════════════

    def adapt_to_size(
        self,
        width: int,
        height: int
    ):

        h_margin = max(
            16,
            min(
                60,
                int(width * 0.05)
            )
        )

        v_margin = max(
            16,
            min(
                48,
                int(height * 0.04)
            )
        )


        self.horizontalLayout_2.setContentsMargins(
            h_margin,
            v_margin,
            h_margin,
            v_margin
        )


        ctrl_h = max(
            42,
            min(
                52,
                int(height * 0.058)
            )
        )


        for name in (
            "InputIdUser",
            "InputNombreUser",
            "InputUser",
            "InputPasswordUser"
        ):

            getattr(
                self,
                name
            ).setMinimumHeight(
                ctrl_h
            )


        self.BtnRolUser.setMinimumHeight(
            ctrl_h
        )

        self.BtnRolUser.setMaximumHeight(
            ctrl_h
        )


        if hasattr(
            self,
            "comboPermisos"
        ):

            self.comboPermisos.setMinimumHeight(
                ctrl_h - 10
            )


        btn_h = max(
            30,
            min(
                38,
                int(height * 0.042)
            )
        )


        for name in (
            "BtnRegistrarUser",
            "BtnEliminar"
        ):

            getattr(
                self,
                name
            ).setMinimumHeight(
                btn_h
            )

            getattr(
                self,
                name
            ).setMaximumHeight(
                btn_h
            )


    # ═══════════════════════════════════════════════════════════════
    # TEXTOS
    # ═══════════════════════════════════════════════════════════════

    def retranslateUi(
        self,
        Form
    ):

        _translate = QtCore.QCoreApplication.translate


        Form.setWindowTitle(
            _translate(
                "Form",
                "Control de Usuarios"
            )
        )


        self.label_3.setText(
            _translate(
                "Form",
                "ID:"
            )
        )


        self.label_5.setText(
            _translate(
                "Form",
                "Nombre:"
            )
        )


        self.label_7.setText(
            _translate(
                "Form",
                "Usuario:"
            )
        )


        self.label.setText(
            _translate(
                "Form",
                "Contraseña:"
            )
        )


        self.label_6.setText(
            _translate(
                "Form",
                "Rol:"
            )
        )


        self.LabelVentasA.setText(
            _translate(
                "Form",
                "Usuarios"
            )
        )


        self.BtnRolUser.setText(
            _translate(
                "Form",
                "ASESOR"
            )
        )


        self.BtnRegistrarUser.setText(
            _translate(
                "Form",
                "Registrar Usuario"
            )
        )


        self.BtnEliminar.setText(
            _translate(
                "Form",
                "Eliminar Usuario"
            )
        )


        for row_idx in range(16):

            item = self.TablaUser.verticalHeaderItem(
                row_idx
            )

            if item is not None:

                item.setText(
                    _translate(
                        "Form",
                        "Nueva fila"
                    )
                )


        headers = [
            "ID",
            "Nombre",
            "Usuario",
            "Contraseña",
            "Rol",
            "Estado",
        ]


        for col_idx, header_text in enumerate(headers):

            item = self.TablaUser.horizontalHeaderItem(
                col_idx
            )

            if item is not None:

                item.setText(
                    _translate(
                        "Form",
                        header_text
                    )
                )