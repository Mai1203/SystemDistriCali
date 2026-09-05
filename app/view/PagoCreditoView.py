from PyQt6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import QDate, Qt, QRegularExpression
from PyQt6.QtGui import QColor, QBrush, QRegularExpressionValidator

from ..ui import Ui_PagoCredito
from ..database.database import SessionLocal
from ..controllers.venta_credito_crud import (
    obtener_ventaCredito_id,
    actualizar_venta_credito,
)
from ..controllers.facturas_crud import (
    obtener_factura_por_id,
    obtener_factura_completa,
    actualizar_factura,
)
from ..controllers.metodo_pago_crud import obtener_metodo_pago_por_nombre
from ..controllers.pago_credito_crud import crear_pago_credito, obtener_pagos_credito
from ..controllers.tipo_ingreso_crud import crear_tipo_ingreso
from ..controllers.ingresos_crud import crear_ingreso
from ..utils.validar_campos import configurar_validador_numerico
from ..utils.enviar_notifi import enviar_notificacion
from datetime import datetime, timedelta
import win32print
import win32ui
import win32con


class PagoCredito_View(QWidget, Ui_PagoCredito):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.id_VentaCredito = None
        self.db = SessionLocal()

        self.configurar_validador()
        self.configurar_eventos()

    def configurar_validador(self):
        configurar_validador_numerico(self.InputPago)
        self.InputPago.setPlaceholderText("$")
        self.MetodoPagoBox.addItems(self.metodo_pago())
        self.MetodoPagoBox.currentIndexChanged.connect(self.configuracion_pago)

    def configurar_eventos(self):
        self.BtnAbonar.clicked.connect(self.abonar)
        self.BtnAtras.clicked.connect(self.volver)

    def volver(self):
        """Regresa a la vista de CrediFactura."""
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, 'cambiar_a_crediFactura'):
            parent_window = parent_window.parent()
        if parent_window and hasattr(parent_window, 'cambiar_a_crediFactura'):
            parent_window.cambiar_a_crediFactura()
        else:
            # Fallback: ocultar esta vista
            self.hide()


    def cargar_informacion(self, id_ventaCredito):
        print(f"[DEBUG] cargar_informacion llamado con id={id_ventaCredito}")
        self.id_VentaCredito = id_ventaCredito
        self.db = SessionLocal()
        try:
            venta_credito = obtener_ventaCredito_id(self.db, id_ventaCredito)
            print(f"[DEBUG] venta_credito={venta_credito}")
            if not venta_credito:
                QMessageBox.warning(self, "Error", "No se encontró la venta a crédito.")
                return

            venta = venta_credito[0]
            print(f"[DEBUG] venta.Total_Deuda={venta.Total_Deuda}, Saldo_Pendiente={venta.Saldo_Pendiente}")

            self.LabelDeuda.setText(f"Total Deuda: ${venta.Total_Deuda:,.0f}")
            self.LabelPendiente.setText(f"Pendiente: ${venta.Saldo_Pendiente:,.0f}")

            estado = venta.estado
            print(f"[DEBUG] estado={estado}")
            if estado:
                self.LabelEstado.setText("Pagada")
                self.LabelEstado.setStyleSheet(
                    "font-size: 14px; font-weight: 700; color: green;"
                    " font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
                )
                self.BtnAbonar.setEnabled(False)
            else:
                self.LabelEstado.setText("Pendiente")
                self.LabelEstado.setStyleSheet(
                    "font-size: 14px; font-weight: 700; color: #C0392B;"
                    " font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
                )
                self.BtnAbonar.setEnabled(True)

            pago_credito = obtener_pagos_credito(self.db, id_ventaCredito)
            print(f"[DEBUG] pagos_credito count={len(pago_credito)}")
            self.cargar_tabla(pago_credito, venta)
        except Exception as e:
            print(f"[DEBUG] ERROR en cargar_informacion: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cargar la información: {e}")
        finally:
            if self.db:
                self.db.close()

    def cargar_tabla(self, pagos, venta):
        self.TablaPagoCredito.setRowCount(0)
        if not pagos:
            return

        self.TablaPagoCredito.setRowCount(len(pagos))
        for row, pago in enumerate(pagos):
            id_pago = str(pago.ID_Pago_Credito)
            cliente = str(venta.cliente)
            fecha_registro = pago.Fecha_Registro.strftime("%d/%m/%Y %H:%M") if hasattr(pago.Fecha_Registro, "strftime") else str(pago.Fecha_Registro)
            id_venta_credito = str(venta.ID_Venta_Credito)
            metodo_pago = str(pago.metodopago)
            tipo_pago = str(pago.tipopago)
            monto = f"${float(pago.Monto):,.0f}"

            items = [
                (id_pago, 0),
                (cliente, 1),
                (fecha_registro, 2),
                (id_venta_credito, 3),
                (metodo_pago, 4),
                (tipo_pago, 5),
                (monto, 6),
            ]

            for value, col_idx in items:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.TablaPagoCredito.setItem(row, col_idx, item)

    def showEvent(self, event):
        super().showEvent(event)
        self.InputPago.setFocus()

    def metodo_pago(self):
        try:
            nombres_metodos = ["Efectivo", "Transferencia"]
            return nombres_metodos
        except Exception as e:
            print(f"Error al obtener métodos de pago: {e}")
            return []

    def configuracion_pago(self):
        metodo_seleccionado = self.MetodoPagoBox.currentText()
        self.InputPago.clear()
        if metodo_seleccionado in ("Efectivo", "Transferencia"):
            self.InputPago.setPlaceholderText("$")
            rx_inpago = QRegularExpression(r"^\d+(\.\d{1,2})?$")
            validator_inpago = QRegularExpressionValidator(rx_inpago)
            self.InputPago.setValidator(validator_inpago)

    def calcular_fecha_futura(self, dias):
        fecha_actual = datetime.now()
        fecha_futura = fecha_actual + timedelta(days=dias)
        return fecha_futura.replace(microsecond=0)

    def abonar(self):
        try:
            abono = self.InputPago.text().strip()
            metodo_pago = self.MetodoPagoBox.currentText().strip()

            if not abono:
                QMessageBox.warning(self, "Error", "Por favor, ingrese un valor válido para el abono.")
                return

            if not self.id_VentaCredito:
                QMessageBox.warning(self, "Error", "No hay una venta a crédito seleccionada.")
                return

            self.db = SessionLocal()
            id_metodo_pago = obtener_metodo_pago_por_nombre(self.db, metodo_pago).ID_Metodo_Pago

            venta_credito = obtener_ventaCredito_id(self.db, self.id_VentaCredito)
            if not venta_credito:
                QMessageBox.warning(self, "Error", "No se pudo obtener la venta a crédito.")
                return

            venta = venta_credito[0]

            if venta.estado is True:
                QMessageBox.warning(self, "Error", "La venta a crédito ya está pagada.")
                return

            if metodo_pago == "Efectivo":
                efectivo = float(abono)
                tranferencia = 0.0
            elif metodo_pago == "Transferencia":
                efectivo = 0.0
                tranferencia = float(abono)
            else:
                if '/' in abono:
                    total = abono.split("/")
                    efectivo = float(total[0]) if total[0] else 0
                    tranferencia = float(total[1]) if total[1] else 0
                    if efectivo == 0 or tranferencia == 0:
                        QMessageBox.warning(self, "Error", "Ingrese el monto efectivo y el monto transferencia separados por una barra (/).")
                        return
                else:
                    QMessageBox.warning(self, "Error", "Ingrese el monto efectivo y el monto transferencia separados por una barra (/).")
                    return

            abono_total = efectivo + tranferencia

            if abono_total > float(venta.Saldo_Pendiente):
                QMessageBox.warning(self, "Error", "El abono no puede ser mayor al saldo pendiente.")
                return

            id_factura = int(venta.ID_Factura)
            factura_antigua = obtener_factura_por_id(self.db, id_factura)

            monto_efectivo = float(factura_antigua.Monto_efectivo)
            monto_transaccion = float(factura_antigua.Monto_TRANSACCION)

            efectivo += monto_efectivo
            tranferencia += monto_transaccion

            total_abonar = efectivo + tranferencia

            if total_abonar == float(venta.Total_Deuda):
                estado = True
                tipo_pago = 2
            else:
                estado = False
                tipo_pago = 1

            fecha_registro = venta.Fecha_Registro
            fecha_limite = venta.Fecha_Limite
            if fecha_limite:
                dias = (fecha_limite - fecha_registro).days
                limite_pago = self.calcular_fecha_futura(dias)
            else:
                limite_pago = self.calcular_fecha_futura(15)

            saldo_pendiente = float(venta.Saldo_Pendiente) - abono_total

            pago_credito = crear_pago_credito(
                db=self.db,
                id_venta_credito=self.id_VentaCredito,
                monto=abono_total,
                id_metodo_pago=id_metodo_pago,
                id_tipo_pago=tipo_pago,
            )
            actualizar_venta_credito(
                db=self.db,
                id_venta_credito=self.id_VentaCredito,
                saldo_pendiente=saldo_pendiente,
                fecha_limite=limite_pago,
            )
            actualizar_factura(
                db=self.db,
                id_factura=id_factura,
                monto_efectivo=efectivo,
                monto_transaccion=tranferencia,
                id_metodo_pago=id_metodo_pago,
                estado=estado,
            )

            tipo_ingreso = crear_tipo_ingreso(db=self.db, tipo_ingreso="FAC-ABONO", id_pago_credito=pago_credito.ID_Pago_Credito)
            crear_ingreso(db=self.db, id_tipo_ingreso=tipo_ingreso.ID_Tipo_Ingreso)

            self._imprimir_ticket_abono(
                venta=venta,
                factura=obtener_factura_completa(self.db, id_factura),
                pagos=obtener_pagos_credito(self.db, self.id_VentaCredito),
                abono=abono_total,
            )

            enviar_notificacion("Éxito", "Abono registrado correctamente.")
            self.InputPago.clear()
            self.cargar_informacion(self.id_VentaCredito)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el abono: {e}")
            print(f"Error al procesar el abono: {e}")
        finally:
            if self.db:
                self.db.close()

    def _imprimir_ticket_abono(self, venta, factura, pagos, abono):
        if not factura:
            return

        try:
            cliente = factura["Cliente"]
            nombre_cliente = f'{cliente["Nombre"]} {cliente["Apellido"]}'.strip()
            direccion = cliente["Direccion"] or ""
            direccion_linea1 = direccion[:35]
            direccion_linea2 = direccion[35:] if len(direccion) > 35 else ""
            detalles = factura["Detalles"]
            max_lines_per_page = 30
            current_line = 0
            empresa_nombre = "Distri Magik"
            empresa_direccion = "Cali, Colombia"
            empresa_telefono = "315-436-31-88"
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            limite_pago_formateado = (
                venta.Fecha_Limite.strftime("%d/%m/%Y")
                if hasattr(venta.Fecha_Limite, "strftime")
                else str(venta.Fecha_Limite)
            )
            total_deuda_formateado = f"${float(venta.Total_Deuda):,.2f}"
            saldo_formateado = f"${max(0, float(venta.Saldo_Pendiente) - abono):,.2f}"

            impresora = win32print.GetDefaultPrinter()
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(impresora)
            hdc.StartDoc("Ticket de Venta")
            hdc.StartPage()

            font_encabezado = win32ui.CreateFont({
                "name": "Lucida Console",
                "height": 28,
                "weight": win32con.FW_BOLD,
            })
            font_size = 18
            line_height = font_size + 10
            font = win32ui.CreateFont({
                "name": "Lucida Console",
                "height": font_size,
                "weight": win32con.FW_BOLD,
            })
            hdc.SelectObject(font_encabezado)

            printer_width = hdc.GetDeviceCaps(win32con.HORZRES)
            center_x = printer_width // 2
            x, y = 2, 2 + 5 * line_height
            for index, linea in enumerate(
                [empresa_nombre, empresa_direccion, empresa_telefono, fecha_actual]
            ):
                text_width = hdc.GetTextExtent(linea)[0]
                hdc.TextOut(center_x - text_width // 2, 50 + index * line_height, linea)
            y += line_height
            hdc.SelectObject(font)

            hdc.TextOut(x, y, "-----------------------------------------------------------------------------------------------------------------")
            y += line_height
            hdc.TextOut(x, y, "Crédito")
            y += line_height
            hdc.TextOut(x, y, f"COT No. 0000{venta.ID_Factura}")
            y += line_height
            hdc.TextOut(x, y, f"Cliente: {nombre_cliente}")
            y += line_height
            hdc.TextOut(x, y, f"Cédula: {cliente['ID_Cliente']}")
            y += line_height
            hdc.TextOut(x, y, f"Teléfono: {cliente['Teléfono'] or ''}")
            y += line_height
            hdc.TextOut(x, y, f"Dirección: {direccion_linea1}")
            y += line_height
            if direccion_linea2:
                hdc.TextOut(x, y, direccion_linea2)
                y += line_height

            hdc.TextOut(x, y, "-----------------------------------------------------------------------------------------------------------------")
            y += line_height
            hdc.TextOut(x, y, "{:<18} {:>6} {:>10} {:>10}".format("Producto", "Cant.", "Precio", "Total"))
            y += line_height

            for detalle in detalles:
                nombre_producto = str(detalle["Producto"]).strip().replace("\n", " ")[:18].ljust(18)
                cantidad = str(detalle["Cantidad"])
                precio_unitario = f"{float(detalle['Precio_Unitario']):,.0f}".replace(",", ".")
                total_producto = f"{float(detalle['Subtotal']):,.0f}".replace(",", ".")
                hdc.TextOut(
                    x,
                    y,
                    "{:<18} {:>6} {:>10} {:>10}".format(
                        nombre_producto, cantidad, precio_unitario, total_producto
                    ),
                )
                y += line_height
                current_line += 1
                if current_line >= max_lines_per_page:
                    hdc.EndPage()
                    hdc.StartPage()
                    y = 2
                    current_line = 0

            totales = f"""
            -----------------------------------------------------------------------------------------------------
            Deuda Total: {total_deuda_formateado}
            Abono actual: ${abono:,.2f}
            Saldo Pendiente: {saldo_formateado}
            Fecha Limite: {limite_pago_formateado}
            -----------------------------------------------------------------------------------------------------

            HISTORIAL DE ABONOS
            """
            for linea in totales.split("\n"):
                hdc.TextOut(x, y, linea.strip())
                y += line_height

            for pago in pagos:
                fecha_pago = pago.Fecha_Registro.strftime("%d/%m/%Y %H:%M")
                hdc.TextOut(
                    x,
                    y,
                    f"{fecha_pago}  ${float(pago.Monto):,.2f}  {pago.metodopago}  {pago.tipopago}",
                )
                y += line_height

            hdc.TextOut(x, y, "-----------------------------------------------------------------------------------------------------")
            y += line_height
            hdc.TextOut(x, y, "¡Gracias por tu compra!")
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        except Exception as error:
            QMessageBox.warning(
                self,
                "Impresión no disponible",
                f"El abono se guardó, pero no se pudo imprimir el recibo: {error}",
            )

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        super().closeEvent(event)
