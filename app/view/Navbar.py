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

        self.comboVentas = QComboBox(self)
        self.comboVentas.setObjectName("comboVentas")
        self.comboVentas.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.comboVentas.setMinimumHeight(40)
        self.comboVentas.setIconSize(QtCore.QSize(18, 18))

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

        # Cuando se hace clic en cualquier otro botón del navbar, desactivar el fondo morado de comboVentas
        self.button_group.buttonClicked.connect(lambda _: self.set_combo_active(False))

        self.lblUserAvatar.setPixmap(
            qta.icon("fa5s.user", color="#FFFFFF").pixmap(22, 22)
        )

        # Inicialmente activo o transparente
        self.set_combo_active(False)

    def set_combo_active(self, active: bool):
        """Establece el estilo de comboVentas para que tenga fondo morado y texto blanco cuando está activo."""
        color_texto = "#FFFFFF" if active else "#201A24"
        bg_color = "#862D6D" if active else "transparent"
        bg_hover = "#6E2259" if active else "#F0EAF0"
        font_wt = "600" if active else "500"

        self.comboVentas.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg_color};
                border: none;
                color: {color_texto};
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: {font_wt};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QComboBox:hover {{
                background-color: {bg_hover};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border: 1px solid #E2DAE1;
                border-radius: 8px;
                selection-background-color: #862D6D;
                selection-color: white;
                outline: none;
                color: #201A24;
            }}
        """)

        # Actualizar los íconos de cada item del combo (blanco cuando está activo, oscuro cuando está inactivo)
        self.comboVentas.blockSignals(True)
        idx_actual = self.comboVentas.currentIndex()
        self.comboVentas.clear()
        icon_color = "#FFFFFF" if active else "#201A24"
        for tipo in TIPOS_VENTA.values():
            self.comboVentas.addItem(qta.icon('fa5s.shopping-cart', color=icon_color), f"  {tipo['nombre']}")
        if idx_actual >= 0 and idx_actual < self.comboVentas.count():
            self.comboVentas.setCurrentIndex(idx_actual)
        self.comboVentas.blockSignals(False)

        if active:
            # Desmarcar temporalmente los botones de button_group para que ninguno quede morado a la vez
            self.button_group.setExclusive(False)
            for btn in self.button_group.buttons():
                btn.setChecked(False)
            self.button_group.setExclusive(True)

    def actualizar_usuario_rol(self, usuario):
        """Actualiza nombre, rol y ícono del usuario activo en el Navbar."""
        nombre = usuario.Nombre
        if " " in nombre:
            nombre = nombre.split(" ")[0]

        self.BtnUsuario.setText(nombre)

        rol_nombre = "Administrador" if usuario.ID_Rol == 1 else "Asesor"
        self.lblUserRole.setText(rol_nombre)

        if usuario.ID_Rol == 1:
            icon_name = "fa5s.user-shield"
        else:
            icon_name = "fa5s.user"
        self.lblUserAvatar.setPixmap(
            qta.icon(icon_name, color="#FFFFFF").pixmap(22, 22)
        )
