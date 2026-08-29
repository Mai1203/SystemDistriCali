from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate, QTimer  # No se usa QDate, pero se puede eliminar si no es necesario
from ..database.database import SessionLocal
from ..ui import Ui_Reportes
from ..controllers.tipo_pago_crud import *
from ..controllers.metodo_pago_crud import *
from ..controllers.pago_credito_crud import *
from ..controllers.venta_credito_crud import *
from ..controllers.producto_crud import *
from ..controllers.ingresos_crud import *
from ..controllers.egresos_crud import *
from ..controllers.facturas_crud import obtener_reporte_facturas
from ..utils.Estructura_Reporte import crear_pdf, generar_analisis_financiero, generar_pdf_productos_mas_vendidos
from ..utils.Credito__Reporte import generar_pdf_creditos
from ..utils import Ingresos_egresos_reporte
from sqlalchemy import and_, func
import os
from datetime import datetime


class Reportes_View(QWidget, Ui_Reportes):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Variables para almacenar fechas
        self.fecha_inicio_caja = None
        self.fecha_fin_caja = None
        self.fecha_inicio_analisis = None
        self.fecha_fin_analisis = None
        self.modo_intervalo_caja = False
        self.modo_intervalo_analisis = False

        # Configurar calendarios
        self.CalendarioCaja.selectionChanged.connect(lambda: self.obtener_fecha(self.CalendarioCaja, "caja"))
        self.CalendarioAnalisis.selectionChanged.connect(lambda: self.obtener_fecha(self.CalendarioAnalisis, "analisis"))

        # Configurar ComboBox
        self.TipoCajaComboBox.addItems(["Ingresos", "Egresos"])
        self.TiempoCajaComboBox.addItems(["Diario", "Intervalo de días"])
        self.TipoProductosComboBox.addItems(["Bajo Stock", "Más  Vendidos - Menos Vendidos", "Inactivos"])
        self.ReporteAnalisisComboBox.addItems(["Comparación Financiera", "Análisis de crédito"])
        self.ReporteAnalisisComboBox.currentIndexChanged.connect(self.cambiar_estado)
        self.TiempoAnalisisComboBox.addItems(["Diario", "Intervalo de días"])

        # Conectar ComboBox de tiempo
        self.TiempoCajaComboBox.currentIndexChanged.connect(lambda: self.cambiar_estado_calendario("caja"))
        self.TiempoAnalisisComboBox.currentIndexChanged.connect(lambda: self.cambiar_estado_calendario("analisis"))
        self.BtnTicketProducto.clicked.connect(lambda: self.generar_pdf())
        self.BtnTicketCaja.clicked.connect(lambda: self.obtener_ingresos_egresos(self.TipoCajaComboBox.currentText()))
        self.BtnTicketAnalisis.clicked.connect(
            lambda: self.obtener_creditos_analisis(self.ReporteAnalisisComboBox.currentText())
        )

        # Habilitar calendarios (ya están habilitados por defecto, pero por claridad)
        self.CalendarioCaja.setEnabled(True)
        self.CalendarioAnalisis.setEnabled(True)

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

    def cambiar_estado(self):
        """Cambiar estado de combobox y calendario."""
        opcion = self.ReporteAnalisisComboBox.currentText()
        if opcion == "Análisis de crédito":
            self.CalendarioAnalisis.setEnabled(False)
            self.TiempoAnalisisComboBox.setEnabled(False)
        else:
            self.CalendarioAnalisis.setEnabled(True)
            self.TiempoAnalisisComboBox.setEnabled(True)

    def obtener_creditos(self, tipo):
        # Este método parece no usarse; se mantiene por compatibilidad
        tipo = "Análisis de crédito"
        self.obtener_creditos_analisis(tipo)

    def obtener_creditos_analisis(self, tipo):
        db = SessionLocal()
        try:
            if tipo == "Análisis de crédito":
                ventas = obtener_ventas_credito(db)
                resultado = []
                for venta in ventas:
                    pagos = db.query(PagoCredito).filter(PagoCredito.ID_Venta_Credito == venta.ID_Venta_Credito).all()
                    resultado.append({
                        "venta": {
                            "ID_Venta_Credito": venta.ID_Venta_Credito,
                            "Total_Deuda": venta.Total_Deuda,
                            "Saldo_Pendiente": venta.Saldo_Pendiente,
                            "Fecha_Registro": venta.Fecha_Registro
                        },
                        "pagos": [{
                            "ID_Pago_Credito": pago.ID_Pago_Credito,
                            "Monto": pago.Monto,
                            "Fecha_Registro": pago.Fecha_Registro,
                            "Metodo_Pago": self.obtener_metodo_pago(db, pago.ID_Metodo_Pago),
                            "Tipo_Pago": self.obtener_tipo_pago(db, pago.ID_Tipo_Pago)
                        } for pago in pagos]
                    })
                generar_pdf_creditos(self, resultado)
            else:
                # Comparación Financiera
                if not self.fecha_inicio_analisis:
                    QMessageBox.warning(self, "Error", "Debes seleccionar una fecha inicial")
                    return
                print(f"Fecha inicio seleccionada: {self.fecha_inicio_analisis}")
                print(f"Fecha fin seleccionada: {self.fecha_fin_analisis}")

                if self.fecha_inicio_analisis and self.fecha_fin_analisis:
                    fecha_inicio = self.fecha_inicio_analisis.toString('yyyy-MM-dd')
                    fecha_fin = self.fecha_fin_analisis.toString('yyyy-MM-dd') + " 23:59:59"
                    analisis = obtener_reporte_facturas(db=db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
                    ingresos = obtener_ingresos_reportes(db=db, FechaInicio=fecha_inicio, FechaFin=fecha_fin)
                    egresos = obtener_egresos_reporte(db=db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
                    try:
                        generar_analisis_financiero(analisis, ingresos, egresos)
                    except Exception as e:
                        print(f"Error al generar pdf Comparación Financiera - Intervalo de días: {e}")
                elif self.fecha_inicio_analisis:
                    fecha_inicio = self.fecha_inicio_analisis.toString('yyyy-MM-dd')
                    fecha_fin = None
                    analisis = obtener_reporte_facturas(db=db, fecha_inicio=fecha_inicio)
                    ingresos = obtener_ingresos_reportes(db=db, FechaInicio=fecha_inicio)
                    egresos = obtener_egresos_reporte(db=db, fecha_inicio=fecha_inicio)
                    try:
                        generar_analisis_financiero(analisis, ingresos, egresos)
                    except Exception as e:
                        print(f"Error al generar pdf Análisis de crédito por fecha: {e}")
        except Exception as e:
            print(f"Error al generar el reporte Comparación Financiera: {e}")
        finally:
            db.close()

    def obtener_metodo_pago(self, db, id_metodo_pago):
        metodo_pago = db.query(MetodoPago).filter(MetodoPago.ID_Metodo_Pago == id_metodo_pago).first()
        return metodo_pago.Nombre if metodo_pago else "Desconocido"

    def obtener_tipo_pago(self, db, id_tipo_pago):
        tipo_pago = db.query(TipoPago).filter(TipoPago.ID_Tipo_Pago == id_tipo_pago).first()
        return tipo_pago.Nombre if tipo_pago else "Desconocido"

    def obtener_ingresos_egresos(self, tipo):
        db = SessionLocal()
        try:
            if not self.fecha_inicio_caja:
                QMessageBox.warning(self, "Error", "Debes seleccionar una fecha inicial")
                return

            if tipo == "Egresos":
                query = db.query(Egresos)
                print(f"Fecha inicio seleccionada: {self.fecha_inicio_caja}")
                print(f"Fecha fin seleccionada: {self.fecha_fin_caja}")

                if self.fecha_inicio_caja and self.fecha_fin_caja:
                    fecha_inicio = self.fecha_inicio_caja.toString('yyyy-MM-dd')
                    fecha_fin = self.fecha_fin_caja.toString('yyyy-MM-dd') + " 23:59:59"
                    query = query.filter(and_(
                        func.date(Egresos.Fecha_Egreso) >= fecha_inicio,
                        func.date(Egresos.Fecha_Egreso) <= fecha_fin
                    ))
                elif self.fecha_inicio_caja:
                    fecha_inicio = self.fecha_inicio_caja.toString('yyyy-MM-dd')
                    fecha_fin = None
                    query = query.filter(func.date(Egresos.Fecha_Egreso) == fecha_inicio)

                egresos = query.all()
                datos = [(e.ID_Egreso, e.Tipo_Egreso, e.Monto_Egreso, e.Fecha_Egreso) for e in egresos]
                Ingresos_egresos_reporte.generar_pdf_transacciones(datos, "egresos", fecha_inicio, fecha_fin)
            else:
                print(f"Fecha inicio seleccionada: {self.fecha_inicio_caja}")
                print(f"Fecha fin seleccionada: {self.fecha_fin_caja}")
                ingresos = []
                if self.fecha_inicio_caja and self.fecha_fin_caja:
                    fecha_inicio = self.fecha_inicio_caja.toString('yyyy-MM-dd')
                    fecha_fin = self.fecha_fin_caja.toString('yyyy-MM-dd') + " 23:59:59"
                    ingresos = obtener_ingresos_reportes(db=db, FechaInicio=fecha_inicio, FechaFin=fecha_fin)
                elif self.fecha_inicio_caja:
                    fecha_inicio = self.fecha_inicio_caja.toString('yyyy-MM-dd')
                    fecha_fin = None
                    ingresos = obtener_ingresos_reportes(db=db, FechaInicio=fecha_inicio)

                datos = []
                for e in ingresos:
                    if e.tipo_ingreso.startswith("Venta FAC-"):
                        datos.append((e.ID_Ingreso, e.tipo_ingreso, e.monto_efectivo, e.monto_transaccion, e.fecha_venta))
                    else:
                        if e.metodo_pago == "Efectivo":
                            efectivo = str(e.monto)
                            transferencia = "0.0"
                        else:
                            transferencia = str(e.monto)
                            efectivo = "0.0"
                        datos.append((e.ID_Ingreso, e.tipo_ingreso, efectivo, transferencia, e.fecha_abono))
                Ingresos_egresos_reporte.generar_pdf_transacciones(datos, "ingresos", fecha_inicio, fecha_fin)
        finally:
            db.close()

    def mostrar_mensaje(self, titulo, mensaje):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

    def obtener_productos(self, tipo):
        db = SessionLocal()
        try:
            if tipo == "Bajo Stock":
                productos = (
                    db.query(Productos.ID_Producto, Productos.Nombre, Productos.Stock_actual)
                    .order_by(Productos.Stock_actual)
                    .all()
                )
                return [(p.ID_Producto, p.Nombre, p.Stock_actual) for p in productos]
            elif tipo == "Más  Vendidos - Menos Vendidos":
                return []
            elif tipo == "Inactivos":
                productos = (
                    db.query(Productos.ID_Producto, Productos.Nombre, Productos.Estado)
                    .filter(Productos.Estado.in_(['0', '1']))
                    .order_by(Productos.Estado)
                    .all()
                )
                return [(p.ID_Producto, p.Nombre, "Activo" if p.Estado == 1 else "Inactivo") for p in productos]
            else:
                return []
        finally:
            db.close()

    def generar_pdf(self):
        tipo_seleccionado = self.TipoProductosComboBox.currentText()

        if tipo_seleccionado == "Más  Vendidos - Menos Vendidos":
            db = SessionLocal()
            productos = obtener_productos_mas_vendidos(db=db, limite=30)
            generar_pdf_productos_mas_vendidos(productos)
            db.close()
        else:
            productos = self.obtener_productos(tipo_seleccionado)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            nombre_pdf_por_defecto = f"{tipo_seleccionado}_{fecha_actual}.pdf"
            ruta_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", nombre_pdf_por_defecto, "PDF Files (*.pdf)")

            if ruta_archivo:
                crear_pdf(ruta_archivo, productos, tipo_seleccionado)
                QMessageBox.information(self, "PDF Generado", f"El archivo PDF ha sido generado en: {ruta_archivo}")
            else:
                QMessageBox.information(self, "Operación cancelada", "No se ha seleccionado ninguna ruta para guardar el archivo.")

    def closeEvent(self, event):
        respuesta = QMessageBox.question(
            self,
            "Salir",
            "¿Estás seguro de que deseas salir sin guardar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def obtener_fecha(self, calendario, tipo):
        fecha = calendario.selectedDate()

        if tipo == "caja":
            if self.modo_intervalo_caja:
                if not self.fecha_inicio_caja:
                    self.fecha_inicio_caja = fecha
                    print(f"[Caja] Fecha de inicio: {self.fecha_inicio_caja.toString('yyyy-MM-dd')}")
                elif not self.fecha_fin_caja:
                    self.fecha_fin_caja = fecha
                    print(f"[Caja] Fecha de fin: {self.fecha_fin_caja.toString('yyyy-MM-dd')}")
                    calendario.setEnabled(False)
            else:
                self.fecha_inicio_caja = fecha
                self.fecha_fin_caja = None
                print(f"[Caja] Fecha seleccionada: {self.fecha_inicio_caja.toString('yyyy-MM-dd')}")
        elif tipo == "analisis":
            if self.modo_intervalo_analisis:
                if not self.fecha_inicio_analisis:
                    self.fecha_inicio_analisis = fecha
                    print(f"[Análisis] Fecha de inicio: {self.fecha_inicio_analisis.toString('yyyy-MM-dd')}")
                elif not self.fecha_fin_analisis:
                    self.fecha_fin_analisis = fecha
                    print(f"[Análisis] Fecha de fin: {self.fecha_fin_analisis.toString('yyyy-MM-dd')}")
                    calendario.setEnabled(False)
            else:
                self.fecha_inicio_analisis = fecha
                self.fecha_fin_analisis = None
                print(f"[Análisis] Fecha seleccionada: {self.fecha_inicio_analisis.toString('yyyy-MM-dd')}")

    def cambiar_estado_calendario(self, tipo):
        if tipo == "caja":
            opcion = self.TiempoCajaComboBox.currentText()
            if opcion == "Diario":
                self.modo_intervalo_caja = False
                self.fecha_inicio_caja = None
                self.fecha_fin_caja = None
                self.CalendarioCaja.setEnabled(True)
                print("[Caja] Modo Diario: Selecciona una sola fecha.")
            elif opcion == "Intervalo de días":
                self.modo_intervalo_caja = True
                self.fecha_inicio_caja = None
                self.fecha_fin_caja = None
                self.CalendarioCaja.setEnabled(True)
                print("[Caja] Modo Intervalo: Selecciona dos fechas.")
            else:
                self.CalendarioCaja.setEnabled(False)
        elif tipo == "analisis":
            opcion = self.TiempoAnalisisComboBox.currentText()
            if opcion == "Diario":
                self.modo_intervalo_analisis = False
                self.fecha_inicio_analisis = None
                self.fecha_fin_analisis = None
                self.CalendarioAnalisis.setEnabled(True)
                print("[Análisis] Modo Diario: Selecciona una sola fecha.")
            elif opcion == "Intervalo de días":
                self.modo_intervalo_analisis = True
                self.fecha_inicio_analisis = None
                self.fecha_fin_analisis = None
                self.CalendarioAnalisis.setEnabled(True)
                print("[Análisis] Modo Intervalo: Selecciona dos fechas.")
            else:
                self.CalendarioAnalisis.setEnabled(False)