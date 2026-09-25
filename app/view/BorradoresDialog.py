import qtawesome as qta
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from ..utils.borradores_manager import cargar_borradores, eliminar_borrador, obtener_borrador_por_id
from ..utils.formateador import formatear_numero

_PRIMARY = "#0EA5E9"
_PRIMARY_HOVER = "#0284C7"
_BG_DARK = "#0F172A"
_CARD_BG = "#1E293B"
_TEXT = "#F8FAFC"
_MUTED = "#94A3B8"
_BORDER = "#334155"
_DANGER = "#EF4444"
_SUCCESS = "#10B981"
_PURPLE = "#8B5CF6"


class BorradoresDialog(QDialog):
    """
    Diálogo modal para visualizar, cargar o eliminar ventas en espera (borradores).
    Soporta filtrado por Ventas de Contado (solo_credito=False) o Ventas a Crédito (solo_credito=True).
    """

    def __init__(self, solo_credito=False, parent=None):
        super().__init__(parent)
        self.solo_credito = solo_credito
        self.borrador_seleccionado = None

        tipo_str = "Crédito" if solo_credito else "Contado"
        self.setWindowTitle(f"Ventas a {tipo_str} en Espera / Borradores")
        self.resize(780, 480)
        self.setMinimumSize(700, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {_BG_DARK};
                color: {_TEXT};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QLabel {{
                color: {_TEXT};
                background: transparent;
                background-color: transparent;
                border: none;
            }}
            QTableWidget {{
                background-color: {_CARD_BG};
                color: {_TEXT};
                gridline-color: {_BORDER};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: #334155;
                color: #F8FAFC;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ── Encabezado ──
        header_layout = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        icon_color = _PURPLE if solo_credito else _PRIMARY
        icon_lbl.setPixmap(qta.icon("fa5s.folder-open", color=icon_color).pixmap(28, 28))
        header_layout.addWidget(icon_lbl)

        title_lbl = QLabel(f"Borradores - Ventas de {tipo_str}")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC; background: transparent; border: none;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        subtitle_lbl = QLabel(f"Listado de borradores guardados para ventas de {tipo_str.lower()}.")
        subtitle_lbl.setStyleSheet(f"color: {_MUTED}; font-size: 13px; background: transparent; border: none;")
        layout.addWidget(subtitle_lbl)

        # ── Tabla de Borradores ──
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Fecha", "Referencia / Cliente", "Items", "Total Est."])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.doubleClicked.connect(self._cargar_seleccionado)
        layout.addWidget(self.tabla)

        # ── Botones de acción ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_eliminar = QPushButton(" Eliminar Borrador")
        self.btn_eliminar.setIcon(qta.icon("fa5s.trash-alt", color="white"))
        self.btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_DANGER};
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 16px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        self.btn_eliminar.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_eliminar.clicked.connect(self._eliminar_seleccionado)
        btn_layout.addWidget(self.btn_eliminar)

        btn_layout.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BORDER};
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 16px;
            }}
            QPushButton:hover {{
                background-color: #475569;
            }}
        """)
        self.btn_cancelar.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)

        self.btn_cargar = QPushButton(" Cargar en Venta Activa")
        self.btn_cargar.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_cargar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_SUCCESS};
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.btn_cargar.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cargar.clicked.connect(self._cargar_seleccionado)
        btn_layout.addWidget(self.btn_cargar)

        layout.addLayout(btn_layout)

        # Cargar datos
        self._cargar_datos()

    def _cargar_datos(self):
        borradores = cargar_borradores(solo_credito=self.solo_credito)
        self.tabla.setRowCount(0)

        for b in borradores:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            items_list = b.get("items", [])
            cant_items = sum(int(item.get("cantidad", 1)) for item in items_list)
            total_est = sum(float(item.get("total", 0)) for item in items_list) + float(b.get("domicilio", 0)) - float(b.get("descuento", 0))

            item_id = QTableWidgetItem(str(b.get("id")))
            item_id.setData(Qt.ItemDataRole.UserRole, b.get("id"))
            item_fecha = QTableWidgetItem(str(b.get("fecha", "")))
            item_ref = QTableWidgetItem(str(b.get("referencia", "Sin Nombre")))
            item_cant = QTableWidgetItem(f"{cant_items} un. ({len(items_list)} prods)")
            item_total = QTableWidgetItem(f"$ {formatear_numero(total_est)}")

            for item in (item_id, item_fecha, item_ref, item_cant, item_total):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item_ref.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.tabla.setItem(row, 0, item_id)
            self.tabla.setItem(row, 1, item_fecha)
            self.tabla.setItem(row, 2, item_ref)
            self.tabla.setItem(row, 3, item_cant)
            self.tabla.setItem(row, 4, item_total)

    def _obtener_id_seleccionado(self):
        row = self.tabla.currentRow()
        if row == -1:
            return None
        item = self.tabla.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _cargar_seleccionado(self):
        borrador_id = self._obtener_id_seleccionado()
        if not borrador_id:
            QMessageBox.warning(self, "Selección requerida", "Por favor seleccione un borrador de la tabla.")
            return

        self.borrador_seleccionado = obtener_borrador_por_id(borrador_id)
        if self.borrador_seleccionado:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se encontró el borrador seleccionado.")

    def _eliminar_seleccionado(self):
        borrador_id = self._obtener_id_seleccionado()
        if not borrador_id:
            QMessageBox.warning(self, "Selección requerida", "Por favor seleccione un borrador para eliminar.")
            return

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este borrador?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_borrador(borrador_id)
            self._cargar_datos()
