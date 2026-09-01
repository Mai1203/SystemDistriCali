from PyQt6.QtWidgets import (
    QWidget,
    QMessageBox,
)
from ..utils.enviar_notifi import Mensajes as QMessageBox
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QTimer

from ..ui import Ui_Facturas
from ..database.database import SessionLocal
from ..controllers.facturas_crud import *
from ..controllers.venta_credito_crud import obtener_ventas_credito
from ..controllers.pago_credito_crud import obtener_pagos_credito
from ..controllers.producto_crud import *
from ..controllers.tipo_ingreso_crud import *
from ..controllers.ingresos_crud import *
from ..utils.enviar_notifi import enviar_notificacion
from ..utils.formateador import formatear_factura_completa


class Facturas_View(QWidget, Ui_Facturas):
    enviar_facturas_A = pyqtSignal(dict)
    enviar_facturas_B = pyqtSignal(dict)
    enviar_facturas_C = pyqtSignal(dict)
    enviar_facturas_D = pyqtSignal(dict)
    enviar_facturas_Credito = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Facturas_View, self).__init__(parent)
        self.setupUi(self)

        self.InputBuscador.setPlaceholderText(
            "Buscar por ID, Cliente, Fecha, Metodo de pago o Tipo deFactura"
        )
        self.InputBuscador.textChanged.connect(self.buscar_facturas)

        self.TablaFacturas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaFacturas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.TablaFacturas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.TablaFacturas.setColumnWidth(0, 50)
        self.TablaFacturas.setColumnWidth(5, 120)
        self.TablaFacturas.setColumnWidth(6, 120)


        self.BtnFacturaPagada.clicked.connect(self.factura_pagada)
        self.BtnVerFactura.clicked.connect(self.ver_factura)
        self.BtnEditarFactura.clicked.connect(self.editar_factura)
        self.BtnVerCancelarVenta.clicked.connect(self.cancelar_venta)

        # Responsividad del Sistema de Diseño (resizeEvent → adapt_to_size)
        QTimer.singleShot(50, self._adapt_current)

    # ── Responsividad ──────────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adapt_current()

    def _adapt_current(self):
        w, h = self.width(), self.height()
        if w > 0 and h > 0:
            self.adapt_to_size(w, h)

    def showEvent(self, event):
        super().showEvent(event)
        self.limpiar_tabla_facturas()
        self.mostrar_facturas()
        self.InputBuscador.clear()
                        
    
    def cancelar_venta(self):
        ids = self.obtener_ids_seleccionados()

        if not ids:
            enviar_notificacion(
                "Advertencia", "No se seleccionaron facturas para cancelar."
            )
            return
        
        for id_factura in ids:
            facturas = obtener_factura_por_id(self.db, id_factura)
            if facturas.Estado == True:
                QMessageBox.warning(self, "Factura", f"La factura {id_factura} ya está pagada.")
                return 
            
            if facturas.tipofactura == "FAC-CREDITO":
                QMessageBox.warning(self, "Factura", f"La factura {id_factura} no es una factura de venta.")
                return

            factura_completa = obtener_factura_completa(self.db, id_factura)
            
            productos = factura_completa["Detalles"]
            
            for producto in productos:
                id_producto = producto["ID_Producto"]
                cantidad = producto["Cantidad"]
                
                producto = obtener_producto_por_id(self.db, id_producto)
                
                stock = producto[0].Stock_actual
                cantidad = cantidad + stock
                actualizar_producto(db=self.db, id_producto=id_producto, stock_actual=cantidad)
                
            eliminar_factura(self.db, id_factura)
            
        self.limpiar_tabla_facturas()
        self.mostrar_facturas()
        enviar_notificacion("Éxito", "Factura(s) cancelada(s) correctamente.")
        
    def mostrar_facturas(self):
        # Obtener datos de la tabla
        self.db = SessionLocal()
        rows = obtener_facturas(self.db)

        self.actualizar_tabla_facturas(rows)
        print("Mostrar facturas en la tabla")

        # Cerrar la conexión a la base de datos
        self.db.close()

    def limpiar_tabla_facturas(self):
        self.TablaFacturas.setRowCount(0)

    def actualizar_tabla_facturas(self, rows):
        if not rows:
            print("No hay filas para mostrar.")
            self.TablaFacturas.setRowCount(0)
            return

        try:
            self.TablaFacturas.setRowCount(0)

             # Ordenar filas por ID en orden descendente (de mayor a menor)
            rows.sort(key=lambda x: x.ID_Factura, reverse=False)
            # Iterar sobre las filas
            for row_idx, row in enumerate(rows):
                # Datos de la fila
                id_factura = str(row.ID_Factura)
                fecha = str(row.Fecha_Factura)
                fecha_conf = str(row.fecha_modificacion) if row.fecha_modificacion else "Actual"
                cliente = str(row.cliente)
                monto_efectivo = str(row.Monto_efectivo)
                monto_transaccion = str(row.Monto_TRANSACCION)
                estado = "Pagado" if row.Estado else "Pendiente"
                id_tipo_factura = str(row.tipofactura)
                id_metodo_pago = str(row.metodopago)
                usuario = str(row.usuario)
                total = row.Monto_efectivo + row.Monto_TRANSACCION
                domicilio = row.Domicilio

                self.TablaFacturas.insertRow(0)
                # Configurar items de la tabla
                items = [
                    (id_factura, 0),
                    (usuario, 1),
                    (id_metodo_pago, 2),
                    (cliente, 3),
                    (id_tipo_factura, 4),
                    (fecha, 5),
                    (fecha_conf, 6),  # Texto fijo
                    (monto_efectivo, 7),
                    (monto_transaccion, 8),
                    (str(total), 9),
                    (estado, 10),
                ]

                # Determinar color de texto
                if domicilio == True:
                    color = QtGui.QColor("green")
                else:
                    color = QtGui.QColor("black")

                # Añadir items a la tabla
                for value, col_idx in items:
                    item = QtWidgets.QTableWidgetItem(value)
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QtGui.QBrush(color))
                    self.TablaFacturas.setItem(0, col_idx, item)
                    
        except Exception as e:
            print(f"Error al mostrar las facturas: {e}")

    def obtener_ids_seleccionados(self):
        """
        Obtiene los IDs de los productos seleccionados en la tabla.
        """
        filas_seleccionadas = self.TablaFacturas.selectionModel().selectedRows()
        ids = []

        for fila in filas_seleccionadas:
            id_producto = self.TablaFacturas.item(
                fila.row(), 0
            ).text()  # Columna 0: ID del producto
            ids.append(int(id_producto))

        return ids

    def buscar_facturas(self):
        """
        Busca facturas en la base de datos y actualiza la tabla.
        """
        busqueda = self.InputBuscador.text().strip()
        if not busqueda:
            self.mostrar_facturas()
            return

        self.db = SessionLocal()

        facturas = buscar_facturas(self.db, busqueda)
        self.actualizar_tabla_facturas(facturas)

        self.db.close()

    def factura_pagada(self):
        """
        Marca la factura como pagada.
        """
        ids = self.obtener_ids_seleccionados()

        if not ids:
            enviar_notificacion(
                "Advertencia", "No se seleccionaron productos para marcar como pagada."
            )
            return       
        
        try:
            db = SessionLocal()

            for id_factura in ids:
                factura = obtener_factura_por_id(db=db, id_factura=id_factura)
                
                if factura.tipofactura == "FAC-CREDITO":
                    QMessageBox.warning(self, "Factura", f"La factura {id_factura} no es una factura de venta.")
                    return
                
                if factura.Estado == True:
                    QMessageBox.warning(
                        self, "Factura", f"La factura {id_factura} ya está pagada."
                    )
                else:
                    actualizar_factura(db=db, id_factura=id_factura, estado=True)
                    tipo_ingreso = crear_tipo_ingreso(
                        db=db,
                        tipo_ingreso=f"Venta {factura.tipofactura}",
                        id_factura=id_factura,
                    )
                    crear_ingreso(db=db, id_tipo_ingreso=tipo_ingreso.ID_Tipo_Ingreso)
            db.commit()
            enviar_notificacion(
                "Éxito", "Factura(s) marcada(s) como pagada(s) correctamente."
            )
            self.limpiar_tabla_facturas()
            self.mostrar_facturas()
        except Exception as e:
            enviar_notificacion(
                "Error", f"Error al marcar factura(s) como pagada(s): {e}"
            )
        finally:
            db.close()

    def editar_factura(self):
        """Abrir ventana centralizada para editar la factura seleccionada."""
        try:
            ids = self.obtener_ids_seleccionados()

            if not ids:
                enviar_notificacion(
                    "Advertencia", "No se seleccionaron facturas para editar."
                )
                return
            
            # Obtener los datos completos de la factura
            factura_completa = obtener_factura_completa(self.db, ids[0])

            if not factura_completa:
                QMessageBox.critical(
                    self, "Error", f"No se encontró la factura con ID {ids[0]}."
                )
                return

            factura = factura_completa["Factura"]
            if factura["Estado"]:
                QMessageBox.warning(
                    self,
                    "Factura bloqueada",
                    "La factura ya está pagada y no puede editarse.",
                )
                return

            venta_credito = next(
                (
                    venta for venta in obtener_ventas_credito(self.db)
                    if venta.ID_Factura == ids[0]
                ),
                None,
            )
            if venta_credito and obtener_pagos_credito(
                self.db, venta_credito.ID_Venta_Credito
            ):
                QMessageBox.warning(
                    self,
                    "Factura bloqueada",
                    "La factura de crédito ya tiene abonos y no puede editarse.",
                )
                return

            # Editar desde el formulario de ventas para conservar su gestión de productos.
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'cambiar_a_ventasA'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'cambiar_a_ventasA'):
                parent_window.cambiar_a_ventasA(factura_completa)
            else:
                self.enviar_facturas_A.emit(factura_completa)

        except Exception as e:
            print(f"Error al abrir ventana de edición: {e}")
            enviar_notificacion("Error", f"Error al editar factura: {e}")

    def ver_factura(self):
        ids = self.obtener_ids_seleccionados()
        if not ids:
            enviar_notificacion(
                "Advertencia", "No se seleccionó ninguna factura para consultar."
            )
            return

        db = SessionLocal()
        try:
            factura_completa = obtener_factura_completa(db, ids[0])
            if not factura_completa:
                QMessageBox.warning(self, "Factura", "No se encontró la factura seleccionada.")
                return

            texto = formatear_factura_completa(factura_completa)
            QMessageBox.information(self, "Ver factura", texto)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo consultar la factura: {e}")
        finally:
            db.close()