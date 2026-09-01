# UI de Egresos — Escrita a mano siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry, tarjetas con sombra, inputs focus/hover, SVG, responsiva)
#
# Reglas aplicadas del design_system_login.txt:
#  · Colores semánticos con prefijo _ (nunca hex inline)
#  · Sin setFixedSize en controles de formulario (solo minHeight + Expanding)
#  · Tarjetas flotantes: border-radius + QGraphicsDropShadowEffect
#  · Inputs/ComboBox con borde 1.5px, focus 2px _PRIMARY, fondo _FOCUS_BG
#  · Botón primario _PRIMARY → hover _PRIMARY_H → pressed _PRIMARY_P
#  · Botón de eliminar en estilo "danger" coherente (mismo radio/tactil)
#  · Tabla con header plum, selección tinte berry, hover suave
#  · resizeEvent → adapt_to_size recalcula márgenes, fuentes y alturas
#  · PointingHandCursor en controles interactivos
#  · Iconos SVG monocromáticos (input_user, input_lock, badge_shield_user)

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

_INPUT_MIN_H = 40
_BTN_MIN_H   = 40


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
#  Hojas de estilo (QSS) reutilizables
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
    QLineEdit:disabled {{
        color: {_MUTED};
        background-color: #FBF7FA;
    }}
    QLineEdit:read-only {{
        color: {_MUTED};
        background-color: #FBF7FA;
    }}
