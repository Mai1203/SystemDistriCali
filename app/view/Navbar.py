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
        self._qss_combo_normal = """
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
            QComboBox::down-arrow { image: none; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E2DAE1;
                border-radius: 8px;
                selection-background-color: #862D6D;
                selection-color: white;
                outline: none;
            }
        """
        
        self._qss_combo_activo = """
            QComboBox {
                background-color: #862D6D;
                border: none;
                color: #FFFFFF;
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox:hover {
                background-color: #6E2259;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow { image: none; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E2DAE1;
                border-radius: 8px;
                selection-background-color: #862D6D;
                selection-color: white;
                outline: none;
                color: #201A24;
            }
        """
        self.comboVentas.setStyleSheet(self._qss_combo_normal)

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

        # Cuando se hace clic en cualquier botón normal, des-iluminar el comboVentas
        self.button_group.buttonClicked.connect(lambda: self.set_combo_active(False))

    def set_combo_active(self, active: bool):
        """Cambia el estilo visual del QComboBox para que parezca marcado/desmarcado."""
        import qtawesome as qta
        if active:
            self.comboVentas.setStyleSheet(self._qss_combo_activo)
            # Actualizamos el ícono a blanco si es necesario, pero los items del comboBox 
            # ya se inicializaron con un ícono. Si queremos cambiar el ícono del ComboBox entero:
            for i in range(self.comboVentas.count()):
                self.comboVentas.setItemIcon(i, qta.icon('fa5s.shopping-cart', color='#FFFFFF'))
        else:
            self.comboVentas.setStyleSheet(self._qss_combo_normal)
            for i in range(self.comboVentas.count()):
                self.comboVentas.setItemIcon(i, qta.icon('fa5s.shopping-cart', color='#201A24'))

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
