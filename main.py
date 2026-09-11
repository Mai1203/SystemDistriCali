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
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6 import QtWidgets  # Para poder reasignar QMessageBox si es necesario


from app.database.config import load_config, is_configured
from app.database.engine import get_engine, reset_engine
from app.database.session import SessionLocal
from app.database.database import init_db
from app.services.connection_service import test_connection
from app.utils.logger import logger
from app.utils.enviar_notifi import (
    Mensajes,
    enviar_notificacion,
)
from app.controllers.usuario_crud import verificar_credenciales, obtener_usuario_por_id
from app.ventanasView import MainApp
from app.view import Login_View
from app.view.SetupWizardView import SetupWizardView
from app.services.permisos_service import obtener_permisos_usuario

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_distrimagik_2026")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.usuario_actual_id = None
        self.setWindowTitle("System Distri Magik")
        self.setWindowIcon(QIcon("assets/Favicon.ico"))
        
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

        self.SetupWizard = SetupWizardView()
        self.Login = Login_View()
        self.MainApp = None

        self.stacked_widget.addWidget(self.SetupWizard)
        self.stacked_widget.addWidget(self.Login)

        self.SetupWizard.configuracion_finalizada.connect(self.al_finalizar_configuracion)
        self.Login.BtnLogin.clicked.connect(self.iniciar_sesion)
        self.Login.InputPassword.returnPressed.connect(self.iniciar_sesion)

        # Reproductor de inicio (suena al arrancar la aplicación)
        self.player_inicio = QMediaPlayer()
        self.audio_inicio = QAudioOutput()
        self.player_inicio.setAudioOutput(self.audio_inicio)
        self.audio_inicio.setVolume(1.0)
        self.player_inicio.setSource(QUrl.fromLocalFile(os.path.abspath("assets/sonidos/Start.mp3")))
        self.player_inicio.play()

        # Flujo de inicio: validar configuración existente
        self.verificar_o_iniciar_configuracion()

    def verificar_o_iniciar_configuracion(self):
        config = load_config()
        if not is_configured():
            logger.info("Sistema no configurado previamente. Mostrando Asistente de Configuración...")
            self.stacked_widget.setCurrentWidget(self.SetupWizard)
            return

        # Probar conexión
        ok, msg = test_connection(config, timeout_seconds=3)
        if not ok:
            logger.warning(f"Conexión inicial falló: {msg}. Redirigiendo al Asistente de Configuración.")
            QMessageBox.warning(
                self,
                "Configuración de Conexión Requerida",
                f"No se pudo conectar a la base de datos configurada ({config.mode}):\n\n{msg}\n\nPor favor revise los datos en el Asistente.",
            )
            self.stacked_widget.setCurrentWidget(self.SetupWizard)
        else:
            logger.info("Conexión inicial verificada con éxito. Inicializando esquema si es necesario...")
            try:
                init_db()
                self.stacked_widget.setCurrentWidget(self.Login)
            except Exception as e:
                logger.error(f"Error al inicializar esquema: {e}")
                self.stacked_widget.setCurrentWidget(self.SetupWizard)

    def al_finalizar_configuracion(self):
        logger.info("Asistente de configuración completado. Cambiando a vista de Login...")
        self.stacked_widget.setCurrentWidget(self.Login)

    def abrir_asistente_configuracion(self):
        """Permite abrir el asistente desde cualquier parte del sistema (ej. ajustes)."""
        self.stacked_widget.setCurrentWidget(self.SetupWizard)

    def crear_mainapp(self):
        if self.MainApp is not None:
            return

        self.MainApp = MainApp()
        self.stacked_widget.addWidget(self.MainApp)
        self.MainApp.navbar.BtnCerrarSesion.clicked.connect(self.cerrar_sesion)

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
        super().showEvent(event)

    def iniciar_sesion(self):
        usuario = self.Login.InputNombreUsuario.text().strip()
        contraseña = self.Login.InputPassword.text().strip()

        if not usuario or not contraseña:
            enviar_notificacion("Error", "Por favor, ingresa tus credenciales")
            return

        db = SessionLocal()
        try:
            usuario_autenticado = verificar_credenciales(db, usuario, contraseña)
            if not usuario_autenticado:
                enviar_notificacion("Error", "Usuario o contraseña incorrectos")
                return

            usuario_data = obtener_usuario_por_id(db, usuario_autenticado.ID_Usuario)
            rol = usuario_data.rol if (usuario_data and usuario_data.rol) else "ASESOR"

            self.usuario_actual_id = usuario_autenticado.ID_Usuario
            self.crear_mainapp()
            self.MainApp.ventas.usuario_actual_id = usuario_autenticado.ID_Usuario
            self.MainApp.ventasCredito.usuario_actual_id = usuario_autenticado.ID_Usuario
            self.MainApp.pagoCredito.usuario_actual_id = usuario_autenticado.ID_Usuario
            self.MainApp.caja.usuario_actual_id = usuario_autenticado.ID_Usuario
            token = self.generar_token(usuario_autenticado.ID_Usuario, rol)

            self.token_actual = token


            # Reproductor de bienvenida (Voz)
            self.player_voz = QMediaPlayer()
            self.audio_voz = QAudioOutput()
            self.player_voz.setAudioOutput(self.audio_voz)
            self.audio_voz.setVolume(1.0)
            self.player_voz.setSource(QUrl.fromLocalFile(os.path.abspath("assets/sonidos/Voz.mp3")))
            self.player_voz.play()

            enviar_notificacion("Inicio de sesión exitoso", "Bienvenido")
            self.stacked_widget.setCurrentWidget(self.MainApp)


            self.configurar_accesos_por_usuario(usuario_autenticado)
            self.MainApp.navbar.actualizar_usuario_rol(usuario_autenticado)
        finally:
            db.close()

    def generar_token(self, usuario_id, rol):
        payload = {
            "id_usuario": usuario_id,
            "rol": rol,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
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
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())