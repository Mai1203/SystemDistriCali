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

def find_bundled_postgres_installer() -> Optional[Path]:
    """
    Busca el instalador de PostgreSQL 15 empaquetado junto a la aplicación o en la carpeta prerequisites.
    """
    import sys
    rutas_busqueda = []
    
    # 1. Si está congelado por PyInstaller
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
        rutas_busqueda.append(base_dir / "prerequisites")
        rutas_busqueda.append(base_dir / "installer")
        rutas_busqueda.append(base_dir)
        if hasattr(sys, "_MEIPASS"):
            rutas_busqueda.append(Path(sys._MEIPASS) / "prerequisites")
            rutas_busqueda.append(Path(sys._MEIPASS))
    else:
        # Modo desarrollo
        app_root = Path(__file__).resolve().parent.parent.parent
        rutas_busqueda.append(app_root / "prerequisites")
        rutas_busqueda.append(app_root / "installer")
        rutas_busqueda.append(app_root)

    for ruta in rutas_busqueda:
        if ruta.exists():
            # Buscar cualquier instalador postgresql-*.exe
            for exe in ruta.glob("postgresql*.exe"):
                if exe.is_file():
                    logger.info(f"Instalador de PostgreSQL encontrado en: {exe}")
                    return exe

    return None


def wait_for_postgresql_service(port: int = 5432, timeout_seconds: int = 75) -> bool:
    """Espera activamente a que el servicio de PostgreSQL esté levantado y respondiendo en el puerto."""
    import time
    inicio = time.time()
    logger.info(f"Esperando inicio del servicio PostgreSQL en puerto {port} (máx {timeout_seconds}s)...")
    while time.time() - inicio < timeout_seconds:
        if is_postgresql_service_running():
            logger.info("Servicio PostgreSQL verificado en estado RUNNING.")
            return True
        time.sleep(2)
    return False


def install_postgresql_silent(
    installer_path: Path,
    admin_password: str = "postgres",
    port: int = 5432,
    install_dir: str = r"C:\Program Files\PostgreSQL\15",
    data_dir: str = r"C:\Program Files\PostgreSQL\15\data"
) -> Tuple[bool, str]:
    """
    Ejecuta la instalación desatendida/silenciosa de PostgreSQL 15 (EDB).
    Instala únicamente el servidor y herramientas de comandos (sin pgAdmin ni StackBuilder).
    """
    if not installer_path or not installer_path.exists():
        return False, f"El archivo instalador no existe en: {installer_path}"

    logger.info(f"Iniciando instalación desatendida de PostgreSQL 15 desde {installer_path}...")

    # Parámetros para EnterpriseDB installer
    args_list = (
        f'--mode unattended '
        f'--unattendedmodeui none '
        f'--superpassword "{admin_password}" '
        f'--servicepassword "{admin_password}" '
        f'--serverport {port} '
        f'--prefix "{install_dir}" '
        f'--datadir "{data_dir}" '
        f'--locale "C" '
        f'--enable-components server,commandlinetools '
        f'--disable-components pgAdmin,stackbuilder'
    )

    try:
        # Ejecutar solicitando elevación de Administrador mediante PowerShell
        escaped_installer = str(installer_path.resolve())
        ps_cmd = (
            f'Start-Process -FilePath "{escaped_installer}" '
            f'-ArgumentList \'{args_list}\' '
            f'-Verb RunAs -Wait -WindowStyle Hidden'
        )

        logger.info("Ejecutando instalador con permisos de Administrador...")
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)

        # Esperar a que el servicio arranque
        if wait_for_postgresql_service(port=port, timeout_seconds=90):
            logger.info("PostgreSQL 15 instalado y servicio iniciado con éxito.")
            return True, "PostgreSQL 15 instalado y servicio en ejecución correctamente."
        else:
            # Comprobar si se instalaron los archivos aunque el servicio tarde
            installed, path_det = detect_postgresql_installation()
            if installed:
                return True, f"PostgreSQL instalado en {path_det}. Iniciando servicio..."
            return False, "La instalación terminó pero el servicio de PostgreSQL no respondió a tiempo."

    except Exception as e:
        logger.error(f"Error durante la instalación silenciosa de PostgreSQL: {e}")
        return False, f"Fallo en la instalación: {str(e)}"


