# UI de Reportes — Escrita a mano siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry, tarjetas con sombra, combos/calendario focus, SVG, responsiva)
#
# Reglas aplicadas del design_system_login.txt:
#  · Colores semánticos con prefijo _
#  · Tarjetas flotantes (border-radius + QGraphicsDropShadowEffect)
#  · ComboBox/inputs con borde 1.5px, foco 2px _PRIMARY, hover plum
#  · Botones primarios _PRIMARY (hover/pressed/disabled) con ícono PDF
#  · QCalendarWidget con cabecera plum y selección berry
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

_FONT = "'Segoe UI', Arial, sans-serif"

_CTRL_MIN_H = 44
_BTN_MIN_H  = 48


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
_COMBO_QSS = f"""
    QComboBox {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 0px 12px;
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

_PRIMARY_BTN_QSS = f"""
    QPushButton {{
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
    QPushButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QPushButton:pressed {{
        background-color: {_PRIMARY_P};
        padding-top: 12px;
    }}
    QPushButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_TITLE_QSS = f"""
    QLabel {{
        font-size: 20px;
        font-weight: 700;
        color: {_PRIMARY};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_SUBTITLE_QSS = f"""
    QLabel {{
        font-size: 12px;
        color: {_MUTED};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_CAPTION_QSS = f"""
    QLabel {{
        font-size: 12px;
        font-weight: 600;
        color: {_MUTED};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_CALENDAR_QSS = f"""
    QCalendarWidget {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 14px;
        font-family: {_FONT};
        color: {_TEXT};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {_PRIMARY};
        border-radius: 13px 13px 0 0;
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {_CARD_BG};
        color: {_TEXT};
        selection-background-color: {_PRIMARY};
        selection-color: #FFFFFF;
        border-radius: 8px;
    }}
    QCalendarWidget QToolButton {{
        color: #FFFFFF;
        background: transparent;
        font-family: {_FONT};
    }}
    QCalendarWidget QMenu {{
        background-color: {_CARD_BG};
        color: {_TEXT};
    }}
"""


def _card_shadow(widget: QtWidgets.QWidget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(40)
    shadow.setXOffset(0)
    shadow.setYOffset(12)
    shadow.setColor(QtGui.QColor(100, 30, 80, 45))
    widget.setGraphicsEffect(shadow)


class Ui_Reportes(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet(f"background-color: {_BG};")

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

        # ── Encabezado ─────────────────────────────────────────────
        self._build_header()

        # ── Área de tarjetas ───────────────────────────────────────
        self.widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("background: transparent;")
        _sp_expand(self.widget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.widget_3 = QtWidgets.QWidget(parent=self.widget)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setStyleSheet("background: transparent;")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(24)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self._build_card_caja()
        self._build_card_productos()
        self._build_card_analisis()

        self.verticalLayout_3.addWidget(self.widget_3)
        self.verticalLayout_2.addWidget(self.widget, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ─────────────────────────────────────────────────────────────
    #  Encabezado
    # ─────────────────────────────────────────────────────────────
    def _build_header(self):
        self.widget_2 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet(f"""
            QWidget#widget_2 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        self.widget_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.widget_2)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(28, 22, 28, 22)
        self.horizontalLayout_3.setSpacing(14)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        badge = QtWidgets.QLabel(parent=self.widget_2)
        badge.setFixedSize(48, 48)
        badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pix = QtGui.QPixmap("assets/iconos/badge_shield_user.svg")
        if not pix.isNull():
            badge.setPixmap(
                pix.scaled(48, 48,
                           QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        self.horizontalLayout_3.addWidget(badge)

        titleCol = QtWidgets.QVBoxLayout()
        titleCol.setSpacing(2)
        self.LabelReportes = QtWidgets.QLabel(parent=self.widget_2)
        self.LabelReportes.setObjectName("LabelReportes")
        self.LabelReportes.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {_PRIMARY};"
            f" font-family: {_FONT}; background: transparent;"
        )
        titleCol.addWidget(self.LabelReportes)

        self.lblReportesSub = QtWidgets.QLabel(parent=self.widget_2)
        self.lblReportesSub.setObjectName("lblReportesSub")
        self.lblReportesSub.setStyleSheet(_SUBTITLE_QSS)
        titleCol.addWidget(self.lblReportesSub)
        self.horizontalLayout_3.addLayout(titleCol)
        self.horizontalLayout_3.addStretch()

        self.verticalLayout_2.addWidget(self.widget_2, 0)

    # ─────────────────────────────────────────────────────────────
    #  Helpers de tarjeta
    # ─────────────────────────────────────────────────────────────
    def _make_card(self, name):
        card = QtWidgets.QWidget(parent=self.widget_3)
        card.setObjectName(name)
        setattr(self, name, card)
        card.setStyleSheet(f"""
            QWidget#{name} {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        card.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        _card_shadow(card)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.setObjectName(f"layout_{name}")
        return card, layout

    def _make_combo(self, name):
        combo = QtWidgets.QComboBox(parent=self.widget_3)
        combo.setObjectName(name)
        _sp_hfix(combo)
        combo.setMinimumHeight(_CTRL_MIN_H)
        combo.setStyleSheet(_COMBO_QSS)
        return combo

    def _make_title(self, name, text):
        lbl = QtWidgets.QLabel(parent=self.widget_3)
        lbl.setObjectName(name)
        lbl.setText(text)
        lbl.setStyleSheet(_TITLE_QSS)
        return lbl

    def _make_subtitle(self, name, text):
        lbl = QtWidgets.QLabel(parent=self.widget_3)
        lbl.setObjectName(name)
        lbl.setText(text)
        lbl.setStyleSheet(_SUBTITLE_QSS)
        return lbl

    def _make_caption(self, name, text):
        lbl = QtWidgets.QLabel(parent=self.widget_3)
        lbl.setObjectName(name)
        lbl.setText(text)
        lbl.setStyleSheet(_CAPTION_QSS)
        return lbl

    def _make_pdf_button(self, name, text):
        btn = QtWidgets.QPushButton(parent=self.widget_3)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        _sp_hfix(btn)
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setStyleSheet(_PRIMARY_BTN_QSS)
        icon_pdf = qta.icon("fa5s.file-pdf", color="#FFFFFF").pixmap(20, 20)
        btn.setIcon(QtGui.QIcon(icon_pdf))
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setText(text)
        return btn

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Reporte de Caja
    # ─────────────────────────────────────────────────────────────
    def _build_card_caja(self):
        card, layout = self._make_card("widget_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.label = self._make_title("label", "Reporte de Caja")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1,
                                  QtCore.Qt.AlignmentFlag.AlignLeft)

        self.label_2 = self._make_subtitle("label_2", "Caja")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1,
                                  QtCore.Qt.AlignmentFlag.AlignLeft)

        self.TipoCajaComboBox = self._make_combo("TipoCajaComboBox")
        self.gridLayout.addWidget(self.TipoCajaComboBox, 2, 0, 1, 1)

        self.label_3 = self._make_caption("label_3", "Tiempo")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1,
                                  QtCore.Qt.AlignmentFlag.AlignLeft)

        self.TiempoCajaComboBox = self._make_combo("TiempoCajaComboBox")
        self.gridLayout.addWidget(self.TiempoCajaComboBox, 4, 0, 1, 1)

        self.CalendarioCaja = QtWidgets.QCalendarWidget(parent=self.widget_3)
        self.CalendarioCaja.setObjectName("CalendarioCaja")
        self.CalendarioCaja.setStyleSheet(_CALENDAR_QSS)
        self.CalendarioCaja.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.gridLayout.addWidget(self.CalendarioCaja, 5, 0, 1, 1,
                                  QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.BtnTicketCaja = self._make_pdf_button(
            "BtnTicketCaja", "   Generar PDF"
        )
        self.gridLayout.addWidget(self.BtnTicketCaja, 6, 0, 1, 1)

        layout.addLayout(self.gridLayout)
        layout.addStretch()
        self.horizontalLayout.addWidget(card)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Reporte de Productos
    # ─────────────────────────────────────────────────────────────
    def _build_card_productos(self):
        card, layout = self._make_card("widget_5")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setVerticalSpacing(12)
        self.gridLayout_3.setHorizontalSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.label_5 = self._make_title("label_5", "Reporte de Productos")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1,
                                    QtCore.Qt.AlignmentFlag.AlignLeft)

        self.TipoProductosComboBox = self._make_combo("TipoProductosComboBox")
        self.gridLayout_3.addWidget(self.TipoProductosComboBox, 1, 0, 1, 1)

        self.BtnTicketProducto = self._make_pdf_button(
            "BtnTicketProducto", "   Generar PDF"
        )
        self.gridLayout_3.addWidget(self.BtnTicketProducto, 2, 0, 1, 1)

        layout.addLayout(self.gridLayout_3)
        layout.addStretch()
        self.horizontalLayout.addWidget(card)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Análisis de Venta
    # ─────────────────────────────────────────────────────────────
    def _build_card_analisis(self):
        card, layout = self._make_card("widget_6")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setVerticalSpacing(12)
        self.gridLayout_4.setHorizontalSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")

        self.label_6 = self._make_title("label_6", "Analisis de Venta")
        self.gridLayout_4.addWidget(self.label_6, 0, 0, 1, 1,
                                    QtCore.Qt.AlignmentFlag.AlignLeft)

        self.label_7 = self._make_subtitle("label_7", "Ventas")
        self.gridLayout_4.addWidget(self.label_7, 1, 0, 1, 1,
                                    QtCore.Qt.AlignmentFlag.AlignLeft)

        self.ReporteAnalisisComboBox = self._make_combo("ReporteAnalisisComboBox")
        self.gridLayout_4.addWidget(self.ReporteAnalisisComboBox, 2, 0, 1, 1)

        self.label_8 = self._make_caption("label_8", "Tiempo")
        self.gridLayout_4.addWidget(self.label_8, 3, 0, 1, 1,
                                    QtCore.Qt.AlignmentFlag.AlignLeft)

        self.TiempoAnalisisComboBox = self._make_combo("TiempoAnalisisComboBox")
        self.gridLayout_4.addWidget(self.TiempoAnalisisComboBox, 4, 0, 1, 1)

        self.CalendarioAnalisis = QtWidgets.QCalendarWidget(parent=self.widget_3)
        self.CalendarioAnalisis.setObjectName("CalendarioAnalisis")
        self.CalendarioAnalisis.setStyleSheet(_CALENDAR_QSS)
        self.CalendarioAnalisis.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.gridLayout_4.addWidget(self.CalendarioAnalisis, 5, 0, 1, 1,
                                    QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.BtnTicketAnalisis = self._make_pdf_button(
            "BtnTicketAnalisis", "   Exportar PDF"
        )
        self.gridLayout_4.addWidget(self.BtnTicketAnalisis, 6, 0, 1, 1)

        layout.addLayout(self.gridLayout_4)
        layout.addStretch()
        self.horizontalLayout.addWidget(card)

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        card_pad = max(20, min(32, int(width * 0.02)))
        for card in (self.widget_4, self.widget_5, self.widget_6):
            card.layout().setContentsMargins(card_pad, card_pad, card_pad, card_pad)

        ctrl_h = max(42, min(52, int(height * 0.058)))
        for combo in (self.TipoCajaComboBox, self.TiempoCajaComboBox,
                      self.TipoProductosComboBox, self.ReporteAnalisisComboBox,
                      self.TiempoAnalisisComboBox):
            combo.setMinimumHeight(ctrl_h)

        btn_h = max(44, min(56, int(height * 0.062)))
        for btn in (self.BtnTicketCaja, self.BtnTicketProducto,
                    self.BtnTicketAnalisis):
            btn.setMinimumHeight(btn_h)

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Reportes · Lady Nail"))
        self.LabelReportes.setText(_translate("Form", "Reportes"))
        self.lblReportesSub.setText(
            _translate("Form", "Genera e exporta los informes del negocio")
        )
        self.label.setText(_translate("Form", "Reporte de Caja"))
        self.label_2.setText(_translate("Form", "Caja"))
        self.label_3.setText(_translate("Form", "Tiempo"))
        self.label_5.setText(_translate("Form", "Reporte de Productos"))
        self.label_6.setText(_translate("Form", "Analisis de Venta"))
        self.label_7.setText(_translate("Form", "Ventas"))
        self.label_8.setText(_translate("Form", "Tiempo"))
        self.BtnTicketCaja.setText(_translate("Form", "   Generar PDF"))
        self.BtnTicketProducto.setText(_translate("Form", "   Generar PDF"))
        self.BtnTicketAnalisis.setText(_translate("Form", "   Exportar PDF"))
