# UI de Respaldo — Escrita a mano siguiendo el Sistema de Diseño Lady Nail
# (paleta plum/berry, tarjeta centrada con sombra, botones primarios, SVG, responsiva)
#
# Reglas aplicadas del design_system_login.txt:
#  · Colores semánticos con prefijo _
#  · Tarjeta flotante (border-radius + QGraphicsDropShadowEffect)
#  · Botones primarios _PRIMARY (hover/pressed/disabled) con íconos SVG
#  · Ícono de base de datos (fa5s.database) en badge plum
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

_BTN_MIN_H = 54


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


_PRIMARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 600;
        font-family: {_FONT};
        padding: 12px 18px;
        letter-spacing: 0.4px;
        min-height: {_BTN_MIN_H}px;
    }}
    QPushButton:hover {{
        background-color: {_PRIMARY_H};
    }}
    QPushButton:pressed {{
        background-color: {_PRIMARY_P};
        padding-top: 14px;
    }}
    QPushButton:disabled {{
        background-color: #C4A8BF;
        color: #F0E8EF;
    }}
"""

_TITLE_QSS = f"""
    QLabel {{
        font-size: 30px;
        font-weight: 700;
        color: {_PRIMARY};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_SUBTITLE_QSS = f"""
    QLabel {{
        font-size: 13px;
        color: {_MUTED};
        font-family: {_FONT};
        background: transparent;
    }}
"""

_NOTE_QSS = f"""
    QLabel {{
        font-size: 11px;
        color: {_MUTED};
        font-family: {_FONT};
        background: transparent;
    }}
"""


def _card_shadow(widget: QtWidgets.QWidget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(40)
    shadow.setXOffset(0)
    shadow.setYOffset(12)
    shadow.setColor(QtGui.QColor(100, 30, 80, 45))
    widget.setGraphicsEffect(shadow)


class Ui_Respaldo(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(720, 560))
        Form.setStyleSheet(f"background-color: {_BG};")

        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.Contenedor = QtWidgets.QWidget(parent=Form)
        self.Contenedor.setObjectName("Contenedor")
        self.Contenedor.setStyleSheet("background-color: transparent;")
        _sp_expand(self.Contenedor)
        self.horizontalLayout.addWidget(self.Contenedor)

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
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # Centrado horizontal de la tarjeta
        hCenter = QtWidgets.QHBoxLayout()
        hCenter.setContentsMargins(0, 0, 0, 0)
        hCenter.setSpacing(0)
        hCenter.addStretch(1)
        hCenter.addWidget(self._build_card())
        hCenter.addStretch(1)
        self.verticalLayout_2.addLayout(hCenter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ─────────────────────────────────────────────────────────────
    #  Tarjeta principal
    # ─────────────────────────────────────────────────────────────
    def _build_card(self):
        # Íconos creados en tiempo de ejecución (requieren QApplication activa)
        icon_download = qta.icon("fa5s.download", color="#FFFFFF").pixmap(22, 22)
        icon_upload = qta.icon("fa5s.upload", color="#FFFFFF").pixmap(22, 22)
        icon_db = qta.icon("fa5s.database", color=_PRIMARY).pixmap(64, 64)

        self.widget_2 = QtWidgets.QWidget(parent=self.ContenidoPage1)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setStyleSheet(f"""
            QWidget#widget_2 {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 22px;
            }}
        """)
        self.widget_2.setMinimumWidth(360)
        self.widget_2.setMaximumWidth(560)
        self.widget_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        _card_shadow(self.widget_2)

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setContentsMargins(36, 36, 36, 36)
        self.verticalLayout_4.setSpacing(18)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        # Cabecera: badge de base de datos + título + subtítulo
        self.widget_3 = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_3.setObjectName("widget_3")
        self.widget_3.setStyleSheet("background: transparent;")
        header = QtWidgets.QHBoxLayout(self.widget_3)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(16)
        header.setObjectName("verticalLayout_5")

        # Badge con ícono de base de datos
        self.widget = QtWidgets.QWidget(parent=self.widget_3)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet(f"""
            QWidget#widget {{
                background-color: #FBEFF7;
                border: 1px solid {_DIVIDER};
                border-radius: 16px;
            }}
        """)
        self.widget.setFixedSize(84, 84)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.label = QtWidgets.QLabel(parent=self.widget)
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(icon_db)
        self.label.setScaledContents(False)
        self.verticalLayout_3.addWidget(self.label)
        header.addWidget(self.widget)

        titleCol = QtWidgets.QVBoxLayout()
        titleCol.setSpacing(4)
        self.LabelRespaldo = QtWidgets.QLabel(parent=self.widget_3)
        self.LabelRespaldo.setObjectName("LabelRespaldo")
        self.LabelRespaldo.setStyleSheet(_TITLE_QSS)
        titleCol.addWidget(self.LabelRespaldo)

        self.lblSubtitle = QtWidgets.QLabel(parent=self.widget_3)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setStyleSheet(_SUBTITLE_QSS)
        self.lblSubtitle.setWordWrap(True)
        titleCol.addWidget(self.lblSubtitle)
        header.addLayout(titleCol)

        self.verticalLayout_4.addWidget(self.widget_3)

        # Separador
        line = QtWidgets.QFrame(parent=self.widget_2)
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setStyleSheet(
            f"color: {_DIVIDER}; background-color: {_DIVIDER}; max-height: 1px;"
        )
        self.verticalLayout_4.addWidget(line)

        # Botones
        self.widget_4 = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setStyleSheet("background: transparent;")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(16)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.BtnRespaldoExportar = self._make_button(
            "BtnRespaldoExportar", "Respaldar Todos Los Datos", icon_download
        )
        self.BtnRespaldoImportar = self._make_button(
            "BtnRespaldoImportar", "Cargar Todos los datos", icon_upload
        )
        self.horizontalLayout_3.addWidget(self.BtnRespaldoExportar)
        self.horizontalLayout_3.addWidget(self.BtnRespaldoImportar)
        self.verticalLayout_4.addWidget(self.widget_4)

        # Nota de respaldo automático
        self.lblNote = QtWidgets.QLabel(parent=self.widget_2)
        self.lblNote.setObjectName("lblNote")
        self.lblNote.setStyleSheet(_NOTE_QSS)
        self.lblNote.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblNote.setWordWrap(True)
        self.verticalLayout_4.addWidget(self.lblNote)

        return self.widget_2

    def _make_button(self, name, text, icon_pix):
        btn = QtWidgets.QPushButton(parent=self.widget_2)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setMinimumHeight(_BTN_MIN_H)
        btn.setStyleSheet(_PRIMARY_BTN_QSS)
        btn.setIcon(QtGui.QIcon(icon_pix))
        btn.setIconSize(QtCore.QSize(22, 22))
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

        card_pad = max(24, min(40, int(min(width, height) * 0.04)))
        self.verticalLayout_4.setContentsMargins(
            card_pad, card_pad, card_pad, card_pad
        )

        btn_h = max(48, min(58, int(height * 0.062)))
        for btn in (self.BtnRespaldoExportar, self.BtnRespaldoImportar):
            btn.setMinimumHeight(btn_h)

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Respaldo · Lady Nail"))
        self.LabelRespaldo.setText(_translate("Form", "Respaldo"))
        self.lblSubtitle.setText(
            _translate("Form",
                       "Copia de seguridad y restauración de la base de datos")
        )
        self.BtnRespaldoExportar.setText(
            _translate("Form", "Respaldar Todos Los Datos")
        )
        self.BtnRespaldoImportar.setText(
            _translate("Form", "Cargar Todos los datos")
        )
        self.lblNote.setText(
            _translate("Form",
                       "El sistema genera respaldos automáticos en el escritorio.")
        )
