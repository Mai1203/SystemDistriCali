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
    QApplication,
)
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QCursor

from app.database.config import DatabaseConfig, save_config, load_config, DEFAULT_SQLITE_PATH
from app.database.engine import reset_engine
from app.database.database import init_db
from app.services.connection_service import test_connection
from app.services.server_setup_service import (
    get_local_ip,
    detect_postgresql_installation,
    is_postgresql_service_running,
    provision_database,
    find_bundled_postgres_installer,
    install_postgresql_silent,
)
from app.services.migration_service import migrate_sqlite_to_postgres
from app.utils.logger import logger


class WorkerThread(QThread):
    """Hilo genérico de fondo para operaciones que puedan bloquear la interfaz."""
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            res = self.func(*self.args, **self.kwargs)
            self.finished_signal.emit(res)
        except Exception as e:
            logger.exception(f"Error en WorkerThread: {e}")
            self.error_signal.emit(str(e))


class SetupWizardView(QWidget):
    configuracion_finalizada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
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

        # Barra de progreso y estado de carga
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

    def set_loading(self, is_loading: bool, message: str = ""):
        """Activa o desactiva los indicadores visuales de carga en la interfaz."""
        if is_loading:
            self.contenedor_carga.setVisible(True)
            self.lbl_estado_carga.setText(message)
            self.progreso.setRange(0, 0)  # Modo indeterminado / animado continuo
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        else:
            self.contenedor_carga.setVisible(False)
            self.lbl_estado_carga.setText("")
            self.progreso.setRange(0, 100)
            self.progreso.setValue(0)
            QApplication.restoreOverrideCursor()

        # Deshabilitar/habilitar controles para prevenir doble envío
        self.btn_guardar.setEnabled(not is_loading)
        self.rb_servidor.setEnabled(not is_loading)
        self.rb_terminal.setEnabled(not is_loading)
        self.rb_local.setEnabled(not is_loading)

        if hasattr(self, 'btn_srv_probar'):
            self.btn_srv_probar.setEnabled(not is_loading)
            self.input_srv_admin_pass.setEnabled(not is_loading)
            self.input_srv_app_pass.setEnabled(not is_loading)
            self.chk_migrar_sqlite.setEnabled(not is_loading)

        if hasattr(self, 'btn_term_test'):
            self.btn_term_test.setEnabled(not is_loading)
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

        # Panel de Estado / Instalación de PostgreSQL
        self.grupo_pg_estado = QGroupBox("Estado del Motor PostgreSQL")
        pg_estado_layout = QVBoxLayout(self.grupo_pg_estado)

        self.lbl_pg_detectado = QLabel("🔍 Verificando instalación de PostgreSQL...")
        self.lbl_pg_detectado.setStyleSheet("font-size: 13px; font-weight: bold;")
        pg_estado_layout.addWidget(self.lbl_pg_detectado)

        self.btn_instalar_pg = QPushButton("🚀 Instalar PostgreSQL 15 en Segundo Plano")
        self.btn_instalar_pg.setObjectName("btnSecundario")
        self.btn_instalar_pg.setStyleSheet("""
            QPushButton#btnSecundario {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton#btnSecundario:hover {
                background-color: #388E3C;
            }
        """)
        self.btn_instalar_pg.clicked.connect(self.instalar_postgresql_servidor)
        self.btn_instalar_pg.setVisible(False)
        pg_estado_layout.addWidget(self.btn_instalar_pg)

        layout.addWidget(self.grupo_pg_estado)

        grupo_db = QGroupBox("Parámetros de Base de Datos PostgreSQL")
        db_layout = QVBoxLayout(grupo_db)

        # Credenciales de administración para configurar
        db_layout.addWidget(QLabel("Contraseña de Administrador PostgreSQL ('postgres'):"))
        self.input_srv_admin_pass = QLineEdit()
        self.input_srv_admin_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_srv_admin_pass.setPlaceholderText("Contraseña del usuario postgres (por defecto: postgres o la elegida)")
        db_layout.addWidget(self.input_srv_admin_pass)

        # Contraseña de la app
        db_layout.addWidget(QLabel("Contraseña de Aplicación ('distri_app'):"))
        self.input_srv_app_pass = QLineEdit("DistriMagik2026*")
        self.input_srv_app_pass.setEchoMode(QLineEdit.EchoMode.Password)
        db_layout.addWidget(self.input_srv_app_pass)

        self.chk_migrar_sqlite = QCheckBox("Importar datos existentes desde la base SQLite local a PostgreSQL")
        self.chk_migrar_sqlite.setChecked(True)
        db_layout.addWidget(self.chk_migrar_sqlite)

        self.btn_srv_probar = QPushButton("Configurar / Inicializar Servidor")
        self.btn_srv_probar.setObjectName("btnSecundario")
        self.btn_srv_probar.clicked.connect(self.aprovisionar_servidor)
        db_layout.addWidget(self.btn_srv_probar)

        self.lbl_srv_estado = QLabel("")
        self.lbl_srv_estado.setWordWrap(True)
        db_layout.addWidget(self.lbl_srv_estado)

        layout.addWidget(grupo_db)
        layout.addStretch()

        self.actualizar_deteccion_postgresql()
        return widget

    def actualizar_deteccion_postgresql(self):
        """Verifica si PostgreSQL está instalado en el equipo y actualiza la UI."""
        instalado, ruta = detect_postgresql_installation()
        if instalado:
            self.lbl_pg_detectado.setText(f"🟢 PostgreSQL detectado en el equipo ({ruta})")
            self.lbl_pg_detectado.setStyleSheet("color: #2E7D32; font-size: 13px; font-weight: bold;")
            self.btn_instalar_pg.setVisible(False)
        else:
            self.lbl_pg_detectado.setText("🟠 PostgreSQL no está instalado en este equipo.")
            self.lbl_pg_detectado.setStyleSheet("color: #D84315; font-size: 13px; font-weight: bold;")
            self.btn_instalar_pg.setVisible(True)

    def instalar_postgresql_servidor(self):
        """Inicia la instalación silenciosa de PostgreSQL 15 en segundo plano."""
        installer_path = find_bundled_postgres_installer()
        if not installer_path:
            QMessageBox.warning(
                self,
                "Instalador no encontrado",
                "No se encontró el instalador de PostgreSQL 15 en la carpeta 'prerequisites/'.\n\n"
                "Por favor asegúrese de colocar el archivo 'postgresql-15.x-windows-x64.exe' en la carpeta de la aplicación."
            )
            return

        admin_pass = self.input_srv_admin_pass.text().strip() or "postgres"
        self.input_srv_admin_pass.setText(admin_pass)

        confirm = QMessageBox.question(
            self,
            "Confirmar Instalación de PostgreSQL 15",
            "El sistema instalará el motor de PostgreSQL 15 como servicio de Windows en segundo plano.\n\n"
            f"• Contraseña de 'postgres': {admin_pass}\n"
            "• Puerto: 5432\n\n"
            "¿Desea iniciar la instalación ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.set_loading(True, "⏳ Instalando servicio PostgreSQL 15 en segundo plano (puede demorar aprox. 1 minuto)...")
        self.lbl_srv_estado.setText("⏳ Instalando PostgreSQL 15 en segundo plano... Por favor acepte el diálogo de permisos de Windows.")
        self.lbl_srv_estado.setStyleSheet("color: #5C2454; font-weight: bold;")

        def _task():
            ok_inst, msg_inst = install_postgresql_silent(
                installer_path=installer_path,
                admin_password=admin_pass,
                port=5432
            )
            return ok_inst, msg_inst

        self._worker = WorkerThread(_task)
        self._worker.finished_signal.connect(self._on_instalacion_pg_finalizada)
        self._worker.error_signal.connect(self._on_aprovisionar_error)
        self._worker.start()

    def _on_instalacion_pg_finalizada(self, result):
        self.set_loading(False)
        ok_inst, msg_inst = result
        self.actualizar_deteccion_postgresql()

        if not ok_inst:
            self.lbl_srv_estado.setText(f"❌ {msg_inst}")
            self.lbl_srv_estado.setStyleSheet("color: #B00020; font-weight: bold;")
            QMessageBox.critical(self, "Error en Instalación", msg_inst)
            return

        self.lbl_srv_estado.setText("✅ PostgreSQL 15 instalado. Procediendo a configurar base de datos y Firewall...")
        self.lbl_srv_estado.setStyleSheet("color: #2E7D32; font-weight: bold;")

        # Aprovisionar inmediatamente de forma automática
        self.aprovisionar_servidor()

    def aprovisionar_servidor(self):
        admin_pass = self.input_srv_admin_pass.text().strip()
        app_pass = self.input_srv_app_pass.text().strip() or "DistriMagik2026*"
        migrar_sqlite = self.chk_migrar_sqlite.isChecked()

        if not admin_pass:
            QMessageBox.warning(self, "Contraseña requerida", "Por favor ingrese la contraseña del usuario 'postgres'.")
            return

        self.lbl_srv_estado.setText("⏳ Configurando base de datos, reglas de red y Firewall de Windows...")
        self.lbl_srv_estado.setStyleSheet("color: #5C2454; font-weight: bold;")
        self.btn_srv_probar.setText("⏳ Configurando Servidor...")
        self.set_loading(True, "⏳ Configurando base de datos, reglas de red y Firewall de Windows...")

        def _task():
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
                return False, msg, None

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
            mig_msg = None
            if migrar_sqlite and Path(DEFAULT_SQLITE_PATH).exists():
                ok_mig, msg_mig = migrate_sqlite_to_postgres(DEFAULT_SQLITE_PATH, temp_config)
                if not ok_mig:
                    mig_msg = msg_mig

            return True, "Servidor configurado correctamente.", mig_msg

        self._worker = WorkerThread(_task)
        self._worker.finished_signal.connect(self._on_aprovisionar_finalizado)
        self._worker.error_signal.connect(self._on_aprovisionar_error)
        self._worker.start()

    def _on_aprovisionar_finalizado(self, result):
        self.set_loading(False)
        self.btn_srv_probar.setText("Configurar / Inicializar Servidor")
        ok, msg, mig_msg = result

        if not ok:
            self.lbl_srv_estado.setText(f"❌ {msg}")
            self.lbl_srv_estado.setStyleSheet("color: #B00020; font-weight: bold;")
            QMessageBox.critical(self, "Error de Configuración", msg)
            return

        if mig_msg:
            QMessageBox.warning(self, "Aviso de migración", f"Base creada pero ocurrió un detalle con los datos existentes: {mig_msg}")

        self.lbl_srv_estado.setText("✅ Servidor PostgreSQL, Firewall y reglas de red listos para recibir terminales.")
        self.lbl_srv_estado.setStyleSheet("color: #2E7D32; font-weight: bold;")
        QMessageBox.information(
            self,
            "Servidor Configurado Exitosamente",
            "El servidor PostgreSQL, la regla del Firewall de Windows (puerto 5432) y las reglas de red (pg_hba) han sido configuradas automáticamente.\n\n"
            f"Las terminales pueden conectarse usando la IP: {get_local_ip()}"
        )

    def _on_aprovisionar_error(self, err_msg):
        self.set_loading(False)
        self.btn_srv_probar.setText("Configurar / Inicializar Servidor")
        self.lbl_srv_estado.setText(f"❌ Error inesperado: {err_msg}")
        self.lbl_srv_estado.setStyleSheet("color: #B00020; font-weight: bold;")
        QMessageBox.critical(self, "Error de Configuración", f"Ocurrió un error inesperado al configurar el servidor:\n{err_msg}")

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

        self.btn_term_test = QPushButton("Probar Conexión con el Servidor")
        self.btn_term_test.setObjectName("btnSecundario")
        self.btn_term_test.clicked.connect(self.probar_conexion_terminal)
        term_layout.addWidget(self.btn_term_test)

        self.lbl_term_estado = QLabel("")
        self.lbl_term_estado.setWordWrap(True)
        term_layout.addWidget(self.lbl_term_estado)

        layout.addWidget(grupo_term)
        layout.addStretch()
        return widget

    def probar_conexion_terminal(self):
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
            QMessageBox.warning(self, "IP Requerida", "Por favor ingrese la IP del servidor.")
            return

        self.lbl_term_estado.setText(f"⏳ Conectando con {host}:{port}... Por favor espere...")
        self.lbl_term_estado.setStyleSheet("color: #5C2454; font-weight: bold;")
        self.btn_term_test.setText("⏳ Probando Conexión...")
        self.set_loading(True, f"⏳ Probando conexión con el servidor en {host}:{port}...")

        test_cfg = DatabaseConfig(
            mode="terminal",
            engine_type="postgresql",
            host=host,
            port=port,
            database="systemdistrimagik",
            user=user,
            password=password,
        )

        def _task():
            return test_connection(test_cfg)

        self._worker = WorkerThread(_task)
        self._worker.finished_signal.connect(self._on_probar_conexion_finalizado)
        self._worker.error_signal.connect(self._on_probar_conexion_error)
        self._worker.start()

    def _on_probar_conexion_finalizado(self, result):
        self.set_loading(False)
        self.btn_term_test.setText("Probar Conexión con el Servidor")
        ok, msg = result
        if ok:
            self.lbl_term_estado.setText(f"✅ {msg}")
            self.lbl_term_estado.setStyleSheet("color: #2E7D32; font-weight: bold;")
        else:
            self.lbl_term_estado.setText(f"❌ {msg}")
            self.lbl_term_estado.setStyleSheet("color: #B00020; font-weight: bold;")

    def _on_probar_conexion_error(self, err_msg):
        self.set_loading(False)
        self.btn_term_test.setText("Probar Conexión con el Servidor")
        self.lbl_term_estado.setText(f"❌ Error inesperado: {err_msg}")
        self.lbl_term_estado.setStyleSheet("color: #B00020; font-weight: bold;")

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

            self.btn_guardar.setText("⏳ Verificando Servidor...")
            self.set_loading(True, "⏳ Verificando conexión local con el servidor PostgreSQL...")

            def _test_srv():
                return test_connection(config)

            def _on_done(result):
                self.set_loading(False)
                self.btn_guardar.setText("Guardar y Continuar")
                ok, msg = result
                if not ok:
                    QMessageBox.warning(
                        self,
                        "Servidor no verificado",
                        "No se pudo conectar a la base local PostgreSQL. Asegúrese de haber hecho clic en 'Configurar / Inicializar Servidor' primero.\n\n" + msg
                    )
                    return
                self._persistir_configuracion(config)

            self._worker = WorkerThread(_test_srv)
            self._worker.finished_signal.connect(_on_done)
            self._worker.error_signal.connect(lambda err: (self.set_loading(False), self.btn_guardar.setText("Guardar y Continuar"), QMessageBox.critical(self, "Error", f"Error al verificar: {err}")))
            self._worker.start()

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

            self.btn_guardar.setText("⏳ Verificando Conexión...")
            self.set_loading(True, f"⏳ Verificando conexión con el servidor en {host}:{port}...")

            def _test_term():
                return test_connection(config)

            def _on_done_term(result):
                self.set_loading(False)
                self.btn_guardar.setText("Guardar y Continuar")
                ok, msg = result
                if not ok:
                    resp = QMessageBox.question(
                        self,
                        "Conexión no verificada",
                        f"La prueba de conexión falló con el siguiente error:\n\n{msg}\n\n¿Desea guardar la configuración de todas formas?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if resp != QMessageBox.StandardButton.Yes:
                        return
                self._persistir_configuracion(config)

            self._worker = WorkerThread(_test_term)
            self._worker.finished_signal.connect(_on_done_term)
            self._worker.error_signal.connect(lambda err: (self.set_loading(False), self.btn_guardar.setText("Guardar y Continuar"), QMessageBox.critical(self, "Error", f"Error al verificar: {err}")))
            self._worker.start()

        else:  # Modo local
            config = DatabaseConfig(
                mode="local",
                engine_type="sqlite",
                sqlite_path=DEFAULT_SQLITE_PATH,
                configured=True,
            )
            self._persistir_configuracion(config)

    def _persistir_configuracion(self, config: DatabaseConfig):
        # Guardar en config.json
        if save_config(config):
            reset_engine(config)
            init_db()
            logger.info(f"Configuración establecida exitosamente en modo {config.mode}.")
            QMessageBox.information(self, "Configuración Exitosa", "La configuración ha sido guardada. Iniciando sistema...")
            self.configuracion_finalizada.emit()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar el archivo de configuración.")

