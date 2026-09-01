from PyQt6.QtWidgets import (
    QWidget,
    QMessageBox,
)
from ..utils.enviar_notifi import Mensajes as QMessageBox
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

from ..ui import Ui_FacturasCredito
from ..database.database import SessionLocal
from ..controllers.venta_credito_crud import *
from ..controllers.facturas_crud import *
from ..controllers.pago_credito_crud import *
from ..utils.enviar_notifi import enviar_notificacion
from datetime import datetime

class CrediFactura_View(QWidget, Ui_FacturasCredito):
    enviar_facturas_Credito = pyqtSignal(dict, int)
    enviar_ventaCredito = pyqtSignal(int)

    def __init__(self, parent=None):
        super(CrediFactura_View, self).__init__(parent)
        self.setupUi(self)
        
        self.TablaFacturasCredito.setColumnWidth(4, 120)
        self.TablaFacturasCredito.setColumnWidth(5, 120)

        self.InputBuscador.setPlaceholderText(
            "Buscar por ID, Cliente, o Fecha de Registro"
        )
        self.InputBuscador.textChanged.connect(self.buscar_ventasCredito)

        self.TablaFacturasCredito.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.TablaFacturasCredito.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        self.TablaFacturasCredito.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.BtnEditarFactura.clicked.connect(self.editar_ventaCredito)
        self.BtnAgregarAbono.clicked.connect(self.agregar_abono)
        self.ComboOrden.currentIndexChanged.connect(self.cambiar_orden)

    def showEvent(self, event):
        super().showEvent(event)
        self.limpiar_tabla()
        self.mostrar_ventasCredito()
        self.InputBuscador.clear()
        self.ComboOrden.setCurrentIndex(0)

    def cambiar_orden(self):
        orden = self.ComboOrden.currentText()
        reverse = orden == "ID Mayor a Menor"
        self.mostrar_ventasCredito(reverse=reverse)

    def mostrar_ventasCredito(self, reverse=False):
        """
        Obtener todos los productos de la base de datos y mostrarlos en la tabla.
        """
        self.db = SessionLocal()
        rows = obtener_ventas_credito(self.db)

        self.actualizar_tabla_ventasCredito(rows, reverse=reverse)

        self.db.close()

    def limpiar_tabla(self):
        self.TablaFacturasCredito.setRowCount(0)

    def actualizar_tabla_ventasCredito(self, rows, reverse=False):
        if not rows:
            print("No hay filas para mostrar.")
            self.TablaFacturasCredito.setRowCount(0)
            return

        try:
            self.TablaFacturasCredito.setRowCount(0)

            rows = sorted(rows, key=lambda x: x.ID_Venta_Credito, reverse=reverse)
            # Iterar sobre las filas
            for row_idx, row in enumerate(rows):
                # Datos de la fila
                id_venta_credito = str(row.ID_Venta_Credito)
                usuario = str(row.usuario)
                id_factura = str(row.ID_Factura)
                cliente = str(row.cliente)
                fecha_registro = str(row.Fecha_Registro)
                fecha_limite = row.Fecha_Limite
                total_deuda = str(row.Total_Deuda)
                saldo_pendiente = str(row.Saldo_Pendiente)
                estado = "Pagado" if row.estado else "Pendiente"

                self.TablaFacturasCredito.insertRow(0)
                # Convertir la fecha límite a datetime
                fecha_actual = datetime.now()
                
                # Configurar items de la tabla
                items = [
                    (id_venta_credito, 0),
                    (usuario, 1),
                    (id_factura, 2),
                    (cliente, 3),
                    (fecha_registro, 4),
                    (str(fecha_limite), 5),
                    (total_deuda, 6),
                    (saldo_pendiente, 7),
                    (estado, 8),
                ]

                # Determinar color de texto
                if estado == "Pagado":
                    color = QtGui.QColor("green")
                else:
                    color = QtGui.QColor("red") if fecha_actual > fecha_limite else QtGui.QColor("black")
                
                # Añadir items a la tabla
                for value, col_idx in items:
                    item = QtWidgets.QTableWidgetItem(value)
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QtGui.QBrush(color))  # Aplicar color
                    self.TablaFacturasCredito.setItem(0, col_idx, item)
        except Exception as e:
            print(f"Error al mostrar venta acredito: {e}")

    def obtener_ids_seleccionados(self):
        """
        Obtiene los IDs de los productos seleccionados en la tabla.
        """
        filas_seleccionadas = self.TablaFacturasCredito.selectionModel().selectedRows()
        ids = []

        for fila in filas_seleccionadas:
            id_producto = self.TablaFacturasCredito.item(
                fila.row(), 0
            ).text()  # Columna 0: ID del producto
            ids.append(int(id_producto))

        return ids

    def buscar_ventasCredito(self):
        """
        Busca facturas en la base de datos y actualiza la tabla.
        """
        busqueda = self.InputBuscador.text().strip()
        if not busqueda:
            self.mostrar_ventasCredito()
            return

        self.db = SessionLocal()

        facturas = buscar_ventas_credito(self.db, busqueda)
        self.actualizar_tabla_ventasCredito(facturas)

        self.db.close()

    def editar_ventaCredito(self):
        """Abrir ventana centralizada de edición de factura de crédito."""
        try:
            ids = self.obtener_ids_seleccionados()

            if not ids:
                enviar_notificacion(
                    "Advertencia", "No se seleccionaron facturas para editar."
                )
                return

            venta_credito = obtener_ventaCredito_id(self.db, ids[0])
            venta = venta_credito[0]
            
            if venta.estado == True:
                QMessageBox.warning(self, "Error", "La venta a crédito ya está pagada.")
                return
            
            factura_completa = obtener_factura_completa(self.db, venta.ID_Factura)

            if not factura_completa:
                QMessageBox.critical(
                    self, "Error", f"No se encontró la factura con ID {venta.ID_Factura}."
                )
                return

            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'cambiar_a_ventasA'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'cambiar_a_ventasA'):
                parent_window.cambiar_a_ventasA(factura_completa)
            else:
                self.enviar_facturas_Credito.emit(factura_completa)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana: {e}")
            print(f"Error detallado: {e}")

    def agregar_abono(self):
        try:
            ids = self.obtener_ids_seleccionados()

            if not ids:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "No se seleccionaron facturas para agregar abono.",
                )
                return

            print(f"[DEBUG] agregar_abono emite id={ids[0]}")
            self.enviar_ventaCredito.emit(ids[0])

        except Exception as e:
            print(f"[DEBUG] Error al agregar abono: {e}")

