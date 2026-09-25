from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6 import sip
from app.services.setup_strategies import SetupStrategy
from app.database.config import save_config
from app.utils.logger import logger

class StrategyWorker(QThread):
    finished_signal = pyqtSignal(bool, str, object) # ok, msg, config
    progress_signal = pyqtSignal(str)
    
    def __init__(self, strategy: SetupStrategy):
        super().__init__()
        self.strategy = strategy
        self.strategy.signals.progress.connect(self.progress_signal.emit)

    def run(self):
        try:
            ok, msg, config = self.strategy.execute()
            if ok and config:
                # Si la estrategia fue exitosa, persistimos la configuración
                save_ok = save_config(config)
                if not save_ok:
                    self.finished_signal.emit(False, "Error al guardar el archivo de configuración.", None)
                    return
            self.finished_signal.emit(ok, msg, config)
        except Exception as e:
            logger.exception(f"Error executing setup strategy: {e}")
            self.finished_signal.emit(False, f"Error inesperado: {str(e)}", None)

class SetupController(QObject):
    on_success = pyqtSignal(str)
    on_error = pyqtSignal(str)
    on_progress = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._worker = None

    def execute_strategy(self, strategy: SetupStrategy):
        if self._worker is not None:
            try:
                if not sip.isdeleted(self._worker) and self._worker.isRunning():
                    self.on_error.emit("Ya hay una configuración en proceso.")
                    return
            except RuntimeError:
                pass
            self._worker = None

        self._worker = StrategyWorker(strategy)
        self._worker.progress_signal.connect(self.on_progress.emit)
        self._worker.finished_signal.connect(self._handle_result)
        self._worker.finished.connect(self._limpiar_worker)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _limpiar_worker(self):
        self._worker = None

    def _handle_result(self, ok: bool, msg: str, config):
        if ok:
            self.on_success.emit(msg)
        else:
            self.on_error.emit(msg)
