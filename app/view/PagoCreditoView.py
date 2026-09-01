from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QDate, Qt, QRegularExpression
from PyQt6.QtGui import QColor, QBrush, QRegularExpressionValidator

from ..ui import Ui_PagoCredito
from ..database.database import SessionLocal
from ..controllers.venta_credito_crud import (
    obtener_ventaCredito_id,
    actualizar_venta_credito,
)
from ..controllers.facturas_crud import obtener_factura_por_id, actualizar_factura
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
                item = QtWidgets.QTableWidgetItem(value)
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

            enviar_notificacion("Éxito", "Abono registrado correctamente.")
            self.InputPago.clear()
            self.cargar_informacion(self.id_VentaCredito)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el abono: {e}")
            print(f"Error al procesar el abono: {e}")
        finally:
            if self.db:
                self.db.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        super().closeEvent(event)
