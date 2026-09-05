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
from ..utils.formateador import formatear_factura_completa
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
        self.BtnVerFactura.clicked.connect(self.ver_factura)
        self.BtnAgregarAbono.clicked.connect(self.agregar_abono)
        self.BtnImprimirTicket.clicked.connect(self.imprimir_ticket)
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

            if obtener_pagos_credito(self.db, venta.ID_Venta_Credito):
                QMessageBox.warning(
                    self,
                    "Factura bloqueada",
                    "La factura de crédito ya tiene abonos y no puede editarse.",
                )
                return
            
            factura_completa = obtener_factura_completa(self.db, venta.ID_Factura)

            if not factura_completa:
                QMessageBox.critical(
                    self, "Error", f"No se encontró la factura con ID {venta.ID_Factura}."
                )
                return

            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'cambiar_a_ventasCredito'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'cambiar_a_ventasCredito'):
                parent_window.cambiar_a_ventasCredito(
                    factura_completa, venta.ID_Venta_Credito
                )
            else:
                self.enviar_facturas_Credito.emit(
                    factura_completa, venta.ID_Venta_Credito
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana: {e}")
            print(f"Error detallado: {e}")

    def ver_factura(self):
        ids = self.obtener_ids_seleccionados()
        if not ids:
            enviar_notificacion(
                "Advertencia", "No se seleccionó ninguna factura para consultar."
            )
            return

        db = SessionLocal()
        try:
            venta_credito = obtener_ventaCredito_id(db, ids[0])
            if not venta_credito:
                QMessageBox.warning(self, "Factura", "No se encontró la factura seleccionada.")
                return

            venta = venta_credito[0]
            factura_completa = obtener_factura_completa(db, venta.ID_Factura)
            credito = {
                "Total_Deuda": venta.Total_Deuda,
                "Saldo_Pendiente": venta.Saldo_Pendiente,
                "Fecha_Limite": venta.Fecha_Limite,
            }
            pagos = obtener_pagos_credito(db, venta.ID_Venta_Credito)
            texto = formatear_factura_completa(factura_completa, credito, pagos)
            QMessageBox.information(self, "Ver factura de crédito", texto)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo consultar la factura: {e}")
        finally:
            db.close()

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

    def imprimir_ticket(self):
        ids = self.obtener_ids_seleccionados()
        if not ids:
            enviar_notificacion("Advertencia", "No se seleccionó ninguna factura para imprimir.")
            return

        db = SessionLocal()
        try:
            import win32print
            import win32ui
            import win32con
            import datetime
            
            venta_credito = obtener_ventaCredito_id(db, ids[0])
            if not venta_credito:
                QMessageBox.warning(self, "Factura", "No se encontró la factura de crédito seleccionada.")
                return
            
            venta = venta_credito[0]
            factura_completa = obtener_factura_completa(db, venta.ID_Factura)
            if not factura_completa:
                QMessageBox.warning(self, "Factura", "No se encontró el detalle de la factura.")
                return

            factura = factura_completa["Factura"]
            cliente = factura_completa["Cliente"]
            detalles = factura_completa["Detalles"]

            client_name = f"{cliente['Nombre']} {cliente['Apellido']}".strip()
            client_id = str(cliente["ID_Cliente"])
            client_address = str(cliente.get("Direccion", ""))
            client_phone = str(cliente.get("Teléfono", ""))
            
            items = []
            for d in detalles:
                items.append((d["Producto"], d["Cantidad"], d["Precio_Unitario"], d["Subtotal"]))

            subtotal = sum(d["Subtotal"] for d in detalles)
            delivery_fee = factura.get("Descuento", 0)
            total = subtotal - delivery_fee
            invoice_number = f"0000{factura['ID_Factura']}"
            limite_pago = venta.Fecha_Limite
            limite_pago_formateado = limite_pago.strftime("%d/%m/%Y") if hasattr(limite_pago, 'strftime') else str(limite_pago)
            
            max_lines_per_page = 30
            current_line = 0
            empresa_nombre = "Distri Magik"
            empresa_direccion = "Cali, Colombia"
            empresa_telefono = "315-038-66-18"
            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            subtotal_formateado = f"${subtotal:,.2f}"
            total_formateado = f"${total:,.2f}"

            delivery_fee = float(delivery_fee)
            if delivery_fee.is_integer():
                delivery_fee_formateado = f"${int(delivery_fee):,.0f}"
            else:
                delivery_fee_formateado = f"${delivery_fee:,.2f}"

            direccion = client_address
            direccion_linea1 = direccion[:35]
            direccion_linea2 = direccion[35:] if len(direccion) > 35 else ""

            impresora = win32print.GetDefaultPrinter()
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(impresora)
            hDC.StartDoc("Ticket de Venta")
            hDC.StartPage()

            font_encabezado = win32ui.CreateFont({
                "name": "Lucida Console",
                "height": 28,
                "weight": win32con.FW_BOLD
            })
            font_size = 18
            line_height = font_size + 10
            font = win32ui.CreateFont({
                "name": "Lucida Console",
                "height": font_size,
                "weight": win32con.FW_BOLD
            })
            hDC.SelectObject(font_encabezado)

            printer_width = hDC.GetDeviceCaps(win32con.HORZRES)
            center_x = printer_width // 2
            x, y = 2, 2 + 5 * line_height

            for i, linea in enumerate([empresa_nombre, empresa_direccion, empresa_telefono, fecha_actual]):
                text_size = hDC.GetTextExtent(linea)
                text_width = text_size[0]
                hDC.TextOut(center_x - (text_width // 2), 50 + (i * line_height), linea)
            y += line_height
            hDC.SelectObject(font)

            hDC.TextOut(x, y, "-----------------------------------------------------------------------------------------------------------------")
            y += line_height
            hDC.TextOut(x, y, "Crédito")
            y += line_height
            hDC.TextOut(x, y, f"COT No. {invoice_number}")
            y += line_height
            hDC.TextOut(x, y, f"Cliente: {client_name}")
            y += line_height
            hDC.TextOut(x, y, f"Cédula: {client_id}")
            y += line_height
            hDC.TextOut(x, y, f"Teléfono: {client_phone}")
            y += line_height
            hDC.TextOut(x, y, f"Dirección: {direccion_linea1}")
            y += line_height
            if direccion_linea2:
                hDC.TextOut(x, y, direccion_linea2)
                y += line_height

            hDC.TextOut(x, y, "-----------------------------------------------------------------------------------------------------------------")
            y += line_height
            header = "{:<18} {:>6} {:>10} {:>10}".format("Producto", "Cant.", "Precio", "Total")
            hDC.TextOut(x, y, header)
            y += line_height

            for item in items:
                nombre_producto = item[0].strip().replace('\n', ' ')[:18].ljust(18)
                cantidad = str(item[1])
                precio_unitario = f"{item[2]:,.0f}".replace(",", ".")
                total_producto = f"{item[3]:,.0f}".replace(",", ".")
                linea = "{:<18} {:>6} {:>10} {:>10}".format(nombre_producto, cantidad, precio_unitario, total_producto)
                hDC.TextOut(x, y, linea)
                y += line_height
                current_line += 1
                if current_line >= max_lines_per_page:
                    hDC.EndPage()
                    hDC.StartPage()
                    y = 2
                    current_line = 0

            totales = f"""
            -----------------------------------------------------------------------------------------------------
            Deuda Total: {subtotal_formateado}
            Envío: {delivery_fee_formateado}
            Fecha Limite: {limite_pago_formateado}
            -----------------------------------------------------------------------------------------------------

            ¡Gracias por tu compra!
            """
            for line in totales.split("\n"):
                hDC.TextOut(x, y, line.strip())
                y += line_height

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
            
            enviar_notificacion("Éxito", "Ticket de crédito enviado a la impresora correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo imprimir el ticket: {e}")
            print(f"[DEBUG] Error al imprimir ticket: {e}")
        finally:
            db.close()

