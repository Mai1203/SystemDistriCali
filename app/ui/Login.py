from PyQt6 import QtCore, QtGui, QtWidgets
import math


# ─────────────────────────────────────────────────────────────────
#  Responsive Login UI  –  Lady Nail SHOP
#  Panel izquierdo: pintado con QPainter (vectorial, sin píxeles)
#  Reglas UX/UI:
#   · Sin tamaños fijos px que rompan el layout
#   · Panel hero vectorial: gradiente + formas decorativas
#   · Panel desaparece cuando el ancho <750 px
#   · Inputs y botón escalan con el viewport (resizeEvent)
#   · Mínimo táctil 44 px para todos los controles interactivos
#   · Contraste WCAG AA  ·  Tab order declarativo
# ─────────────────────────────────────────────────────────────────

_PRIMARY   = "#862D6D"
_PRIMARY_H = "#6E2259"
_PRIMARY_P = "#551443"
_BG        = "#F5F0F4"
_CARD_BG   = "#FFFFFF"
_BORDER    = "#D8C8D5"
_TEXT      = "#201A24"
_MUTED     = "#7B737F"
_FOCUS_BG  = "#FFFAFE"
_DIVIDER   = "#E2DAE1"

_INPUT_MIN_H = 44
_BTN_MIN_H   = 46


def _sp(w: QtWidgets.QWidget):
    sp = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    w.setSizePolicy(sp)
    return sp


def _sp_hfix(w: QtWidgets.QWidget):
    sp = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    w.setSizePolicy(sp)
    return sp


_INPUT_QSS = f"""
    QLineEdit {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 0px 10px 0px 38px;
        font-size: 13px;
        color: {_TEXT};
        font-family: 'Segoe UI', Arial, sans-serif;
        selection-background-color: {_PRIMARY};
    }}
    QLineEdit:focus {{
        border: 2px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QLineEdit:hover {{
        border-color: #A97099;
    }}
"""

_INPUT_PASS_QSS = f"""
    QLineEdit {{
        background-color: {_CARD_BG};
        border: 1.5px solid {_BORDER};
        border-radius: 10px;
        padding: 0px 38px 0px 38px;
        font-size: 13px;
        color: {_TEXT};
        font-family: 'Segoe UI', Arial, sans-serif;
        selection-background-color: {_PRIMARY};
    }}
    QLineEdit:focus {{
        border: 2px solid {_PRIMARY};
        background-color: {_FOCUS_BG};
    }}
    QLineEdit:hover {{
        border-color: #A97099;
    }}
"""


