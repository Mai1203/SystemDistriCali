# PyQt6 imports
from PyQt6.QtWidgets import QMessageBox, QWidget, QTableWidgetItem
from PyQt6.QtCore import QRegularExpression, QTimer, QUrl, Qt
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtMultimedia import QMediaPlayer
from decimal import Decimal
from datetime import datetime, timedelta
import re

# Relative imports
from ..database.database import SessionLocal
from ..controllers.producto_crud import *
from ..controllers.detalle_factura_crud import *
from ..controllers.clientes_crud import *
from ..controllers.facturas_crud import *
from ..controllers.metodo_pago_crud import *
from ..controllers.venta_credito_crud import *
from ..controllers.pago_credito_crud import *
from ..controllers.historial_modificacion_crud import *
from ..controllers.caja_crud import obtener_cajas
from ..ui import Ui_VentasCredito
from ..utils.autocomplementado import configurar_autocompletado
from ..utils.formateador import formatear_numero
from ..utils.restructura_ticket import *

# Standard library imports
import os
import locale
import win32print
import win32ui
import win32con


from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class VentasCredito_View(QWidget, Ui_VentasCredito):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Configuración inicial
        self.usuario_actual_id = None
        self.productos = []
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        
        QTimer.singleShot(0, self.InputCodigo.setFocus)
        self.id_categoria = None
        self.cantidades = []
        self.invoice_number = None
        self.id_venta_credito = None
        self.en_edicion = False
        self.fila_seleccionada = None
        self.timer = QTimer(self)

        # Placeholders
        self.InputCedula.setPlaceholderText("Ej: 10004194608")
        self.InputNombreCli.setPlaceholderText("Ej: Pepito")
        self.InputApellidoCli.setPlaceholderText("Ej: Perez")
        self.InputTelefonoCli.setPlaceholderText("Ej: 3170065430")
        self.InputDireccion.setPlaceholderText("Ej: Calle 1, 123 - Piso 1")
        
        self.comboBoxPrecio.clear()
        self.comboBoxPrecio.addItems(["PV-01", "PV-02", "PV-03", "PV-04"])
        
        self.InputCodigo.setPlaceholderText("Ej: 7709991003078")
        self.InputNombre.setPlaceholderText("Ej: Esmalte")

        # Inicialización y configuración
        self.limpiar_tabla()
        self.configurar_localizacion()
        self.validar_campos()

        # Conexiones de señales
        self.db = SessionLocal()
        self.InputCodigo.returnPressed.connect(self._on_codigo_return)
        self.InputCodigo.textChanged.connect(self.iniciar_timer)
        self.InputCantidad.returnPressed.connect(self.actualizar_datos)
        self.InputPrecioUnitario.returnPressed.connect(self.actualizar_datos)
        self.InputCedula.returnPressed.connect(self._on_cedula_return)
        self.InputCedula.textChanged.connect(self.validar_campos)
        self.comboBoxPrecio.currentIndexChanged.connect(self.cambiar_precio)
        configurar_autocompletado(
            self.InputNombre, obtener_productos, "Nombre", self.db, self.procesar_codigo
        )
        configurar_autocompletado(
            self.InputNombreCli,
            obtener_cliente_nombre_apellido,
            "NombreCompleto",
            self.db,
            self.insertar_cliente,
        )

        # Botones y tabla
        self.BtnEliminar.clicked.connect(self.eliminar_fila)
        self.BtnGenerarVentaCredito.clicked.connect(self.generar_venta)
        self.TablaVentasCredito.cellClicked.connect(self.cargar_datos)
        self.TablaVentasCredito.itemChanged.connect(self.actualizar_total)

        self.timer.timeout.connect(self.procesar_codigo_y_agregar)

    def cargar_información(self, factura_completa, id_venta_credito=None):
        factura = factura_completa["Factura"]
        cliente = factura_completa["Cliente"]
        detalles = factura_completa["Detalles"]

        self.invoice_number = factura["ID_Factura"]
        self.id_venta_credito = id_venta_credito
        self.en_edicion = True
        self.LabelVentasA.setText("Editando Credi Factura")
        self.comboBoxPrecio.setCurrentIndex(0)
        self.comboBoxPrecio.setEnabled(False)

        self.TablaVentasCredito.setRowCount(len(detalles))
        self.cantidades = []
        for row, detalle in enumerate(detalles):
            self.cantidades.append((detalle["ID_Producto"], detalle["Cantidad"]))
            valores = [
                detalle["ID_Producto"],
                detalle["Producto"],
                detalle["Marca"],
                detalle["Categoria"],
                detalle["Cantidad"],
                detalle["Precio_Unitario"],
                detalle["Subtotal"],
            ]
            for column, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.TablaVentasCredito.setItem(row, column, item)

        self.InputCedula.setText(str(cliente["ID_Cliente"]))
        self.InputNombreCli.setText(str(cliente["Nombre"]))
        self.InputApellidoCli.setText(str(cliente["Apellido"]))
        self.InputTelefonoCli.setText(str(cliente["Teléfono"]))
        self.InputDireccion.setText(str(cliente["Direccion"]))
        self.actualizar_total()

    # def cargar_información(self, factura_completa, id_venta_credito=None):
    #     self.id_venta_credito = id_venta_credito

    #     factura = factura_completa["Factura"]
    #     cliente = factura_completa["Cliente"]
    #     detalles = factura_completa["Detalles"]

    #     subtotal = sum(detalle["Subtotal"] for detalle in detalles)

    #     client_name = cliente["Nombre"]
    #     client_apellido = cliente["Apellido"]
    #     client_id = cliente["ID_Cliente"]
    #     client_address = cliente["Direccion"]
    #     client_phone = cliente["Teléfono"]

    #     total = subtotal

    #     self.invoice_number = factura["ID_Factura"]

    #     try:
    #         self.TablaVentasCredito.setRowCount(len(detalles))
    #         cant = []
    #         for row_idx, row in enumerate(detalles):
    #             id_producto = str(row["ID_Producto"])
    #             try:
    #                 id_producto_int = int(row["ID_Producto"])
    #             except ValueError:
    #                 print(f"Valor inválido para id_producto en la fila {row_idx}. Se asigna valor 0.")
    #                 id_producto_int = 0
    #             producto = str(row["Producto"])
    #             marca = str(row["Marca"])
    #             categoria = str(row["Categoria"])
    #             cantidad = str(row["Cantidad"])
    #             try:
    #                 cantidad_num = int(row["Cantidad"])
    #             except ValueError:
    #                 print(f"Valor inválido para cantidad en la fila {row_idx}. Se asigna valor 0.")
    #                 cantidad_num = 0
    #             cant.append((id_producto_int, cantidad_num))
    #             precio_unitario = str(row["Precio_Unitario"])
    #             subtotal_producto = str(row["Subtotal"])

    #             items = [
    #                 (id_producto, 0),
    #                 (producto, 1),
    #                 (marca, 2),
    #                 (categoria, 3),
    #                 (cantidad, 4),
    #                 (precio_unitario, 5),
    #                 (subtotal_producto, 6),
    #             ]

    #             for value, col_idx in items:
    #                 item = QTableWidgetItem(value)
    #                 item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                 self.TablaVentasCredito.setItem(row_idx, col_idx, item)
    #         self.cantidades = cant
    #         self.TablaVentasCredito.resizeColumnsToContents()

    #     except Exception as e:
    #         print(f"Error al cargar datos en la tablaVentasCredito: {e}")

    #     self.InputCedula.setText(str(client_id))
    #     self.InputNombreCli.setText(str(client_name))
    #     self.InputApellidoCli.setText(str(client_apellido))
    #     self.InputTelefonoCli.setText(str(client_phone))
    #     self.InputDireccion.setText(str(client_address))
    #     self.LabelSubtotal.setText(f"{subtotal:,.2f}")
    #     self.LabelTotal.setText(f"{total:,.2f}")

    def actualizar_factura(
        self,
        db,
        id_factura,
        produc_datos,
        usuario_actual_id,
        deuda,
        limite_pago,
    ):
        venta_credito = obtener_ventaCredito_id(db, self.id_venta_credito)
        venta = venta_credito[0]

        pagado = venta.Total_Deuda - venta.Saldo_Pendiente

        # Obtener los detalles actuales de la factura
        detalles_actuales = (
            db.query(DetalleFacturas)
            .filter(DetalleFacturas.ID_Factura == id_factura)
            .all()
        )

        productos_actuales = {
            detalle.ID_Producto: detalle.Cantidad for detalle in detalles_actuales
        }

        productos_nuevos = {
            int(codigo): cantidad for codigo, cantidad, _ in produc_datos
        }

        productos_eliminados = set(productos_actuales.keys()) - set(
            productos_nuevos.keys()
        )

        for id_producto in productos_eliminados:
            cantidad_vendida = productos_actuales[id_producto]
            producto = (
                db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
            )
            producto.Stock_actual += cantidad_vendida
            db.delete(
                db.query(DetalleFacturas)
                .filter(
                    DetalleFacturas.ID_Factura == id_factura,
                    DetalleFacturas.ID_Producto == id_producto,
                )
                .first()
            )

        for id_producto, nueva_cantidad in productos_nuevos.items():
            if id_producto in productos_actuales:
                detalle = (
                    db.query(DetalleFacturas)
                    .filter(
                        DetalleFacturas.ID_Factura == id_factura,
                        DetalleFacturas.ID_Producto == id_producto,
                    )
                    .first()
                )

                diferencia_cantidad = nueva_cantidad - productos_actuales[id_producto]
                detalle.Cantidad = nueva_cantidad
                detalle.Subtotal = nueva_cantidad * detalle.Precio_unitario

                producto = (
                    db.query(Productos)
                    .filter(Productos.ID_Producto == id_producto)
                    .first()
                )
                producto.Stock_actual -= diferencia_cantidad
            else:
                precio_unitario = (
                    db.query(Productos)
                    .filter(Productos.ID_Producto == id_producto)
                    .first()
                    .Precio_venta_1
                )
                subtotal = nueva_cantidad * precio_unitario

                nuevo_detalle = DetalleFacturas(
                    ID_Factura=id_factura,
                    ID_Producto=id_producto,
                    Cantidad=nueva_cantidad,
                    Precio_unitario=precio_unitario,
                    Subtotal=subtotal,
                )
                db.add(nuevo_detalle)

                producto = (
                    db.query(Productos)
                    .filter(Productos.ID_Producto == id_producto)
                    .first()
                )
                producto.Stock_actual -= nueva_cantidad

        saldo = deuda - pagado
        actualizar_venta_credito(
            db=db,
            id_venta_credito=self.id_venta_credito,
            total_deuda=deuda,
            saldo_pendiente=saldo,
            fecha_limite=limite_pago,
        )

        factura = db.query(Facturas).filter(Facturas.ID_Factura == id_factura).first()
        factura.ID_Usuario = usuario_actual_id

        crear_historial_modificacion(
            db=db,
            id_usuario=usuario_actual_id,
            descripcion="Factura actualizada",
            id_factura=id_factura,
        )

        db.commit()

        self.invoice_number = None
        self.id_venta_credito = None

    def showEvent(self, event):
        super().showEvent(event)
        self.InputCodigo.setFocus()
        self.limpiar_tabla()
        self.limpiar_campos()
        self.limpiar_datos_cliente()
        self.invoice_number = None
        self.id_venta_credito = None
        self.en_edicion = False
        self.comboBoxPrecio.setEnabled(True)
        self.LabelVentasA.setText("Ventas a Crédito")
        configurar_autocompletado(
            self.InputNombre, obtener_productos, "Nombre", self.db, self.procesar_codigo
        )
        configurar_autocompletado(
            self.InputNombreCli,
            obtener_cliente_nombre_apellido,
            "NombreCompleto",
            self.db,
            self.insertar_cliente,
        )

    def calcular_fecha_futura(self, dias):
        fecha_actual = datetime.now()
        fecha_futura = fecha_actual + timedelta(days=dias)
        return fecha_futura.replace(microsecond=0)

    def generar_venta(self):
        # Verificar que haya una caja abierta
        try:
            _db = SessionLocal()
            cajas = obtener_cajas(db=_db)
            _db.close()
            caja_abierta = any(c.Estado is True for c in cajas)
        except Exception:
            caja_abierta = False
        if not caja_abierta:
            QMessageBox.critical(
                self, "⚠️ Caja cerrada",
                "No puedes realizar ventas si la caja no está abierta.\n"
                "Por favor abre la caja antes de continuar."
            )
            return

        if self.TablaVentasCredito.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No hay productos en la venta.")
            self.InputCodigo.setFocus()
            return
        try:
            client_name = self.InputNombreCli.text().strip()
            client_apellido = self.InputApellidoCli.text().strip()
            client_id = self.InputCedula.text().strip()
            client_address = self.InputDireccion.text().strip()
            client_phone = self.InputTelefonoCli.text().strip()
            limite_pago = self.LimitePagoBox.currentText().strip()

            client_name = f"{client_name} {client_apellido}"

            match = re.search(r'(\d+)', limite_pago)
            if match:
                dias = int(match.group(1))
                limite_pago = self.calcular_fecha_futura(dias)
            else:
                limite_pago = self.calcular_fecha_futura(15)

            if not client_name or not client_apellido or not client_address or not client_phone or not client_id:
                QMessageBox.information(
                    self, "Campos obligatorios", "Todos los campos son obligatorios"
                )
                QTimer.singleShot(0, self.InputNombreCli.setFocus)
                return

            if len(client_phone) != 10 or not client_phone.isdigit():
                QMessageBox.warning(
                    self, "Teléfono inválido", "El teléfono debe tener 10 dígitos."
                )
                QTimer.singleShot(0, self.InputTelefonoCli.setFocus)
                return

            db = SessionLocal()

            cliente_existente = obtener_cliente_por_id(db, client_id)
            if not cliente_existente:
                QMessageBox.critical(self, "Error", "El cliente no está registrado en la base de datos.\nNo se pueden generar ventas a crédito a clientes no registrados.")
                db.close()
                return

            produc_datos = []
            items = []
            for row in range(self.TablaVentasCredito.rowCount()):
                codigo = self.TablaVentasCredito.item(row, 0).text()
                description = self.TablaVentasCredito.item(row, 1).text()
                quantity = int(self.TablaVentasCredito.item(row, 4).text())
                precio_unitario = float(self.TablaVentasCredito.item(row, 5).text())
                value = float(self.TablaVentasCredito.item(row, 6).text())

                producto = obtener_producto_por_id(db, int(codigo))
                if not producto:
                    QMessageBox.warning(
                        self, "Error", f"Producto con código {codigo} no encontrado."
                    )
                    return

                producto = producto[0]
                items.append((description, quantity, precio_unitario, value))
                produc_datos.append((codigo, quantity, precio_unitario))

            subtotal = sum(item[3] for item in items)
            total = subtotal
            delivery_fee = 0.0
            
            if total <= 0:
                QMessageBox.critical(self, "Error", "No se pueden generar ventas por un total de $0 pesos.")
                db.close()
                return

            if self.invoice_number and self.invoice_number != "":
                self.actualizar_factura(
                    db,
                    self.invoice_number,
                    produc_datos,
                    self.usuario_actual_id,
                    subtotal,
                    limite_pago,
                )
                mensaje = "Factura actualizada exitosamente."
            else:
                for codigo, quantity, _ in produc_datos:
                    producto = obtener_producto_por_id(db, codigo)[0]
                    stock_actual = producto.Stock_actual - quantity
                    actualizar_producto(
                        db, id_producto=int(codigo), stock_actual=stock_actual
                    )

                id_factura = self.guardar_factura(
                    db,
                    client_id,
                    "Efectivo",
                    produc_datos,
                    "0.00",
                    0.0,
                    self.usuario_actual_id,
                    subtotal,
                    limite_pago,
                )
                self.invoice_number = f"0000{id_factura}"
                mensaje = "Factura generada exitosamente."

            # Impresión del ticket (no requiere cambios de PyQt6)
            max_lines_per_page = 30
            current_line = 0
            empresa_nombre = "LadyNailShop"
            empresa_direccion = "Pasto, Colombia"
            empresa_telefono = "+57 316-144-44-74"
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            limite_pago_formateado = limite_pago.strftime("%d/%m/%Y") if hasattr(limite_pago, 'strftime') else str(limite_pago)
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
                "weight": win32con.FW_BOLD,
            })
            font_size = 18
            line_height = font_size + 10
            font = win32ui.CreateFont({
                "name": "Lucida Console",
                "height": font_size,
                "weight": win32con.FW_BOLD,
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
            hDC.TextOut(x, y, f"COT No. {self.invoice_number}")
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
                linea = "{:<18} {:>6} {:>10} {:>10}".format(
                    nombre_producto, cantidad, precio_unitario, total_producto
                )
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

            db.close()
            QMessageBox.information(self, "Éxito", mensaje)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error al generar la factura: {str(e)}"
            )
            print(e)

        self.limpiar_tabla()
        self.limpiar_campos()
        self.limpiar_datos_cliente()
        self.invoice_number = None
        self.id_venta_credito = None
        self.en_edicion = False
        self.comboBoxPrecio.setEnabled(True)
        self.LabelVentasA.setText("Ventas a Crédito")

    def guardar_factura(
        self,
        db,
        client_id,
        payment_method,
        items,
        monto_pago,
        descuento,
        id_usuario,
        deuda,
        limite_pago,
    ):
        try:
            id_metodo_pago = obtener_metodo_pago_por_nombre(db, payment_method)
            if not id_metodo_pago:
                QMessageBox.warning(
                    self, "Error", f"Método de pago {payment_method} no encontrado."
                )
                return False

            if "/" in monto_pago:
                total = monto_pago.split("/")
                efectivo = float(total[0])
                tranferencia = float(total[1])
            else:
                efectivo = float(monto_pago)
                tranferencia = float(monto_pago)

            factura = crear_factura(
                db=db,
                monto_efectivo=efectivo if payment_method != "Transferencia" else 0.0,
                monto_transaccion=tranferencia if payment_method != "Efectivo" else 0.0,
                descuento=descuento,
                estado=False,
                id_metodo_pago=id_metodo_pago.ID_Metodo_Pago,
                id_tipo_factura=5,
                id_cliente=client_id,
                id_usuario=id_usuario,
                domicilio=False,
            )

            id_factura = factura.ID_Factura

            for item in items:
                codigo, quantity, precio_unitario = item
                total = quantity * precio_unitario
                crear_detalle_factura(
                    db=db,
                    cantidad=quantity,
                    precio_unitario=precio_unitario,
                    subtotal=total,
                    id_producto=codigo,
                    id_factura=id_factura,
                )

            crear_venta_credito(
                db=db,
                total_deuda=deuda,
                saldo_pendiente=deuda,
                fecha_limite=limite_pago,
                id_factura=id_factura,
            )

            db.commit()
            return id_factura

        except Exception as e:
            db.rollback()
            print(f"Error al guardar la factura: {e}")
            raise

    def limpiar_datos_cliente(self):
        self.InputCedula.setText("")
        self.InputNombreCli.setText("")
        self.InputApellidoCli.setText("")
        self.InputTelefonoCli.setText("")
        self.InputDireccion.setText("")
        self.LimitePagoBox.setCurrentIndex(0)
        self.LabelSubtotal.setText("$ 0")
        self.LabelTotal.setText("$ 0")

    def mostrar_mensaje_temporal(self, titulo, mensaje, duracion=2200):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        QTimer.singleShot(duracion, msg_box.close)
        msg_box.exec()

    def reproducir_sonido(self):
        sonido_path = os.path.abspath("./assets/Sonido.mp3")
        if os.path.exists(sonido_path):
            try:
                self.player.setSource(QUrl.fromLocalFile(sonido_path))
                self.player.play()
            except Exception as e:
                print(f"Error al reproducir sonido: {e}")
        else:
            print("No se encontró el archivo de sonido")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.navegar_widgets()
        elif event.key() == Qt.Key.Key_Down:
            self.navegar_widgets_atras()
        super().keyPressEvent(event)

    def navegar_widgets(self):
        if self.focusWidget() == self.InputCodigo:
            self.InputNombre.setFocus()
        elif self.focusWidget() == self.InputNombre:
            self.InputCedula.setFocus()
        elif self.focusWidget() == self.InputCedula:
            self.InputNombreCli.setFocus()
        elif self.focusWidget() == self.InputNombreCli:
            self.InputApellidoCli.setFocus()
        elif self.focusWidget() == self.InputApellidoCli:
            self.InputTelefonoCli.setFocus()
        elif self.focusWidget() == self.InputTelefonoCli:
            self.InputDireccion.setFocus()
        elif self.focusWidget() == self.InputDireccion:
            self.InputCodigo.setFocus()

    def navegar_widgets_atras(self):
        if self.focusWidget() == self.InputCodigo:
            self.InputDireccion.setFocus()
        elif self.focusWidget() == self.InputDireccion:
            self.InputTelefonoCli.setFocus()
        elif self.focusWidget() == self.InputTelefonoCli:
            self.InputApellidoCli.setFocus()
        elif self.focusWidget() == self.InputApellidoCli:
            self.InputNombreCli.setFocus()
        elif self.focusWidget() == self.InputNombreCli:
            self.InputCedula.setFocus()
        elif self.focusWidget() == self.InputCedula:
            self.InputNombre.setFocus()
        elif self.focusWidget() == self.InputNombre:
            self.InputCodigo.setFocus()

    def configurar_localizacion(self):
        try:
            locale.setlocale(locale.LC_ALL, "es_CO.UTF-8")
        except locale.Error:
            print("No se pudo configurar la localización de Colombia.")

    def _leer_precio(self, producto, campo_precio):
        valor = getattr(producto, campo_precio, None)
        if valor is None:
            valor = getattr(producto, "Precio_venta_1", 0.0)
        try:
            return float(valor)
        except (TypeError, ValueError):
            return 0.0

    def procesar_codigo(self):
        codigo = self.InputCodigo.text().strip()
        nombre = self.InputNombre.text().strip()
        tipo_precio = self.comboBoxPrecio.currentText().strip()

        precios_map = {
            "PV-01": "Precio_venta_1",
            "PV-02": "Precio_venta_2",
            "PV-03": "Precio_venta_3",
            "PV-04": "Precio_venta_4",
        }
        campo_precio = precios_map.get(tipo_precio, "Precio_venta_1")

        db = SessionLocal()
        try:
            if codigo:
                if not codigo.isdigit():
                    QMessageBox.warning(
                        self, "Error", "El código debe ser un número válido."
                    )
                    return

                codigo = int(codigo)
                productos = obtener_producto_por_id(db, codigo)

                if productos:
                    producto = productos[0]
                    self.InputCodigo.setText(str(producto.ID_Producto))
                    self.InputNombre.setText(producto.Nombre)
                    self.InputMarca.setText(str(producto.marcas))
                    self.InputMarca.setEnabled(False)
                    self.id_categoria = producto.categorias
                    self.InputCantidad.clear()
                    
                    precio_val = self._leer_precio(producto, campo_precio)
                    self.InputPrecioUnitario.setText(str(precio_val))
                    self.InputPrecioUnitario.setEnabled(False)
                else:
                    self.mostrar_mensaje_temporal(
                        "Producto no encontrado",
                        "No existe un producto asociado a este código.",
                    )
                    self.limpiar_campos()
                return

            elif nombre:
                productos_nom = buscar_productos(db, nombre)
                if productos_nom:
                    producto = productos_nom[0]
                    self.InputCodigo.setText(str(producto.ID_Producto))
                    self.InputNombre.setText(producto.Nombre)
                    self.InputMarca.setText(str(producto.marcas))
                    self.InputMarca.setEnabled(False)
                    self.id_categoria = producto.categorias
                    self.InputCantidad.clear()
                    
                    precio_val = self._leer_precio(producto, campo_precio)
                    self.InputPrecioUnitario.setText(str(precio_val))
                    self.InputPrecioUnitario.setEnabled(False)
                else:
                    QMessageBox.warning(
                        self,
                        "Producto no encontrado",
                        "No existe un producto asociado a este nombre.",
                    )
                return

            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Por favor, ingrese un código o un nombre para buscar el producto.",
                )

        except Exception as e:
             QMessageBox.critical(
                self, "Error", f"Error al buscar el producto: {str(e)}"
            )
        finally:
            db.close()

    def _on_codigo_return(self):
        self.procesar_codigo()

    def _on_cedula_return(self):
        self.completar_campos()

    def limpiar_tabla(self):
        self.TablaVentasCredito.setRowCount(0)

    def iniciar_timer(self):
        self.timer.stop()
        self.timer.start(500)

    def procesar_codigo_y_agregar(self):
        self.timer.stop()
        codigo = self.InputCodigo.text().strip()
        if codigo:
            self.procesar_codigo()
            if self.id_categoria is not None:
                self.InputCantidad.setText("1")
                self.agregar_producto(mostrar_mensaje=False)
                self.InputCodigo.clear()
                self.InputCodigo.setFocus()

    def agregar_producto(self, mostrar_mensaje=True):
        codigo = self.InputCodigo.text().strip()
        nombre = self.InputNombre.text().strip()
        marca = self.InputMarca.text().strip()
        categoria = str(self.id_categoria)
        cantidad = self.InputCantidad.text().strip()
        precio_unitario = self.InputPrecioUnitario.text().strip()

        try:
            cantidad = int(cantidad)
            precio_unitario = float(precio_unitario)
        except ValueError:
            if mostrar_mensaje:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Por favor, ingrese valores numéricos válidos para la cantidad y el precio.",
                )
            return

        for row in range(self.TablaVentasCredito.rowCount()):
            item_codigo = self.TablaVentasCredito.item(row, 0)
            if item_codigo and item_codigo.text() == codigo:
                self.mostrar_mensaje_temporal(
                    "Error", "Este código de producto ya existe."
                )
                self.limpiar_campos()
                return

        db = SessionLocal()
        try:
            productos = obtener_producto_por_id(db, int(codigo))
            if productos:
                producto = productos[0]
                stock_disponible = producto.Stock_actual
                if cantidad > stock_disponible:
                    QMessageBox.warning(
                        self,
                        "Stock insuficiente",
                        f"No hay suficiente stock para esta venta. Solo quedan {stock_disponible} unidades.",
                    )
                    return
            else:
                QMessageBox.warning(
                    self,
                    "Producto no encontrado",
                    "No existe un producto asociado a este código.",
                )
                return

            total = cantidad * precio_unitario
            total_redondeado = round(total / 100) * 100

            rowPosition = self.TablaVentasCredito.rowCount()
            self.TablaVentasCredito.insertRow(rowPosition)

            item_codigo = QTableWidgetItem(codigo)
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_codigo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 0, item_codigo)

            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 1, item_nombre)

            item_marca = QTableWidgetItem(marca)
            item_marca.setFlags(item_marca.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_marca.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 2, item_marca)

            item_categoria = QTableWidgetItem(categoria)
            item_categoria.setFlags(item_categoria.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_categoria.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 3, item_categoria)

            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setFlags(item_cantidad.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 4, item_cantidad)

            item_precio = QTableWidgetItem(str(precio_unitario))
            item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 5, item_precio)

            item_total_redondeado = QTableWidgetItem(str(total_redondeado))
            item_total_redondeado.setFlags(item_total_redondeado.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_total_redondeado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.TablaVentasCredito.setItem(rowPosition, 6, item_total_redondeado)

            self.reproducir_sonido()
            self.limpiar_campos()
            self.actualizar_total()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error al agregar el producto: {str(e)}"
            )
        finally:
            db.close()

    def limpiar_campos(self):
        self.InputCodigo.clear()
        self.InputNombre.clear()
        self.InputMarca.clear()
        self.InputCantidad.clear()
        self.InputPrecioUnitario.clear()
        self.comboBoxPrecio.setCurrentIndex(0)
        self.InputCodigo.setFocus()

    def eliminar_fila(self):
        fila_seleccionada = self.TablaVentasCredito.currentRow()
        if fila_seleccionada != -1:
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                "¿Estás seguro de que deseas eliminar este producto?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.TablaVentasCredito.removeRow(fila_seleccionada)
                self.limpiar_campos()
                self.actualizar_total()
        else:
            QMessageBox.warning(
                self, "Error", "Por favor, selecciona un producto para eliminar."
            )

    def calcular_subtotal(self):
        subtotal = 0.0
        for row in range(self.TablaVentasCredito.rowCount()):
            total_item = self.TablaVentasCredito.item(row, 6)
            if total_item is not None:
                try:
                    subtotal += float(total_item.text())
                except ValueError:
                    continue
        return subtotal

    def actualizar_total(self):
        subtotal = self.calcular_subtotal()
        if subtotal.is_integer():
            subtotal_formateado = f"$ {formatear_numero(int(subtotal))}"
        else:
            subtotal_formateado = f"$ {formatear_numero(subtotal)}"

        self.LabelSubtotal.setText(subtotal_formateado)

        total = subtotal
        if total.is_integer():
            total_formateado = f"$ {formatear_numero(int(total))}"
        else:
            total_formateado = f"$ {formatear_numero(total)}"

        self.LabelTotal.setText(total_formateado)
        return subtotal

    def cargar_datos(self, row, column):
        try:
            if row >= 0 and row < self.TablaVentasCredito.rowCount():
                nombre_item = self.TablaVentasCredito.item(row, 1)
                marca_item = self.TablaVentasCredito.item(row, 2)
                categoria_item = self.TablaVentasCredito.item(row, 3)
                cantidad_item = self.TablaVentasCredito.item(row, 4)
                precio_unitario_item = self.TablaVentasCredito.item(row, 5)

                if all(
                    item is not None
                    for item in [
                        nombre_item,
                        marca_item,
                        categoria_item,
                        cantidad_item,
                        precio_unitario_item,
                    ]
                ):
                    nombre = nombre_item.text()
                    marca = marca_item.text()
                    categoria = categoria_item.text()
                    cantidad = cantidad_item.text()
                    precio_unitario = precio_unitario_item.text()

                    self.InputNombre.setText(nombre)
                    self.InputMarca.setText(marca)
                    self.InputCantidad.setText(cantidad)
                    self.InputPrecioUnitario.setText(precio_unitario)

                    self.fila_seleccionada = row
                    self.InputCantidad.setFocus()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Algunas celdas de la fila seleccionada están vacías.",
                    )
            else:
                QMessageBox.warning(self, "Error", "Fila seleccionada fuera de rango.")
                self.fila_seleccionada = None
        except AttributeError:
            QMessageBox.warning(
                self, "Error", "Algunas celdas de la fila seleccionada están vacías."
             )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Ocurrió un error al cargar los datos: {e}"
            )
            self.InputCodigo.setFocus()

    def actualizar_datos(self):
        self.InputCodigo.setFocus()
        if self.fila_seleccionada is not None:
            try:
                cantidad_str = self.InputCantidad.text().strip()
                precio_unitario_str = self.InputPrecioUnitario.text().strip()

                if not cantidad_str or not precio_unitario_str:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Por favor, ingrese valores para cantidad.",
                    )
                    return

                cantidad = int(cantidad_str)
                precio_unitario = float(precio_unitario_str)

                row = self.fila_seleccionada
                if row < self.TablaVentasCredito.rowCount():
                    item_codigo = self.TablaVentasCredito.item(row, 0)
                    if item_codigo:
                        codigo = item_codigo.text().strip()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "No se pudo obtener el código del producto desde la fila seleccionada.",
                        )
                        return
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "La fila seleccionada ya no existe en la tabla.",
                    )
                    return

                db = SessionLocal()
                try:
                    productos = obtener_producto_por_id(db, int(codigo))
                    if productos:
                        producto = productos[0]
                        stock_disponible = producto.Stock_actual
                    else:
                        QMessageBox.warning(
                            self,
                            "Producto no encontrado",
                            "No existe un producto asociado a este código.",
                        )
                        return

                    if self.invoice_number and self.invoice_number != "":
                        cant = 0
                        for id_producto, canti in self.cantidades:
                            if id_producto == int(codigo):
                                cant = canti
                                break

                        cantidad_adicional = cantidad - cant
                        if cantidad_adicional > stock_disponible:
                            QMessageBox.warning(
                                self,
                                "Stock insuficiente",
                                f"No hay suficiente stock para esta venta. Solo quedan {stock_disponible} unidades.",
                            )
                            return
                    else:
                        if cantidad > stock_disponible:
                            QMessageBox.warning(
                                self,
                                "Stock insuficiente",
                                f"No hay suficiente stock para esta venta. Solo quedan {stock_disponible} unidades.",
                            )
                            return

                finally:
                    db.close()

                self.TablaVentasCredito.setItem(row, 4, QTableWidgetItem(str(cantidad)))
                self.TablaVentasCredito.item(row, 4).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.TablaVentasCredito.setItem(
                    row, 5, QTableWidgetItem(str(precio_unitario))
                )
                self.TablaVentasCredito.item(row, 5).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                total = cantidad * precio_unitario
                total_redondeado = round(total / 100) * 100
                self.TablaVentasCredito.setItem(row, 6, QTableWidgetItem(str(total_redondeado)))
                self.TablaVentasCredito.item(row, 6).setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.actualizar_total()
                self.limpiar_campos()
                QMessageBox.information(
                    self, "Actualización", "Datos actualizados satisfactoriamente."
                )
                self.fila_seleccionada = None

            except ValueError:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Ingrese valores numéricos válidos para cantidad y precio unitario.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Ocurrió un error al actualizar los datos: {e}"
                )
        else:
            QMessageBox.warning(
                self, "Error", "No se ha seleccionado ninguna fila para actualizar."
            )

    def validar_campos(self):
        rx_codigo = QRegularExpression(r"^\d+$")
        validator_codigo = QRegularExpressionValidator(rx_codigo)
        self.InputCodigo.setValidator(validator_codigo)

        rx_cantidad = QRegularExpression(r"^\d+$")
        validator_cantidad = QRegularExpressionValidator(rx_cantidad)
        self.InputCantidad.setValidator(validator_cantidad)

        rx_precio_unitario = QRegularExpression(r"^\d+\.\d+$")
        validator_precio_unitario = QRegularExpressionValidator(rx_precio_unitario)
        self.InputPrecioUnitario.setValidator(validator_precio_unitario)

        rx_cedula = QRegularExpression(r"^\d+$")
        validator_cedula = QRegularExpressionValidator(rx_cedula)
        self.InputCedula.setValidator(validator_cedula)

        rx_nombre = QRegularExpression(r"^[a-zA-Z]+$")
        validator_nombre = QRegularExpressionValidator(rx_nombre)
        self.InputNombreCli.setValidator(validator_nombre)

        rx_apellido = QRegularExpression(r"^[a-zA-Z]+$")
        validator_apellido = QRegularExpressionValidator(rx_apellido)
        self.InputApellidoCli.setValidator(validator_apellido)

        rx_telefono = QRegularExpression(r"^[0-9]{10}$")
        validator_telefono = QRegularExpressionValidator(rx_telefono)
        self.InputTelefonoCli.setValidator(validator_telefono)

    def verificar_cliente(self):
        cedula = self.InputCedula.text().strip()
        nombre = self.InputNombreCli.text().strip()
        apellido = self.InputApellidoCli.text().strip()
        direccion = self.InputDireccion.text().strip()
        telefono = self.InputTelefonoCli.text().strip()

        db = SessionLocal()
        try:
            cliente_existente = obtener_cliente_por_id(db, cedula)
            if not cliente_existente:
                nuevo_cliente = crear_cliente(
                    db=db,
                    id_cliente=cedula,
                    nombre=nombre,
                    apellido=apellido,
                    direccion=direccion,
                    telefono=telefono,
                )
                if nuevo_cliente:
                    QMessageBox.information(
                        self, "Cliente creado", "El cliente ha sido creado exitosamente"
                    )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error al procesar el cliente: {str(e)}"
            )
        finally:
            db.close()

    def completar_campos(self):
        id_cliente = int(self.InputCedula.text().strip())
        self.db = SessionLocal()
        try:
            cliente = obtener_cliente_por_id(self.db, id_cliente)
            if cliente:
                self.InputNombreCli.setText(cliente.Nombre)
                self.InputApellidoCli.setText(cliente.Apellido)
                self.InputTelefonoCli.setText(cliente.Teléfono)
                self.InputDireccion.setText(cliente.Direccion)
            else:
                QMessageBox.warning(
                    self, "Error", f"Cliente con cédula {id_cliente} no encontrado."
                )
        except Exception as e:
            print(f"Error al obtener cliente: {e}")
        finally:
            self.db.close()

    def cambiar_precio(self):
        metodo_seleccionado = self.comboBoxPrecio.currentText().strip()

        precios_map = {
            "PV-01": "Precio_venta_1",
            "PV-02": "Precio_venta_2",
            "PV-03": "Precio_venta_3",
            "PV-04": "Precio_venta_4",
        }
        
        campo_precio = precios_map.get(metodo_seleccionado, "Precio_venta_1")

        # Actualizar InputPrecioUnitario si hay un producto cargado
        codigo_input = self.InputCodigo.text().strip()
        if codigo_input and codigo_input.isdigit():
            db_temp = SessionLocal()
            try:
                prod = obtener_producto_por_id(db_temp, int(codigo_input))
                if prod:
                    precio_val = self._leer_precio(prod[0], campo_precio)
                    self.InputPrecioUnitario.setText(str(precio_val))
            except Exception:
                pass
            finally:
                db_temp.close()

        db = SessionLocal()
        try:
            for row in range(self.TablaVentasCredito.rowCount()):
                codigo = self.TablaVentasCredito.item(row, 0).text()
                cantidad = int(self.TablaVentasCredito.item(row, 4).text())
                producto = obtener_producto_por_id(db, int(codigo))
                if producto:
                    producto = producto[0]
                    precio = self._leer_precio(producto, campo_precio)
                    self.TablaVentasCredito.item(row, 5).setText(str(precio))
                    total = cantidad * precio
                    total_redondeado = round(total / 100) * 100
                    self.TablaVentasCredito.item(row, 6).setText(str(total_redondeado))

            self.actualizar_total()
        finally:
            db.close()

    def insertar_cliente(self):
        nombreCompleto = self.InputNombreCli.text().strip()
        self.InputNombreCli.clear()
        self.db = SessionLocal()
        try:
            datos_cliente = obtener_cliente_por_nombre_completo(
                db=self.db, nombre_completo=nombreCompleto
            )
            if datos_cliente:
                self.InputCedula.setText(datos_cliente.ID_Cliente)
                self.InputNombreCli.setText(datos_cliente.Nombre)
                self.InputApellidoCli.setText(datos_cliente.Apellido)
                self.InputDireccion.setText(datos_cliente.Direccion)
                self.InputTelefonoCli.setText(datos_cliente.Teléfono)
        except Exception as e:
            print(e)