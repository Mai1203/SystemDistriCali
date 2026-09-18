from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QLineEdit, QStackedWidget, QMessageBox, 
    QFrame, QGroupBox, QProgressBar, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

from app.database.config import load_config
from app.services.server_setup_service import get_local_ip, detect_postgresql_installation
from app.controllers.setup_controller import SetupController
from app.services.setup_strategies import (
    LocalSetupStrategy, 
    ServerSetupStrategy, 
    TerminalSetupStrategy
)

class SetupWizardView(QWidget):
    configuracion_finalizada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = SetupController()
        self.controller.on_success.connect(self._on_success)
        self.controller.on_error.connect(self._on_error)
        self.controller.on_progress.connect(self._on_progress)

        self.setWindowTitle("Asistente de Configuración - System Distri Magik")
        self.resize(750, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #FDFBFE;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2D2D2D;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0D4DE;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #5C2454;
            }
            QLineEdit {
                border: 1px solid #D0C2CE;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #5C2454;
            }
            QLineEdit:disabled {
                background-color: #F4EFF3;
                color: #888888;
            }
            QPushButton {
                background-color: #5C2454;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7A3070;
            }
            QPushButton:pressed {
                background-color: #42193C;
            }
            QPushButton:disabled {
                background-color: #A38C9E;
                color: #EFEAEF;
            }
            QPushButton#btnSecundario {
                background-color: #ECE5EB;
                color: #5C2454;
                border: 1px solid #D0C2CE;
            }
            QPushButton#btnSecundario:hover {
                background-color: #DFD4DE;
            }
            QPushButton#btnSecundario:disabled {
                background-color: #F5F0F4;
                color: #B0A2AD;
                border: 1px solid #E0D8DF;
            }
            QRadioButton {
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QProgressBar {
                border: 1px solid #D0C2CE;
                border-radius: 6px;
                text-align: center;
                height: 18px;
                background-color: #F3EBF1;
                color: #5C2454;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5C2454, stop:1 #9E3E91);
                border-radius: 5px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(15)

        lbl_titulo = QLabel("Configuración Inicial del Sistema")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #5C2454;")
        
        lbl_subtitulo = QLabel("Seleccione el modo en que operará este computador dentro de su negocio.")
        lbl_subtitulo.setStyleSheet("color: #666666; font-size: 13px;")

        main_layout.addWidget(lbl_titulo)
        main_layout.addWidget(lbl_subtitulo)

        modo_frame = QFrame()
        modo_layout = QHBoxLayout(modo_frame)
        modo_layout.setSpacing(20)

        self.rb_servidor = QRadioButton("🖥️ Servidor (Principal)")
        self.rb_terminal = QRadioButton("💻 Terminal (Puesto de Venta)")
        self.rb_local = QRadioButton("📁 Local (Monousuario)")

        self.rb_servidor.toggled.connect(self.cambiar_pestana)
        self.rb_terminal.toggled.connect(self.cambiar_pestana)
        self.rb_local.toggled.connect(self.cambiar_pestana)

        modo_layout.addWidget(self.rb_servidor)
        modo_layout.addWidget(self.rb_terminal)
        modo_layout.addWidget(self.rb_local)
        main_layout.addWidget(modo_frame)

        self.stacked_widget = QStackedWidget()
        self.vista_servidor = self.crear_vista_servidor()
        self.vista_terminal = self.crear_vista_terminal()
        self.vista_local = self.crear_vista_local()

        self.stacked_widget.addWidget(self.vista_servidor)
        self.stacked_widget.addWidget(self.vista_terminal)
        self.stacked_widget.addWidget(self.vista_local)
        main_layout.addWidget(self.stacked_widget, 1)

        self.contenedor_carga = QWidget()
        layout_carga = QVBoxLayout(self.contenedor_carga)
        layout_carga.setContentsMargins(0, 0, 0, 0)
        layout_carga.setSpacing(4)

        self.lbl_estado_carga = QLabel("")
        self.lbl_estado_carga.setStyleSheet("color: #5C2454; font-size: 12px; font-weight: bold;")
        self.lbl_estado_carga.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)

        layout_carga.addWidget(self.lbl_estado_carga)
        layout_carga.addWidget(self.progreso)
        self.contenedor_carga.setVisible(False)
        main_layout.addWidget(self.contenedor_carga)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar y Continuar")
        self.btn_guardar.clicked.connect(self.guardar_configuracion)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        main_layout.addLayout(btn_layout)

        config = load_config()
        if config.mode == "server":
            self.rb_servidor.setChecked(True)
        elif config.mode == "terminal":
            self.rb_terminal.setChecked(True)
        else:
            self.rb_local.setChecked(True)

    def set_loading(self, is_loading: bool, message: str = ""):
        if is_loading:
            self.contenedor_carga.setVisible(True)
            self.lbl_estado_carga.setText(message)
            self.progreso.setRange(0, 0)
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        else:
            self.contenedor_carga.setVisible(False)
            self.lbl_estado_carga.setText("")
            self.progreso.setRange(0, 100)
            self.progreso.setValue(0)
            QApplication.restoreOverrideCursor()

        self.btn_guardar.setEnabled(not is_loading)
        self.rb_servidor.setEnabled(not is_loading)
        self.rb_terminal.setEnabled(not is_loading)
        self.rb_local.setEnabled(not is_loading)

        if hasattr(self, 'input_srv_admin_pass'):
            self.input_srv_admin_pass.setEnabled(not is_loading)
            self.input_srv_app_pass.setEnabled(not is_loading)

        if hasattr(self, 'input_term_ip'):
            self.input_term_ip.setEnabled(not is_loading)
            self.input_term_port.setEnabled(not is_loading)
            self.input_term_user.setEnabled(not is_loading)
            self.input_term_pass.setEnabled(not is_loading)

    def cambiar_pestana(self):
        if self.rb_servidor.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_servidor)
            self.actualizar_deteccion_postgresql()
        elif self.rb_terminal.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_terminal)
        elif self.rb_local.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_local)

    def crear_vista_servidor(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        grupo_info = QGroupBox("Información de Red del Servidor")
        info_layout = QVBoxLayout(grupo_info)
        ip_lan = get_local_ip()
        info_layout.addWidget(QLabel(f"<b>Dirección IP Local para Terminales:</b> <span style='color: #5C2454; font-size: 14px;'>{ip_lan}</span>"))
        layout.addWidget(grupo_info)

        self.grupo_pg_estado = QGroupBox("Estado del Motor PostgreSQL")
        pg_estado_layout = QVBoxLayout(self.grupo_pg_estado)
        self.lbl_pg_detectado = QLabel("🔍 Verificando instalación de PostgreSQL...")
        self.lbl_pg_detectado.setStyleSheet("font-size: 13px; font-weight: bold;")
        pg_estado_layout.addWidget(self.lbl_pg_detectado)
        layout.addWidget(self.grupo_pg_estado)

        grupo_db = QGroupBox("Parámetros de Base de Datos PostgreSQL")
        db_layout = QVBoxLayout(grupo_db)

        db_layout.addWidget(QLabel("Contraseña de Administrador PostgreSQL ('postgres'):"))
        self.input_srv_admin_pass = QLineEdit()
        self.input_srv_admin_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_srv_admin_pass.setPlaceholderText("Contraseña del usuario postgres (por defecto: postgres o la elegida)")
        db_layout.addWidget(self.input_srv_admin_pass)

        db_layout.addWidget(QLabel("Contraseña de Aplicación ('distri_app'):"))
        self.input_srv_app_pass = QLineEdit("DistriMagik2026*")
        self.input_srv_app_pass.setEchoMode(QLineEdit.EchoMode.Password)
        db_layout.addWidget(self.input_srv_app_pass)

        layout.addWidget(grupo_db)
        layout.addStretch()

        self.actualizar_deteccion_postgresql()
        return widget

    def actualizar_deteccion_postgresql(self):
        instalado, ruta = detect_postgresql_installation()
        if instalado:
            self.lbl_pg_detectado.setText(f"🟢 PostgreSQL detectado en el equipo ({ruta})")
            self.lbl_pg_detectado.setStyleSheet("color: #2E7D32; font-size: 13px; font-weight: bold;")
        else:
            self.lbl_pg_detectado.setText("🟠 PostgreSQL no está instalado en este equipo. (Se instalará automáticamente)")
            self.lbl_pg_detectado.setStyleSheet("color: #D84315; font-size: 13px; font-weight: bold;")

    def crear_vista_terminal(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        grupo_term = QGroupBox("Datos de Conexión con el PC Servidor")
        term_layout = QVBoxLayout(grupo_term)

        term_layout.addWidget(QLabel("Dirección IP del Servidor (LAN):"))
        self.input_term_ip = QLineEdit()
        self.input_term_ip.setPlaceholderText("Ejemplo: 192.168.1.50")
        term_layout.addWidget(self.input_term_ip)

        term_layout.addWidget(QLabel("Puerto:"))
        self.input_term_port = QLineEdit("5432")
        term_layout.addWidget(self.input_term_port)

        term_layout.addWidget(QLabel("Usuario de Aplicación:"))
        self.input_term_user = QLineEdit("distri_app")
        term_layout.addWidget(self.input_term_user)

        term_layout.addWidget(QLabel("Contraseña de Aplicación:"))
        self.input_term_pass = QLineEdit("DistriMagik2026*")
        self.input_term_pass.setEchoMode(QLineEdit.EchoMode.Password)
        term_layout.addWidget(self.input_term_pass)

        layout.addWidget(grupo_term)
        layout.addStretch()
        return widget

    def crear_vista_local(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        grupo_local = QGroupBox("Modo Local (PostgreSQL Monousuario)")
        local_layout = QVBoxLayout(grupo_local)

        lbl_desc = QLabel(
            "En este modo, el sistema instala y usa PostgreSQL localmente en este computador.<br><br>"
            "<b>Características:</b><br>"
            "• Base de datos PostgreSQL completa (no SQLite)<br>"
            "• Solo accesible desde este equipo (localhost)<br>"
            "• No expone puertos en la red local<br>"
            "• No requiere configuración de firewall<br>"
            "• Ideal para un solo puesto de venta independiente"
        )
        lbl_desc.setWordWrap(True)
        local_layout.addWidget(lbl_desc)

        layout.addWidget(grupo_local)
        layout.addStretch()
        return widget

    def guardar_configuracion(self):
        if self.rb_servidor.isChecked():
            admin_pass = self.input_srv_admin_pass.text().strip() or "postgres"
            app_pass = self.input_srv_app_pass.text().strip() or "DistriMagik2026*"
            
            confirm = QMessageBox.question(
                self,
                "Confirmar Configuración de Servidor",
                "El sistema configurará una base de datos PostgreSQL.\n\n"
                f"• Contraseña 'postgres': {admin_pass}\n\n"
                "¿Desea iniciar la configuración ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

            self.set_loading(True, "Iniciando configuración del servidor...")
            strategy = ServerSetupStrategy(admin_pass, app_pass)
            self.controller.execute_strategy(strategy)

        elif self.rb_terminal.isChecked():
            host = self.input_term_ip.text().strip()
            port_text = self.input_term_port.text().strip() or "5432"
            try:
                port = int(port_text)
            except ValueError:
                QMessageBox.warning(self, "Puerto Inválido", "El puerto debe ser un número entero válido.")
                return
            user = self.input_term_user.text().strip() or "distri_app"
            password = self.input_term_pass.text().strip()

            if not host:
                QMessageBox.warning(self, "IP requerida", "Por favor ingrese la IP del servidor.")
                return

            self.set_loading(True, f"Probando conexión con el servidor {host}:{port}...")
            strategy = TerminalSetupStrategy(host, port, user, password)
            self.controller.execute_strategy(strategy)

        else:  # Modo local
            self.set_loading(True, "Configurando entorno local...")
            strategy = LocalSetupStrategy()
            self.controller.execute_strategy(strategy)

    def _on_progress(self, msg: str):
        self.lbl_estado_carga.setText(msg)

    def _on_success(self, msg: str):
        self.set_loading(False)
        from app.services.server_setup_service import get_local_ip
        ip = get_local_ip()
        
        if self.rb_servidor.isChecked():
            msg += f"\n\n📡 Servidor listo en:\n   IP: {ip}\n   Puerto: 5432\n\nComparta esta IP con las terminales para conectarse."
        elif self.rb_local.isChecked():
            msg += f"\n\n💻 Modo Local activo en:\n   Host: localhost (127.0.0.1)\n   Puerto: 5432 (solo local)\n\nPostgreSQL instalado localmente, sin exposición en red."
        QMessageBox.information(self, "Configuración Exitosa", f"{msg}\n\nIniciando sistema...")
        self.configuracion_finalizada.emit()

    def _on_error(self, msg: str):
        self.set_loading(False)
        QMessageBox.critical(self, "Error de Configuración", msg)
