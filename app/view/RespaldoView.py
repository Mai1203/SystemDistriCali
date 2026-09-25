from PyQt6.QtCore import QTimer, QDate, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QInputDialog, QProgressDialog
from PyQt6.QtCore import Qt
from ..ui import Ui_Respaldo
import os
from datetime import datetime
from pathlib import Path

from app.database.config import load_config
from app.services.backup_service import (
    crear_respaldo,
    restaurar_respaldo,
    get_extension_respaldo,
    get_filtro_dialogo,
    nombre_respaldo_automatico,
    verificar_herramientas_postgres,
)


# ─────────────────────────────────────────────────────────────────────────────
# Workers QThread — evitan que la UI se congele durante operaciones largas
# ─────────────────────────────────────────────────────────────────────────────

class _BackupWorker(QThread):
    """Worker que ejecuta crear_respaldo() en un hilo secundario."""
    terminado = pyqtSignal(bool, str)  # (éxito, mensaje)

    def __init__(self, ruta_destino: str, config):
        super().__init__()
        self.ruta_destino = ruta_destino
        self.config = config

    def run(self):
        exito, mensaje = crear_respaldo(self.ruta_destino, self.config)
        self.terminado.emit(exito, mensaje)


class _RestoreWorker(QThread):
    """Worker que ejecuta restaurar_respaldo() en un hilo secundario."""
    terminado = pyqtSignal(bool, str)  # (éxito, mensaje)

    def __init__(self, ruta_origen: str, config):
        super().__init__()
        self.ruta_origen = ruta_origen
        self.config = config

    def run(self):
        exito, mensaje = restaurar_respaldo(self.ruta_origen, self.config)
        self.terminado.emit(exito, mensaje)


