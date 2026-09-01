# UI de Respaldo — Diseño Minimalista Profesional
# Limpio, espacial, tipografía elegante, sin elementos decorativos innecesarios

from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta


# ─────────────────────────────────────────────────────────────────
#  Paleta minimalista
# ─────────────────────────────────────────────────────────────────
_PRIMARY     = "#862D6D"
_PRIMARY_H   = "#6E2259"
_PRIMARY_P   = "#551443"
_BG          = "#FAFAFA"
_TEXT        = "#1A1A1A"
_MUTED       = "#6B7280"
_LIGHT_MUTED = "#9CA3AF"
_DIVIDER     = "#E5E7EB"
_CARD_BORDER = "#E5E7EB"

_FONT = "'Segoe UI', Arial, sans-serif"


def _sp_expand(w: QtWidgets.QWidget):
    w.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    return w


class Ui_Respaldo(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setMinimumSize(QtCore.QSize(680, 480))
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
        self.horizontalLayout_2.setContentsMargins(48, 40, 48, 40)
        self.horizontalLayout_2.setSpacing(32)
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

        # Centrado del contenido principal
        self.verticalLayout_2.addStretch(1)
        self.verticalLayout_2.addLayout(self._build_header())
        self.verticalLayout_2.addSpacing(40)
        self.verticalLayout_2.addLayout(self._build_actions())
        self.verticalLayout_2.addStretch(1)
        self.verticalLayout_2.addWidget(self._build_footer())

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # ─────────────────────────────────────────────────────────────
    #  Header minimalista
    # ─────────────────────────────────────────────────────────────
    def _build_header(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Icono pequeño y elegante
        icon_db = qta.icon("fa5s.database", color=_PRIMARY).pixmap(32, 32)
        self.labelIcon = QtWidgets.QLabel(parent=self.ContenidoPage1)
        self.labelIcon.setObjectName("labelIcon")
        self.labelIcon.setPixmap(icon_db)
        self.labelIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelIcon.setStyleSheet("background: transparent;")
        layout.addWidget(self.labelIcon, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Título limpio
        self.LabelRespaldo = QtWidgets.QLabel(parent=self.ContenidoPage1)
        self.LabelRespaldo.setObjectName("LabelRespaldo")
        self.LabelRespaldo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.LabelRespaldo.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: 600;
                color: {_TEXT};
                font-family: {_FONT};
                background: transparent;
                letter-spacing: -0.5px;
            }}
        """)
        layout.addWidget(self.LabelRespaldo)

        # Subtitulo sutil
        self.lblSubtitle = QtWidgets.QLabel(parent=self.ContenidoPage1)
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblSubtitle.setWordWrap(False)
        self.lblSubtitle.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred
        )
        self.lblSubtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {_MUTED};
                font-family: {_FONT};
                background: transparent;
                line-height: 1.5;
            }}
        """)
        layout.addWidget(self.lblSubtitle, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        return layout

    # ─────────────────────────────────────────────────────────────
    #  Botones de acción - minimalistas
    # ─────────────────────────────────────────────────────────────
    def _build_actions(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.BtnRespaldoExportar = self._make_button(
            "BtnRespaldoExportar", "Exportar", "fa5s.download"
        )
        self.BtnRespaldoImportar = self._make_button(
            "BtnRespaldoImportar", "Importar", "fa5s.upload"
        )

        layout.addWidget(self.BtnRespaldoExportar)
        layout.addWidget(self.BtnRespaldoImportar)

        return layout

    def _make_button(self, name, text, icon_name):
        icon = qta.icon(icon_name, color="#FFFFFF").pixmap(16, 16)
        btn = QtWidgets.QPushButton(parent=self.ContenidoPage1)
        btn.setObjectName(name)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setMinimumHeight(44)
        btn.setMinimumWidth(160)
        btn.setIcon(QtGui.QIcon(icon))
        btn.setIconSize(QtCore.QSize(16, 16))
        btn.setText(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                font-family: {_FONT};
                padding: 8px 24px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {_PRIMARY_H};
            }}
            QPushButton:pressed {{
                background-color: {_PRIMARY_P};
            }}
            QPushButton:disabled {{
                background-color: #D1D5DB;
                color: #9CA3AF;
            }}
        """)
        return btn

    # ─────────────────────────────────────────────────────────────
    #  Footer con nota
    # ─────────────────────────────────────────────────────────────
    def _build_footer(self):
        widget = QtWidgets.QWidget(parent=self.ContenidoPage1)
        widget.setObjectName("footerWidget")
        widget.setStyleSheet("background: transparent;")

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Icono de info sutil
        icon_info = qta.icon("fa5s.info-circle", color=_LIGHT_MUTED).pixmap(14, 14)
        lbl_icon = QtWidgets.QLabel(parent=widget)
        lbl_icon.setObjectName("lblInfoIcon")
        lbl_icon.setPixmap(icon_info)
        lbl_icon.setStyleSheet("background: transparent;")
        layout.addWidget(lbl_icon)

        self.lblNote = QtWidgets.QLabel(parent=widget)
        self.lblNote.setObjectName("lblNote")
        self.lblNote.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {_LIGHT_MUTED};
                font-family: {_FONT};
                background: transparent;
            }}
        """)
        layout.addWidget(self.lblNote)

        return widget

    # ─────────────────────────────────────────────────────────────
    #  Responsividad dinámica
    # ─────────────────────────────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        h_margin = max(32, min(80, int(width * 0.06)))
        v_margin = max(24, min(56, int(height * 0.06)))
        self.horizontalLayout_2.setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        btn_h = max(40, min(48, int(height * 0.055)))
        for btn in (self.BtnRespaldoExportar, self.BtnRespaldoImportar):
            btn.setMinimumHeight(btn_h)

    # ─────────────────────────────────────────────────────────────
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Respaldo"))
        self.LabelRespaldo.setText(_translate("Form", "Respaldo"))
        self.lblSubtitle.setText(
            _translate("Form",
                       "Protege la información de tu negocio con copias de seguridad")
        )
        self.BtnRespaldoExportar.setText(
            _translate("Form", "Exportar")
        )
        self.BtnRespaldoImportar.setText(
            _translate("Form", "Importar")
        )
        self.lblNote.setText(
            _translate("Form",
                       "Respaldos automáticos activados")
        )
