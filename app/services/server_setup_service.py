import os
import urllib.parse
import socket
import subprocess
from pathlib import Path
from typing import Tuple, List, Optional
from sqlalchemy import create_engine, text
from app.utils.logger import logger

os.environ.setdefault("PGCLIENTENCODING", "utf-8")


def get_local_ip() -> str:
    """Detecta la dirección IP de red local (LAN) de este computador."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No envía paquetes reales, solo resuelve la interfaz LAN preferida
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def detect_postgresql_installation() -> Tuple[bool, str]:
    """Detecta si PostgreSQL está instalado en las rutas estándar de Windows."""
    rutas_comunes = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "PostgreSQL",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "PostgreSQL",
    ]

    for base_path in rutas_comunes:
        if base_path.exists():
            subdirs = [d for d in base_path.iterdir() if d.is_dir() and (d / "bin" / "psql.exe").exists()]
            if subdirs:
                # Retorna la versión más reciente encontrada
                subdirs.sort(reverse=True)
                return True, str(subdirs[0])

    # Verificar si psql está en el PATH
    try:
        res = subprocess.run(["psql", "--version"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            return True, "Encontrado en PATH"
    except Exception:
        pass

    return False, "No detectado en rutas estándar"


def is_postgresql_service_running() -> bool:
    """Verifica si el servicio de PostgreSQL en Windows está activo."""
    try:
        output = subprocess.check_output("sc query state= all", shell=True, text=True, errors="ignore")
        return "SERVICE_NAME: postgresql" in output.lower() and "STATE              : 4  RUNNING" in output
    except Exception:
        # Intento de conexión socket rápida al puerto 5432
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", 5432))
            sock.close()
            return result == 0
        except Exception:
            return False


def provision_database(
    admin_user: str = "postgres",
    admin_password: str = "",
    host: str = "localhost",
    port: int = 5432,
    db_name: str = "systemdistrimagik",
    app_user: str = "distri_app",
    app_password: str = "DistriMagik2026*",
) -> Tuple[bool, str]:
    """
    Se conecta como administrador de PostgreSQL para:
    1. Crear el usuario de aplicación si no existe.
    2. Crear la base de datos si no existe.
    3. Asignar permisos al usuario de aplicación sobre la base de datos y esquema public.
    """
    enc_admin_user = urllib.parse.quote_plus(admin_user)
    enc_admin_pass = urllib.parse.quote_plus(admin_password)
    admin_url = f"postgresql+psycopg2://{enc_admin_user}:{enc_admin_pass}@{host}:{port}/postgres?client_encoding=utf8"
    
    try:
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 5})
        with admin_engine.connect() as conn:
            # 1. Crear usuario si no existe
            user_exists = conn.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :username"),
                {"username": app_user}
            ).scalar()

            if not user_exists:
                logger.info(f"Creando usuario de aplicación '{app_user}'...")
                # SQL seguro con comillas para evitar inyecciones
                conn.execute(text(f'CREATE USER "{app_user}" WITH PASSWORD :password'), {"password": app_password})
            else:
                logger.info(f"Usuario '{app_user}' ya existe. Actualizando contraseña...")
                conn.execute(text(f'ALTER USER "{app_user}" WITH PASSWORD :password'), {"password": app_password})

            # 2. Crear base de datos si no existe
            db_exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name}
            ).scalar()

            if not db_exists:
                logger.info(f"Creando base de datos '{db_name}'...")
                conn.execute(text(f'CREATE DATABASE "{db_name}" OWNER "{app_user}"'))
            else:
                logger.info(f"Base de datos '{db_name}' ya existe.")
                conn.execute(text(f'ALTER DATABASE "{db_name}" OWNER TO "{app_user}"'))

        admin_engine.dispose()

        # 3. Conectarse a la nueva base de datos para otorgar permisos en schema public
        target_db_url = f"postgresql+psycopg2://{enc_admin_user}:{enc_admin_pass}@{host}:{port}/{db_name}?client_encoding=utf8"
        target_engine = create_engine(target_db_url, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 5})
        with target_engine.connect() as conn:
            conn.execute(text(f'GRANT ALL ON SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "{app_user}"'))
            conn.execute(text(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "{app_user}"'))
        target_engine.dispose()

        logger.info("Base de datos y usuario de aplicación configurados exitosamente.")
        return True, "Base de datos y usuario configurados correctamente."
    except Exception as e:
        logger.error(f"Error durante el provisionamiento de PostgreSQL: {e}")
        return False, f"Error al aprovisionar PostgreSQL: {str(e)}"
