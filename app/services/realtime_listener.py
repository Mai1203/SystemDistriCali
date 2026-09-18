import json
import select
import time
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from app.database.config import DatabaseConfig, load_config
from app.database.triggers import NOTIFICATION_CHANNEL
from app.utils.logger import logger


class RealtimeListener(QThread):
    """
    Hilo de fondo que escucha notificaciones en tiempo real desde PostgreSQL
    a través del canal LISTEN/NOTIFY y emite señales de PyQt6 a la interfaz gráfica.
    """

    # Señal genérica que emite todo el payload recibido
    evento_recibido = pyqtSignal(dict)

    # Señales específicas por entidad/tabla
    facturas_cambiadas = pyqtSignal(dict)
    productos_cambiados = pyqtSignal(dict)
    caja_cambiada = pyqtSignal(dict)
    ventas_credito_cambiadas = pyqtSignal(dict)
    pagos_credito_cambiados = pyqtSignal(dict)
    egresos_cambiados = pyqtSignal(dict)
    clientes_cambiados = pyqtSignal(dict)

    def __init__(self, config: Optional[DatabaseConfig] = None, parent=None):
        super().__init__(parent)
        self.config = config or load_config()
        self._is_running = True
        self._conn = None

    def run(self):
        try:
            import psycopg2
            import psycopg2.extensions
        except ImportError:
            logger.error("RealtimeListener: psycopg2 no está disponible para LISTEN/NOTIFY.")
            return

        channel = NOTIFICATION_CHANNEL
        logger.info(f"Iniciando RealtimeListener en canal '{channel}' ({self.config.host}:{self.config.port})...")

        backoff = 2
        while self._is_running:
            try:
                self._conn = psycopg2.connect(
                    host=self.config.host or "localhost",
                    port=self.config.port or 5432,
                    dbname=self.config.database or "systemdistrimagik",
                    user=self.config.user or "distri_app",
                    password=self.config.password or "",
                    connect_timeout=5,
                )
                self._conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

                with self._conn.cursor() as cur:
                    cur.execute(f"LISTEN {channel};")
                    logger.info(f"RealtimeListener conectado y escuchando canal '{channel}'.")

                backoff = 2  # Restablecer backoff al conectar exitosamente

                while self._is_running:
                    # select con timeout de 1 segundo para verificar periódicamente self._is_running
                    if select.select([self._conn], [], [], 1.0) == ([], [], []):
                        continue

                    self._conn.poll()
                    while self._conn.notifies:
                        notify = self._conn.notifies.pop(0)
                        self._procesar_notificacion(notify.payload)

            except Exception as e:
                if not self._is_running:
                    break
                logger.warning(f"RealtimeListener conexión interrumpida ({e}). Reintentando en {backoff}s...")
                self._cerrar_conexion()
                # Espera fraccionada para responder rápidamente a stop()
                for _ in range(int(backoff * 2)):
                    if not self._is_running:
                        break
                    time.sleep(0.5)
                backoff = min(backoff * 2, 15)

        self._cerrar_conexion()
        logger.info("RealtimeListener detenido limpiamente.")

    def _procesar_notificacion(self, raw_payload: str):
        """Parsea el payload JSON y emite las señales de PyQt correspondientes."""
        try:
            payload = json.loads(raw_payload)
            table = payload.get("table", "").upper()
            action = payload.get("action", "")

            logger.info(f"[Tiempo Real] Evento recibido: Tabla={table}, Acción={action}")

            # Emitir señal general
            self.evento_recibido.emit(payload)

            # Despachar a la señal específica según la tabla
            if table == "FACTURA":
                self.facturas_cambiadas.emit(payload)
            elif table == "PRODUCTOS":
                self.productos_cambiados.emit(payload)
            elif table == "CAJA":
                self.caja_cambiada.emit(payload)
            elif table == "VENTA_CREDITO":
                self.ventas_credito_cambiadas.emit(payload)
            elif table == "PAGO_CREDITO":
                self.pagos_credito_cambiados.emit(payload)
            elif table == "EGRESOS":
                self.egresos_cambiados.emit(payload)
            elif table == "CLIENTES":
                self.clientes_cambiados.emit(payload)

        except Exception as e:
            logger.error(f"Error al procesar payload de notificación en tiempo real: {e}")

    def _cerrar_conexion(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def stop(self):
        """Detiene de forma segura el bucle de escucha y cierra la conexión."""
        self._is_running = False
        self.wait(1500)
        self._cerrar_conexion()