def configure_windows_firewall(port: int = 5432, rule_name: str = "SystemDistri - PostgreSQL 5432") -> Tuple[bool, str]:
    """
    Crea o verifica la regla en el Firewall de Windows para permitir conexiones entrantes en el puerto de PostgreSQL.
    Si se requieren permisos de Administrador, solicita elevación mediante el diálogo de UAC de Windows.
    """
    try:
        # 1. Verificar si la regla ya existe
        check_cmd = f'netsh advfirewall firewall show rule name="{rule_name}"'
        res = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, errors="ignore")
        if res.returncode == 0 and ("Rule Name:" in res.stdout or "Nombre de regla:" in res.stdout):
            logger.info(f"Regla de Firewall '{rule_name}' ya existe.")
            return True, f"Regla de firewall '{rule_name}' ya configurada."

        # 2. Intentar crear directamente
        add_cmd = (
            f'netsh advfirewall firewall add rule name="{rule_name}" '
            f'dir=in action=allow protocol=TCP localport={port} profile=any'
        )
        add_res = subprocess.run(add_cmd, shell=True, capture_output=True, text=True, errors="ignore")
        if add_res.returncode == 0:
            logger.info(f"Regla de Firewall para puerto {port} creada exitosamente.")
            return True, f"Regla de Firewall para puerto {port} creada con éxito."

        # 3. Si falló por falta de elevación, solicitar UAC mediante PowerShell Start-Process -Verb RunAs
        logger.info("Solicitando permisos de Administrador (UAC) para crear la regla en el Firewall de Windows...")
        ps_script = (
            f'Start-Process netsh -ArgumentList \'advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port} profile=any\' -Verb RunAs -Wait -WindowStyle Hidden'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, errors="ignore")

        # 4. Verificar si la regla fue creada tras el diálogo UAC
        verify_res = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, errors="ignore")
        if verify_res.returncode == 0 and ("Rule Name:" in verify_res.stdout or "Nombre de regla:" in verify_res.stdout):
            logger.info(f"Regla de Firewall '{rule_name}' creada exitosamente con permisos elevados.")
            return True, f"Regla de Firewall creada con éxito para el puerto {port}."
        else:
            err = add_res.stderr.strip() or add_res.stdout.strip()
            logger.warning(f"No se pudo crear regla de firewall tras solicitud de elevación: {err}")
            return False, f"Aviso de firewall: No se autorizaron permisos de Administrador para abrir el puerto {port}."
    except Exception as e:
        logger.warning(f"Excepción creando regla de firewall: {e}")
        return False, str(e)


def restart_postgresql_service() -> bool:
    """Intenta reiniciar el servicio de PostgreSQL en Windows (con elevación si es necesario)."""
    try:
        # Buscar el nombre exacto del servicio postgresql
        output = subprocess.check_output("sc query state= all", shell=True, text=True, errors="ignore")
        service_name = None
        for line in output.splitlines():
            line_clean = line.strip()
            if line_clean.lower().startswith("service_name:") and "postgres" in line_clean.lower():
                service_name = line_clean.split(":", 1)[1].strip()
                break
        
        if service_name:
            logger.info(f"Reiniciando servicio '{service_name}'...")
            res_stop = subprocess.run(f"net stop {service_name}", shell=True, capture_output=True, text=True)
            if res_stop.returncode != 0:
                # Intentar con elevación
                ps_restart = f'Start-Process powershell -ArgumentList \'-NoProfile -Command "Restart-Service {service_name}"\' -Verb RunAs -Wait -WindowStyle Hidden'
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_restart], capture_output=True, text=True, errors="ignore")
                return True
            res_start = subprocess.run(f"net start {service_name}", shell=True, capture_output=True)
            return res_start.returncode == 0
    except Exception as e:
        logger.warning(f"No se pudo reiniciar el servicio de PostgreSQL automáticamente: {e}")
    return False


