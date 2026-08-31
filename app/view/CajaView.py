from datetime import datetime

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget

from ..ui import Ui_Caja

from ..utils.Estructura_Reporte import *
from ..utils.validar_campos import *
from ..utils.enviar_notifi import Mensajes as QMessageBox

from ..database.database import *

from ..controllers.caja_crud import *
from ..controllers.egresos_crud import *
from ..controllers.ingresos_crud import *
from ..controllers.metodo_pago_crud import *

class Caja_View(QWidget, Ui_Caja):


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.usuario_actual_id = None

        # Dar foco al campo de monto cuando se crea la vista
        QTimer.singleShot(0, self.InputMontoCaja.setFocus)

        # Timer para evitar consultas excesivas
        self.timer = QTimer(self)

        self.InputMontoCaja.setPlaceholderText("Ej : 45000")

        self.TablaCaja.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Conexiones
        self.BtnCajaApertura.clicked.connect(self.crear_caja)
        self.BtnCajaCierre.clicked.connect(self.cerrar_caja)
        self.InputBuscador.textChanged.connect(self.buscar_caja)
        self.TablaCaja.itemSelectionChanged.connect(self.seleccionar_fila)
        self.BtnCajaImprimir.clicked.connect(self.generar_reporte)

        # Placeholders
        self.InputBuscador.setPlaceholderText(
            "Buscar por Usuario o Fecha de Apertura AAAA/MM/DD"
        )

        configurar_validador_numerico(self.InputMontoCaja)

        self.limpiar_tabla()

    def showEvent(self, event):
        super().showEvent(event)

        self.InputMontoCaja.clear()

        self.limpiar_tabla()
        self.mostrar_tabla()
        self.sumar_total()
        self.seleccionar_caja_abierta()

    def seleccionar_caja_abierta(self):
        """Selecciona la caja abierta para cargar automáticamente sus movimientos."""
        for row in range(self.TablaCaja.rowCount()):
            estado = self.TablaCaja.item(row, 8)
            if estado and estado.text() == "Abierta":
                self.TablaCaja.setCurrentCell(row, 0)
                return True
        return False

    def seleccionar_fila(self):
        selected_row = self.TablaCaja.currentRow()

        if selected_row == -1:
            print("No hay una fila seleccionada.")
            return

        # Resetear colores de todas las filas
        for row in range(self.TablaCaja.rowCount()):
            for col in range(self.TablaCaja.columnCount()):
                item = self.TablaCaja.item(row, col)

                if item is not None:
                    item.setBackground(QColor(255, 255, 255))

        # Cambiar color de la fila seleccionada
        for col in range(self.TablaCaja.columnCount()):
            item = self.TablaCaja.item(selected_row, col)

            if item is not None:
                item.setBackground(QColor(173, 216, 230))

        # Obtener datos de la fila seleccionada
        id_caja = self.TablaCaja.item(selected_row, 0).text()
        id_usuario = self.TablaCaja.item(selected_row, 1).text()
        monto_base = self.TablaCaja.item(selected_row, 2).text()
        fecha_apertura_item = self.TablaCaja.item(selected_row, 3)
        fecha_cierre_item = self.TablaCaja.item(selected_row, 4)
        fecha_apertura = fecha_apertura_item.data(Qt.ItemDataRole.UserRole)
        fecha_cierre = fecha_cierre_item.data(Qt.ItemDataRole.UserRole)
        fecha_apertura = fecha_apertura if fecha_apertura is not None else fecha_apertura_item.text()
        fecha_cierre = fecha_cierre if fecha_cierre is not None else fecha_cierre_item.text()
        monto_efectivo = self.TablaCaja.item(selected_row, 5).text()
        monto_transaccion = self.TablaCaja.item(selected_row, 6).text()
        monto_final = self.TablaCaja.item(selected_row, 7).text()
        estado = self.TablaCaja.item(selected_row, 8).text()

        print(
            f"Fila seleccionada: ID Caja {id_caja}, "
            f"Apertura: {fecha_apertura}, "
            f"Cierre: {fecha_cierre}"
        )

        # Guardar datos de la fila seleccionada
        self.fecha_inicio = fecha_apertura
        self.fecha_fin = fecha_cierre
        self.id_caja = id_caja
        self.monto_base = monto_base
        self.monto_efectivo = monto_efectivo
        self.monto_transaccion = monto_transaccion
        self.monto_final = monto_final
        self.estado = estado
        self.id_usuario = id_usuario

        # Cargar movimientos (ingresos + egresos) de la caja seleccionada
        self.cargar_movimientos_caja(fecha_apertura, fecha_cierre, float(monto_base or 0))

    def generar_reporte(self):
        """
        Filtra los ingresos según la fecha de la caja seleccionada
        y envía los datos a la función del PDF.
        """

        db = SessionLocal()

        try:
            if not hasattr(self, "fecha_inicio") or not hasattr(self, "fecha_fin"):
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se ha seleccionado una caja correctamente."
                )
                return

            fecha_inicio = self.fecha_inicio
            fecha_fin = self.fecha_fin

            # Consultar ingresos en el rango de fechas
            ingresos = obtener_ingresos(
                db,
                fecha_inicio,
                fecha_fin
            )

            if ingresos:

                # Crear objeto caja con los datos de la fila seleccionada
                caja = Caja(
                    Monto_Base=self.monto_base,
                    Monto_Efectivo=self.monto_efectivo,
                    Monto_Transaccion=self.monto_transaccion,
                    Monto_Final_calculado=self.monto_final,
                    Fecha_Apertura=fecha_inicio,
                    Fecha_Cierre=fecha_fin,
                    Estado=self.estado,
                    ID_Usuario=self.id_usuario
                )

                # Generar PDF
                generar_pdf_caja_ingresos(
                    caja,
                    ingresos
                )

            else:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    "No se encontraron ingresos en el rango de fechas seleccionado."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al generar el reporte: {e}"
            )

            print(f"Error al generar el reporte: {e}")

        finally:
            db.close()

    def limpiar_tabla(self):
        self.TablaCaja.setRowCount(0)
        self.TablaIngresos.setRowCount(0)

    def cargar_movimientos_caja(self, fecha_apertura, fecha_cierre, monto_base=0.0):
        """Carga ingresos y egresos de una caja específica en TablaIngresos."""
        self.TablaIngresos.setRowCount(0)

        db = SessionLocal()
        try:
            # Parse dates
            def to_dt(val):
                if isinstance(val, datetime):
                    return val
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                    try:
                        return datetime.strptime(str(val), fmt)
                    except ValueError:
                        pass
                return None

            dt_inicio = to_dt(fecha_apertura)
            dt_fin = to_dt(fecha_cierre) if fecha_cierre and str(fecha_cierre) not in ("None", "") else datetime.now()

            movimientos = []  # (fecha, tipo, descripcion, efectivo, transferencia)

            # ── Ingresos ──
            ingresos = obtener_ingresos(db=db, FechaInicio=dt_inicio, FechaFin=dt_fin) or []
            for ing in ingresos:
                tipo = str(ing.tipo_ingreso)
                if tipo.startswith("Venta "):
                    ef = float(ing.monto_efectivo or 0)
                    tr = float(ing.monto_transaccion or 0)
                else:
                    metodo = str(getattr(ing, 'metodo_pago', '') or '')
                    monto = float(getattr(ing, 'monto', 0) or 0)
                    ef = monto if metodo == "Efectivo" else 0.0
                    tr = monto if metodo != "Efectivo" else 0.0
                movimientos.append((getattr(ing, 'Fecha_Ingreso', dt_inicio), tipo, tipo, ef, tr))

            # ── Egresos ──
            egresos = obtener_egresos_reporte(db=db, fecha_inicio=dt_inicio, fecha_fin=dt_fin) or []
            for eg in egresos:
                eg_tipo = getattr(eg, 'Tipo_Egreso', 'Egreso')
                eg_fecha = getattr(eg, 'Fecha_Egreso', dt_inicio)
                monto = float(getattr(eg, 'Monto_Egreso', 0) or 0)
                metodo_id = getattr(eg, 'ID_Metodo_Pago', None)

                # Aplicar el egreso al medio de pago con el que fue registrado.
                metodo_nombre = "Efectivo"
                if metodo_id:
                    mp = obtener_metodo_pago_por_id(db, metodo_id)
                    if mp:
                        metodo_nombre = mp.Nombre

                ef_eg = monto if metodo_nombre == "Efectivo" else 0.0
                tr_eg = monto if metodo_nombre != "Efectivo" else 0.0
                movimientos.append((eg_fecha, f"Egreso - {eg_tipo}", f"Egreso - {eg_tipo}", -ef_eg, -tr_eg))

            # ── Populate table ──
            total_ef = monto_base
            total_tr = 0.0
            for fecha, tipo, desc, ef, tr in movimientos:
                row = self.TablaIngresos.rowCount()
                self.TablaIngresos.insertRow(row)
                for col, val in enumerate([desc, f"{ef:,.2f}", f"{tr:,.2f}"]):
                    it = QtWidgets.QTableWidgetItem(str(val))
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.TablaIngresos.setItem(row, col, it)
                total_ef += ef
                total_tr += tr

            # ── Update summary labels ──
            self.OutEfectivo.setText(f"{total_ef:,.2f}")
            self.OutTransferencia.setText(f"{total_tr:,.2f}")
            self.OutTotal.setText(f"{total_ef + total_tr:,.2f}")
            if hasattr(self, 'OutMontoBase'):
                self.OutMontoBase.setText(f"{monto_base:,.2f}")

        except Exception as e:
            print(f"Error cargando movimientos: {e}")
        finally:
            db.close()

    def mostrar_tabla(self):
        self.db = SessionLocal()

        try:
            ingresos = None

            cajas = obtener_cajas(db=self.db)

            for caja in cajas:
                if caja.Estado is True:
                    fecha_apertura = caja.Fecha_Apertura
                    fecha_cierre = caja.Fecha_Cierre

                    ingresos = obtener_ingresos(
                        db=self.db,
                        FechaInicio=fecha_apertura,
                        FechaFin=fecha_cierre
                    )

        except Exception as e:
            print(f"Error al obtener datos de la caja: {e}")
            return

        finally:
            self.db.close()

        self.actualizar_tabla(
            ingresos=ingresos,
            caja=cajas
        )

    def actualizar_tabla(self, ingresos=None, caja=None):

        # ==============================
        # TABLA DE CAJAS
        # ==============================

        try:
            if caja:

                caja.sort(
                    key=lambda x: x.ID_Caja,
                    reverse=False
                )

                for caja_item in caja:

                    id_caja = str(caja_item.ID_Caja)
                    usuario = str(caja_item.usuario)
                    monto = str(caja_item.Monto_Base)
                    fechaA_raw = caja_item.Fecha_Apertura
                    fechaC_raw = caja_item.Fecha_Cierre or ""
                    fechaA = self.formatear_fecha_tabla(fechaA_raw)
                    fechaC = self.formatear_fecha_tabla(fechaC_raw)
                    efectivo = str(caja_item.Monto_Efectivo)
                    trasferencia = str(caja_item.Monto_Transaccion)
                    total = str(caja_item.Monto_Final_calculado)

                    estado = (
                        "Abierta"
                        if caja_item.Estado
                        else "Cerrada"
                    )

                    self.TablaCaja.insertRow(0)

                    items = [
                        (id_caja, 0, None),
                        (usuario, 1, None),
                        (monto, 2, None),
                        (fechaA, 3, fechaA_raw),
                        (fechaC, 4, fechaC_raw),
                        (efectivo, 5, None),
                        (trasferencia, 6, None),
                        (total, 7, None),
                        (estado, 8, None),
                    ]

                    for value, col_idx, raw_value in items:

                        item = QtWidgets.QTableWidgetItem(value)

                        if raw_value is not None:
                            item.setData(Qt.ItemDataRole.UserRole, raw_value)
                            item.setToolTip(str(raw_value))

                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter
                        )

                        self.TablaCaja.setItem(
                            0,
                            col_idx,
                            item
                        )

        except Exception as e:
            print(f"Error en Tabla caja: {e}")

    @staticmethod
    def formatear_fecha_tabla(fecha):
        """Devuelve una fecha compacta para que las columnas de caja se mantengan legibles."""
        if not fecha:
            return "Abierta"
        if isinstance(fecha, datetime):
            return fecha.strftime("%d/%m %H:%M")
        try:
            return datetime.fromisoformat(str(fecha)).strftime("%d/%m %H:%M")
        except ValueError:
            return str(fecha)

    def sumar_total(self):
        """Reset summary; it is now driven by cargar_movimientos_caja."""
        self.OutEfectivo.setText("0.00")
        self.OutTransferencia.setText("0.00")
        self.OutTotal.setText("0.00")

    def crear_caja(self):

        # Verificar si ya existe una caja abierta
        for row in range(self.TablaCaja.rowCount()):

            if self.TablaCaja.item(row, 8).text() == "Abierta":

                QMessageBox.warning(
                    self,
                    "Error",
                    "Ya existe una caja abierta."
                )

                return

        try:

            base = self.InputMontoCaja.text().strip()

            if not base:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Ingrese un monto válido."
                )

                return

            if float(base) < 0:

                QMessageBox.warning(
                    self,
                    "Error",
                    "El monto no puede ser negativo."
                )

                return

            self.db = SessionLocal()

            try:

                id_usuario = self.usuario_actual_id
                base = float(base)
                estado = True

                caja = crear_caja(
                    db=self.db,
                    monto_base=base,
                    id_usuario=id_usuario,
                    estado=estado
                )

                self.limpiar_tabla()
                self.mostrar_tabla()

                QMessageBox.information(
                    self,
                    "Caja creada",
                    "La caja ha sido creada exitosamente."
                )

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al crear la caja en bd: {str(e)}"
                )

            finally:
                self.db.close()

        except Exception as e:
            print(f"Error al crear la caja: {e}")

        self.InputMontoCaja.clear()

    def cerrar_caja(self):

        count = 0

        for row in range(self.TablaCaja.rowCount()):

            if self.TablaCaja.item(row, 8).text() == "Cerrada":

                count += 1

                if count == self.TablaCaja.rowCount():

                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se encontró ninguna caja Abierta."
                    )

                    return

            if self.TablaCaja.item(row, 8).text() == "Abierta":

                efectivo = self.OutEfectivo.text().strip()
                efectivo = float(
                    efectivo.replace("$", "").replace(",", "").strip()
                )

                trasferencia = self.OutTransferencia.text().strip()
                trasferencia = float(
                    trasferencia.replace("$", "").replace(",", "").strip()
                )

                total = self.OutTotal.text().strip()
                total = float(
                    total.replace("$", "").replace(",", "").strip()
                )

                id_caja = self.TablaCaja.item(row, 0).text()

                self.db = SessionLocal()

                try:

                    actualizar_caja(
                        db=self.db,
                        id_caja=id_caja,
                        estado=False,
                        monto_efectivo=efectivo,
                        monto_transaccion=trasferencia,
                        monto_final_calculado=total,
                        fecha_cierre=datetime.now().replace(
                            microsecond=0
                        )
                    )

                    self.limpiar_tabla()
                    self.mostrar_tabla()

                    QMessageBox.information(
                        self,
                        "Caja cerrada",
                        "La caja ha sido cerrada exitosamente."
                    )

                except Exception as e:

                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al cerrar la caja en bd: {str(e)}"
                    )

                finally:
                    self.db.close()

        self.OutEfectivo.setText("0.00")
        self.OutTotal.setText("0.00")
        self.OutTransferencia.setText("0.00")

    def buscar_caja(self):

        buscar = self.InputBuscador.text().strip()

        if not buscar:

            self.limpiar_tabla()
            self.mostrar_tabla()

            return

        self.db = SessionLocal()

        try:

            caja = buscar_cajas(
                db=self.db,
                buscar=buscar
            )

            self.actualizar_tabla(
                caja=caja
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Error al buscar la caja en bd: {str(e)}"
            )

        finally:
            self.db.close()
