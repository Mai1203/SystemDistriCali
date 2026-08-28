from PyQt6 import QtCore
import qtawesome as qta

from PyQt6.QtWidgets import (
    QWidget,
    QButtonGroup,
    QComboBox,
)

from ..ui import Ui_Navbar
from ..configuracion import TIPOS_VENTA


class Navbar_View(QWidget, Ui_Navbar):

    def __init__(self, parent=None):
        super(Navbar_View, self).__init__(parent)

        self.setupUi(self)

        import qtawesome as qta
        self.comboVentas = QComboBox(self)
        for tipo in TIPOS_VENTA.values():
            self.comboVentas.addItem(qta.icon('fa5s.shopping-cart', color='#201A24'), f"  {tipo['nombre']}")
            
        self.comboVentas.setObjectName("comboVentas")
        self.comboVentas.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.comboVentas.setMinimumHeight(40)
        self.comboVentas.setIconSize(QtCore.QSize(18, 18))
        
        # Estilo integrado con el nuevo diseño
        self.comboVentas.setStyleSheet("""
            QComboBox {
                background-color: transparent;
                border: none;
                color: #201A24;
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox:hover {
                background-color: #F8F5F8;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none; /* Podemos omitir la flecha nativa si queremos que parezca un btn normal */
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E2DAE1;
                border-radius: 8px;
                selection-background-color: #862D6D;
                selection-color: white;
                outline: none;
            }
        """)

        # Reemplazamos BtnVentas por comboVentas
        self.rootLayout.replaceWidget(self.BtnVentas, self.comboVentas)
        self.BtnVentas.hide()

        # Usamos QButtonGroup para gestionar el estado "checked"
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.button_group.addButton(self.BtnCaja)
        self.button_group.addButton(self.BtnCredito)
        self.button_group.addButton(self.BtnEgreso)
        self.button_group.addButton(self.BtnRespaldo)
        self.button_group.addButton(self.BtnProductos)
        self.button_group.addButton(self.BtnCrediFactura)
        self.button_group.addButton(self.BtnFacturas)
        self.button_group.addButton(self.BtnReportes)
        self.button_group.addButton(self.BtnClientes)

        self.lblUserAvatar.setPixmap(
            qta.icon("fa5s.user", color="#FFFFFF").pixmap(22, 22)
        )

    def actualizar_usuario_rol(self, usuario):
        """Actualiza nombre, rol y ícono del usuario activo en el Navbar."""
        nombre = usuario.Nombre
        if " " in nombre:
            nombre = nombre.split(" ")[0]

        self.BtnUsuario.setText(nombre)

        rol_nombre = "Administrador" if usuario.ID_Rol == 1 else "Asesor"
        self.lblUserRole.setText(rol_nombre)

        # Ícono SVG según el rol (sin PNGs)
        if usuario.ID_Rol == 1:
            icon_name = "fa5s.user-shield"  # Admin = escudo
        else:
            icon_name = "fa5s.user"         # Asesor = usuario simple
        self.lblUserAvatar.setPixmap(
            qta.icon(icon_name, color="#FFFFFF").pixmap(22, 22)
        )
