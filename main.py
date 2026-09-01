import sys
import os
import time
import datetime
from pathlib import Path

import jwt
from dotenv import load_dotenv

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QProgressDialog,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets  # Para poder reasignar QMessageBox si es necesario

from init_db import conectar_base, inicializar_db
from app.database.database import init_db
from app.utils.enviar_notifi import (
    Mensajes,
    enviar_notificacion,
)
from app.controllers.usuario_crud import verificar_credenciales, obtener_usuario_por_id
from app.ventanasView import MainApp
from app.view import Login_View
from app.services.permisos_service import obtener_permisos_usuario

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.usuario_actual_id = None
        self.setWindowTitle("System DistriCali")
        self.setWindowIcon(QIcon("assets/logo1.ico"))
        self.inicializar_db()
        # Tamaño inicial relativo a la pantalla (80% del espacio disponible)
        self.setMinimumSize(480, 520)
        screen = QApplication.primaryScreen().availableGeometry()
        init_w = max(900, min(1280, int(screen.width() * 0.80)))
        init_h = max(560, min(800, int(screen.height() * 0.80)))
        self.resize(init_w, init_h)
        self.setStyleSheet("background-color: #F8F5F8;")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.Login = Login_View()
        self.MainApp = None

        self.stacked_widget.addWidget(self.Login)

        self.Login.BtnLogin.clicked.connect(self.iniciar_sesion)
        self.Login.InputPassword.returnPressed.connect(self.iniciar_sesion)

        self.db = conectar_base()

    def crear_mainapp(self):
        if self.MainApp is not None:
            return

        self.MainApp = MainApp()
        self.stacked_widget.addWidget(self.MainApp)
        self.MainApp.navbar.BtnCerrarSesion.clicked.connect(self.cerrar_sesion)

    def inicializar_db(self):
        app_data_dir = Path(os.getenv("APPDATA") or os.path.expanduser("~")) / "SystemDistriCali"
        app_data_dir.mkdir(parents=True, exist_ok=True)

        db_path = app_data_dir / "systemdistricali.db"

        if not db_path.exists():
            progress = QProgressDialog("Creando la base de datos...", None, 0, 0, self)
            progress.setWindowTitle("Por favor espera")
            progress.setCancelButton(None)
            progress.setMinimumDuration(0)
            progress.show()

            QApplication.processEvents()

            inicializar_db()
            time.sleep(2)

            progress.close()
        else:
            print("✅ La base de datos ya existe. Continuando con el programa...")
            init_db()

    def cerrar_sesion(self):
        enviar_notificacion("Sesión cerrada", "Puedes iniciar sesión nuevamente")
        self.stacked_widget.setCurrentWidget(self.Login)
        self.limpiar_campos()

    def limpiar_campos(self):
        self.Login.InputNombreUsuario.clear()
        self.Login.InputPassword.clear()

    def closeEvent(self, event):
        respuesta = QMessageBox.question(
            self,
            "Salir del programa",
            "¿Estás seguro de que deseas cerrar el programa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def showEvent(self, event):
        # La ventana ya abre maximizada; no se necesita centrado manual.
        super().showEvent(event)

    def iniciar_sesion(self):
        usuario = self.Login.InputNombreUsuario.text().strip()
        contraseña = self.Login.InputPassword.text().strip()

        if not usuario or not contraseña:
            enviar_notificacion("Error", "Por favor, ingresa tus credenciales")
            return

        usuario_autenticado = verificar_credenciales(self.db, usuario, contraseña)
        if not usuario_autenticado:
            enviar_notificacion("Error", "Usuario o contraseña incorrectos")
            return

        usuario_data = obtener_usuario_por_id(self.db, usuario_autenticado.ID_Usuario)
        rol = usuario_data.rol if (usuario_data and usuario_data.rol) else "ASESOR"

        self.usuario_actual_id = usuario_autenticado.ID_Usuario
        self.crear_mainapp()
        self.MainApp.ventas.usuario_actual_id = usuario_autenticado.ID_Usuario
        self.MainApp.ventasCredito.usuario_actual_id = usuario_autenticado.ID_Usuario
        self.MainApp.pagoCredito.usuario_actual_id = usuario_autenticado.ID_Usuario
        self.MainApp.caja.usuario_actual_id = usuario_autenticado.ID_Usuario
        token = self.generar_token(usuario_autenticado.ID_Usuario, rol)

        self.token_actual = token

        enviar_notificacion("Inicio de sesión exitoso", "Bienvenido")
        self.stacked_widget.setCurrentWidget(self.MainApp)

        self.configurar_accesos_por_usuario(usuario_autenticado)
        self.MainApp.navbar.actualizar_usuario_rol(usuario_autenticado)
        self.db.close()

    def generar_token(self, usuario_id, rol):
        payload = {
            "id_usuario": usuario_id,
            "rol": rol,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        # PyJWT 2.x devuelve bytes, lo convertimos a string si es necesario
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def configurar_accesos_por_usuario(self, usuario):
        navbar = self.MainApp.navbar
        nombres_permitidos = obtener_permisos_usuario(usuario)
        es_admin = usuario.rol and usuario.rol.Nombre == "ADMINISTRADOR"

        permisos = {
            "Ventas": navbar.comboVentas,
            "Caja": navbar.BtnCaja,
            "Credito": navbar.BtnCredito,
            "Egreso": navbar.BtnEgreso,
            "Respaldo": navbar.BtnRespaldo,
            "Productos": navbar.BtnProductos,
            "CrediFactura": navbar.BtnCrediFactura,
            "Facturas": navbar.BtnFacturas,
            "Reportes": navbar.BtnReportes,
            "ControlUsuario": navbar.BtnControlUsuario,
            "Clientes": navbar.BtnClientes,
        }

        for nombre, control in permisos.items():
            control.setEnabled(es_admin or nombre in nombres_permitidos)

        permitidos = [nombre for nombre in permisos if es_admin or nombre in nombres_permitidos]
        if permitidos:
            primer_permiso = permitidos[0]
            if primer_permiso == "Ventas":
                self.MainApp.cambiar_tipo_venta(navbar.comboVentas.currentIndex())
            else:
                controles_vistas = {
                    "Caja": self.MainApp.caja,
                    "Credito": self.MainApp.ventasCredito,
                    "Egreso": self.MainApp.egreso,
                    "Respaldo": self.MainApp.respaldo_view,
                    "Productos": self.MainApp.productos,
                    "CrediFactura": self.MainApp.crediFactura,
                    "Facturas": self.MainApp.facturas,
                    "Reportes": self.MainApp.reportes,
                    "ControlUsuario": self.MainApp.control_usuario_view,
                    "Clientes": self.MainApp.Clientes,
                }
                self.MainApp.stacked_widget.setCurrentWidget(controles_vistas[primer_permiso])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Si deseas reemplazar QMessageBox globalmente, usa:
    # QtWidgets.QMessageBox = Mensajes
    # (asegúrate de importar QtWidgets)
    main_window = MainWindow()
    main_window.showMaximized()  # Pantalla completa al iniciar
    sys.exit(app.exec())