"""

_COMBO_QSS = f"""
    QComboBox {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 0px 12px 0px 38px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
    }}
    QComboBox:focus, QComboBox:hover {{
        border: 2px solid {_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        color: {_TEXT};
        selection-background-color: {_PRIMARY};
        selection-color: #FFFFFF;
        border-radius: 10px;
        padding: 4px;
        font-family: {_FONT};
    }}
"""

_LABEL_QSS = f"""
    QLabel {{
        font-size: 12px;
        font-weight: 600;
        color: {_MUTED};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_PRIMARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 0 16px;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QPushButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_DANGER_BTN_QSS = f"""
    QPushButton {{
        background-color: {_DANGER};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 0 16px;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {_DANGER_H};
    }}
    QPushButton:disabled {{
        background-color: #D9B8B2;
        color: #F7EEEC;
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


class Ui_Egreso(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(720, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # ── Contenedor principal ──────────────────────────────────
        self.Contenedor = QtWidgets.QWidget(parent=Form)
        self.Contenedor.setObjectName("Contenedor")
        self.Contenedor.setStyleSheet("background-color: transparent;")
        _sp_expand(self.Contenedor)
        self.horizontalLayout.addWidget(self.Contenedor)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Contenedor)
        self.horizontalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.horizontalLayout_2.setSpacing(24)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # ── Área de contenido (stacked, 1 página) ─────────────────
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

        # ── Tarjeta de formulario ─────────────────────────────────
        self._build_form_card()

        # ── Tarjeta de tabla ──────────────────────────────────────
        self._build_table_card()

        # ── Pie ───────────────────────────────────────────────────
        self._build_footer()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta de formulario
    # ─────────────────────────────────────────────────────────────
    def _build_form_card(self):
        self.widget_3 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setStyleSheet(f"""
            QWidget#widget_3 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        self.widget_3.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.widget_3)

        self.gridLayout = QtWidgets.QGridLayout(self.widget_3)
        self.gridLayout.setContentsMargins(32, 28, 32, 28)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setHorizontalSpacing(16)
        self.gridLayout_2.setVerticalSpacing(14)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        # Encabezado: badge + título + subtítulo
        header = QtWidgets.QWidget(parent=self.widget_3)
        header.setStyleSheet("background: transparent;")
        hrow = QtWidgets.QHBoxLayout(header)
        hrow.setContentsMargins(0, 0, 0, 0)
        hrow.setSpacing(14)

        self.lblBadge = QtWidgets.QLabel(parent=header)
        self.lblBadge.setFixedSize(48, 48)
        self.lblBadge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pix = QtGui.QPixmap("assets/iconos/badge_shield_user.svg")
        if not pix.isNull():
            self.lblBadge.setPixmap(
                pix.scaled(48, 48,
                           QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        hrow.addWidget(self.lblBadge)

        titleCol = QtWidgets.QVBoxLayout()
        titleCol.setSpacing(2)
        self.LabelVentasA = QtWidgets.QLabel(parent=header)
        self.LabelVentasA.setObjectName("LabelVentasA")
        self.LabelVentasA.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        titleCol.addWidget(self.LabelVentasA)

        self.lblSubtitle = QtWidgets.QLabel(parent=header)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setStyleSheet(
            f"font-size: 13px; color: {_MUTED}; font-family: {_FONT};"
            f" background: transparent;"
        )
        titleCol.addWidget(self.lblSubtitle)
        hrow.addLayout(titleCol)
        hrow.addStretch()

        self.gridLayout_2.addWidget(header, 0, 0, 1, 2)

        # Filas de campos (etiqueta | control)
        self._add_field_row(1, "label_3", "Tipo de Gasto",
                            self._make_tipo_gasto(), "assets/iconos/input_user.svg")
        self._add_field_row(2, "label_5", "Descripcion",
                            self._make_descripcion(), "assets/iconos/input_user.svg")
        self._add_field_row(3, "label", "Fecha",
                            self._make_fecha(), None)
        self._add_field_row(4, "label_7", "Pago",
                            self._make_pago(), "assets/iconos/input_lock.svg")
        self._add_field_row(5, "label_6", "Metodo de Pago",
                            self._make_metodo(), None)

        # Botones
        btnRow = QtWidgets.QHBoxLayout()
        btnRow.setSpacing(12)
        btnRow.addStretch()

        self.BtnRegistrarEgreso = QtWidgets.QPushButton(parent=self.widget_3)
        self.BtnRegistrarEgreso.setObjectName("BtnRegistrarEgreso")
        self.BtnRegistrarEgreso.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.BtnRegistrarEgreso.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.BtnRegistrarEgreso.setMinimumHeight(_BTN_MIN_H)
        self.BtnRegistrarEgreso.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        icon = QtGui.QIcon("assets/iconos/lock_white.svg")
        self.BtnRegistrarEgreso.setIcon(icon)
        btnRow.addWidget(self.BtnRegistrarEgreso)

        self.BtnEliminar = QtWidgets.QPushButton(parent=self.widget_3)
        self.BtnEliminar.setObjectName("BtnEliminar")
        self.BtnEliminar.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.BtnEliminar.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.BtnEliminar.setMinimumHeight(_BTN_MIN_H)
        self.BtnEliminar.setStyleSheet(f"background-color: {_DANGER}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        trash = qta.icon("fa5s.trash-alt", color="#FFFFFF")
        self.BtnEliminar.setIcon(trash)
        btnRow.addWidget(self.BtnEliminar)

        self.gridLayout_2.addLayout(btnRow, 6, 0, 1, 2)

        self.verticalLayout_2.addWidget(self.widget_3, 0)

    def _add_field_row(self, row, label_name, label_text, control, icon_path):
        label = QtWidgets.QLabel(parent=self.widget_3)
        label.setObjectName(label_name)
        setattr(self, label_name, label)
        label.setText(label_text)
        label.setStyleSheet(_LABEL_QSS)
        label.setMinimumHeight(_INPUT_MIN_H)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.gridLayout_2.addWidget(label, row, 0)

        if icon_path:
            control.addAction(
                QtGui.QIcon(icon_path),
                QtWidgets.QLineEdit.ActionPosition.LeadingPosition
                if isinstance(control, QtWidgets.QLineEdit)
                else QtWidgets.QComboBox.ActionPosition.LeadingPosition,
            )
        self.gridLayout_2.addWidget(control, row, 1)

    # ── Constructores de controles ────────────────────────────────
    def _make_tipo_gasto(self):
        w = QtWidgets.QLineEdit(parent=self.widget_3)
        w.setObjectName("InputTipoGasto")
        _sp_hfix(w)
        w.setMinimumHeight(_INPUT_MIN_H)
        w.setStyleSheet(_INPUT_QSS)
        self.InputTipoGasto = w
        return w

    def _make_descripcion(self):
        w = QtWidgets.QLineEdit(parent=self.widget_3)
        w.setObjectName("InputDescripcionEgreso")
        _sp_hfix(w)
        w.setMinimumHeight(_INPUT_MIN_H)
        w.setStyleSheet(_INPUT_QSS)
        self.InputDescripcionEgreso = w
        return w

    def _make_fecha(self):
        w = QtWidgets.QLineEdit(parent=self.widget_3)
        w.setObjectName("InputFechaEgreso")
        _sp_hfix(w)
        w.setMinimumHeight(_INPUT_MIN_H)
        w.setStyleSheet(_INPUT_QSS)
        self.InputFechaEgreso = w
        return w

    def _make_pago(self):
        w = QtWidgets.QLineEdit(parent=self.widget_3)
        w.setObjectName("InputPagoEgreso")
        _sp_hfix(w)
        w.setMinimumHeight(_INPUT_MIN_H)
        w.setStyleSheet(_INPUT_QSS)
        self.InputPagoEgreso = w
        return w

    def _make_metodo(self):
        w = QtWidgets.QComboBox(parent=self.widget_3)
        w.setObjectName("MetodoPagoBox")
        _sp_hfix(w)
        w.setMinimumHeight(_INPUT_MIN_H)
        w.setStyleSheet(_COMBO_QSS)
        self.MetodoPagoBox = w
        return w

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta de tabla
    # ─────────────────────────────────────────────────────────────
    def _build_table_card(self):
        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet(f"""
            QWidget#widget {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        _sp_expand(self.widget)
        _card_shadow(self.widget)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(16, 16, 16, 16)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.TablaEgreso = QtWidgets.QTableWidget(parent=self.widget)
        self.TablaEgreso.setObjectName("TablaEgreso")
        _sp_expand(self.TablaEgreso)
        self.TablaEgreso.setMinimumHeight(280)
        self.TablaEgreso.setStyleSheet(_TABLE_QSS)
        self.TablaEgreso.setColumnCount(6)
        self.TablaEgreso.setRowCount(0)
        self.TablaEgreso.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaEgreso.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.TablaEgreso.verticalHeader().setVisible(False)
        self.TablaEgreso.setShowGrid(False)
        self.verticalLayout_3.addWidget(self.TablaEgreso)

        self.verticalLayout_2.addWidget(self.widget, 1)

    # ─────────────────────────────────────────────────────────────
    #  Pie (crédito / acceso restringido)
    # ─────────────────────────────────────────────────────────────
    def _build_footer(self):
        self.widget_4 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setStyleSheet("background: transparent;")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        line = QtWidgets.QFrame(parent=self.widget_4)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setStyleSheet(
            f"color: {_DIVIDER}; background-color: {_DIVIDER}; max-height: 1px;"
        )
        self.gridLayout_3.addWidget(line, 0, 0, 1, 1)

        self.lblFooter = QtWidgets.QLabel(parent=self.widget_4)
        self.lblFooter.setObjectName("lblFooter")
        self.lblFooter.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblFooter.setStyleSheet(
            f"font-size: 11px; color: {_MUTED}; font-family: {_FONT};"
            f" background: transparent;"
        )
        self.gridLayout_3.addWidget(self.lblFooter, 1, 0, 1, 1)

        self.verticalLayout_2.addWidget(self.widget_4, 0)

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        card_h = max(24, min(40, int(width * 0.03)))
        card_v = max(22, min(40, int(height * 0.038)))
        self.gridLayout.setContentsMargins(card_h, card_v, card_h, card_v)

        min_input = max(40, min(48, int(height * 0.052)))
        for w in (self.InputTipoGasto, self.InputDescripcionEgreso,
                  self.InputFechaEgreso, self.InputPagoEgreso,
                  self.MetodoPagoBox):
            w.setMinimumHeight(min_input)

        self.BtnRegistrarEgreso.setMinimumHeight(
            max(40, min(48, int(height * 0.055)))
        )
        self.BtnEliminar.setMinimumHeight(
            max(40, min(48, int(height * 0.055)))
        )

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Egresos · Lady Nail"))
        self.LabelVentasA.setText(_translate("Form", "Egresos"))
        self.lblSubtitle.setText(
            _translate("Form", "Registra y controla los gastos del negocio")
        )
        self.label_3.setText(_translate("Form", "Tipo de Gasto"))
        self.label_5.setText(_translate("Form", "Descripcion"))
        self.label.setText(_translate("Form", "Fecha"))
        self.label_7.setText(_translate("Form", "Pago"))
        self.label_6.setText(_translate("Form", "Metodo de Pago"))
        self.BtnRegistrarEgreso.setText(_translate("Form", "  Registrar Egreso"))
        self.BtnEliminar.setText(_translate("Form", "  Eliminar Egreso"))
        self.lblFooter.setText(
            _translate("Form", "Solo personal autorizado · Lady Nail SHOP")
        )

        headers = [
            "ID Egr", "T.Gasto", "Descripcion", "M.Pago", "Monto", "Fecha"
        ]
        for col, text in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(_translate("Form", text))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaEgreso.setHorizontalHeaderItem(col, item)