def configure_remote_access_in_postgresql(conn) -> Tuple[bool, str]:
    """
    Configura listen_addresses = '*' y añade reglas de acceso remoto en pg_hba.conf automáticamente.
    """
    try:
        # 1. Configurar listen_addresses = '*'
        try:
            conn.execute(text("ALTER SYSTEM SET listen_addresses = '*'"))
            logger.info("Configurado listen_addresses = '*' mediante ALTER SYSTEM.")
        except Exception as e:
            logger.warning(f"Aviso al configurar listen_addresses: {e}")

        # 2. Localizar pg_hba.conf
        hba_path_raw = conn.execute(text("SHOW hba_file")).scalar()
        if hba_path_raw:
            hba_file = Path(hba_path_raw)
            if hba_file.exists():
                contenido = ""
                try:
                    contenido = hba_file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        contenido = hba_file.read_text(encoding="latin-1")
                    except Exception:
                        pass

                # Verificar si ya existe regla para 0.0.0.0/0 o similar
                regla_ipv4 = "host    all             all             0.0.0.0/0               scram-sha-256"
                regla_ipv6 = "host    all             all             ::/0                    scram-sha-256"
                
                necesita_actualizar = False
                lineas_nuevas = []
                
                if "0.0.0.0/0" not in contenido and "all             all             all" not in contenido:
                    lineas_nuevas.append(regla_ipv4)
                    necesita_actualizar = True
                
                if "::/0" not in contenido and "all             all             all" not in contenido:
                    lineas_nuevas.append(regla_ipv6)
                    necesita_actualizar = True

                if necesita_actualizar:
                    logger.info(f"Añadiendo reglas de acceso LAN a {hba_file}...")
                    texto_a_anadir = "\n# Reglas de red añadidas automaticamente por SystemDistri\n" + "\n".join(lineas_nuevas) + "\n"
                    with open(hba_file, "a", encoding="utf-8") as f:
                        f.write(texto_a_anadir)
                    logger.info("pg_hba.conf actualizado con éxito.")

        # 3. Recargar configuración de PostgreSQL
        try:
            conn.execute(text("SELECT pg_reload_conf()"))
            logger.info("PostgreSQL config reloaded via pg_reload_conf().")
        except Exception as e:
            logger.warning(f"Aviso al recargar config: {e}")

        return True, "Reglas de acceso remoto de PostgreSQL configuradas."
    except Exception as e:
        logger.warning(f"Error configurando acceso remoto en PostgreSQL: {e}")
        return False, str(e)


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
    4. Configurar pg_hba.conf y listen_addresses para permitir acceso a las terminales.
    5. Crear regla de Firewall en Windows para el puerto de PostgreSQL.
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

            # 3. Configurar pg_hba.conf y listen_addresses para admitir terminales
            configure_remote_access_in_postgresql(conn)

        admin_engine.dispose()

        # 4. Conectarse a la nueva base de datos para otorgar permisos en schema public
        target_db_url = f"postgresql+psycopg2://{enc_admin_user}:{enc_admin_pass}@{host}:{port}/{db_name}?client_encoding=utf8"
        target_engine = create_engine(target_db_url, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 5})
        with target_engine.connect() as conn:
            conn.execute(text(f'GRANT ALL ON SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{app_user}"'))
            conn.execute(text(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "{app_user}"'))
            conn.execute(text(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "{app_user}"'))
        target_engine.dispose()

        # 5. Configurar regla de Firewall en Windows automáticamente
        fw_ok, fw_msg = configure_windows_firewall(port=port)
        logger.info(f"Estado de regla de firewall: {fw_msg}")

        logger.info("Base de datos, permisos, red y firewall configurados exitosamente.")
        return True, "Base de datos, permisos, acceso de red y Firewall configurados correctamente."
    except Exception as e:
        logger.error(f"Error durante el provisionamiento de PostgreSQL: {e}")
        return False, f"Error al aprovisionar PostgreSQL: {str(e)}"
