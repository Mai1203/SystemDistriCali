from typing import Tuple, Optional
from PyQt6.QtCore import pyqtSignal, QObject
from app.database.config import DatabaseConfig
from app.services.connection_service import test_connection
from app.services.server_setup_service import (
    provision_database,
    find_bundled_postgres_installer,
    install_postgresql_silent,
    detect_postgresql_installation,
)
from app.database.manager import db_manager
from app.database.database import init_db

class SetupSignals(QObject):
    progress = pyqtSignal(str)

class SetupStrategy:
    def __init__(self):
        self.signals = SetupSignals()
    
    def emit_progress(self, msg: str):
        self.signals.progress.emit(msg)

    def execute(self) -> Tuple[bool, str, Optional[DatabaseConfig]]:
        raise NotImplementedError

class LocalSetupStrategy(SetupStrategy):
    """Modo Local: PostgreSQL instalado localmente, solo accesible desde localhost."""
    def execute(self) -> Tuple[bool, str, Optional[DatabaseConfig]]:
        self.emit_progress("Configurando modo Local (PostgreSQL local)...")
        
        instalado, _ = detect_postgresql_installation()
        if not instalado:
            self.emit_progress("Instalando PostgreSQL 15 (esto puede tomar 1 o 2 minutos)...")
            installer_path = find_bundled_postgres_installer()
            if not installer_path:
                return False, "Instalador de PostgreSQL no encontrado. Colóquelo en la carpeta correcta.", None
            
            ok_inst, msg_inst = install_postgresql_silent(installer_path, "postgres", 5432)
            if not ok_inst:
                return False, f"Error instalando PostgreSQL: {msg_inst}", None

        self.emit_progress("Configurando base de datos y usuario local...")
        # expose_network=False: solo localhost, no expone puerto en LAN
        ok_prov, msg_prov = provision_database(
            admin_user="postgres",
            admin_password="postgres",
            host="localhost",
            port=5432,
            db_name="systemdistrimagik",
            app_user="distri_app",
            app_password="DistriMagik2026*",
            expose_network=False,
        )
        if not ok_prov:
            return False, f"Error aprovisionando la BD: {msg_prov}", None

        config = DatabaseConfig(
            mode="local",
            host="localhost",
            port=5432,
            database="systemdistrimagik",
            user="distri_app",
            password="DistriMagik2026*",
            configured=True,
        )

        self.emit_progress("Creando estructura inicial y datos por defecto...")
        try:
            db_manager.initialize(config)
            init_db()
        except Exception as e:
            return False, f"Error inicializando tablas: {e}", None

        return True, "Modo Local (PostgreSQL) configurado exitosamente.", config

class TerminalSetupStrategy(SetupStrategy):
    def __init__(self, host: str, port: int, user: str, password: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def execute(self) -> Tuple[bool, str, Optional[DatabaseConfig]]:
        self.emit_progress(f"Verificando conexión con el servidor en {self.host}:{self.port}...")
        config = DatabaseConfig(
            mode="terminal",
            host=self.host,
            port=self.port,
            database="systemdistrimagik",
            user=self.user,
            password=self.password,
            configured=True,
        )
        ok, msg = test_connection(config, timeout_seconds=4)
        if not ok:
            return False, f"Fallo la prueba de conexión: {msg}", config
        return True, "Conexión con el servidor exitosa.", config

class ServerSetupStrategy(SetupStrategy):
    def __init__(self, admin_pass: str, app_pass: str):
        super().__init__()
        self.admin_pass = admin_pass or "postgres"
        self.app_pass = app_pass or "DistriMagik2026*"

    def execute(self) -> Tuple[bool, str, Optional[DatabaseConfig]]:
        instalado, _ = detect_postgresql_installation()
        if not instalado:
            self.emit_progress("Instalando PostgreSQL 15 (esto puede tomar 1 o 2 minutos)...")
            installer_path = find_bundled_postgres_installer()
            if not installer_path:
                return False, "Instalador de PostgreSQL no encontrado. Colóquelo en la carpeta correcta.", None
            
            ok_inst, msg_inst = install_postgresql_silent(installer_path, self.admin_pass, 5432)
            if not ok_inst:
                return False, f"Error instalando PostgreSQL: {msg_inst}", None

        self.emit_progress("Configurando base de datos limpia y usuario de la aplicación...")
        # expose_network=True: permite conexiones desde LAN
        ok_prov, msg_prov = provision_database(
            admin_user="postgres",
            admin_password=self.admin_pass,
            host="localhost",
            port=5432,
            db_name="systemdistrimagik",
            app_user="distri_app",
            app_password=self.app_pass,
            expose_network=True,
        )
        if not ok_prov:
            return False, f"Error aprovisionando la BD: {msg_prov}", None

        config = DatabaseConfig(
            mode="server",
            host="localhost",
            port=5432,
            database="systemdistrimagik",
            user="distri_app",
            password=self.app_pass,
            configured=True,
        )

        self.emit_progress("Creando estructura inicial y datos por defecto...")
        try:
            db_manager.initialize(config)
            init_db()
        except Exception as e:
            return False, f"Error inicializando tablas: {e}", None

        return True, "Servidor PostgreSQL configurado exitosamente.", config