# ══════════════════════════════════════════════════════════════════
#  Widget decorativo vectorial (panel izquierdo)
#  Usa QPainter → nunca pixela, se ve perfecto en cualquier DPI
# ══════════════════════════════════════════════════════════════════
class _HeroPanel(QtWidgets.QWidget):
    """
    Panel izquierdo pintado 100% con QPainter.
    · Gradiente lineal diagonal profundo (plum → berry → magenta oscuro)
    · Círculos decorativos translúcidos con bordes suaves
    · Texto de marca centrado con sombra
    · Patrón de puntos sutil (dot-grid) para textura premium
    · Todo vectorial → sin píxeles en ningún tamaño
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("heroPanel")
        _sp(self)
        self.setMinimumWidth(280)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        rect = QtCore.QRectF(0, 0, w, h)

        # ── 1. Gradiente de fondo diagonal ────────────────────────
        grad = QtGui.QLinearGradient(0, 0, w * 0.6, h)
        grad.setColorAt(0.00, QtGui.QColor("#3D0A30"))   # muy oscuro / índigo-plum
        grad.setColorAt(0.35, QtGui.QColor("#6B1853"))   # plum medio
        grad.setColorAt(0.70, QtGui.QColor("#862D6D"))   # plum Lady Nail
        grad.setColorAt(1.00, QtGui.QColor("#A83880"))   # berry claro
        painter.fillRect(rect, grad)

        # ── 2. Capa overlay suave para profundidad ────────────────
        overlay = QtGui.QLinearGradient(w, 0, 0, h)
        overlay.setColorAt(0.0, QtGui.QColor(255, 255, 255, 12))
        overlay.setColorAt(1.0, QtGui.QColor(0, 0, 0, 30))
        painter.fillRect(rect, overlay)

        # ── 3. Círculos decorativos ────────────────────────────────
        circles = [
            # (cx_frac, cy_frac, r_frac, alpha)
            (0.85, 0.08, 0.32, 30),   # grande arriba-derecha
            (0.10, 0.80, 0.28, 25),   # grande abajo-izquierda
            (0.70, 0.55, 0.18, 20),   # mediano centro
            (0.20, 0.18, 0.14, 22),   # pequeño arriba-izquierda
            (0.90, 0.75, 0.20, 18),   # mediano abajo-derecha
            (0.45, 0.90, 0.10, 28),   # pequeño abajo-centro
        ]
        for (cx, cy, r, a) in circles:
            cx_px = cx * w
            cy_px = cy * h
            r_px  = r * min(w, h)
            # borde blanco translúcido
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255, a + 15))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(QtGui.QColor(255, 255, 255, a // 2))
            painter.drawEllipse(
                QtCore.QPointF(cx_px, cy_px), r_px, r_px
            )

        # ── 4. Patrón de puntos (dot-grid) ─── textura premium ─────
        dot_spacing = max(20, min(32, int(min(w, h) * 0.04)))
        dot_r = max(1.2, dot_spacing * 0.06)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(255, 255, 255, 18))
        cols = int(w / dot_spacing) + 1
        rows = int(h / dot_spacing) + 1
        for row in range(rows):
            for col in range(cols):
                ox = (row % 2) * (dot_spacing / 2)  # offset filas pares
                x = col * dot_spacing + ox
                y = row * dot_spacing
                painter.drawEllipse(
                    QtCore.QPointF(x, y), dot_r, dot_r
                )

        # ── 5. Línea decorativa horizontal centrada ────────────────
        line_y = h * 0.52
        line_w = w * 0.55
        line_x = (w - line_w) / 2
        line_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 60))
        line_pen.setWidth(1)
        painter.setPen(line_pen)
        painter.drawLine(
            QtCore.QPointF(line_x, line_y),
            QtCore.QPointF(line_x + line_w, line_y),
        )

        # ── 6. Texto de marca ──────────────────────────────────────
        # Nombre de la marca grande
        font_title = QtGui.QFont("Segoe UI", 1)
        font_title.setBold(True)
        font_title.setLetterSpacing(
            QtGui.QFont.SpacingType.AbsoluteSpacing, 1.5
        )
        title_size = max(22, min(36, int(w * 0.09)))
        font_title.setPixelSize(title_size)
        painter.setFont(font_title)

        # Sombra del texto
        painter.setPen(QtGui.QColor(0, 0, 0, 60))
        title_rect = QtCore.QRectF(2, h * 0.37 + 2, w, h * 0.12)
        painter.drawText(
            title_rect,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
            "Distri Magik"
        )
        # Texto real blanco
        painter.setPen(QtGui.QColor(255, 255, 255, 240))
        title_rect2 = QtCore.QRectF(0, h * 0.37, w, h * 0.12)
        painter.drawText(
            title_rect2,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
            "Distri Magik"
        )

        # "SHOP" espaciado
        font_sub = QtGui.QFont("Segoe UI", 1)
        font_sub.setLetterSpacing(
            QtGui.QFont.SpacingType.AbsoluteSpacing, 6.0
        )
        sub_size = max(9, min(14, int(w * 0.035)))
        font_sub.setPixelSize(sub_size)
        painter.setFont(font_sub)
        painter.setPen(QtGui.QColor(255, 200, 235, 200))
        sub_rect = QtCore.QRectF(0, h * 0.49, w, h * 0.07)
        painter.drawText(
            sub_rect,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
            "S H O P"
        )

        # "SISTEMA DE INVENTARIO" pequeño
        font_tag = QtGui.QFont("Segoe UI", 1)
        font_tag.setLetterSpacing(
            QtGui.QFont.SpacingType.AbsoluteSpacing, 2.5
        )
        tag_size = max(7, min(10, int(w * 0.022)))
        font_tag.setPixelSize(tag_size)
        painter.setFont(font_tag)
        painter.setPen(QtGui.QColor(255, 255, 255, 130))
        tag_rect = QtCore.QRectF(0, h * 0.57, w, h * 0.06)
        painter.drawText(
            tag_rect,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
            "SISTEMA DE INVENTARIO"
        )

        # ── 7. Cita motivacional (abajo) ──────────────────────────
        font_quote = QtGui.QFont("Segoe UI", 1)
        font_quote.setItalic(True)
        quote_size = max(8, min(12, int(w * 0.028)))
        font_quote.setPixelSize(quote_size)
        painter.setFont(font_quote)
        painter.setPen(QtGui.QColor(255, 255, 255, 100))
        quote_rect = QtCore.QRectF(w * 0.10, h * 0.82, w * 0.80, h * 0.12)
        painter.drawText(
            quote_rect,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter
            | QtCore.Qt.TextFlag.TextWordWrap,
            "Belleza que inspira,\norganización que transforma."
        )

        painter.end()


# ══════════════════════════════════════════════════════════════════
#  UI principal
# ══════════════════════════════════════════════════════════════════
class Ui_Login(object):

    def setupUi(self, CONTENEDEDOR1):
        CONTENEDEDOR1.setObjectName("CONTENEDEDOR1")
        CONTENEDEDOR1.setMinimumSize(QtCore.QSize(480, 520))
        CONTENEDEDOR1.setStyleSheet(f"background-color: {_BG};")

        self.rootLayout = QtWidgets.QHBoxLayout(CONTENEDEDOR1)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName("rootLayout")

        # Panel izquierdo vectorial
        self.heroPanel = _HeroPanel(parent=CONTENEDEDOR1)
        self.rootLayout.addWidget(self.heroPanel)

        # Panel derecho con formulario
        self._build_form_panel(CONTENEDEDOR1)

        # Proporción 42/58 inicial
        self.rootLayout.setStretch(0, 42)
        self.rootLayout.setStretch(1, 58)

        self.retranslateUi(CONTENEDEDOR1)
        self._set_tab_order(CONTENEDEDOR1)
        QtCore.QMetaObject.connectSlotsByName(CONTENEDEDOR1)

    # ── Panel derecho ──────────────────────────────────────────────
    def _build_form_panel(self, parent):
        self.formPanel = QtWidgets.QWidget(parent=parent)
        self.formPanel.setObjectName("formPanel")
        self.formPanel.setStyleSheet(f"background-color: {_BG};")
        _sp(self.formPanel)

        outerV = QtWidgets.QVBoxLayout(self.formPanel)
        outerV.setContentsMargins(32, 32, 32, 32)
        outerV.setSpacing(0)
        outerV.addStretch(1)

        outerH = QtWidgets.QHBoxLayout()
        outerH.setSpacing(0)
        outerH.addStretch(1)
        outerH.addWidget(self._build_card(self.formPanel))
        outerH.addStretch(1)

        outerV.addLayout(outerH)
        outerV.addStretch(1)

        self.rootLayout.addWidget(self.formPanel)

    # ── Card ───────────────────────────────────────────────────────
    def _build_card(self, parent) -> QtWidgets.QWidget:
        self.cardWidget = QtWidgets.QWidget(parent=parent)
        self.cardWidget.setObjectName("cardWidget")

        sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.cardWidget.setSizePolicy(sp)
        self.cardWidget.setMinimumWidth(340)
        self.cardWidget.setMaximumWidth(480)

        self.cardWidget.setStyleSheet(f"""
            QWidget#cardWidget {{
                background-color: {_CARD_BG};
                border-radius: 22px;
                border: 1px solid #EAE0E8;
            }}
        """)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self.cardWidget)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QtGui.QColor(100, 30, 80, 45))
        self.cardWidget.setGraphicsEffect(shadow)

        self.cardLayout = QtWidgets.QVBoxLayout(self.cardWidget)
        self.cardLayout.setContentsMargins(36, 32, 36, 32)
        self.cardLayout.setSpacing(0)

        self._add_logo()
        self._add_spacer_v(14)
        self._add_welcome_banner()
        self._add_spacer_v(22)
        self._add_username_input()
        self._add_spacer_v(14)
        self._add_password_input()
        self._add_spacer_v(12)
        self._add_forgot_link()
        self._add_spacer_v(20)
        self._add_login_button()
        self._add_hidden_widgets()
        self._add_divider()
        self._add_footer()

        return self.cardWidget

    # ── Helpers ────────────────────────────────────────────────────
    def _add_spacer_v(self, px: int):
        self.cardLayout.addItem(
            QtWidgets.QSpacerItem(
                0, px,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
        )

    def _add_logo(self):
        self.lblLogo = QtWidgets.QLabel(parent=self.cardWidget)
        self.lblLogo.setObjectName("lblLogo")
        self.lblLogo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblLogo.setMinimumHeight(56)
        self.lblLogo.setMaximumHeight(88)
        sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.lblLogo.setSizePolicy(sp)
        self.logoPixmap = QtGui.QPixmap("assets/LogoDistriMagik.png")
        self.lblLogo.setStyleSheet(
            f"background-color: {_CARD_BG};"
        )
        if self.logoPixmap.isNull():
            self.lblLogo.setText("DistriCali")
            self.lblLogo.setStyleSheet(
                f"font-size: 28px; font-weight: bold; color: #000000;"
                f" background-color: {_CARD_BG};"
            )
        else:
            self._resize_logo()
        self.cardLayout.addWidget(self.lblLogo)

    def _resize_logo(self):
        if self.logoPixmap.isNull():
            return
        available_width = max(1, self.lblLogo.width())
        self.lblLogo.setPixmap(
            self.logoPixmap.scaled(
                available_width,
                88,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _add_welcome_banner(self):
        container = QtWidgets.QWidget(parent=self.cardWidget)
        container.setStyleSheet("background: transparent;")
        row = QtWidgets.QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)

        self.lblWelcomeBadge = QtWidgets.QLabel(parent=container)
        self.lblWelcomeBadge.setFixedSize(48, 48)
        self.lblWelcomeBadge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pix = QtGui.QPixmap("assets/iconos/badge_shield_user.svg")
        if not pix.isNull():
            self.lblWelcomeBadge.setPixmap(
                pix.scaled(48, 48,
                           QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        row.addWidget(self.lblWelcomeBadge)

        textCol = QtWidgets.QVBoxLayout()
        textCol.setSpacing(3)

        self.lblWelcomeTitle = QtWidgets.QLabel(parent=container)
        self.lblWelcomeTitle.setObjectName("lblWelcomeTitle")
        self.lblWelcomeTitle.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {_TEXT};"
            f" font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
        )
        self.lblWelcomeTitle.setWordWrap(True)
        textCol.addWidget(self.lblWelcomeTitle)

        self.lblWelcomeSubtitle = QtWidgets.QLabel(parent=container)
        self.lblWelcomeSubtitle.setObjectName("lblWelcomeSubtitle")
        self.lblWelcomeSubtitle.setStyleSheet(
            f"font-size: 12px; color: {_MUTED};"
            f" font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
        )
        self.lblWelcomeSubtitle.setWordWrap(True)
        textCol.addWidget(self.lblWelcomeSubtitle)

        row.addLayout(textCol)
        row.addStretch()
        self.cardLayout.addWidget(container)

    def _add_username_input(self):
        self.InputNombreUsuario = QtWidgets.QLineEdit(parent=self.cardWidget)
        self.InputNombreUsuario.setObjectName("InputNombreUsuario")
        self.InputNombreUsuario.setMinimumHeight(_INPUT_MIN_H)
        _sp_hfix(self.InputNombreUsuario)
        self.InputNombreUsuario.setStyleSheet(_INPUT_QSS)
        icon = QtGui.QIcon("assets/iconos/input_user.svg")
        self.InputNombreUsuario.addAction(
            icon, QtWidgets.QLineEdit.ActionPosition.LeadingPosition
        )
        self.cardLayout.addWidget(self.InputNombreUsuario)

    def _add_password_input(self):
        self.InputPassword = QtWidgets.QLineEdit(parent=self.cardWidget)
        self.InputPassword.setObjectName("InputPassword")
        self.InputPassword.setMinimumHeight(_INPUT_MIN_H)
        self.InputPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        _sp_hfix(self.InputPassword)
        self.InputPassword.setStyleSheet(_INPUT_PASS_QSS)

        lock_icon = QtGui.QIcon("assets/iconos/input_lock.svg")
        self.InputPassword.addAction(
            lock_icon, QtWidgets.QLineEdit.ActionPosition.LeadingPosition
        )
        eye_icon = QtGui.QIcon("assets/iconos/eye_closed.svg")
        self.passAction = self.InputPassword.addAction(
            eye_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition
        )

        # toolButton oculto para compatibilidad
        self.toolButton = QtWidgets.QToolButton(parent=self.cardWidget)
        self.toolButton.setVisible(False)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setIcon(eye_icon)

        self.cardLayout.addWidget(self.InputPassword)

    def _add_forgot_link(self):
        """Solo el link ¿Olvidaste tu contraseña? alineado a la derecha."""
        container = QtWidgets.QWidget(parent=self.cardWidget)
        container.setStyleSheet("background: transparent;")
        row = QtWidgets.QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addStretch()

        self.lblOlvidaste = QtWidgets.QLabel(parent=container)
        self.lblOlvidaste.setObjectName("lblOlvidaste")
        self.lblOlvidaste.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.lblOlvidaste.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
            }}
            QLabel:hover {{
                color: {_PRIMARY_H};
                text-decoration: underline;
            }}
        """)
        row.addWidget(self.lblOlvidaste)
        self.cardLayout.addWidget(container)

    def _add_login_button(self):
        self.BtnLogin = QtWidgets.QPushButton(parent=self.cardWidget)
        self.BtnLogin.setObjectName("BtnLogin")
        self.BtnLogin.setMinimumHeight(_BTN_MIN_H)
        self.BtnLogin.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        _sp_hfix(self.BtnLogin)
        self.BtnLogin.setStyleSheet(f"""
            QPushButton {{
                background-color: {_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 10px 16px;
                letter-spacing: 0.4px;
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
        """)
        lock_icon = QtGui.QIcon("assets/iconos/lock_white.svg")
        self.BtnLogin.setIcon(lock_icon)
        self.BtnLogin.setIconSize(QtCore.QSize(16, 16))
        self.cardLayout.addWidget(self.BtnLogin)

    def _add_hidden_widgets(self):
        """Compatibilidad total con main.py (BtnRol invisible)."""
        self.BtnRol = QtWidgets.QPushButton(parent=self.cardWidget)
        self.BtnRol.setObjectName("BtnRol")
        self.BtnRol.setText("ADMINISTRADOR")
        self.BtnRol.setVisible(False)
        self.BtnRol.setFixedSize(1, 1)

    def _add_divider(self):
        self._add_spacer_v(16)
        container = QtWidgets.QWidget(parent=self.cardWidget)
        container.setStyleSheet("background: transparent;")
        row = QtWidgets.QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        for attr in ("lineLeft", "lineRight"):
            line = QtWidgets.QFrame(parent=container)
            line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
            line.setStyleSheet(
                f"color: {_DIVIDER}; background-color: {_DIVIDER}; max-height: 1px;"
            )
            sp = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
            line.setSizePolicy(sp)
            setattr(self, attr, line)

        self.lblAcceso = QtWidgets.QLabel(parent=container)
        self.lblAcceso.setObjectName("lblAcceso")
        self.lblAcceso.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblAcceso.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 600;
            color: #B0A8B4;
            letter-spacing: 2px;
            font-family: 'Segoe UI', Arial, sans-serif;
            background: transparent;
        """)
        sp2 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.lblAcceso.setSizePolicy(sp2)

        row.addWidget(self.lineLeft)
        row.addWidget(self.lblAcceso)
        row.addWidget(self.lineRight)
        self.cardLayout.addWidget(container)

    def _add_footer(self):
        self._add_spacer_v(10)
        container = QtWidgets.QWidget(parent=self.cardWidget)
        container.setStyleSheet("background: transparent;")
        row = QtWidgets.QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.lblFooterIcon = QtWidgets.QLabel(parent=container)
        self.lblFooterIcon.setFixedSize(14, 14)
        footer_pix = QtGui.QPixmap("assets/iconos/lock_plum.svg")
        if not footer_pix.isNull():
            self.lblFooterIcon.setPixmap(
                footer_pix.scaled(14, 14,
                                  QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                  QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        self.lblFooterIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self.lblFooterIcon)

        self.lblFooterText = QtWidgets.QLabel(parent=container)
        self.lblFooterText.setObjectName("lblFooterText")
        self.lblFooterText.setStyleSheet(
            f"font-size: 11px; color: {_MUTED};"
            f" font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
        )
        row.addWidget(self.lblFooterText)

        self.cardLayout.addWidget(container)

    # ── Tab order ──────────────────────────────────────────────────
    def _set_tab_order(self, root):
        QtWidgets.QWidget.setTabOrder(self.InputNombreUsuario, self.InputPassword)
        QtWidgets.QWidget.setTabOrder(self.InputPassword, self.BtnLogin)

    # ── Responsividad dinámica ─────────────────────────────────────
    def adapt_to_size(self, width: int, height: int):
        # Hero: visible ≥ 720 px de ancho
        show_hero = width >= 720
        self.heroPanel.setVisible(show_hero)
        if show_hero:
            hero_pct = max(28, min(45, int(42 * 1000 / width)))
            self.rootLayout.setStretch(0, hero_pct)
            self.rootLayout.setStretch(1, 100 - hero_pct)
        else:
            self.rootLayout.setStretch(0, 0)
            self.rootLayout.setStretch(1, 100)

        # Márgenes formPanel
        h_margin = max(16, min(60, int(width * 0.05)))
        v_margin = max(16, min(48, int(height * 0.04)))
        self.formPanel.layout().setContentsMargins(
            h_margin, v_margin, h_margin, v_margin
        )

        card_w = min(480, max(340, int(width * (0.42 if not show_hero else 0.28))))

        # Márgenes card
        card_h_m = max(24, min(40, int(card_w * 0.075)))
        card_v_m = max(22, min(40, int(height * 0.038)))
        self.cardLayout.setContentsMargins(
            card_h_m, card_v_m, card_h_m, card_v_m
        )

        # Inputs y botón
        min_input = max(42, min(52, int(height * 0.058)))
        for widget in (self.InputNombreUsuario, self.InputPassword):
            widget.setMinimumHeight(min_input)
        self.BtnLogin.setMinimumHeight(max(44, min(54, int(height * 0.062))))
        self._resize_logo()

    # ── Textos ─────────────────────────────────────────────────────
    def retranslateUi(self, CONTENEDEDOR1):
        t = QtCore.QCoreApplication.translate
        CONTENEDEDOR1.setWindowTitle(
            t("CONTENEDEDOR1", "Distri Magik – Sistema de Inventario")
        )
        self.lblWelcomeTitle.setText(
            t("CONTENEDEDOR1", "Bienvenido de nuevo")
        )
        self.lblWelcomeSubtitle.setText(
            t("CONTENEDEDOR1", "Inicia sesión para continuar")
        )
        self.InputNombreUsuario.setPlaceholderText(
            t("CONTENEDEDOR1", "Usuario")
        )
        self.InputPassword.setPlaceholderText(
            t("CONTENEDEDOR1", "Contraseña")
        )
        self.lblOlvidaste.setText(
            t("CONTENEDEDOR1", "¿Olvidaste tu contraseña?")
        )
        self.BtnLogin.setText(t("CONTENEDEDOR1", "  Iniciar Sesión"))
        self.lblAcceso.setText(t("CONTENEDEDOR1", "ACCESO RESTRINGIDO"))
        self.lblFooterText.setText(
            t("CONTENEDEDOR1", "Solo personal autorizado")
        )
