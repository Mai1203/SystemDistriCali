from PyQt6.QtWidgets import (
    QWidget,
)
from ..ui import Ui_Egreso
from PyQt6.QtCore import QTimer
from PyQt6 import QtWidgets

from ..database.database import SessionLocal
from ..utils.validar_campos import *
from ..controllers.egresos_crud import *
from PyQt6.QtCore import Qt
from datetime import datetime
from ..controllers.metodo_pago_crud import *
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtWidgets import QMessageBox
from ..utils.enviar_notifi import Mensajes as QMessageBox

QtWidgets.QMessageBox = QMessageBox

from PyQt6.QtWidgets import QAbstractItemView


class Egreso_View(QWidget, Ui_Egreso):

    def __init__(self, parent=None):
        super(Egreso_View, self).__init__(parent)
        self.setupUi(self)

        QTimer.singleShot(0, self.InputTipoGasto.setFocus)

        fecha_hora = datetime.now()
        fecha_hora_formateada = fecha_hora.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        self.TablaEgreso.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        self.TablaEgreso.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # placeholder
        self.InputFechaEgreso.setText(fecha_hora_formateada)
        self.InputTipoGasto.setPlaceholderText("Ej: Compra")
        self.InputDescripcionEgreso.setPlaceholderText(
            "Ej: Compra de productos"
        )
        self.InputPagoEgreso.setPlaceholderText("Ej: 100000")

        configurar_validador_fecha(self.InputFechaEgreso)
        configurar_validador_texto(self.InputTipoGasto)
        configurar_validador_numerico(self.InputPagoEgreso)
        configurar_validador_texto(self.InputDescripcionEgreso)

        self.InputTipoGasto.textChanged.connect(
            self.verificar_tipo_gasto
        )

        self.limpiar_tabla()
        self.metodo_pago()
        self.agregar_egreso()

        # Conectar el botón al método agregar_egreso
        self.BtnRegistrarEgreso.clicked.connect(
            self.agregar_egreso
        )

        self.BtnEliminar.clicked.connect(
            self.eliminar_egreso
        )

        self.TablaEgreso.selectionModel().currentRowChanged.connect(
            self.mostrar_datos_egreso
        )

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
        self.limpiar_formulario()
        self.cargar_egresos()

    def fecha_egreso(self):
        fecha_hora = datetime.now()
        fecha_hora_formateada = fecha_hora.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        # placeholder
        self.InputFechaEgreso.setText(
            fecha_hora_formateada
        )

    def mostrar_datos_egreso(self):

        # Obtener la fila seleccionada
        fila_seleccionada = self.TablaEgreso.currentRow()

        # Verificar si se ha seleccionado una fila
        if fila_seleccionada != -1:

            # Obtener los datos de la fila seleccionada
            tipo_gasto = self.TablaEgreso.item(
                fila_seleccionada, 1
            ).text()

            descripcion_egreso = self.TablaEgreso.item(
                fila_seleccionada, 2
            ).text()

            metodo_pago = self.TablaEgreso.item(
                fila_seleccionada, 3
            ).text()

            pago_egreso = self.TablaEgreso.item(
                fila_seleccionada, 4
            ).text()

            fecha_egreso = self.TablaEgreso.item(
                fila_seleccionada, 5
            ).text()

            # Cargar los datos en los inputs correspondientes
            # y hacerlos de solo lectura
            self.InputTipoGasto.setText(tipo_gasto)
            self.InputDescripcionEgreso.setText(
                descripcion_egreso
            )
            self.InputPagoEgreso.setText(
                pago_egreso
            )
            self.InputFechaEgreso.setText(
                fecha_egreso
            )

    def verificar_tipo_gasto(self):
        """ Borra los demás campos si InputTipoGasto está vacío. """

        if not self.InputTipoGasto.text().strip():
            self.limpiar_formulario()

        self.fecha_egreso()

    def obtener_ids_seleccionados(self):
        """
        Obtiene los IDs de los productos seleccionados en la tabla.
        """

        filas_seleccionadas = (
            self.TablaEgreso
            .selectionModel()
            .selectedRows()
        )

        ids = []

        for fila in filas_seleccionadas:

            id_egreso = self.TablaEgreso.item(
                fila.row(), 0
            ).text()

            ids.append(int(id_egreso))

        return ids

    def eliminar_egreso(self):

        # Obtener las filas seleccionadas
        ids = self.obtener_ids_seleccionados()

        if not ids:
            QMessageBox.warning(
                self,
                "Advertencia",
                "No hay filas seleccionadas para eliminar."
            )
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar "
            f"{len(ids)} egreso(s)?",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if respuesta == QtWidgets.QMessageBox.StandardButton.Yes:

            try:

                self.db = SessionLocal()

                for id_egreso in ids:
                    eliminar_egreso(
                        self.db,
                        id_egreso
                    )

                self.db.commit()

                QMessageBox.information(
                    self,
                    "Éxito",
                    "Egreso(s) eliminado(s) correctamente."
                )

                self.limpiar_tabla()
                self.cargar_egresos()

            except Exception as e:

                QMessageBox.warning(
                    self,
                    "Error",
                    f"Error al eliminar egresos: {e}"
                )

            finally:
                self.db.close()

    def obtener_nombres_metodos_pago(
        self,
        db,
        metodo_id
    ):

        metodo = (
            db.query(MetodoPago)
            .filter(
                MetodoPago.ID_Metodo_Pago == metodo_id
            )
            .first()
        )

        return (
            metodo.Nombre
            if metodo
            else "Desconocido"
        )

    def cargar_egresos(self):

        # Obtener la lista de egresos desde la base de datos
        db = SessionLocal()

        egresos = obtener_egresos(db)

        print(egresos)

        # Limpiar la tabla antes de cargar nuevos datos
        self.TablaEgreso.setRowCount(0)

        for egreso in egresos:

            row_position = (
                self.TablaEgreso.rowCount()
            )

            self.TablaEgreso.insertRow(
                row_position
            )

            # Obtener nombre del método de pago
            nombre_metodo_pago = (
                self.obtener_nombres_metodos_pago(
                    db,
                    egreso.ID_Metodo_Pago
                )
            )

            # Asignar los valores de las celdas

            item_id_egreso = QTableWidgetItem(
                str(egreso.ID_Egreso)
            )

            item_id_egreso.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                0,
                item_id_egreso
            )

            item_tipo_gasto = QTableWidgetItem(
                egreso.Tipo_Egreso
            )

            item_tipo_gasto.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                1,
                item_tipo_gasto
            )

            item_descripcion = QTableWidgetItem(
                egreso.Descripcion
            )

            item_descripcion.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                2,
                item_descripcion
            )

            item_metodo_pago = QTableWidgetItem(
                str(nombre_metodo_pago)
            )

            item_metodo_pago.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                3,
                item_metodo_pago
            )

            item_monto_egreso = QTableWidgetItem(
                str(egreso.Monto_Egreso)
            )

            item_monto_egreso.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                4,
                item_monto_egreso
            )

            item_fecha_egreso = QTableWidgetItem(
                egreso.Fecha_Egreso.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            )

            item_fecha_egreso.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.TablaEgreso.setItem(
                row_position,
                5,
                item_fecha_egreso
            )

        db.close()

    def agregar_egreso(self):

        # Obtener los datos del formulario
        tipo_gasto = self.InputTipoGasto.text()
        fecha_egreso = self.InputFechaEgreso.text()
        pago_egreso = self.InputPagoEgreso.text()
        descripcion_egreso = (
            self.InputDescripcionEgreso.text()
        )

        metodo_pago = (
            self.MetodoPagoBox.currentText()
        )

        monto_egreso = (
            self.InputPagoEgreso.text()
        )

        # Validación de campos
        fecha_hora = datetime.now()

        fecha_hora_formateada = fecha_hora.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        self.InputFechaEgreso.setText(
            fecha_hora_formateada
        )

        # Verificar si hay campos vacíos

        if not tipo_gasto:
            self.InputTipoGasto.setFocus()
            return

        if not descripcion_egreso:
            self.InputDescripcionEgreso.setFocus()
            return

        if not pago_egreso:
            self.InputPagoEgreso.setFocus()
            return

        if not fecha_egreso:
            self.InputFechaEgreso.setFocus()
            return

        if not metodo_pago:
            self.InputMetodoPago.setFocus()
            return

        if not monto_egreso:
            self.InputMontoEgreso.setFocus()
            return

        # Obtener el ID del método de pago
        db = SessionLocal()

        metodos = obtener_metodos_pago(db)

        metodo_pago_id = None

        for metodo in metodos:

            if metodo.Nombre == metodo_pago:

                metodo_pago_id = (
                    metodo.ID_Metodo_Pago
                )

                break

        if metodo_pago_id is None:

            print("Método de pago no válido.")
            db.close()
            return

        # Convertir monto de egreso a float
        try:

            monto_egreso = float(
                monto_egreso
            )

        except ValueError:

            print("Monto de egreso no válido.")
            db.close()
            return

        # Crear el egreso en la base de datos
        nuevo_egreso = crear_egreso(
            db,
            tipo_gasto,
            descripcion_egreso,
            monto_egreso,
            metodo_pago_id
        )

        # Agregar la fila a la tabla
        row_position = (
            self.TablaEgreso.rowCount()
        )

        self.TablaEgreso.insertRow(
            row_position
        )

        # ID Egreso
        item_id_egreso = QTableWidgetItem(
            str(nuevo_egreso.ID_Egreso)
        )

        item_id_egreso.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            0,
            item_id_egreso
        )

        # Tipo de Gasto
        item_tipo_gasto = QTableWidgetItem(
            tipo_gasto
        )

        item_tipo_gasto.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            1,
            item_tipo_gasto
        )

        # Descripción
        item_descripcion_egreso = QTableWidgetItem(
            descripcion_egreso
        )

        item_descripcion_egreso.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            2,
            item_descripcion_egreso
        )

        # Método de Pago
        item_metodo_pago = QTableWidgetItem(
            metodo_pago
        )

        item_metodo_pago.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            3,
            item_metodo_pago
        )

        # Monto
        item_monto_egreso = QTableWidgetItem(
            str(monto_egreso)
        )

        item_monto_egreso.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            4,
            item_monto_egreso
        )

        # Fecha
        item_fecha_egreso = QTableWidgetItem(
            fecha_egreso
        )

        item_fecha_egreso.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.TablaEgreso.setItem(
            row_position,
            5,
            item_fecha_egreso
        )

        # Limpiar el formulario después de agregar
        self.limpiar_formulario()

        db.close()

        self.fecha_egreso()

    def metodo_pago(self):

        try:

            # Iniciar conexión con la base de datos
            db = SessionLocal()

            # Verificar si la conexión fue exitosa
            if db:

                metodos = obtener_metodos_pago(db)

                # Obtener nombres de los métodos de pago
                if metodos:

                    nombres_metodos = [
                        metodo.Nombre
                        for metodo in metodos
                    ]

                    print(
                        "Métodos de pago encontrados:",
                        nombres_metodos
                    )

                    self.MetodoPagoBox.addItems(
                        nombres_metodos[:2]
                    )

                else:

                    nombres_metodos = []

                    print(
                        "No se encontraron métodos de pago."
                    )

            else:

                nombres_metodos = []

                print(
                    "No se pudo establecer conexión "
                    "con la base de datos."
                )

            return nombres_metodos

        except Exception as e:

            print(
                f"Error al obtener los métodos de pago: {e}"
            )

            return []

        finally:

            db.close()

    def limpiar_formulario(self):

        self.InputTipoGasto.setText("")
        self.InputFechaEgreso.setText("")
        self.InputPagoEgreso.setText("")
        self.InputDescripcionEgreso.setText("")

        self.InputTipoGasto.setFocus()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Up:
            self.navegar_widgets()

        elif event.key() == Qt.Key.Key_Down:
            self.navegar_widgets_atras()

        # Llamar al método original
        super().keyPressEvent(event)

    def navegar_widgets(self):

        if self.focusWidget() == self.InputTipoGasto:

            self.InputDescripcionEgreso.setFocus()

        elif self.focusWidget() == self.InputDescripcionEgreso:

            self.InputPagoEgreso.setFocus()

        elif self.focusWidget() == self.InputPagoEgreso:

            self.InputFechaEgreso.setFocus()

        elif self.focusWidget() == self.InputFechaEgreso:

            self.InputTipoGasto.setFocus()

    def navegar_widgets_atras(self):

        if self.InputFechaEgreso == self.focusWidget():

            self.InputPagoEgreso.setFocus()

        elif self.InputPagoEgreso == self.focusWidget():

            self.InputDescripcionEgreso.setFocus()

        elif self.InputDescripcionEgreso == self.focusWidget():

            self.InputTipoGasto.setFocus()

        elif self.InputTipoGasto == self.focusWidget():

            self.InputFechaEgreso.setFocus()

    def limpiar_tabla(self):

        self.TablaEgreso.setRowCount(0)

