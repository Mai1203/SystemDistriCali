import json
import os
import base64
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import urllib.parse
from app.utils.logger import logger

os.environ.setdefault("PGCLIENTENCODING", "utf-8")
APP_DATA_DIR = Path(os.getenv("APPDATA") or os.path.expanduser("~/.local/share")) / "SystemDistriMagik"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE_PATH = APP_DATA_DIR / "config.json"
DEFAULT_SQLITE_PATH = str(APP_DATA_DIR / "systemdistrimagik.db")


def _obfuscate(text: str) -> str:
    """Ofuscación simple para no guardar contraseñas en texto plano directo."""
    if not text:
        return ""
    try:
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")
    except Exception:
        return text


def _deobfuscate(text: str) -> str:
    """Recupera el texto ofuscado."""
    if not text:
        return ""
    try:
        return base64.b64decode(text.encode("utf-8")).decode("utf-8")
    except Exception:
        return text


@dataclass
class DatabaseConfig:
    mode: str = "local"  # "server", "terminal", "local"
    engine_type: str = "sqlite"  # "postgresql", "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "systemdistrimagik"
    user: str = "distri_app"
    password: str = ""
    sqlite_path: str = DEFAULT_SQLITE_PATH
    configured: bool = False

    def to_dict(self, obfuscate_pass: bool = True) -> dict:
        data = asdict(self)
        if obfuscate_pass and self.password:
            data["password"] = _obfuscate(self.password)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "DatabaseConfig":
        raw_pass = data.get("password", "")
        # Desofuscar si viene en base64
        password = _deobfuscate(raw_pass) if raw_pass else ""
        return cls(
            mode=data.get("mode", "local"),
            engine_type=data.get("engine_type", "sqlite"),
            host=data.get("host", "localhost"),
            port=int(data.get("port", 5432)),
            database=data.get("database", "systemdistrimagik"),
            user=data.get("user", "distri_app"),
            password=password,
            sqlite_path=data.get("sqlite_path", DEFAULT_SQLITE_PATH),
            configured=data.get("configured", False),
        )

    def get_connection_url(self) -> str:
        """Genera la URL de conexión SQLAlchemy adecuada."""
        if self.mode == "local" or self.engine_type == "sqlite":
            normalized_path = Path(self.sqlite_path).as_posix()
            return f"sqlite:///{normalized_path}"

        # PostgreSQL (para server o terminal)
        user = urllib.parse.quote_plus(self.user or "distri_app")
        host = self.host or "localhost"
        port = self.port or 5432
        db_name = self.database or "systemdistrimagik"

        if self.password:
            password = urllib.parse.quote_plus(self.password)
            return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}?client_encoding=utf8"
        return f"postgresql+psycopg2://{user}@{host}:{port}/{db_name}?client_encoding=utf8"


def load_config() -> DatabaseConfig:
    """Carga la configuración desde config.json. Si no existe, devuelve la configuración por defecto."""
    if not CONFIG_FILE_PATH.exists():
        logger.info(f"Archivo de configuración no encontrado en {CONFIG_FILE_PATH}. Usando valores por defecto.")
        # Si ya existe un sqlite anterior, marcar como local existente
        if Path(DEFAULT_SQLITE_PATH).exists():
            return DatabaseConfig(mode="local", engine_type="sqlite", configured=True)
        return DatabaseConfig(mode="local", engine_type="sqlite", configured=False)

    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        config = DatabaseConfig.from_dict(data)
        logger.info(f"Configuración cargada exitosamente: modo={config.mode}, motor={config.engine_type}")
        return config
    except Exception as e:
        logger.error(f"Error al leer config.json: {e}. Usando configuración por defecto.")
        return DatabaseConfig(mode="local", engine_type="sqlite", configured=False)


def save_config(config: DatabaseConfig) -> bool:
    """Guarda la configuración en config.json de manera segura."""
    try:
        config.configured = True
        data = config.to_dict(obfuscate_pass=True)
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Configuración guardada en {CONFIG_FILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar config.json: {e}")
        return False


def is_configured() -> bool:
    """Verifica si el sistema ya fue configurado previamente."""
    if not CONFIG_FILE_PATH.exists():
        # Si el archivo SQLite tradicional ya existe, se considera configurado localmente
        if Path(DEFAULT_SQLITE_PATH).exists():
            return True
        return False
    config = load_config()
    return config.configured
