"""Gestión y persistencia de configuración de impresoras para facturas y recibos."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.utils.logger import logger

APP_DATA_DIR = Path(os.getenv("APPDATA") or os.path.expanduser("~/.local/share")) / "SystemDistriMagik"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
PRINTER_CONFIG_FILE = APP_DATA_DIR / "printer_config.json"

# Formatos de papel soportados
PAPER_CARTA = "Carta"
PAPER_OFICIO = "Oficio"

PAPER_DIMENSIONS_MM = {
    PAPER_CARTA: (215.9, 279.4),
    PAPER_OFICIO: (215.9, 330.2),  # Oficio Colombia (Folio tradicional)
}


def load_printer_config() -> dict:
    """Carga la configuración de impresora guardada en el equipo local.

    Retorna un diccionario con:
      - configured: bool
      - printer_name: str
      - paper_type: str ("Carta" u "Oficio")
      - auto_silent_print: bool
    """
    default_config = {
        "configured": False,
        "printer_name": "",
        "paper_type": PAPER_CARTA,
        "auto_silent_print": True,
    }

    if not PRINTER_CONFIG_FILE.exists():
        return default_config

    try:
        with open(PRINTER_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {
                    "configured": bool(data.get("configured", False)),
                    "printer_name": str(data.get("printer_name", "")),
                    "paper_type": (
                        PAPER_OFICIO
                        if data.get("paper_type") == PAPER_OFICIO
                        else PAPER_CARTA
                    ),
                    "auto_silent_print": bool(data.get("auto_silent_print", True)),
                }
    except Exception as e:
        logger.error(f"Error al leer {PRINTER_CONFIG_FILE}: {e}")

    return default_config


def save_printer_config(
    printer_name: str, paper_type: str = PAPER_CARTA, auto_silent_print: bool = True
) -> bool:
    """Guarda la configuración de impresora en el almacenamiento local del equipo."""
    config_data = {
        "configured": True,
        "printer_name": printer_name,
        "paper_type": PAPER_OFICIO if paper_type == PAPER_OFICIO else PAPER_CARTA,
        "auto_silent_print": auto_silent_print,
    }
    try:
        with open(PRINTER_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        logger.info(
            f"Configuración de impresora guardada: {printer_name} ({config_data['paper_type']})"
        )
        return True
    except Exception as e:
        logger.error(f"Error al guardar {PRINTER_CONFIG_FILE}: {e}")
        return False


def get_available_printers() -> List[QPrinterInfo]:
    """Obtiene la lista de impresoras instaladas en Windows."""
    try:
        return QPrinterInfo.availablePrinters() or []
    except Exception as e:
        logger.error(f"Error al listar impresoras de Windows: {e}")
        return []


def find_printer_info(printer_name: str) -> Optional[QPrinterInfo]:
    """Busca una impresora por nombre entre las disponibles en el sistema."""
    if not printer_name:
        return None
    for p in get_available_printers():
        if p.printerName() == printer_name:
            return p
    return None


def validate_printer_ready(
    config: Optional[dict] = None,
) -> Tuple[bool, str, Optional[QPrinterInfo]]:
    """Comprueba si la impresora configurada está lista y disponible.

    Retorna:
      (is_ready, reason_message, printer_info)
    """
    if config is None:
        config = load_printer_config()

    if not config.get("configured") or not config.get("printer_name"):
        return False, "La impresora aún no ha sido configurada.", None

    target_name = config["printer_name"]
    printers = get_available_printers()
    if not printers:
        return (
            False,
            "Windows no detecta ninguna impresora instalada en este equipo.",
            None,
        )

    for p in printers:
        if p.printerName() == target_name:
            return True, "OK", p

    return (
        False,
        f"La impresora configurada «{target_name}» no fue encontrada. "
        "Puede estar desconectada, apagada o haber cambiado de nombre en Windows.",
        None,
    )


class ConfigurarImpresoraDialog(QDialog):
    """Diálogo modal para configurar la impresora y tamaño de hoja predeterminados."""

    def __init__(self, parent=None, reason_message: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Impresora - Distri Magik")
        self.setMinimumWidth(480)
        self.resize(520, 280)

        self._current_config = load_printer_config()
        self._printers = get_available_printers()

        self._init_ui(reason_message)

    def _init_ui(self, reason_message: Optional[str]):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Mensaje de advertencia o motivo si aplica
        if reason_message:
            warn_card = QWidget(self)
            warn_card.setStyleSheet("""
                QWidget {
                    background-color: #FEF3C7;
                    border: 1px solid #F59E0B;
                    border-radius: 6px;
                }
            """)
            warn_layout = QHBoxLayout(warn_card)
            warn_label = QLabel(reason_message, warn_card)
            warn_label.setWordWrap(True)
            warn_label.setStyleSheet("color: #92400E; font-weight: 500; font-size: 12px; border: none;")
            warn_layout.addWidget(warn_label)
            layout.addWidget(warn_card)

        # Instrucción principal
        desc_label = QLabel(
            "Seleccione la impresora y el tamaño de papel predeterminado. "
            "El sistema recordará estos ajustes para imprimir automáticamente sin interrupciones.",
            self,
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #4B5563; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(desc_label)

        # Formulario
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setSpacing(10)

        # Combo impresoras
        self.combo_impresoras = QComboBox(self)
        self.combo_impresoras.setMinimumHeight(32)
        default_win_name = ""
        try:
            default_win_name = QPrinterInfo.defaultPrinter().printerName()
        except Exception:
            pass

        saved_name = self._current_config.get("printer_name", "")
        selected_index = -1

        if not self._printers:
            self.combo_impresoras.addItem("No hay impresoras disponibles", None)
            self.combo_impresoras.setEnabled(False)
        else:
            for i, p_info in enumerate(self._printers):
                p_name = p_info.printerName()
                label = p_name
                if p_name == default_win_name:
                    label += " (Predeterminada de Windows)"
                self.combo_impresoras.addItem(label, p_info)

                if saved_name and p_name == saved_name:
                    selected_index = i
                elif selected_index == -1 and p_name == default_win_name:
                    selected_index = i

            if selected_index >= 0:
                self.combo_impresoras.setCurrentIndex(selected_index)

        form.addRow("Impresora:", self.combo_impresoras)

        # Combo tamaño de papel
        self.combo_papel = QComboBox(self)
        self.combo_papel.setMinimumHeight(32)
        self.combo_papel.addItem("Carta (215.9 × 279.4 mm)", PAPER_CARTA)
        self.combo_papel.addItem("Oficio Colombia (215.9 × 330.2 mm)", PAPER_OFICIO)

        if self._current_config.get("paper_type") == PAPER_OFICIO:
            self.combo_papel.setCurrentIndex(1)
        else:
            self.combo_papel.setCurrentIndex(0)

        form.addRow("Tamaño de Papel:", self.combo_papel)
        layout.addLayout(form)

        # Checkbox recordar / modo automático
        self.chk_auto = QCheckBox(
            "Imprimir automáticamente sin volver a preguntar (Recomendado)", self
        )
        self.chk_auto.setChecked(self._current_config.get("auto_silent_print", True))
        self.chk_auto.setStyleSheet("color: #374151; font-size: 12px; margin-top: 6px;")
        layout.addWidget(self.chk_auto)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self.btn_save = buttons.button(QDialogButtonBox.StandardButton.Save)
        self.btn_save.setText("Guardar e Imprimir")
        self.btn_save.setEnabled(bool(self._printers))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #1A2640;
                color: white;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2D3D60;
            }
        """)

        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save(self):
        p_info: Optional[QPrinterInfo] = self.combo_impresoras.currentData()
        if not p_info:
            QMessageBox.warning(
                self,
                "Impresora no válida",
                "Por favor seleccione una impresora válida.",
            )
            return

        printer_name = p_info.printerName()
        paper_type = self.combo_papel.currentData() or PAPER_CARTA
        auto_silent = self.chk_auto.isChecked()

        if save_printer_config(printer_name, paper_type, auto_silent):
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error al guardar",
                "No se pudo guardar la configuración de impresora en el disco.",
            )

    def get_selected_printer_info(self) -> Optional[QPrinterInfo]:
        return self.combo_impresoras.currentData()

    def get_selected_paper_type(self) -> str:
        return self.combo_papel.currentData() or PAPER_CARTA
