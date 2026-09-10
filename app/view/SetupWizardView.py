from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QLineEdit,
    QStackedWidget,
    QMessageBox,
    QFrame,
    QGroupBox,
    QCheckBox,
    QProgressBar,
)
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from app.database.config import DatabaseConfig, save_config, load_config, DEFAULT_SQLITE_PATH
from app.database.engine import reset_engine
from app.database.database import init_db
from app.services.connection_service import test_connection
from app.services.server_setup_service import (
    get_local_ip,
    detect_postgresql_installation,
    is_postgresql_service_running,
    provision_database,
)
from app.services.migration_service import migrate_sqlite_to_postgres
from app.utils.logger import logger


class SetupWizardView(QWidget):
    configuracion_finalizada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
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
            QPushButton#btnSecundario {
                background-color: #ECE5EB;
                color: #5C2454;
                border: 1px solid #D0C2CE;
            }
            QPushButton#btnSecundario:hover {
                background-color: #DFD4DE;
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
        """)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(15)

        # Encabezado
        lbl_titulo = QLabel("Configuración Inicial del Sistema")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #5C2454;")
        
        lbl_subtitulo = QLabel(
            "Seleccione el modo en que operará este computador dentro de su negocio."
        )
        lbl_subtitulo.setStyleSheet("color: #666666; font-size: 13px;")

        main_layout.addWidget(lbl_titulo)
        main_layout.addWidget(lbl_subtitulo)

        # Contenedor de selección de modo
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

        # Vistas apiladas para cada modo
        self.stacked_widget = QStackedWidget()
        self.vista_servidor = self.crear_vista_servidor()
        self.vista_terminal = self.crear_vista_terminal()
        self.vista_local = self.crear_vista_local()

        self.stacked_widget.addWidget(self.vista_servidor)
        self.stacked_widget.addWidget(self.vista_terminal)
        self.stacked_widget.addWidget(self.vista_local)
        main_layout.addWidget(self.stacked_widget, 1)

        # Barra de progreso para migraciones o aprovisionamiento
        self.progreso = QProgressBar()
        self.progreso.setVisible(False)
        self.progreso.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D0C2CE;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #5C2454;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progreso)

        # Botones de acción inferiores
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar y Continuar")
        self.btn_guardar.clicked.connect(self.guardar_configuracion)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        main_layout.addLayout(btn_layout)

        # Cargar configuración existente o por defecto
        config = load_config()
        if config.mode == "server":
            self.rb_servidor.setChecked(True)
        elif config.mode == "terminal":
            self.rb_terminal.setChecked(True)
        else:
            self.rb_local.setChecked(True)

    def cambiar_pestana(self):
        if self.rb_servidor.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_servidor)
        elif self.rb_terminal.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_terminal)
        elif self.rb_local.isChecked():
            self.stacked_widget.setCurrentWidget(self.vista_local)

    # ─────────────────────────────────────────────────────────────
    # VISTA SERVIDOR
    # ─────────────────────────────────────────────────────────────
    def crear_vista_servidor(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        grupo_info = QGroupBox("Información de Red del Servidor")
        info_layout = QVBoxLayout(grupo_info)
        
        ip_lan = get_local_ip()
        self.lbl_ip_info = QLabel(f"<b>Dirección IP Local para Terminales:</b> <span style='color: #5C2454; font-size: 14px;'>{ip_lan}</span>")
        info_layout.addWidget(self.lbl_ip_info)
        layout.addWidget(grupo_info)

        grupo_db = QGroupBox("Parámetros de Base de Datos PostgreSQL")
        db_layout = QVBoxLayout(grupo_db)

        # Credenciales de administración para configurar
        db_layout.addWidget(QLabel("Contraseña de Administrador PostgreSQL ('postgres'):"))
        self.input_srv_admin_pass = QLineEdit()
        self.input_srv_admin_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_srv_admin_pass.setPlaceholderText("Contraseña del usuario postgres instalada en este equipo")
        db_layout.addWidget(self.input_srv_admin_pass)

        # Contraseña de la app
        db_layout.addWidget(QLabel("Contraseña de Aplicación ('distri_app'):"))
        self.input_srv_app_pass = QLineEdit("DistriMagik2026*")
        self.input_srv_app_pass.setEchoMode(QLineEdit.EchoMode.Password)
        db_layout.addWidget(self.input_srv_app_pass)

        self.chk_migrar_sqlite = QCheckBox("Importar datos existentes desde la base SQLite local a PostgreSQL")
        self.chk_migrar_sqlite.setChecked(True)
        db_layout.addWidget(self.chk_migrar_sqlite)

        btn_srv_probar = QPushButton("Configurar / Inicializar Servidor")
        btn_srv_probar.setObjectName("btnSecundario")
        btn_srv_probar.clicked.connect(self.aprovisionar_servidor)
        db_layout.addWidget(btn_srv_probar)

        self.lbl_srv_estado = QLabel("")
        db_layout.addWidget(self.lbl_srv_estado)

        layout.addWidget(grupo_db)
        layout.addStretch()
        return widget

    def aprovisionar_servidor(self):
        admin_pass = self.input_srv_admin_pass.text().strip()
        app_pass = self.input_srv_app_pass.text().strip() or "DistriMagik2026*"

        if not admin_pass:
            QMessageBox.warning(self, "Contraseña requerida", "Por favor ingrese la contraseña del usuario 'postgres'.")
            return

        self.lbl_srv_estado.setText("⏳ Configurando base de datos y usuario de red...")
        self.lbl_srv_estado.setStyleSheet("color: #5C2454;")

        ok, msg = provision_database(
            admin_user="postgres",
            admin_password=admin_pass,
            host="localhost",
            port=5432,
            db_name="systemdistrimagik",
            app_user="distri_app",
            app_password=app_pass,
        )

        if not ok:
            self.lbl_srv_estado.setText(f"❌ {msg}")
            self.lbl_srv_estado.setStyleSheet("color: #B00020;")
            QMessageBox.critical(self, "Error de Configuración", msg)
            return

        # Inicializar tablas
        temp_config = DatabaseConfig(
            mode="server",
            engine_type="postgresql",
            host="localhost",
            port=5432,
            database="systemdistrimagik",
            user="distri_app",
            password=app_pass,
            configured=True,
        )
        reset_engine(temp_config)
        init_db()

        # Migración opcional si seleccionada
        if self.chk_migrar_sqlite.isChecked():
            from app.database.config import DEFAULT_SQLITE_PATH
            if Path(DEFAULT_SQLITE_PATH).exists():
                self.lbl_srv_estado.setText("⏳ Migrando datos históricos de SQLite a PostgreSQL...")
                ok_mig, msg_mig = migrate_sqlite_to_postgres(DEFAULT_SQLITE_PATH, temp_config)
                if not ok_mig:
                    QMessageBox.warning(self, "Aviso de migración", f"Base creada pero ocurrió un detalle: {msg_mig}")

        self.lbl_srv_estado.setText("✅ Servidor PostgreSQL configurado y tablas inicializadas con éxito.")
        self.lbl_srv_estado.setStyleSheet("color: #2E7D32; font-weight: bold;")
        QMessageBox.information(self, "Éxito", "El servidor ha sido configurado y está listo para recibir terminales.")

    # ─────────────────────────────────────────────────────────────
    # VISTA TERMINAL
    # ─────────────────────────────────────────────────────────────
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

        btn_term_test = QPushButton("Probar Conexión con el Servidor")
        btn_term_test.setObjectName("btnSecundario")
        btn_term_test.clicked.connect(self.probar_conexion_terminal)
        term_layout.addWidget(btn_term_test)

        self.lbl_term_estado = QLabel("")
        self.lbl_term_estado.setWordWrap(True)
        term_layout.addWidget(self.lbl_term_estado)

        layout.addWidget(grupo_term)
        layout.addStretch()
        return widget

    def probar_conexion_terminal(self):
        host = self.input_term_ip.text().strip()
        port = int(self.input_term_port.text().strip() or 5432)
        user = self.input_term_user.text().strip() or "distri_app"
        password = self.input_term_pass.text().strip()

        if not host:
            QMessageBox.warning(self, "IP Requerida", "Por favor ingrese la IP del servidor.")
            return

        self.lbl_term_estado.setText("⏳ Probando conexión...")
        self.lbl_term_estado.setStyleSheet("color: #5C2454;")

        test_cfg = DatabaseConfig(
            mode="terminal",
            engine_type="postgresql",
            host=host,
            port=port,
            database="systemdistrimagik",
            user=user,
            password=password,
        )

        ok, msg = test_connection(test_cfg)
        if ok:
            self.lbl_term_estado.setText(f"✅ {msg}")
            self.lbl_term_estado.setStyleSheet("color: #2E7D32; font-weight: bold;")
        else:
            self.lbl_term_estado.setText(f"❌ {msg}")
            self.lbl_term_estado.setStyleSheet("color: #B00020;")

    # ─────────────────────────────────────────────────────────────
    # VISTA LOCAL
    # ─────────────────────────────────────────────────────────────
    def crear_vista_local(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        grupo_local = QGroupBox("Modo Local Independiente")
        local_layout = QVBoxLayout(grupo_local)

        lbl_desc = QLabel(
            "En este modo, el sistema utiliza una base de datos SQLite directamente en este computador.<br><br>"
            "<b>Ubicación:</b> " + DEFAULT_SQLITE_PATH + "<br><br>"
            "<i>Nota: Este modo no permite conectar otros computadores simultáneamente por red.</i>"
        )
        lbl_desc.setWordWrap(True)
        local_layout.addWidget(lbl_desc)

        layout.addWidget(grupo_local)
        layout.addStretch()
        return widget

    # ─────────────────────────────────────────────────────────────
    # GUARDAR Y FINALIZAR
    # ─────────────────────────────────────────────────────────────
    def guardar_configuracion(self):
        if self.rb_servidor.isChecked():
            app_pass = self.input_srv_app_pass.text().strip() or "DistriMagik2026*"
            config = DatabaseConfig(
                mode="server",
                engine_type="postgresql",
                host="localhost",
                port=5432,
                database="systemdistrimagik",
                user="distri_app",
                password=app_pass,
                configured=True,
            )
            # Probar conexión antes de guardar
            ok, msg = test_connection(config)
            if not ok:
                QMessageBox.warning(
                    self,
                    "Servidor no verificado",
                    "No se pudo conectar a la base local PostgreSQL. Asegúrese de haber hecho clic en 'Configurar / Inicializar Servidor' primero.\n\n" + msg
                )
                return

        elif self.rb_terminal.isChecked():
            host = self.input_term_ip.text().strip()
            port = int(self.input_term_port.text().strip() or 5432)
            user = self.input_term_user.text().strip() or "distri_app"
            password = self.input_term_pass.text().strip()

            if not host:
                QMessageBox.warning(self, "IP requerida", "Por favor ingrese la IP del servidor.")
                return

            config = DatabaseConfig(
                mode="terminal",
                engine_type="postgresql",
                host=host,
                port=port,
                database="systemdistrimagik",
                user=user,
                password=password,
                configured=True,
            )
            ok, msg = test_connection(config)
            if not ok:
                resp = QMessageBox.question(
                    self,
                    "Conexión no verificada",
                    f"La prueba de conexión falló con el siguiente error:\n\n{msg}\n\n¿Desea guardar la configuración de todas formas?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return

        else:  # Modo local
            config = DatabaseConfig(
                mode="local",
                engine_type="sqlite",
                sqlite_path=DEFAULT_SQLITE_PATH,
                configured=True,
            )

        # Guardar en config.json
        if save_config(config):
            reset_engine(config)
            init_db()
            logger.info(f"Configuración establecida exitosamente en modo {config.mode}.")
            QMessageBox.information(self, "Configuración Exitosa", "La configuración ha sido guardada. Iniciando sistema...")
            self.configuracion_finalizada.emit()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar el archivo de configuración.")