class Respaldo_View(QWidget, Ui_Respaldo):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # Configuración inicial
        self.ruta_carpeta_respaldos = os.path.join(
            os.path.expanduser("~"), "Desktop", "Respaldos"
        )
        self.intentos_respaldo = 0  # Contador de intentos de respaldo en el día
        self.ultima_fecha_respaldo = None  # Última fecha de respaldo registrado

        self.BtnRespaldoExportar.clicked.connect(self.exportar_base_datos)
        self.BtnRespaldoImportar.clicked.connect(self.importar_base_datos)

        # Responsividad del Sistema de Diseño (resizeEvent → adapt_to_size)
        QTimer.singleShot(50, self._adapt_current)

        # Configuración del temporizador (verifica cada hora)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.respaldo_automatico)
        self.timer.start(1 * 60 * 1000)  # Verificar cada hora (60 minutos)

    # ── Responsividad ──────────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adapt_current()

    def _adapt_current(self):
        w, h = self.width(), self.height()
        if w > 0 and h > 0:
            self.adapt_to_size(w, h)

    # ─────────────────────────────────────────────────────────────
    def exportar_base_datos(self):
        """Exporta la base de datos PostgreSQL a un archivo de respaldo .sql."""
        self.config = load_config()

        ext = get_extension_respaldo(self.config)
        filtro = get_filtro_dialogo(self.config)

        # Verificar herramientas de PostgreSQL
        ok, msg_tools = verificar_herramientas_postgres()
        if not ok:
            QMessageBox.warning(
                self,
                "Herramientas no encontradas",
                f"{msg_tools}\n\nInstala PostgreSQL y asegúrate de que la "
                f"carpeta 'bin' esté en el PATH del sistema.",
            )
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Exportar base de datos")
        msg.setText("Selecciona el tipo de exportación:")
        msg.setIcon(QMessageBox.Icon.Question)

        btn_todo = msg.addButton("Exportar toda la base de datos", QMessageBox.ButtonRole.ActionRole)
        btn_tabla = msg.addButton("Exportar tabla específica", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        if msg.clickedButton() == btn_todo:
            self._exportar_todo(ext, filtro)
        elif msg.clickedButton() == btn_tabla:
            self._exportar_tabla(ext, filtro)

    def _exportar_todo(self, ext: str, filtro: str):
        """Exporta la base de datos completa en un hilo secundario."""
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"SystemDistriMagik_{fecha_actual}{ext}"

        ruta_exportar, _ = QFileDialog.getSaveFileName(
            self, "Exportar Base de Datos", nombre_archivo, filtro,
        )
        if not ruta_exportar:
            return

        self._mostrar_progreso("Exportando…", "Creando respaldo, por favor espera…")

        self._worker_backup = _BackupWorker(ruta_exportar, self.config)
        self._worker_backup.terminado.connect(self._on_exportacion_terminada)
        self._worker_backup.start()

    def _exportar_tabla(self, ext: str, filtro: str):
        """Exporta una tabla específica (para PostgreSQL se exporta toda la BD con el nombre de la tabla)."""
        tabla, ok_tabla = QInputDialog.getText(
            self, "Exportar tabla", "Ingrese el nombre de la tabla a exportar:"
        )
        if not ok_tabla or not tabla:
            return

        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"{tabla}_{fecha_actual}{ext}"

        ruta_exportar, _ = QFileDialog.getSaveFileName(
            self, "Exportar Tabla", nombre_archivo, filtro,
        )
        if not ruta_exportar:
            return

        self._mostrar_progreso("Exportando…", f"Exportando tabla '{tabla}', por favor espera…")

        self._worker_backup = _BackupWorker(ruta_exportar, self.config)
        self._worker_backup.terminado.connect(
            lambda ok, msg: self._on_exportacion_terminada(
                ok, f"Tabla '{tabla}' exportada correctamente.\n{msg}" if ok else msg
            )
        )
        self._worker_backup.start()

    def _on_exportacion_terminada(self, exito: bool, mensaje: str):
        self._cerrar_progreso()
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
        else:
            QMessageBox.critical(self, "Error al exportar", mensaje)

    # ─────────────────────────────────────────────────────────────
    def importar_base_datos(self):
        """Importa/restaura la base de datos PostgreSQL desde un archivo de respaldo en un hilo secundario."""
        self.config = load_config()
        filtro = get_filtro_dialogo(self.config)

        filtro_completo = f"{filtro};;Todos los archivos (*.*)"

        ruta_importar, _ = QFileDialog.getOpenFileName(
            self, "Importar Respaldo", "", filtro_completo
        )
        if not ruta_importar:
            return

        if not os.path.exists(ruta_importar):
            QMessageBox.warning(self, "Error", "El archivo seleccionado no existe.")
            return

        aviso = (
            "Esto restaurará la base de datos PostgreSQL desde el respaldo.\n\n"
            "⚠️ TODOS los datos actuales serán reemplazados por los del respaldo.\n"
            "La operación es atómica: si algo falla, los datos actuales se conservan.\n\n"
            "¿Deseas continuar?"
        )

        respuesta = QMessageBox.question(
            self,
            "Confirmar Restauración",
            aviso,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        self._mostrar_progreso(
            "Restaurando…",
            "Restaurando base de datos, por favor espera…\n"
            "Esta operación puede tardar varios minutos.",
        )

        self._worker_restore = _RestoreWorker(ruta_importar, self.config)
        self._worker_restore.terminado.connect(self._on_importacion_terminada)
        self._worker_restore.start()

    def _on_importacion_terminada(self, exito: bool, mensaje: str):
        self._cerrar_progreso()
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
        else:
            QMessageBox.critical(self, "Error al importar", mensaje)

    # ─────────────────────────────────────────────────────────────
    def respaldo_automatico(self):
        """
        Verifica si ya se realizó un respaldo hoy y lo realiza si no existe.
        Máximo 2 intentos por día. Funciona para PostgreSQL.
        El respaldo automático corre en hilo secundario para no bloquear la UI.
        """
        self.config = load_config()
        fecha_actual = QDate.currentDate().toString("yyyy-MM-dd")

        if self.ultima_fecha_respaldo == fecha_actual:
            return
        if self.intentos_respaldo >= 2:
            return

        nombre_respaldo_hoy = nombre_respaldo_automatico(self.config, fecha_actual)
        ruta_respaldo_hoy = os.path.join(self.ruta_carpeta_respaldos, nombre_respaldo_hoy)

        if os.path.exists(ruta_respaldo_hoy):
            self.ultima_fecha_respaldo = fecha_actual
            self.timer.stop()
            return

        os.makedirs(self.ruta_carpeta_respaldos, exist_ok=True)

        self._auto_backup_worker = _BackupWorker(ruta_respaldo_hoy, self.config)

        # Capturamos fecha_actual en el closure para el callback
        _fecha = fecha_actual

        def _on_auto_backup_done(exito: bool, mensaje: str):
            self._auto_backup_worker = None
            from app.utils.logger import logger
            if exito:
                logger.info(f"Respaldo automático creado: {ruta_respaldo_hoy}")
                self.ultima_fecha_respaldo = _fecha
                self.timer.stop()
            else:
                logger.warning(
                    f"Respaldo automático fallido "
                    f"(intento {self.intentos_respaldo + 1}): {mensaje}"
                )
                self.intentos_respaldo += 1

        self._auto_backup_worker.terminado.connect(_on_auto_backup_done)
        self._auto_backup_worker.finished.connect(self._auto_backup_worker.deleteLater)
        self._auto_backup_worker.start()

    # ─────────────────────────────────────────────────────────────
    # Helpers de UI para progreso
    # ─────────────────────────────────────────────────────────────
    def _mostrar_progreso(self, titulo: str, mensaje: str):
        if hasattr(self, '_progreso_dialog') and self._progreso_dialog is not None:
            self._progreso_dialog.close()
        self._progreso_dialog = QProgressDialog(mensaje, None, 0, 0, self)
        self._progreso_dialog.setWindowTitle(titulo)
        self._progreso_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progreso_dialog.setMinimumDuration(0)
        self._progreso_dialog.setCancelButton(None)
        self._progreso_dialog.setAutoClose(False)
        self._progreso_dialog.setAutoReset(False)
        self._progreso_dialog.show()

    def _cerrar_progreso(self):
        if hasattr(self, '_progreso_dialog') and self._progreso_dialog is not None:
            self._progreso_dialog.close()
            self._progreso_dialog = None