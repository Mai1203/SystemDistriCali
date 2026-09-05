# UI de Reportes — Rediseño Completo siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry #862D6D, tarjetas flotantes con sombra, QScrollArea responsivo, SVG, Gráficas Mensuales)

from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


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
_BADGE_BG    = "#F9EEF6"

_FONT = "'Segoe UI', Arial, sans-serif"

_CTRL_MIN_H = 40
_BTN_MIN_H  = 38


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
        border-radius: 8px;
        padding: 0px 12px;
        font-size: 13px;
        color: {_TEXT};
        font-family: {_FONT};
    }}
    QComboBox:focus, QComboBox:hover {{
        border: 2px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        color: {_TEXT};
        selection-background-color: {_PRIMARY};
        selection-color: #FFFFFF;
        border-radius: 8px;
        padding: 4px;
        font-family: {_FONT};
    }}
"""

_PRIMARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 0px 12px;
        height: 32px;
    }}
    QPushButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QPushButton:pressed {{
        background-color: {_PRIMARY_P};
    }}
    QPushButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_TITLE_QSS = f"""
    QLabel {{
        font-size: 16px;
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

_INFO_BADGE_QSS = f"""
    QLabel {{
        font-size: 11px;
        font-weight: 600;
        color: {_PRIMARY};
        background-color: {_BADGE_BG};
        border: 1px solid {_BORDER_H};
        border-radius: 6px;
        padding: 4px 8px;
        font-family: {_FONT};
    }}
"""

_CALENDAR_QSS = f"""
    QCalendarWidget {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 10px;
        font-family: {_FONT};
        color: {_TEXT};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {_PRIMARY};
        border-radius: 9px 9px 0 0;
        padding: 2px;
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {_CARD_BG};
        color: {_TEXT};
        selection-background-color: {_PRIMARY};
        selection-color: #FFFFFF;
        border-radius: 4px;
        outline: none;
    }}
    QCalendarWidget QToolButton {{
        color: #FFFFFF;
        background: transparent;
        font-family: {_FONT};
        font-weight: 600;
        border-radius: 4px;
        padding: 2px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QCalendarWidget QMenu {{
        background-color: {_CARD_BG};
        color: {_TEXT};
        border: 1px solid {_DIVIDER};
    }}
"""


class ChartCanvas(FigureCanvasQTAgg):
    """Canvas interactivo de Matplotlib para gráficas mensuales estilizadas."""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4.0, 2.8), dpi=100, facecolor="#FFFFFF")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumHeight(210)
        self.setMaximumHeight(260)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )


