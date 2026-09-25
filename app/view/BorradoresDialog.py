from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QWidget,
    QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor
import qtawesome as qta
import traceback

from ..utils.borradores_manager import cargar_borradores, eliminar_borrador


class BorradoresDialog(QDialog):
    """
    Diálogo modal de diseño oscuro (basado en la imagen de referencia) para cargar
    o eliminar borradores guardados.
    """

    borrador_seleccionado = pyqtSignal(dict)

    # ---------- ESTILOS (Light Theme Principal) ----------
    _BG_MAIN = "#F5F0F4"      # Fondo principal
    _BG_CARD = "#FFFFFF"      # Fondo tabla y barra sup
    _BG_HEADER = "#FDF0F6"    # Encabezado tabla (tono sutil)
    _TEXT = "#201A24"         # Texto principal oscuro
    _MUTED = "#7B737F"        # Texto secundario
    _DIVIDER = "#E2DAE1"      # Bordes
    
    _BTN_RED = "#F44336"      # Rojo (Eliminar)
    _BTN_GRAY = "#7B737F"     # Gris (Cancelar)
    _BTN_GREEN = "#862D6D"    # Morado primario (Cargar)

    def __init__(self, tipo: str, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self._borradores = []

        self.setWindowTitle("Ventas en Espera / Borradores")
        self.setMinimumSize(750, 480)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self._BG_MAIN};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QMessageBox {{
                background-color: {self._BG_MAIN};
                color: {self._TEXT};
            }}
            QMessageBox QLabel {{
                color: {self._TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {self._BTN_GRAY};
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }}
        """)

        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # ── Cabecera (Icono + Titulo + Subtitulo) ──
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon("fa5s.folder-open", color="#38BDF8").pixmap(28, 28))
        title_layout.addWidget(lbl_icon)

        lbl_title = QLabel("Ventas en Espera (Borradores)")
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self._TEXT};")
        title_layout.addWidget(lbl_title)
        title_layout.addStretch()

        header_layout.addLayout(title_layout)

        lbl_subtitle = QLabel("Seleccione un borrador guardado para cargarlo en la venta activa o eliminarlo.")
        lbl_subtitle.setStyleSheet(f"font-size: 13px; color: {self._MUTED}; background-color: {self._BG_CARD}; padding: 6px 10px; border-radius: 4px;")
        header_layout.addWidget(lbl_subtitle)
        
        root.addLayout(header_layout)

        # ── Tabla de Borradores ──
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Fecha", "Referencia / Cliente", "Items", "Total Est."])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setShowGrid(False)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Ajuste de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Fecha
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Referencia/Cliente
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Items
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Total

        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self._BG_CARD};
                border: 1px solid {self._DIVIDER};
                border-radius: 8px;
                color: {self._TEXT};
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 10px 5px;
                border-bottom: 1px solid {self._DIVIDER};
            }}
            QTableWidget::item:selected {{
                background-color: #EFE8EE; /* Fila seleccionada claro */
                color: {self._TEXT};
            }}
            QHeaderView::section {{
                background-color: {self._BG_HEADER};
                color: {self._TEXT};
                font-weight: bold;
                border: none;
                padding: 8px 5px;
                border-bottom: 2px solid {self._DIVIDER};
            }}
            QScrollBar:vertical {{
                background: {self._BG_CARD};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self._MUTED};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        root.addWidget(self.tabla)

        # ── Botones Inferiores ──
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 0)

        # Izquierda (Eliminar)
        self.btn_eliminar = QPushButton("  Eliminar Borrador")
        self.btn_eliminar.setIcon(qta.icon("fa5s.trash-alt", color="white"))
        self.btn_eliminar.setMinimumHeight(38)
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._BTN_RED};
                color: white;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: #D32F2F; }}
            QPushButton:disabled {{ background-color: #FFCDD2; color: #9CA3AF; }}
        """)
        self.btn_eliminar.clicked.connect(self._eliminar_seleccionado)
        btn_layout.addWidget(self.btn_eliminar)

        btn_layout.addStretch()

        # Derecha (Cancelar, Cargar)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setMinimumHeight(38)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._BTN_GRAY};
                color: white;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: #625B65; }}
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)

        self.btn_cargar = QPushButton("  Cargar en Venta Activa")
        self.btn_cargar.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_cargar.setMinimumHeight(38)
        self.btn_cargar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cargar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._BTN_GREEN};
                color: white;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: #6E2259; }}
            QPushButton:disabled {{ background-color: #E2DAE1; color: #7B737F; }}
        """)
        self.btn_cargar.clicked.connect(self._cargar_seleccionado)
        btn_layout.addWidget(self.btn_cargar)

        root.addLayout(btn_layout)

    # ------------------------------------------------------------------ #
    #  Logica                                                               #
    # ------------------------------------------------------------------ #
    def _cargar_datos(self):
        """Recarga la lista desde disco a la tabla."""
        self._borradores = cargar_borradores(self.tipo)
        self.tabla.setRowCount(0)

        if not self._borradores:
            self.btn_cargar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)
            return

        self.btn_cargar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

        for i, b in enumerate(self._borradores):
            self.tabla.insertRow(i)
            datos = b.get("datos", {})
            productos = datos.get("productos", [])
            n_productos = len(productos)
            
            # Formatear el total (reemplazar comas/puntos extraños o hacer parse)
            total_str = datos.get("total", "0")
            try:
                # Intentamos limpiar por si es string '500,000'
                if isinstance(total_str, str):
                    total_val = float(total_str.replace(",", "").replace("$", "").strip())
                else:
                    total_val = float(total_str)
                total_fmt = f"$ {total_val:,.0f}"
            except Exception:
                total_fmt = f"$ {total_str}"

            cliente = datos.get("cliente_nombre", "").strip()
            if not cliente:
                cliente = "Cliente General"
            fecha = b.get("fecha", "—")
            
            # Usar un prefijo corto de ID para no llenar la celda
            id_corto = str(b.get("id", ""))[:6].upper()

            # --- Crear items ---
            item_id = QTableWidgetItem(id_corto)
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_id.setData(Qt.ItemDataRole.UserRole, b["id"]) # Guardar ID original

            item_fecha = QTableWidgetItem(fecha)
            item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_cliente = QTableWidgetItem(cliente)
            item_cliente.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            item_items = QTableWidgetItem(str(n_productos))
            item_items.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_total = QTableWidgetItem(total_fmt)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

            self.tabla.setItem(i, 0, item_id)
            self.tabla.setItem(i, 1, item_fecha)
            self.tabla.setItem(i, 2, item_cliente)
            self.tabla.setItem(i, 3, item_items)
            self.tabla.setItem(i, 4, item_total)

        self.tabla.selectRow(0)

    def _borrador_seleccionado_id(self):
        """Devuelve el ID del borrador actualmente seleccionado en la tabla."""
        rows = self.tabla.selectedItems()
        if not rows:
            return None
        # Tomar de la columna 0 el UserRole
        row = rows[0].row()
        return self.tabla.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _cargar_seleccionado(self):
        borrador_id = self._borrador_seleccionado_id()
        if not borrador_id:
            return

        borrador = next((b for b in self._borradores if b["id"] == borrador_id), None)
        if not borrador:
            return

        # Eliminar del disco
        eliminar_borrador(borrador_id)
        self.borrador_seleccionado.emit(borrador["datos"])
        self.accept()

    def _eliminar_seleccionado(self):
        borrador_id = self._borrador_seleccionado_id()
        if not borrador_id:
            return

        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Estás seguro de que deseas eliminar este borrador?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_borrador(borrador_id)
            self._cargar_datos()
