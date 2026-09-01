# PyQt6 imports
from PyQt6.QtWidgets import QMessageBox, QWidget, QTableWidgetItem
from PyQt6.QtCore import QRegularExpression, QTimer, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Relative imports
from ..database.database import SessionLocal
from ..controllers.producto_crud import *
from ..controllers.detalle_factura_crud import *
from ..controllers.facturas_crud import *
from ..controllers.metodo_pago_crud import *
from ..controllers.tipo_ingreso_crud import *
from ..controllers.clientes_crud import *
from ..controllers.ingresos_crud import *
from ..controllers.historial_modificacion_crud import *
from ..controllers.caja_crud import obtener_cajas
from ..ui import Ui_VentasA
from ..configuracion import obtener_precio_producto
from ..services.ventas_service import calcular_total_venta, validar_pago
from ..services.form_validation_service import validar_campos_requeridos
from ..utils.formateador import formatear_numero
from ..utils.autocomplementado import configurar_autocompletado

# Standard library imports
import os
import locale
import win32print
import win32ui
import win32con
import datetime


class VentasA_View(QWidget, Ui_VentasA):
    cambiar_a_ventanab = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Configuración inicial
        QTimer.singleShot(0, self.InputCodigo.setFocus)
        self.usuario_actual_id = None
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        self.InputCodigo.setFocus()
        self.id_categoria = None
        self.valor_domicilio = 0.0
        self.invoice_number = None
        self.tipo_venta = 0
        self.cantidades = []
        self.fila_seleccionada = None
        self.aplicando_descuento = False
        self.timer = QTimer(self)

        # Placeholders
        self.InputPago.setPlaceholderText("$")
        self.InputCedula.setPlaceholderText("Ej: 10004194608")
        self.InputNombreCli.setPlaceholderText("Ej: Pepito Perez")
        self.InputTelefonoCli.setPlaceholderText("Ej: 3170065430")
        self.InputDireccion.setPlaceholderText("Ej: Calle 1, 123 - Piso 1")
        self.BtnFacturaA.setStyleSheet("""
            QPushButton {
                background-color: red; 
            }
        """)
        self.BtnFacturaA.hide()
        self.BtnFacturaB.hide()
        self.InputCodigo.setPlaceholderText("Ej: 7709991003078")
        self.InputNombre.setPlaceholderText("Ej: Esmalte")
        self.InputDomicilio.setPlaceholderText("Ej: 5000")
        self.InputDescuento.setPlaceholderText("Ej: 500")

        # Inicialización y configuración
        self.limpiar_tabla()
        self.configurar_localizacion()
        self.validar_campos()
        self.MetodoPagoBox.addItems(self.metodo_pago())

        # Conexiones de señales - Entradas de texto
        self.db = SessionLocal()
        self.InputCodigo.returnPressed.connect(self.procesar_codigo)
        self.InputCodigo.textChanged.connect(self.iniciar_timer)
        self.InputCantidad.returnPressed.connect(self.actualizar_datos)
        self.InputPrecioUnitario.returnPressed.connect(self.actualizar_datos)
        self.InputDomicilio.textChanged.connect(self.actualizar_total)
        self.InputCedula.textChanged.connect(self.validar_campos)
        self.InputCedula.returnPressed.connect(self.completar_campos)
        self.InputDescuento.textChanged.connect(self.aplicar_descuento)
        self.InputPago.returnPressed.connect(self.generar_venta)
        self.InputPagoTransferencia.returnPressed.connect(self.generar_venta)
        self.MetodoPagoBox.currentIndexChanged.connect(self.configuracion_pago)
        configurar_autocompletado(self.InputNombre, obtener_productos, "Nombre", self.db, self.procesar_codigo)
        configurar_autocompletado(self.InputNombreCli, obtener_cliente_nombre_apellido, "NombreCompleto", self.db, self.insertar_cliente)

        # ── Pill buttons → sincronizan con MetodoPagoBox oculto ──
        metodos_validos = [self.MetodoPagoBox.itemText(i) for i in range(self.MetodoPagoBox.count())]
        for lbl, btn in self._pill_buttons.items():
            if lbl in metodos_validos:
                def _pill_clicked(checked, label=lbl):
                    if checked:
                        idx = self.MetodoPagoBox.findText(label)
                        if idx >= 0:
                            self.MetodoPagoBox.setCurrentIndex(idx)
                        self.configuracion_pago()
                btn.toggled.connect(_pill_clicked)
        # Seleccionar Efectivo por defecto
        if "Efectivo" in self._pill_buttons:
            self._pill_buttons["Efectivo"].setChecked(True)

        # Conexiones de señales - Botones y tabla
        self.BtnFacturaB.clicked.connect(self.cambiar_a_ventanab)
        self.BtnGenerarVenta.clicked.connect(self.generar_venta)
        self.BtnEliminar.clicked.connect(self.eliminar_fila)
        self.BtnAgregar.clicked.connect(self.procesar_codigo)
        if hasattr(self, 'BtnCrearCliente'):
            self.BtnCrearCliente.clicked.connect(self.crear_cliente_rapido)
        self.tableWidget.cellClicked.connect(self.cargar_datos)
        self.tableWidget.itemChanged.connect(self.actualizar_total)

        # Timer
        self.timer.timeout.connect(self.procesar_codigo_y_agregar)

    # def cargar_información(self, factura_completa):
    #     factura = factura_completa["Factura"]
    #     cliente = factura_completa["Cliente"]
    #     detalles = factura_completa["Detalles"]

    #     subtotal = sum(detalle["Subtotal"] for detalle in detalles)
    #     delivery_fee = factura["Descuento"]

    #     client_name = f"{cliente['Nombre']} {cliente['Apellido']}"
    #     client_id = cliente["ID_Cliente"]
    #     client_address = cliente["Direccion"]
    #     client_phone = cliente["Teléfono"]

    #     total = subtotal - delivery_fee

    #     payment_method = factura["MetodoPago"]
    #     self.invoice_number = factura["ID_Factura"]

    #     if payment_method == "Efectivo":
    #         pago = str(factura["Monto_efectivo"])
    #     elif payment_method == "Transferencia":
    #         pago = str(factura["Monto_TRANSACCION"])
    #     else:
    #         pago = f"{factura['Monto_efectivo']}/{factura['Monto_TRANSACCION']}"

    #     self.tableWidget.setRowCount(len(detalles))

    #     cant = []
    #     for row, detalles in enumerate(detalles):
    #         id_producto = detalles["ID_Producto"]
    #         producto = detalles["Producto"]
    #         marca = detalles["Marca"]
    #         categoria = detalles["Categoria"]
    #         cantidad = detalles["Cantidad"]
    #         cant.append((id_producto, cantidad))
    #         precio_unitario = detalles["Precio_Unitario"]
    #         subtotal_producto = detalles["Subtotal"]

    #         item_id_producto = QTableWidgetItem(str(id_producto))
    #         item_id_producto.setFlags(item_id_producto.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_id_producto.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 0, item_id_producto)

    #         item_nombre = QTableWidgetItem(producto)
    #         item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 1, item_nombre)

    #         item_marca = QTableWidgetItem(marca)
    #         item_marca.setFlags(item_marca.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_marca.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 2, item_marca)

    #         item_categoria = QTableWidgetItem(categoria)
    #         item_categoria.setFlags(item_categoria.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_categoria.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 3, item_categoria)

    #         item_cantidad = QTableWidgetItem(str(cantidad))
    #         item_cantidad.setFlags(item_cantidad.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 4, item_cantidad)

    #         item_precio = QTableWidgetItem(str(precio_unitario))
    #         item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 5, item_precio)

    #         item_subtotal = QTableWidgetItem(str(subtotal_producto))
    #         item_subtotal.setFlags(item_subtotal.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #         item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.tableWidget.setItem(row, 6, item_subtotal)

    #     self.cantidades = cant
    #     self.tableWidget.resizeColumnsToContents()

    #     self.InputCedula.setText(str(client_id))
    #     self.InputNombreCli.setText(str(client_name))
    #     self.InputTelefonoCli.setText(str(client_phone))
    #     self.InputDireccion.setText(str(client_address))
    #     self.InputPago.setText(str(pago))
    #     self.InputDescuento.setText(str(delivery_fee))
    #     self.LabelSubtotal.setText(f"{subtotal:,.2f}")
    #     self.LabelTotal.setText(f"{total:,.2f}")
    #     self.MetodoPagoBox.setCurrentText(payment_method)

    def configurar_tipo_venta(self, indice):
        self.tipo_venta = indice
        self.actualizar_precios_segun_tipo_venta()

    def actualizar_precios_segun_tipo_venta(self):
        """Actualiza los precios unitarios y subtotales de los productos en la tabla según el tipo de factura seleccionado."""
        codigo_input = self.InputCodigo.text().strip()
        if codigo_input and codigo_input.isdigit():
            db_temp = SessionLocal()
            try:
                prod = obtener_producto_por_id(db_temp, int(codigo_input))
                if prod:
                    nuevo_p = obtener_precio_producto(prod[0], self.tipo_venta)
                    self.InputPrecioUnitario.setText(str(nuevo_p))
            except Exception:
                pass
            finally:
                db_temp.close()

        if self.tableWidget.rowCount() == 0:
            return

        db = SessionLocal()
        try:
            for row in range(self.tableWidget.rowCount()):
                item_cod = self.tableWidget.item(row, 0)
                item_cant = self.tableWidget.item(row, 4)
                if not item_cod or not item_cant:
                    continue
                try:
                    codigo = int(item_cod.text().strip())
                    cantidad = int(item_cant.text().strip())
                except ValueError:
                    continue

                productos = obtener_producto_por_id(db, codigo)
                if productos:
                    producto = productos[0]
                    nuevo_precio = float(obtener_precio_producto(producto, self.tipo_venta))
                    nuevo_total = cantidad * nuevo_precio
                    nuevo_total_redondeado = round(nuevo_total / 100) * 100

                    item_precio = QTableWidgetItem(str(nuevo_precio))
                    item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, 5, item_precio)

                    item_total = QTableWidgetItem(str(nuevo_total_redondeado))
                    item_total.setFlags(item_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, 6, item_total)

            self.actualizar_total()
            self.InputPago.clear()
            if hasattr(self, 'InputPagoTransferencia'):
                self.InputPagoTransferencia.clear()
        except Exception as e:
            print(f"Error al actualizar precios de la tabla según tipo de venta: {e}")
        finally:
            db.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.InputCodigo.setFocus()
        self.limpiar_tabla()
        self.limpiar_campos()
        self.limpiar_datos_cliente()
        self.invoice_number = None
        configurar_autocompletado(self.InputNombre, obtener_productos, "Nombre", self.db, self.procesar_codigo)
        configurar_autocompletado(self.InputNombreCli, obtener_cliente_nombre_apellido, "NombreCompleto", self.db, self.insertar_cliente)

    def mostrar_mensaje_temporal(self, titulo, mensaje, duracion=2200):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        QTimer.singleShot(duracion, msg_box.close)
        msg_box.exec()

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

        if self.tableWidget.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No hay productos en la venta.")
            self.InputCodigo.setFocus()
            return
        try:
            client_name = self.InputNombreCli.text().strip()
            client_id = self.InputCedula.text().strip()
            client_address = self.InputDireccion.text().strip()
            client_phone = self.InputTelefonoCli.text().strip()
            monto_efectivo_str = self.InputPago.text().strip()
            monto_trans_str   = self.InputPagoTransferencia.text().strip()
            payment_method    = self.MetodoPagoBox.currentText().strip()
            descuento         = float(self.InputDescuento.text().strip()) if self.InputDescuento.text() else 0.0
            domicilio_val     = self.obtener_valor_domicilio()

            # Calcular total desde la tabla
            subtotal_items = 0.0
            for row in range(self.tableWidget.rowCount()):
                try:
                    subtotal_items += float(self.tableWidget.item(row, 6).text().replace(",", ""))
                except (AttributeError, ValueError):
                    pass
            # Subtotal de los ítems con descuento aplicado (base para cobrar/base de datos)
            monto_items = subtotal_items - descuento
            # Total general que incluye domicilio (si aplica)
            total_venta = subtotal_items + domicilio_val - descuento

            # ── VALIDACIÓN DE PAGO ──
            if not payment_method:
                QMessageBox.critical(self, "Método requerido", "Debes seleccionar un método de pago.")
                return

            if payment_method == "Efectivo":
                try:
                    monto = float(monto_efectivo_str.replace(",", "."))
                except ValueError:
                    QMessageBox.critical(self, "Pago inválido", "Ingresa un monto en efectivo válido.")
                    self.InputPago.setFocus()
                    return
                monto_minimo = monto_items if domicilio_val > 0 else total_venta
                if monto < monto_minimo:
                    QMessageBox.critical(
                        self, "❌ Pago insuficiente",
                        f"El efectivo recibido (${monto:,.2f}) es menor al total a cobrar (${monto_minimo:,.2f}).\n"
                        f"Diferencia: ${monto_minimo - monto:,.2f}"
                    )
                    self.InputPago.setFocus()
                    return
                cobro_base = total_venta if (monto >= total_venta and domicilio_val > 0) else monto_items
                vuelto = monto - cobro_base
                if vuelto > 0:
                    QMessageBox.information(
                        self, "💰 Vuelto",
                        f"Vuelto a entregar al cliente: ${vuelto:,.2f}"
                    )
                monto_pago = str(monto)

            elif payment_method == "Transferencia":
                try:
                    monto = float(monto_efectivo_str.replace(",", "."))
                except ValueError:
                    QMessageBox.critical(self, "Pago inválido", "Ingresa un monto de transferencia válido.")
                    self.InputPago.setFocus()
                    return
                if abs(monto - monto_items) > 0.01 and abs(monto - total_venta) > 0.01:
                    QMessageBox.critical(
                        self, "❌ Monto incorrecto",
                        f"La transferencia (${monto:,.2f}) debe ser igual al subtotal de los ítems (${monto_items:,.2f})."
                    )
                    self.InputPago.setFocus()
                    return
                monto_pago = str(monto)

            elif payment_method == "Mixto":
                try:
                    m_ef = float(monto_efectivo_str.replace(",", ".")) if monto_efectivo_str else 0.0
                    m_tr = float(monto_trans_str.replace(",", ".")) if monto_trans_str else 0.0
                except ValueError:
                    QMessageBox.critical(self, "Pago inválido", "Ingresa montos válidos en ambos campos.")
                    return
                if m_ef <= 0 or m_tr <= 0:
                    QMessageBox.critical(self, "❌ Campos vacíos", "En pago Mixto ambos montos deben ser mayores a $0.")
                    return
                suma = m_ef + m_tr
                if abs(suma - monto_items) > 0.01 and abs(suma - total_venta) > 0.01:
                    QMessageBox.critical(
                        self, "❌ Monto incorrecto",
                        f"La suma de los pagos (${suma:,.2f}) debe ser igual al subtotal de los productos (${monto_items:,.2f}).\n"
                        f"Diferencia: ${monto_items - suma:,.2f}"
                    )
                    return
                monto_pago = f"{m_ef}/{m_tr}"
            else:
                monto_pago = monto_efectivo_str

            self.verificar_cliente(client_id, client_name, client_address, client_phone)

            db = SessionLocal()

            produc_datos = []
            items = []
            for row in range(self.tableWidget.rowCount()):
                codigo = self.tableWidget.item(row, 0).text()
                description = self.tableWidget.item(row, 1).text()
                quantity = int(self.tableWidget.item(row, 4).text())
                precio_unitario = float(self.tableWidget.item(row, 5).text())
                value = float(self.tableWidget.item(row, 6).text())

                producto = obtener_producto_por_id(db, int(codigo))
                if not producto:
                    QMessageBox.warning(self, "Error", f"Producto con código {codigo} no encontrado.")
                    return
                producto = producto[0]
                items.append((description, quantity, precio_unitario, value))
                produc_datos.append((codigo, quantity, precio_unitario))

            subtotal = sum(item[3] for item in items)
            delivery_fee = float(self.InputDomicilio.text()) if self.InputDomicilio.text() else 0.0
            total = calcular_total_venta(subtotal, delivery_fee, descuento)
            pago = self.InputPago.text().strip()

            domicilio = True if delivery_fee > 0 else False

            if self.invoice_number and self.invoice_number != "":
                self.actualizar_factura(db, self.invoice_number, payment_method, produc_datos, monto_pago, delivery_fee, self.usuario_actual_id)
                mensaje = "Factura actualizada exitosamente."
            else:
                for codigo, quantity, _ in produc_datos:
                    producto = obtener_producto_por_id(db, codigo)[0]
                    stock_actual = producto.Stock_actual - quantity
                    actualizar_producto(db, id_producto=int(codigo), stock_actual=stock_actual)

                id_factura = self.guardar_factura(db, client_id, payment_method, produc_datos, monto_pago, descuento, self.usuario_actual_id, domicilio)
                self.invoice_number = f"0000{id_factura}"
                mensaje = "Factura generada exitosamente."

            # Impresión del ticket
            max_lines_per_page = 30
            current_line = 0
            empresa_nombre = "LadyNailShop"
            empresa_direccion = "Pasto, Colombia"
            empresa_telefono = "+57 316-144-44-74"
            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            subtotal_formateado = f"${subtotal:,.2f}"
            total_formateado = f"${total:,.2f}"

            if isinstance(pago, str) and "/" in pago:
                pagos = [float(p.replace(".", "").replace(",", ".")) for p in pago.split("/")]
            else:
                pagos = [float(pago.replace(".", "").replace(",", "."))]
            if len(pagos) == 1:
                pago_formateado = f" ${pagos[0]:,.2f}"
            elif len(pagos) == 2:
                pago_formateado = f"Efectivo: ${pagos[0]:,.2f}\nTransferencia: ${pagos[1]:,.2f}"

            descuento_formateado = f"${descuento:,.2f}"
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
            print(f"🖨️ Impresora predeterminada: {impresora}")
            print(f"📄 Tamaño del papel: {printer_width}  píxeles")
            x, y = 2, 2 + 5 * line_height

            for i, linea in enumerate([empresa_nombre, empresa_direccion, empresa_telefono, fecha_actual]):
                text_size = hDC.GetTextExtent(linea)
                text_width = text_size[0]
                hDC.TextOut(center_x - (text_width // 2), 50 + (i * line_height), linea)
            y += line_height
            hDC.SelectObject(font)

            hDC.TextOut(x, y, "-----------------------------------------------------------------------------------------------------------------")
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
            header = "{:<18} {:>6} {:>10} {:>10}".format("Producto", "Cant.", "P.Unit", "Total")
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
            Subtotal: {subtotal_formateado}
            Envío: {delivery_fee_formateado}
            Total: {total_formateado}
            Método de Pago: {payment_method}
            -----------------------------------------------------------------------------------------------------
            ¡Gracias por tu compra!
            -----------------------------------------------------------------------------------------------------
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
            QMessageBox.critical(self, "Error", f"Error al generar la factura: {str(e)}")
            print(e)

        self.limpiar_tabla()
        self.limpiar_campos()
        self.InputDomicilio.clear()
        self.limpiar_datos_cliente()
        self.invoice_number = None

    def actualizar_factura(self, db, id_factura, payment_method, produc_datos, monto_pago, delivery_fee, usuario_actual_id):
        detalles_actuales = db.query(DetalleFacturas).filter(DetalleFacturas.ID_Factura == id_factura).all()
        productos_actuales = {detalle.ID_Producto: detalle.Cantidad for detalle in detalles_actuales}
        productos_nuevos = {int(codigo): cantidad for codigo, cantidad, _ in produc_datos}
        productos_eliminados = set(productos_actuales.keys()) - set(productos_nuevos.keys())

        for id_producto in productos_eliminados:
            cantidad_vendida = productos_actuales[id_producto]
            producto = db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
            producto.Stock_actual += cantidad_vendida
            db.delete(db.query(DetalleFacturas).filter(
                DetalleFacturas.ID_Factura == id_factura,
                DetalleFacturas.ID_Producto == id_producto
            ).first())

        for id_producto, nueva_cantidad in productos_nuevos.items():
            if id_producto in productos_actuales:
                detalle = db.query(DetalleFacturas).filter(
                    DetalleFacturas.ID_Factura == id_factura,
                    DetalleFacturas.ID_Producto == id_producto
                ).first()
                diferencia_cantidad = nueva_cantidad - productos_actuales[id_producto]
                detalle.Cantidad = nueva_cantidad
                detalle.Subtotal = nueva_cantidad * detalle.Precio_unitario
                producto = db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
                producto.Stock_actual -= diferencia_cantidad
            else:
                producto = db.query(Productos).filter(Productos.ID_Producto == id_producto).first()
                precio_unitario = obtener_precio_producto(producto, self.tipo_venta)
                subtotal = nueva_cantidad * precio_unitario
                nuevo_detalle = DetalleFacturas(
                    ID_Factura=id_factura,
                    ID_Producto=id_producto,
                    Cantidad=nueva_cantidad,
                    Precio_unitario=precio_unitario,
                    Subtotal=subtotal,
                )
                db.add(nuevo_detalle)
                producto.Stock_actual -= nueva_cantidad

        id_metodo_pago = obtener_metodo_pago_por_nombre(db, payment_method)

        if '/' in monto_pago:
            total = monto_pago.split("/")
            efectivo = float(total[0])
            tranferencia = float(total[1])
        else:
            efectivo = float(monto_pago)
            tranferencia = float(monto_pago)

        factura = db.query(Facturas).filter(Facturas.ID_Factura == id_factura).first()
        factura.Monto_TRANSACCION = tranferencia if payment_method in ["Transferencia", "Mixto"] else 0.0
        factura.Monto_efectivo = efectivo if payment_method in ["Efectivo", "Mixto"] else 0.0
        factura.ID_Metodo_Pago = id_metodo_pago.ID_Metodo_Pago
        factura.ID_Usuario = usuario_actual_id

        crear_historial_modificacion(db=db, id_usuario=usuario_actual_id, descripcion="Factura actualizada", id_factura=id_factura)
        db.commit()

    def verificar_cliente(self, cedula, nombre_completo, direccion, telefono):
        db = SessionLocal()
        try:
            cliente_existente = obtener_cliente_por_id(db, cedula)
            if not cliente_existente:
                try:
                    nombres = nombre_completo.split(" ")
                    nombre = nombres[0]
                    apellido = nombres[1]
                except Exception as e:
                    print(f"Error al procesar el nombre del cliente: {e}")
                    return
                nuevo_cliente = crear_cliente(
                    db=db,
                    id_cliente=cedula,
                    nombre=nombre,
                    apellido=apellido,
                    direccion=direccion,
                    telefono=telefono,
                )
                if nuevo_cliente:
                    QMessageBox.information(self, "Cliente creado", "El cliente ha sido creado exitosamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar el cliente: {str(e)}")
        finally:
            db.close()

    def guardar_factura(self, db, client_id, payment_method, items, monto_pago, descuento, id_usuario, domicilio):
        try:
            id_metodo_pago = obtener_metodo_pago_por_nombre(db, payment_method)
            if not id_metodo_pago:
                QMessageBox.warning(self, "Error", f"Método de pago {payment_method} no encontrado.")
                return False

            if self.valor_domicilio == 0.0:
                estado = True
            else:
                estado = False

            if '/' in monto_pago:
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
                estado=estado,
                id_metodo_pago=id_metodo_pago.ID_Metodo_Pago,
                id_tipo_factura=self.tipo_venta + 1,
                id_cliente=client_id,
                id_usuario=id_usuario,
                domicilio=domicilio,
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
                    id_factura=id_factura
                )

            db.commit()
            if self.valor_domicilio == 0.0:
                tipo_ingreso = crear_tipo_ingreso(
                    db=db,
                    tipo_ingreso=f"Venta FAC-{self.tipo_venta + 1:02d}",
                    id_factura=id_factura,
                )
                crear_ingreso(db=db, id_tipo_ingreso=tipo_ingreso.ID_Tipo_Ingreso)
            return id_factura

        except Exception as e:
            db.rollback()
            print(f"Error al guardar la factura: {e}")
            raise

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
            self.InputDomicilio.setFocus()
        elif self.focusWidget() == self.InputDomicilio:
            self.InputCedula.setFocus()
        elif self.focusWidget() == self.InputCedula:
            self.InputNombreCli.setFocus()
        elif self.focusWidget() == self.InputNombreCli:
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
            self.InputNombreCli.setFocus()
        elif self.focusWidget() == self.InputNombreCli:
            self.InputCedula.setFocus()
        elif self.focusWidget() == self.InputCedula:
            self.InputDomicilio.setFocus()
        elif self.focusWidget() == self.InputDomicilio:
            self.InputNombre.setFocus()
        elif self.focusWidget() == self.InputNombre:
            self.InputCodigo.setFocus()

    def configurar_localizacion(self):
        try:
            locale.setlocale(locale.LC_ALL, "es_CO.UTF-8")
        except locale.Error:
            print("No se pudo configurar la localización de Colombia.")

    def procesar_codigo(self):
        codigo = self.InputCodigo.text().strip()
        nombre = self.InputNombre.text().strip()

        db = SessionLocal()
        try:
            if codigo:
                if not codigo.isdigit():
                    QMessageBox.warning(self, "Error", "El código debe ser un número válido.")
                    return

                codigo = int(codigo)
                productos = obtener_producto_por_id(db, codigo)

                if productos:
                    producto = productos[0]
                    self.InputCodigo.setText(str(producto.ID_Producto))
                    self.InputNombre.setText(producto.Nombre)
                    self.InputMarca.setText(str(producto.marcas))
                    self.InputMarca.setEnabled(False)
                    self.InputPrecioUnitario.setText(str(obtener_precio_producto(producto, self.tipo_venta)))
                    self.InputPrecioUnitario.setEnabled(False)
                    self.id_categoria = producto.categorias
                    self.InputCantidad.clear()
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
                    self.InputPrecioUnitario.setText(str(obtener_precio_producto(producto, self.tipo_venta)))
                    self.InputPrecioUnitario.setEnabled(False)
                    self.id_categoria = producto.categorias
                    self.InputCantidad.clear()
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
            QMessageBox.critical(self, "Error", f"Error al buscar el producto: {str(e)}")
        finally:
            db.close()

    def limpiar_tabla(self):
        self.tableWidget.setRowCount(0)

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
                self.InputPago.clear()

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

        for row in range(self.tableWidget.rowCount()):
            item_codigo = self.tableWidget.item(row, 0)
            if item_codigo and item_codigo.text() == codigo:
                self.mostrar_mensaje_temporal("Error", "Este código de producto ya existe.")
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
                    self.limpiar_campos()
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

            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)

            item_codigo = QTableWidgetItem(codigo)
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_codigo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 0, item_codigo)

            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 1, item_nombre)

            item_marca = QTableWidgetItem(marca)
            item_marca.setFlags(item_marca.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_marca.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 2, item_marca)

            item_categoria = QTableWidgetItem(categoria)
            item_categoria.setFlags(item_categoria.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_categoria.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 3, item_categoria)

            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setFlags(item_cantidad.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 4, item_cantidad)

            item_precio = QTableWidgetItem(str(precio_unitario))
            item_precio.setFlags(item_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 5, item_precio)

            item_total_redondeado = QTableWidgetItem(str(total_redondeado))
            item_total_redondeado.setFlags(item_total_redondeado.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_total_redondeado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(rowPosition, 6, item_total_redondeado)

            self.reproducir_sonido()
            self.limpiar_campos()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar el producto: {str(e)}")
        finally:
            db.close()

    def limpiar_campos(self):
        self.InputCodigo.clear()
        self.InputNombre.clear()
        self.InputMarca.clear()
        self.InputCantidad.clear()
        self.InputPrecioUnitario.clear()
        self.InputCodigo.setFocus()

    def eliminar_fila(self):
        filas_seleccionadas = self.tableWidget.selectionModel().selectedRows()
        if not filas_seleccionadas:
            QMessageBox.warning(self, "Error", "Por favor, selecciona al menos un producto para eliminar.")
            return

        n = len(filas_seleccionadas)
        msg = f"¿Eliminar {n} producto{'s' if n > 1 else ''}?"
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Eliminar de mayor a menor índice para no desplazar filas
            for idx in sorted([f.row() for f in filas_seleccionadas], reverse=True):
                self.tableWidget.removeRow(idx)
            self.limpiar_campos()
            self.actualizar_total()
            self.InputPago.clear()

    def obtener_valor_domicilio(self):
        if self.InputDomicilio.isEnabled():
            VarDomicilio = self.InputDomicilio.text().strip()
            try:
                self.valor_domicilio = float(VarDomicilio) if VarDomicilio else 0.0
            except ValueError:
                QMessageBox.warning(self, "Error", "Ingrese un número válido.")
                self.valor_domicilio = 0.0
                self.InputDomicilio.clear()
                return 0.0
            return self.valor_domicilio
        else:
            return self.valor_domicilio

    def calcular_subtotal(self):
        subtotal = 0.0
        for row in range(self.tableWidget.rowCount()):
            total_item = self.tableWidget.item(row, 6)
            if total_item is not None:
                try:
                    subtotal += float(total_item.text())
                except ValueError:
                    continue
        return subtotal

    def actualizar_total(self):
        subtotal = self.calcular_subtotal()
        domicilio = self.obtener_valor_domicilio()
        descuento_str = self.InputDescuento.text().strip() if hasattr(self, 'InputDescuento') else ""
        try:
            descuento = float(descuento_str) if descuento_str else 0.0
        except ValueError:
            descuento = 0.0
        
        total = subtotal + domicilio - descuento
        self.LabelSubtotal.setText(f"$ {formatear_numero(subtotal)}")
        if hasattr(self, 'lblResumenDescuento'):
            self.lblResumenDescuento.setText(f"- $ {formatear_numero(descuento)}")
        if hasattr(self, 'lblResumenDomicilio'):
            self.lblResumenDomicilio.setText(f"+ $ {formatear_numero(domicilio)}")
        self.LabelTotal.setText(f"$ {formatear_numero(total)}")

    def aplicar_descuento(self):
        try:
            descuento_str = self.InputDescuento.text().strip()
            if descuento_str == "":
                descuento = 0.0
            else:
                descuento = float(descuento_str)
                if descuento < 0:
                    raise ValueError("El descuento no puede ser negativo.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Valor de descuento no válido.")
            self.InputDescuento.clear()
            return

        subtotal_antes_descuento = self.calcular_subtotal()
        if descuento > subtotal_antes_descuento:
            QMessageBox.warning(self, "Error", "El descuento no puede ser mayor al subtotal.")
            self.InputDescuento.clear()
            return

        self.actualizar_total()

    def cargar_datos(self, row, column):
        try:
            if row >= 0 and row < self.tableWidget.rowCount():
                nombre_item = self.tableWidget.item(row, 1)
                marca_item = self.tableWidget.item(row, 2)
                categoria_item = self.tableWidget.item(row, 3)
                cantidad_item = self.tableWidget.item(row, 4)
                precio_unitario_item = self.tableWidget.item(row, 5)

                if all(item is not None for item in [nombre_item, marca_item, categoria_item, cantidad_item, precio_unitario_item]):
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
                    self.InputDomicilio.setEnabled(True)
                    self.InputDomicilio.setText(str(self.valor_domicilio))
                    self.InputCantidad.setFocus()
                else:
                    QMessageBox.warning(self, "Error", "Algunas celdas de la fila seleccionada están vacías.")
            else:
                QMessageBox.warning(self, "Error", "Fila seleccionada fuera de rango.")
                self.fila_seleccionada = None
                self.InputDomicilio.clear()
        except AttributeError:
            QMessageBox.warning(self, "Error", "Algunas celdas de la fila seleccionada están vacías.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al cargar los datos: {e}")

        self.fila_seleccionada = row

    def actualizar_datos(self):
        if self.fila_seleccionada is not None:
            try:
                cantidad_str = self.InputCantidad.text().strip()
                precio_unitario_str = self.InputPrecioUnitario.text().strip()

                if not cantidad_str or not precio_unitario_str:
                    QMessageBox.warning(self, "Error", "Por favor, ingrese valores para cantidad.")
                    return

                cantidad = int(cantidad_str)
                precio_unitario = float(precio_unitario_str)

                row = self.fila_seleccionada
                if row < self.tableWidget.rowCount():
                    item_codigo = self.tableWidget.item(row, 0)
                    if item_codigo:
                        codigo = item_codigo.text().strip()
                    else:
                        QMessageBox.warning(self, "Error", "No se pudo obtener el código del producto desde la fila seleccionada.")
                        return
                else:
                    QMessageBox.warning(self, "Error", "La fila seleccionada ya no existe en la tabla.")
                    return

                db = SessionLocal()
                try:
                    productos = obtener_producto_por_id(db, int(codigo))
                    if productos:
                        producto = productos[0]
                        stock_disponible = producto.Stock_actual
                    else:
                        QMessageBox.warning(self, "Producto no encontrado", "No existe un producto asociado a este código.")
                        return

                    if self.invoice_number and self.invoice_number != "":
                        cant = 0
                        for id_producto, canti in self.cantidades:
                            if id_producto == int(codigo):
                                cant = canti
                                break

                        cantidad_adicional = cantidad - cant
                        if cantidad_adicional > stock_disponible:
                            QMessageBox.warning(self, "Stock insuficiente", f"No hay suficiente stock para esta venta. Solo quedan {stock_disponible} unidades.")
                            return
                    else:
                        if cantidad > stock_disponible:
                            QMessageBox.warning(self, "Stock insuficiente", f"No hay suficiente stock para esta venta. Solo quedan {stock_disponible} unidades.")
                            return

                finally:
                    db.close()

                self.tableWidget.setItem(row, 4, QTableWidgetItem(str(cantidad)))
                self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 5, QTableWidgetItem(str(precio_unitario)))
                self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total = cantidad * precio_unitario
                self.tableWidget.setItem(row, 6, QTableWidgetItem(str(total)))
                self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.actualizar_total()
                self.limpiar_campos()
                QMessageBox.information(self, "Actualización", "Datos actualizados satisfactoriamente.")
                self.fila_seleccionada = None

            except ValueError:
                QMessageBox.warning(self, "Error", "Ingrese valores numéricos válidos para cantidad y precio unitario.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al actualizar los datos: {e}")
        else:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ninguna fila para actualizar.")
        self.InputPago.clear()

    def validar_campos(self):
        rx_codigo = QRegularExpression(r"^\d+$")
        validator_codigo = QRegularExpressionValidator(rx_codigo)
        self.InputCodigo.setValidator(validator_codigo)

        rx_precioU = QRegularExpression(r"^\d+\.\d+$")
        validator_precioU = QRegularExpressionValidator(rx_precioU)
        self.InputPrecioUnitario.setValidator(validator_precioU)

        rx_domicilio = QRegularExpression(r"^\d+\.\d+$")
        validator_domicilio = QRegularExpressionValidator(rx_domicilio)
        self.InputDomicilio.setValidator(validator_domicilio)

        rx_cantidad = QRegularExpression(r"^\d+$")
        validator_cantidad = QRegularExpressionValidator(rx_cantidad)
        self.InputCantidad.setValidator(validator_cantidad)

        rx_cedula = QRegularExpression(r"^\d+$")
        validator_cedula = QRegularExpressionValidator(rx_cedula)
        self.InputCedula.setValidator(validator_cedula)

        rx_nombre = QRegularExpression(r"^[a-zA-Z ]+$")
        validator_nombre = QRegularExpressionValidator(rx_nombre)
        self.InputNombreCli.setValidator(validator_nombre)

        rx_telefono = QRegularExpression(r"^[0-9]{10}$")
        validator_telefono = QRegularExpressionValidator(rx_telefono)
        self.InputTelefonoCli.setValidator(validator_telefono)

        rx_descuento = QRegularExpression(r"^\d+\.\d+$")
        validator_descuento = QRegularExpressionValidator(rx_descuento)
        self.InputDescuento.setValidator(validator_descuento)
        rx_descuento = QRegularExpression(r"^\d+$")
        validator_descuento = QRegularExpressionValidator(rx_descuento)
        self.InputDescuento.setValidator(validator_descuento)

    def completar_campos(self):
        id_cliente = int(self.InputCedula.text().strip())
        self.db = SessionLocal()
        try:
            cliente = obtener_cliente_por_id(self.db, id_cliente)
            if cliente:
                self.InputNombreCli.setText(f"{cliente.Nombre} {cliente.Apellido}")
                self.InputTelefonoCli.setText(cliente.Teléfono)
                self.InputDireccion.setText(cliente.Direccion)
            else:
                QMessageBox.warning(self, "Error", f"Cliente con cédula {id_cliente} no encontrado.")
        except Exception as e:
            print(f"Error al obtener cliente: {e}")
        finally:
            self.db.close()

    def crear_cliente_rapido(self):
        client_id = self.InputCedula.text().strip()
        client_name = self.InputNombreCli.text().strip()
        client_phone = self.InputTelefonoCli.text().strip()
        client_address = self.InputDireccion.text().strip()

        if not (client_id and client_name and client_phone and client_address):
            QMessageBox.warning(self, "Campos incompletos", "Llena Cédula, Nombre, Teléfono y Dirección para crear el cliente.")
            return

        db = SessionLocal()
        try:
            if obtener_cliente_por_id(db, client_id):
                QMessageBox.information(self, "Información", f"El cliente con cédula {client_id} ya existe en el sistema.")
                return
            
            nombres = client_name.split(" ", 1)
            nombre = nombres[0]
            apellido = nombres[1] if len(nombres) > 1 else ""

            nuevo = crear_cliente(
                db=db,
                id_cliente=client_id,
                nombre=nombre,
                apellido=apellido,
                direccion=client_address,
                telefono=client_phone
            )
            if nuevo:
                QMessageBox.information(self, "Éxito", f"Cliente {nombre} registrado exitosamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el cliente: {e}")
        finally:
            db.close()

    def metodo_pago(self):
        try:
            db = SessionLocal()
            if db:
                metodos = obtener_metodos_pago(db)
                if metodos:
                    nombres_metodos = [metodo.Nombre for metodo in metodos]
                else:
                    nombres_metodos = []
            else:
                nombres_metodos = []
            return nombres_metodos
        except Exception as e:
            return []
        finally:
            db.close()

    def configuracion_pago(self):
        """Gestiona la UI de pago según el método seleccionado por los pill buttons."""
        metodo = self.MetodoPagoBox.currentText()
        self.InputPago.clear()
        self.InputPagoTransferencia.clear()

        es_mixto = (metodo == "Mixto")
        self._lblTransferencia.setVisible(es_mixto)
        self.InputPagoTransferencia.setVisible(es_mixto)

        if metodo == "Efectivo":
            self._lblEfectivo.setText("Monto recibido (permite vuelto si es mayor)")
            self.InputPago.setPlaceholderText("$ Efectivo recibido")
            self.lblPagoInfo.setText("El sistema calculará el vuelto si el monto es mayor al total.")
        elif metodo == "Transferencia":
            self._lblEfectivo.setText("Monto de la Transferencia")
            self.InputPago.setPlaceholderText("$ Debe ser EXACTAMENTE igual al total")
            self.lblPagoInfo.setText("⚠️ La transferencia debe ser exactamente igual al total de la venta.")
        elif es_mixto:
            self._lblEfectivo.setText("Monto en Efectivo")
            self.InputPago.setPlaceholderText("$ Parte en efectivo")
            self.InputPagoTransferencia.setPlaceholderText("$ Parte en transferencia")
            self.lblPagoInfo.setText("La suma de ambos montos debe ser ≥ total de la venta.")
        else:
            self.lblPagoInfo.setText("")

        rx = QRegularExpression(r"^\d+(\.\d{1,2})?$")
        self.InputPago.setValidator(QRegularExpressionValidator(rx))
        self.InputPagoTransferencia.setValidator(QRegularExpressionValidator(rx))

    def limpiar_datos_cliente(self):
        self.InputPago.clear()
        if hasattr(self, 'InputPagoTransferencia'):
            self.InputPagoTransferencia.clear()
        self.InputCedula.clear()
        self.InputNombreCli.clear()
        self.InputTelefonoCli.clear()
        self.InputDireccion.clear()
        self.InputDescuento.clear()
        self.LabelTotal.setText("$ 0")
        self.LabelSubtotal.setText("$ 0")
        if hasattr(self, 'lblResumenDescuento'):
            self.lblResumenDescuento.setText("- $ 0")
        if hasattr(self, 'lblResumenDomicilio'):
            self.lblResumenDomicilio.setText("+ $ 0")

    def insertar_cliente(self):
        nombreCompleto = self.InputNombreCli.text().strip()
        self.db = SessionLocal()
        try:
            datos_cliente = obtener_cliente_por_nombre_completo(db=self.db, nombre_completo=nombreCompleto)
            if datos_cliente:
                self.InputCedula.setText(datos_cliente.ID_Cliente)
                self.InputDireccion.setText(datos_cliente.Direccion)
                self.InputTelefonoCli.setText(datos_cliente.Teléfono)
        except Exception as e:
            print(e)