def _card_shadow(widget: QtWidgets.QWidget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setXOffset(0)
    shadow.setYOffset(6)
    shadow.setColor(QtGui.QColor(100, 30, 80, 25))
    widget.setGraphicsEffect(shadow)


class Ui_Reportes(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(850, 560))
        Form.setStyleSheet(f"background-color: {_BG};")

        self.main_layout = QtWidgets.QVBoxLayout(Form)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName("main_layout")

        # ── Contenedor Scrollable Responsivo ────────────────────────
        self.scrollArea = QtWidgets.QScrollArea(parent=Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scrollArea.setStyleSheet(f"""
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
                background: {_BORDER_H};
                border-radius: 4px;
                min-height: 32px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {_PRIMARY};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {_PRIMARY_H};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {_DIVIDER};
                height: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {_BORDER_H};
                border-radius: 4px;
                min-width: 32px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {_PRIMARY};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background: {_PRIMARY_H};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.Contenedor = QtWidgets.QWidget()
        self.Contenedor.setObjectName("Contenedor")
        self.Contenedor.setStyleSheet("background-color: transparent;")
        _sp_expand(self.Contenedor)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.Contenedor)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(18, 18, 18, 18)
        self.horizontalLayout_2.setSpacing(18)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout.addLayout(self.horizontalLayout_2)

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
        _sp_hfix(self.widget_3)

        self.cards_grid = QtWidgets.QGridLayout(self.widget_3)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setHorizontalSpacing(16)
        self.cards_grid.setVerticalSpacing(16)
        self.cards_grid.setColumnStretch(0, 1)  # Columna 1: Reporte de Caja
        self.cards_grid.setColumnStretch(1, 1)  # Columna 2: Análisis Financiero
        self.cards_grid.setColumnStretch(2, 1)  # Columna 3: Gráficas Mensuales

        self._build_card_caja()
        self._build_card_productos()
        self._build_card_analisis()
        self._build_card_graficas()

        # Disposición en 3 Columnas arriba + Productos abajo:
        # Fila 0 (3 Columnas principales):
        self.cards_grid.addWidget(self.widget_4, 0, 0, 1, 1)         # Col 0: Caja
        self.cards_grid.addWidget(self.widget_6, 0, 1, 1, 1)         # Col 1: Análisis
        self.cards_grid.addWidget(self.widget_graficas, 0, 2, 1, 1)  # Col 2: Gráficas

        # Fila 1 (Abajo): Reporte de Productos abarcando las 3 columnas
        self.cards_grid.addWidget(self.widget_5, 1, 0, 1, 3)

        self.verticalLayout_3.addWidget(self.widget_3, 0)
        self.verticalLayout_3.addStretch(1)

        self.verticalLayout_2.addWidget(self.widget, 0)
        self.verticalLayout_2.addStretch(1)

        self.scrollArea.setWidget(self.Contenedor)
        self.main_layout.addWidget(self.scrollArea)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ─────────────────────────────────────────────────────────────
    #  Encabezado Hero
    # ─────────────────────────────────────────────────────────────
    def _build_header(self):
        self.widget_2 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet(f"""
            QWidget#widget_2 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 14px;
            }}
        """)
        self.widget_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.widget_2)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(18, 12, 18, 12)
        self.horizontalLayout_3.setSpacing(12)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        badge = QtWidgets.QLabel(parent=self.widget_2)
        badge.setFixedSize(38, 38)
        badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pix = QtGui.QPixmap("assets/iconos/badge_shield_user.svg")
        if not pix.isNull():
            badge.setPixmap(
                pix.scaled(38, 38,
                           QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        self.horizontalLayout_3.addWidget(badge)

        titleCol = QtWidgets.QVBoxLayout()
        titleCol.setSpacing(2)
        self.LabelReportes = QtWidgets.QLabel(parent=self.widget_2)
        self.LabelReportes.setObjectName("LabelReportes")
        self.LabelReportes.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {_PRIMARY};"
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
    #  Helpers de Tarjeta
    # ─────────────────────────────────────────────────────────────
    def _make_card(self, name):
        card = QtWidgets.QWidget(parent=self.widget_3)
        card.setObjectName(name)
        setattr(self, name, card)
        card.setStyleSheet(f"""
            QWidget#{name} {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 14px;
            }}
        """)
        card.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(card)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
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
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        btn.setFixedHeight(32)
        btn.setStyleSheet(_PRIMARY_BTN_QSS)
        icon_pdf = qta.icon("fa5s.file-pdf", color="#FFFFFF").pixmap(14, 14)
        btn.setIcon(QtGui.QIcon(icon_pdf))
        btn.setIconSize(QtCore.QSize(14, 14))
        btn.setText(text)
        return btn

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Reporte de Caja
    # ─────────────────────────────────────────────────────────────
    def _build_card_caja(self):
        card, layout = self._make_card("widget_4")

        # Header de tarjeta con ícono
        h_box = QtWidgets.QHBoxLayout()
        h_box.setSpacing(8)
        icon_lbl = QtWidgets.QLabel(parent=card)
        icon_lbl.setPixmap(qta.icon("fa5s.cash-register", color=_PRIMARY).pixmap(20, 20))
        h_box.addWidget(icon_lbl)
        self.label = self._make_title("label", "Reporte de Caja")
        h_box.addWidget(self.label)
        h_box.addStretch()
        layout.addLayout(h_box)

        # Opciones
        opts_layout = QtWidgets.QGridLayout()
        opts_layout.setSpacing(8)

        self.label_2 = self._make_caption("label_2", "Tipo de Movimiento")
        opts_layout.addWidget(self.label_2, 0, 0)
        self.TipoCajaComboBox = self._make_combo("TipoCajaComboBox")
        opts_layout.addWidget(self.TipoCajaComboBox, 1, 0)

        self.label_3 = self._make_caption("label_3", "Modalidad de Tiempo")
        opts_layout.addWidget(self.label_3, 0, 1)
        self.TiempoCajaComboBox = self._make_combo("TiempoCajaComboBox")
        opts_layout.addWidget(self.TiempoCajaComboBox, 1, 1)

        layout.addLayout(opts_layout)

        # Indicador visual de fecha seleccionada
        self.lblInfoFechaCaja = QtWidgets.QLabel("Fecha seleccionada: Haz clic en el calendario", parent=card)
        self.lblInfoFechaCaja.setObjectName("lblInfoFechaCaja")
        self.lblInfoFechaCaja.setStyleSheet(_INFO_BADGE_QSS)
        layout.addWidget(self.lblInfoFechaCaja)

        # Calendario
        self.CalendarioCaja = QtWidgets.QCalendarWidget(parent=card)
        self.CalendarioCaja.setObjectName("CalendarioCaja")
        self.CalendarioCaja.setStyleSheet(_CALENDAR_QSS)
        self.CalendarioCaja.setMinimumHeight(200)
        self.CalendarioCaja.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        layout.addWidget(self.CalendarioCaja)

        # Botón PDF en contenedor alineado a la derecha
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        self.BtnTicketCaja = self._make_pdf_button(
            "BtnTicketCaja", "  Generar PDF de Caja"
        )
        btn_box.addWidget(self.BtnTicketCaja)
        layout.addLayout(btn_box)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Reporte de Productos
    # ─────────────────────────────────────────────────────────────
    def _build_card_productos(self):
        card, layout = self._make_card("widget_5")

        h_main = QtWidgets.QHBoxLayout()
        h_main.setSpacing(16)

        # Columna izquierda: Ícono, Título y Subtítulo
        v_info = QtWidgets.QVBoxLayout()
        v_info.setSpacing(2)

        h_title = QtWidgets.QHBoxLayout()
        h_title.setSpacing(8)
        icon_lbl = QtWidgets.QLabel(parent=card)
        icon_lbl.setPixmap(qta.icon("fa5s.boxes", color=_PRIMARY).pixmap(20, 20))
        h_title.addWidget(icon_lbl)
        self.label_5 = self._make_title("label_5", "Reporte de Productos e Inventario")
        h_title.addWidget(self.label_5)
        h_title.addStretch()
        v_info.addLayout(h_title)

        sub_lbl = self._make_subtitle("lblProdSub", "Filtra y exporta inventario por stock, ventas o estado")
        v_info.addWidget(sub_lbl)

        h_main.addLayout(v_info, stretch=1)

        # Columna derecha: Controles (ComboBox + Botón PDF)
        h_ctrls = QtWidgets.QHBoxLayout()
        h_ctrls.setSpacing(12)

        self.TipoProductosComboBox = self._make_combo("TipoProductosComboBox")
        self.TipoProductosComboBox.setMinimumWidth(260)
        h_ctrls.addWidget(self.TipoProductosComboBox)

        self.BtnTicketProducto = self._make_pdf_button(
            "BtnTicketProducto", "  Generar PDF de Productos"
        )
        h_ctrls.addWidget(self.BtnTicketProducto)

        h_main.addLayout(h_ctrls, stretch=0)
        layout.addLayout(h_main)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Análisis de Venta
    # ─────────────────────────────────────────────────────────────
    def _build_card_analisis(self):
        card, layout = self._make_card("widget_6")

        # Header de tarjeta con ícono
        h_box = QtWidgets.QHBoxLayout()
        h_box.setSpacing(8)
        icon_lbl = QtWidgets.QLabel(parent=card)
        icon_lbl.setPixmap(qta.icon("fa5s.chart-line", color=_PRIMARY).pixmap(20, 20))
        h_box.addWidget(icon_lbl)
        self.label_6 = self._make_title("label_6", "Análisis Financiero & Crédito")
        h_box.addWidget(self.label_6)
        h_box.addStretch()
        layout.addLayout(h_box)

        # Opciones
        opts_layout = QtWidgets.QGridLayout()
        opts_layout.setSpacing(8)

        self.label_7 = self._make_caption("label_7", "Tipo de Análisis")
        opts_layout.addWidget(self.label_7, 0, 0)
        self.ReporteAnalisisComboBox = self._make_combo("ReporteAnalisisComboBox")
        opts_layout.addWidget(self.ReporteAnalisisComboBox, 1, 0)

        self.label_8 = self._make_caption("label_8", "Modalidad de Tiempo")
        opts_layout.addWidget(self.label_8, 0, 1)
        self.TiempoAnalisisComboBox = self._make_combo("TiempoAnalisisComboBox")
        opts_layout.addWidget(self.TiempoAnalisisComboBox, 1, 1)

        layout.addLayout(opts_layout)

        # Indicador visual de fecha seleccionada
        self.lblInfoFechaAnalisis = QtWidgets.QLabel("Fecha seleccionada: Haz clic en el calendario", parent=card)
        self.lblInfoFechaAnalisis.setObjectName("lblInfoFechaAnalisis")
        self.lblInfoFechaAnalisis.setStyleSheet(_INFO_BADGE_QSS)
        layout.addWidget(self.lblInfoFechaAnalisis)

        # Calendario
        self.CalendarioAnalisis = QtWidgets.QCalendarWidget(parent=card)
        self.CalendarioAnalisis.setObjectName("CalendarioAnalisis")
        self.CalendarioAnalisis.setStyleSheet(_CALENDAR_QSS)
        self.CalendarioAnalisis.setMinimumHeight(200)
        self.CalendarioAnalisis.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        layout.addWidget(self.CalendarioAnalisis)

        # Botón PDF en contenedor alineado a la derecha
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        self.BtnTicketAnalisis = self._make_pdf_button(
            "BtnTicketAnalisis", "  Exportar PDF Financiero"
        )
        btn_box.addWidget(self.BtnTicketAnalisis)
        layout.addLayout(btn_box)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta: Gráficas Mensuales
    # ─────────────────────────────────────────────────────────────
    def _build_card_graficas(self):
        card, layout = self._make_card("widget_graficas")

        # Header de tarjeta con ícono
        h_box = QtWidgets.QHBoxLayout()
        h_box.setSpacing(8)
        icon_lbl = QtWidgets.QLabel(parent=card)
        icon_lbl.setPixmap(qta.icon("fa5s.chart-bar", color=_PRIMARY).pixmap(20, 20))
        h_box.addWidget(icon_lbl)
        lbl_title = self._make_title("lblGraficasTitle", "Estadísticas & Tendencias Mensuales del Negocio")
        h_box.addWidget(lbl_title)
        h_box.addStretch()
        layout.addLayout(h_box)

        sub_lbl = self._make_subtitle("lblGraficasSub", "Comparativa de ingresos vs egresos y distribución de métodos de pago")
        layout.addWidget(sub_lbl)

        # Matplotlib canvas widget
        self.canvas_graficas = ChartCanvas(parent=card)
        layout.addWidget(self.canvas_graficas)

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(12, min(32, int(width * 0.03)))
        v_margin = max(12, min(32, int(height * 0.03)))
        if hasattr(self, "horizontalLayout_2") and self.horizontalLayout_2:
            self.horizontalLayout_2.setContentsMargins(
                h_margin, v_margin, h_margin, v_margin
            )

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Reportes · Distri Magik"))
        self.LabelReportes.setText(_translate("Form", "Panel de Reportes & Analítica"))
        self.lblReportesSub.setText(
            _translate("Form", "Genera, analiza y exporta los informes de caja, productos y finanzas del negocio")
        )
        self.label.setText(_translate("Form", "Reporte de Caja"))
        self.label_2.setText(_translate("Form", "Tipo de Movimiento"))
        self.label_3.setText(_translate("Form", "Modalidad de Tiempo"))
        self.label_5.setText(_translate("Form", "Reporte de Productos e Inventario"))
        self.label_6.setText(_translate("Form", "Análisis Financiero & Crédito"))
        self.label_7.setText(_translate("Form", "Tipo de Análisis"))
        self.label_8.setText(_translate("Form", "Modalidad de Tiempo"))
        self.BtnTicketCaja.setText(_translate("Form", "  Generar PDF de Caja"))
        self.BtnTicketProducto.setText(_translate("Form", "  Generar PDF de Productos"))
        self.BtnTicketAnalisis.setText(_translate("Form", "  Exportar PDF Financiero"))


