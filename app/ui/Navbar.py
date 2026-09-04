from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

_PRIMARY = "#862D6D"
_PRIMARY_HOVER = "#6E2259"
_BG = "#F5F0F4"
_CARD_BG = "#FFFFFF"
_TEXT = "#201A24"
_MUTED = "#7B737F"
_DIVIDER = "#E2DAE1"

# QSS dinámico: el ícono cambia de color cuando está checked via qta
_MENU_BTN_QSS = f"""
    QToolButton {{
        background-color: transparent;
        border: none;
        color: {_TEXT};
        border-radius: 10px;
        padding: 10px 14px;
        text-align: left;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QToolButton:hover {{
        background-color: #F0EAF0;
    }}
    QToolButton:checked {{
        background-color: {_PRIMARY};
        color: #FFFFFF;
        font-weight: 600;
    }}
"""

_CTRL_USR_QSS = f"""
    QToolButton {{
        background-color: {_PRIMARY};
        border: none;
        color: #FFFFFF;
        border-radius: 12px;
        padding: 12px 16px;
        text-align: left;
        font-size: 14px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QToolButton:hover {{
        background-color: {_PRIMARY_HOVER};
    }}
"""

# Mapa de ícono qtawesome para cada botón del menú
_ICONS = {
    "BtnVentas":       ("fa5s.shopping-cart", _TEXT, "#FFFFFF"),
    "BtnCaja":         ("fa5s.cash-register",  _TEXT, "#FFFFFF"),
    "BtnCredito":      ("fa5s.credit-card",    _TEXT, "#FFFFFF"),
    "BtnEgreso":       ("fa5s.file-invoice",   _TEXT, "#FFFFFF"),
    "BtnRespaldo":     ("fa5s.database",       _TEXT, "#FFFFFF"),
    "BtnProductos":    ("fa5s.box-open",       _TEXT, "#FFFFFF"),
    "BtnCrediFactura": ("fa5s.receipt",        _TEXT, "#FFFFFF"),
    "BtnFacturas":     ("fa5s.file-alt",       _TEXT, "#FFFFFF"),
    "BtnReportes":     ("fa5s.chart-line",     _TEXT, "#FFFFFF"),
    "BtnClientes":     ("fa5s.users",          _TEXT, "#FFFFFF"),
}


