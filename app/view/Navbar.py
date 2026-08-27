from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
import os

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

        self.comboVentas = QComboBox(self.QWNavbar)
        self.comboVentas.addItems(
            [tipo["nombre"] for tipo in TIPOS_VENTA.values()]
        )

        self.comboVentas.setObjectName("comboVentas")

        self.comboVentas.setCursor(
            QtCore.Qt.CursorShape.PointingHandCursor
        )

        self.comboVentas.setMinimumHeight(40)

        self.comboVentas.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: none;
                color: rgb(50, 50, 50);
                padding: 5px 10px;
                font-size: 18px;
            }

            QComboBox:hover {
                background-color: #f2f2f2;
            }
        """)

        self.verticalLayout.replaceWidget(
            self.BtnVentas,
            self.comboVentas
        )

        self.BtnVentas.hide()

        self.BtnCaja.setStyleSheet(
            "background-color: #f2f2f2;\n"
        )

        self.button_group = QButtonGroup(self)

        self.button_group.addButton(self.BtnVentas)
        self.button_group.addButton(self.BtnCredito)
        self.button_group.addButton(self.BtnProductos)
        self.button_group.addButton(self.BtnCaja)
        self.button_group.addButton(self.BtnCrediFactura)
        self.button_group.addButton(self.BtnControlUsuario)
        self.button_group.addButton(self.BtnEgreso)
        self.button_group.addButton(self.BtnFacturas)
        self.button_group.addButton(self.BtnReportes)
        self.button_group.addButton(self.BtnRespaldo)
        self.button_group.addButton(self.BtnClientes)

        self.button_group.buttonClicked.connect(
            self.cambiar_color_boton
        )

        self.estilo_normal = """
            QToolButton {
                background-color: white;
                border: none;
                color: rgb(50, 50, 50);
                border-radius: 15px;
                padding: 5px 10px;
                height: 40px;
                text-align: left;
                font-size: 18px;
                cursor: pointer;
            }

            QToolButton:hover {
                background-color: #f2f2f2;
                cursor: pointer;
            }
        """

        self.estilo_seleccionado = (
            "background-color: #f2f2f2;"
        )

        self.icon_asesor = "./assets/iconos/asesor.png"
        self.icon_admin = "./assets/iconos/perfil.png"

    def cambiar_color_boton(self, boton_seleccionado):
        """
        Cambia el color del botón seleccionado
        en función de su estado.
        """

        # Restaurar el estilo normal a todos los botones
        for button in self.button_group.buttons():
            button.setStyleSheet(self.estilo_normal)

        # Aplicar el estilo seleccionado
        # al botón que fue presionado
        boton_seleccionado.setStyleSheet(
            self.estilo_seleccionado
        )

    def actualizar_usuario_rol(self, usuario):
        """
        Actualiza el texto del botón con el nombre de usuario.
        """

        nombre = usuario.Nombre

        if " " in nombre:
            nombre = nombre.split(" ")[0]

        self.BtnUsuario.setText(f"{nombre}")

        # Si el usuario no es "ADMIN", cambia el ícono
        if usuario.ID_Rol != 1:

            # Verifica si el archivo existe antes de asignar el ícono
            if os.path.exists(self.icon_asesor):

                self.BtnUsuario.setIcon(
                    QIcon(self.icon_asesor)
                )

            else:
                print(
                    "Error: No se encuentra el archivo de ícono."
                )

        else:
            self.BtnUsuario.setIcon(
                QIcon(self.icon_admin)
            )