class Ui_Navbar(object):
    def setupUi(self, Navbar):
        Navbar.setObjectName("Navbar")
        Navbar.setMinimumWidth(240)
        Navbar.setMaximumWidth(280)
        Navbar.setStyleSheet(f"background-color: {_CARD_BG}; border-right: 1px solid {_DIVIDER};")

        self.rootLayout = QtWidgets.QVBoxLayout(Navbar)
        self.rootLayout.setContentsMargins(16, 24, 16, 24)
        self.rootLayout.setSpacing(4)

        # ── LOGO ──
        self.LabelImgNavbar = QtWidgets.QLabel(parent=Navbar)
        self.LabelImgNavbar.setMinimumHeight(80)
        self.LabelImgNavbar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pix = QtGui.QPixmap("assets/LogoDistriMagik.png")
        if not pix.isNull():
            self.LabelImgNavbar.setPixmap(pix.scaledToHeight(60, QtCore.Qt.TransformationMode.SmoothTransformation))
        self.LabelImgNavbar.setStyleSheet("background-color: transparent; border: none;")
        self.rootLayout.addWidget(self.LabelImgNavbar)
        self.rootLayout.addSpacing(12)

        # ── FUNCIONALIDADES ──
        self.LabelFuncionalidades = QtWidgets.QLabel("FUNCIONALIDADES", parent=Navbar)
        self.LabelFuncionalidades.setStyleSheet(
            f"color: {_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; border: none; padding: 4px 6px;"
        )
        self.rootLayout.addWidget(self.LabelFuncionalidades)

        self._create_menu_button(Navbar, "BtnVentas",   "Ventas")
        self._create_menu_button(Navbar, "BtnCaja",     "Caja")
        self._create_menu_button(Navbar, "BtnCredito",  "Crédito")
        self._create_menu_button(Navbar, "BtnEgreso",   "Egreso")
        self._create_menu_button(Navbar, "BtnRespaldo", "Respaldo")

        self.rootLayout.addSpacing(12)

        # ── DATOS ──
        self.LabelDatos = QtWidgets.QLabel("DATOS", parent=Navbar)
        self.LabelDatos.setStyleSheet(
            f"color: {_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; border: none; padding: 4px 6px;"
        )
        self.rootLayout.addWidget(self.LabelDatos)

        self._create_menu_button(Navbar, "BtnProductos",    "Productos")
        self._create_menu_button(Navbar, "BtnCrediFactura", "CrediFactura")
        self._create_menu_button(Navbar, "BtnFacturas",     "Factura")
        self._create_menu_button(Navbar, "BtnReportes",     "Reportes")
        self._create_menu_button(Navbar, "BtnClientes",     "Clientes")

        self.rootLayout.addStretch()

        # ── CONTROL USUARIOS ──
        self.BtnControlUsuario = QtWidgets.QToolButton(parent=Navbar)
        self.BtnControlUsuario.setObjectName("BtnControlUsuario")
        self.BtnControlUsuario.setText("  Control Usuarios")
        self.BtnControlUsuario.setIcon(qta.icon("fa5s.user-shield", color="#FFFFFF"))
        self.BtnControlUsuario.setIconSize(QtCore.QSize(18, 18))
        self.BtnControlUsuario.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.BtnControlUsuario.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.BtnControlUsuario.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnControlUsuario.setStyleSheet(_CTRL_USR_QSS)
        self.rootLayout.addWidget(self.BtnControlUsuario)

        self.rootLayout.addSpacing(20)

        # ── USUARIO PROFILE ──
        self.userWidget = QtWidgets.QWidget(parent=Navbar)
        self.userWidget.setStyleSheet(
            f"border: 1px solid {_DIVIDER}; border-radius: 12px; background: transparent; padding: 4px;"
        )
        userLayout = QtWidgets.QHBoxLayout(self.userWidget)
        userLayout.setContentsMargins(8, 8, 8, 8)
        userLayout.setSpacing(10)

        # Avatar (ícono SVG qta)
        self.lblUserAvatar = QtWidgets.QLabel(parent=self.userWidget)
        self.lblUserAvatar.setFixedSize(40, 40)
        self.lblUserAvatar.setStyleSheet(
            f"border-radius: 20px; background-color: {_PRIMARY}; border: none;"
        )
        self.lblUserAvatar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblUserAvatar.setPixmap(qta.icon("fa5s.user", color="#FFFFFF").pixmap(22, 22))
        userLayout.addWidget(self.lblUserAvatar)

        # User Info
        userInfoLayout = QtWidgets.QVBoxLayout()
        userInfoLayout.setSpacing(1)

        self.BtnUsuario = QtWidgets.QLabel("Usuario", parent=self.userWidget)
        self.BtnUsuario.setObjectName("BtnUsuario")
        self.BtnUsuario.setStyleSheet(f"color: {_TEXT}; font-weight: 600; font-size: 13px; border: none;")
        userInfoLayout.addWidget(self.BtnUsuario)

        self.lblUserRole = QtWidgets.QLabel("Administrador", parent=self.userWidget)
        self.lblUserRole.setStyleSheet(f"color: {_MUTED}; font-size: 11px; border: none;")
        userInfoLayout.addWidget(self.lblUserRole)

        self.BtnCerrarSesion = QtWidgets.QPushButton("Cerrar sesión", parent=self.userWidget)
        self.BtnCerrarSesion.setObjectName("BtnCerrarSesion")
        self.BtnCerrarSesion.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnCerrarSesion.setIcon(qta.icon("fa5s.sign-out-alt", color="#D32F2F"))
        self.BtnCerrarSesion.setStyleSheet(
            "color: #D32F2F; font-size: 11px; font-weight: 500; border: none; "
            "background: transparent; text-align: left; padding: 0;"
        )
        userInfoLayout.addWidget(self.BtnCerrarSesion)

        userLayout.addLayout(userInfoLayout)
        userLayout.addStretch()
        self.rootLayout.addWidget(self.userWidget)

        QtCore.QMetaObject.connectSlotsByName(Navbar)

    def _create_menu_button(self, parent, obj_name, text):
        icon_name, color_normal, color_checked = _ICONS.get(obj_name, ("fa5s.circle", _TEXT, "#FFFFFF"))

        btn = QtWidgets.QToolButton(parent=parent)
        btn.setObjectName(obj_name)
        btn.setText(f"  {text}")
        # Íconos duotono: normal y checked (blanco cuando está activo)
        btn.setIcon(qta.icon(icon_name, color=color_normal))
        btn.setIconSize(QtCore.QSize(18, 18))
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setCheckable(True)
        btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(_MENU_BTN_QSS)

        # Actualizar ícono cuando cambia el estado checked
        def _on_toggled(checked, b=btn, iname=icon_name, cn=color_normal, cc=color_checked):
            b.setIcon(qta.icon(iname, color=cc if checked else cn))

        btn.toggled.connect(_on_toggled)

        self.rootLayout.addWidget(btn)
        setattr(self, obj_name, btn)
