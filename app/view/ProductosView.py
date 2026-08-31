from PyQt6.QtWidgets import (
    QMessageBox,
    QWidget,
    QLineEdit,
)
from ..utils.enviar_notifi import Mensajes as QMessageBox
from PyQt6 import QtWidgets, QtCore, QtGui
from ..utils import *
from ..utils.autocomplementado import configurar_autocompletado
from ..database.database import SessionLocal
from ..controllers.producto_crud import *
from ..controllers.marca_crud import *
from ..controllers.categorias_crud import *
from ..ui import Ui_Productos
from PyQt6.QtCore import Qt


class Productos_View(QWidget, Ui_Productos):
    def __init__(self, parent=None):
        super(Productos_View, self).__init__(parent)
        self.setupUi(self)

        # Placeholders
        self.InputCodigo.setPlaceholderText("Ej: 1000")
        self.InputNombre.setPlaceholderText("Ej: Esmalte Rosa Pastel")
        self.InputMarca.setPlaceholderText("Ej: Predeterminado")
        self.InputCategoria.setPlaceholderText("Ej: Predeterminado")
        self.InputCantidad.setPlaceholderText("Ej: 10")
        self.InputCantidadMin.setPlaceholderText("Ej: 3")
        self.InputPrecioCompra.setPlaceholderText("Ej: 2500")
        self.InputPrecioVenta1.setPlaceholderText("PV-1 (50% margen)")
        self.InputPrecioVenta2.setPlaceholderText("PV-2 (35% margen)")
        self.InputPrecioVenta3.setPlaceholderText("PV-3 opcional")
        self.InputPrecioVenta4.setPlaceholderText("PV-4 opcional")
        self.InputGanancia1.setPlaceholderText("Auto")
        self.InputGanancia2.setPlaceholderText("Auto")
        self.InputGanancia3.setPlaceholderText("Auto")
        self.InputGanancia4.setPlaceholderText("Auto")

        # Solo lectura para ganancias
        self.InputGanancia1.setReadOnly(True)
        self.InputGanancia2.setReadOnly(True)
        self.InputGanancia3.setReadOnly(True)
        self.InputGanancia4.setReadOnly(True)

        # Tab order
        self.setTabOrder(self.InputCodigo, self.InputNombre)
        self.setTabOrder(self.InputNombre, self.InputMarca)
        self.setTabOrder(self.InputMarca, self.InputCategoria)
        self.setTabOrder(self.InputCategoria, self.InputCantidad)
        self.setTabOrder(self.InputCantidad, self.InputCantidadMin)
        self.setTabOrder(self.InputCantidadMin, self.InputPrecioCompra)
        self.setTabOrder(self.InputPrecioCompra, self.InputPrecioVenta1)
        self.setTabOrder(self.InputPrecioVenta1, self.InputPrecioVenta2)
        self.setTabOrder(self.InputPrecioVenta2, self.InputPrecioVenta3)
        self.setTabOrder(self.InputPrecioVenta3, self.InputPrecioVenta4)

        self.InputBuscador.setPlaceholderText(
            "Buscar por código, Nombre, Marca o Categoria"
        )
        self.InputBuscador.textChanged.connect(self.buscar_productos)

        self.db = SessionLocal()

        # Validadores numéricos
        configurar_validador_numerico(self.InputCodigo)
        configurar_validador_numerico(self.InputCantidad)
        configurar_validador_numerico(self.InputCantidadMin)
        configurar_validador_numerico(self.InputPrecioCompra)
        configurar_validador_numerico(self.InputPrecioVenta1)
        configurar_validador_numerico(self.InputPrecioVenta2)
        configurar_validador_numerico(self.InputPrecioVenta3)
        configurar_validador_numerico(self.InputPrecioVenta4)

        # Validadores texto
        configurar_validador_texto_y_numeros(self.InputNombre)
        configurar_validador_texto(self.InputMarca)
        configurar_validador_texto(self.InputCategoria)

        self.InputPrecioCompra.textChanged.connect(self.agregar_placeholder)
        self.InputPrecioVenta1.textChanged.connect(self.calcular_ganancias)
        self.InputPrecioVenta2.textChanged.connect(self.calcular_ganancias)
        self.InputPrecioVenta3.textChanged.connect(self.calcular_ganancias)
        self.InputPrecioVenta4.textChanged.connect(self.calcular_ganancias)
        self.InputPrecioCompra.textChanged.connect(self.calcular_ganancias)

        configurar_autocompletado(self.InputMarca, obtener_marcas, "Nombre", self.db)
        configurar_autocompletado(
            self.InputCategoria, obtener_categorias, "Nombre", self.db
        )

        self.TablaProductos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaProductos.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.TablaProductos.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Conectar Enter en inputs → editar
        for inp in [
            self.InputNombre, self.InputPrecioCompra, self.InputCantidad,
            self.InputCantidadMin, self.InputMarca,
            self.InputCategoria, self.InputPrecioVenta1, self.InputPrecioVenta2,
            self.InputPrecioVenta3, self.InputPrecioVenta4,
        ]:
            inp.returnPressed.connect(self.editar_producto)

        self.InputCodigo.textChanged.connect(self.verififcarInput)
        self.InputCodigo.returnPressed.connect(self.procesar_codigo)

        # Un doble clic abre el formulario con los datos del producto seleccionado.
        self.TablaProductos.cellDoubleClicked.connect(self._doble_clic_editar)

        self.BtnRegistrarProducto.clicked.connect(self.abrir_nuevo_producto)
        self.BtnIngresarProducto.clicked.connect(self.ingresar_producto)
        self.BtnActualizar.clicked.connect(self.editar_producto)
        self.BtnEliminar.clicked.connect(self.eliminar_productos)
        self.BtnLimpiar.clicked.connect(self.volver_al_listado)
        self.BtnVolver.clicked.connect(self.volver_al_listado)

        # Estado inicial: modo NUEVO
        self._set_modo_nuevo()

    # ─── Modo Nuevo / Modo Editar ────────────────────────────────────────────────

    def _set_modo_nuevo(self):
        """Cambia la UI a modo 'Nuevo Producto'."""
        self.BtnIngresarProducto.setVisible(True)
        self.BtnActualizar.setVisible(False)
        self.InputCodigo.setReadOnly(False)
        self.LabelTituloFormulario.setText("Registrar producto")
        self.BadgeModo.setText("● NUEVO PRODUCTO")
        self.BadgeModo.setObjectName("BadgeNuevo")
        # Re-aplicar stylesheet para que el cambio de objectName surta efecto
        self.BadgeModo.style().unpolish(self.BadgeModo)
        self.BadgeModo.style().polish(self.BadgeModo)

    def _set_modo_editar(self, codigo):
        """Cambia la UI a modo 'Editando #codigo'."""
        self.BtnIngresarProducto.setVisible(False)
        self.BtnActualizar.setVisible(True)
        self.InputCodigo.setReadOnly(True)   # No permitir cambiar el código al editar
        self.LabelTituloFormulario.setText("Editar producto")
        self.BadgeModo.setText(f"✎  EDITANDO  #{codigo}")
        self.BadgeModo.setObjectName("BadgeEditando")
        self.BadgeModo.style().unpolish(self.BadgeModo)
        self.BadgeModo.style().polish(self.BadgeModo)

    def _doble_clic_editar(self, row, col):
        """Abre el formulario de edición para la fila seleccionada."""
        self.cargar_datos_fila()
        self.InputNombre.setFocus()
        self.InputNombre.selectAll()

    def abrir_nuevo_producto(self):
        """Muestra el formulario vacío para registrar un producto."""
        self.limpiar_formulario()
        self.Contenido.setCurrentWidget(self.PanelFormulario)
        self.FormularioScroll.verticalScrollBar().setValue(0)
        self.InputCodigo.setFocus()

    def volver_al_listado(self):
        """Descarta el formulario en curso y vuelve al listado de productos."""
        self.limpiar_formulario()
        self.Contenido.setCurrentWidget(self.PanelListado)
        self.InputBuscador.setFocus()

    # ─── Helpers ────────────────────────────────────────────────────────────────

    def verififcarInput(self):
        """Borra los demás campos si InputCodigo está vacío."""
        if not self.InputCodigo.text().strip():
            self.limpiar_formulario()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.navegar_widgets()
        elif event.key() == Qt.Key.Key_Down:
            self.navegar_widgets_atras()
        super().keyPressEvent(event)

    def navegar_widgets(self):
        nav = [
            self.InputCodigo, self.InputNombre, self.InputMarca,
            self.InputCategoria, self.InputCantidad, self.InputCantidadMin,
            self.InputPrecioCompra,
            self.InputPrecioVenta1, self.InputPrecioVenta2,
            self.InputPrecioVenta3, self.InputPrecioVenta4,
        ]
        focused = self.focusWidget()
        if focused in nav:
            idx = nav.index(focused)
            nav[(idx + 1) % len(nav)].setFocus()

    def navegar_widgets_atras(self):
        nav = [
            self.InputCodigo, self.InputNombre, self.InputMarca,
            self.InputCategoria, self.InputCantidad, self.InputCantidadMin,
            self.InputPrecioCompra,
            self.InputPrecioVenta1, self.InputPrecioVenta2,
            self.InputPrecioVenta3, self.InputPrecioVenta4,
        ]
        focused = self.focusWidget()
        if focused in nav:
            idx = nav.index(focused)
            nav[(idx - 1) % len(nav)].setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.Contenido.setCurrentWidget(self.PanelListado)
        self.InputBuscador.clear()
        self.limpiar_tabla_productos()
        self.mostrar_productos()
        self.limpiar_formulario()
        self.InputBuscador.setFocus()

    def agregar_placeholder(self):
        """Muestra precios sugeridos (50% y 35% de margen) como placeholder."""
        precio_compra = self.InputPrecioCompra.text().strip()
        if not precio_compra:
            self.InputPrecioVenta1.setPlaceholderText("PV-1")
            self.InputPrecioVenta2.setPlaceholderText("PV-2")
            return
        try:
            costo = float(precio_compra)
            pv1 = redondear_a_cientos(costo + costo * 0.50)
            pv2 = redondear_a_cientos(costo + costo * 0.35)
            self.InputPrecioVenta1.setPlaceholderText(f"{pv1}")
            self.InputPrecioVenta2.setPlaceholderText(f"{pv2}")
        except ValueError:
            pass

    def calcular_ganancias(self):
        """Calcula y muestra las ganancias en tiempo real."""
        try:
            costo = float(self.InputPrecioCompra.text() or 0)
            for inp_pv, inp_g in [
                (self.InputPrecioVenta1, self.InputGanancia1),
                (self.InputPrecioVenta2, self.InputGanancia2),
                (self.InputPrecioVenta3, self.InputGanancia3),
                (self.InputPrecioVenta4, self.InputGanancia4),
            ]:
                txt = inp_pv.text().strip()
                if txt:
                    ganancia = float(txt) - costo
                    inp_g.setText(f"{ganancia:,.0f}")
                else:
                    inp_g.setText("")
        except ValueError:
            pass

    # ─── Tabla ──────────────────────────────────────────────────────────────────

    def obtener_ids_seleccionados(self):
        filas = self.TablaProductos.selectionModel().selectedRows()
        return [int(self.TablaProductos.item(f.row(), 0).text()) for f in filas]

    def buscar_productos(self):
        busqueda = self.InputBuscador.text().strip()
        if not busqueda:
            self.mostrar_productos()
            return
        self.db = SessionLocal()
        productos = buscar_productos(self.db, busqueda)
        self.actualizar_tabla_productos(productos)
        self.db.close()

    def actualizar_tabla_productos(self, productos):
        """Rellena la QTableWidget con la lista de productos."""
        if not productos:
            self.TablaProductos.setRowCount(0)
            self.LabelTotalCp.setText("$0.00")
            return

        COLS = [
            "Código","Nombre","Marca","Categoria","Stock","CMin",
            "PCosto","PV1","PV2","PV3","PV4","G1","G2","G3","G4","Estado"
        ]
        self.TablaProductos.setRowCount(len(productos))
        self.TablaProductos.setColumnCount(len(COLS))
        for i, h in enumerate(COLS):
            item = QtWidgets.QTableWidgetItem(h)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaProductos.setHorizontalHeaderItem(i, item)

        precio_cp = 0

        for row_idx, row in enumerate(productos):
            precio_cp += row.Precio_costo * row.Stock_actual
            estado = "Activo" if row.Estado else "Inactivo"

            valores = [
                str(row.ID_Producto),
                str(row.Nombre),
                str(row.marcas),
                str(row.categorias),
                str(row.Stock_actual),
                str(row.Stock_min),
                str(row.Precio_costo),
                str(row.Precio_venta_1),
                str(row.Precio_venta_2),
                str(row.Precio_venta_3),
                str(row.Precio_venta_4),
                str(row.Ganancia_1),
                str(row.Ganancia_2),
                str(row.Ganancia_3),
                str(row.Ganancia_4),
                estado,
            ]

            for col_idx, val in enumerate(valores):
                cell = QtWidgets.QTableWidgetItem(val)
                align = QtCore.Qt.AlignmentFlag.AlignRight if col_idx >= 6 else QtCore.Qt.AlignmentFlag.AlignCenter
                cell.setTextAlignment(align)
                self.TablaProductos.setItem(row_idx, col_idx, cell)

            if row.Stock_actual <= row.Stock_min:
                for col in range(self.TablaProductos.columnCount()):
                    it = self.TablaProductos.item(row_idx, col)
                    if it:
                        it.setForeground(QtGui.QColor(200, 30, 30))
                self.TablaProductos.viewport().update()

        self.LabelTotalCp.setText(f"${precio_cp:,.2f}")

    def procesar_codigo(self):
        self.limpiar_formulario_codigo()
        self.InputCantidadMin.setText("3")
        self.InputMarca.setText("Predeterminado")
        self.InputCategoria.setText("Predeterminado")

    def obtener_id_producto(self):
        fila = self.TablaProductos.currentRow()
        if fila == -1:
            enviar_notificacion("Error", "Seleccione un Producto!")
            return None
        id_item = self.TablaProductos.item(fila, 0)
        return id_item.text() if id_item else None

    def cargar_datos_fila(self):
        """Carga los datos de la fila seleccionada en el formulario y activa modo editar."""
        fila = self.TablaProductos.currentRow()
        if fila < 0:
            return
        datos = [
            (self.TablaProductos.item(fila, c).text()
             if self.TablaProductos.item(fila, c) else "")
            for c in range(self.TablaProductos.columnCount())
        ]
        self.InputCodigo.setText(datos[0])
        self.InputNombre.setText(datos[1])
        self.InputMarca.setText(datos[2])
        self.InputCategoria.setText(datos[3])
        self.InputCantidad.setText(datos[4])
        self.InputCantidadMin.setText(datos[5])
        self.InputPrecioCompra.setText(datos[6])
        self.InputPrecioVenta1.setText(datos[7])
        self.InputPrecioVenta2.setText(datos[8])
        self.InputPrecioVenta3.setText(datos[9])
        self.InputPrecioVenta4.setText(datos[10])
        self.InputGanancia1.setText(datos[11])
        self.InputGanancia2.setText(datos[12])
        self.InputGanancia3.setText(datos[13])
        self.InputGanancia4.setText(datos[14])
        estado_txt = datos[15] if len(datos) > 15 else "Activo"
        idx = self.InputEstado.findText(estado_txt)
        if idx >= 0:
            self.InputEstado.setCurrentIndex(idx)
        # ✨ Activar modo editar con el código del producto cargado
        self._set_modo_editar(datos[0])
        self.Contenido.setCurrentWidget(self.PanelFormulario)
        self.FormularioScroll.verticalScrollBar().setValue(0)

    def mostrar_productos(self):
        self.db = SessionLocal()
        rows = obtener_productos(self.db)
        self.actualizar_tabla_productos(rows)
        self.db.close()

    def limpiar_tabla_productos(self):
        self.TablaProductos.setRowCount(0)

    # ─── CRUD ───────────────────────────────────────────────────────────────────

    def ingresar_producto(self):
        """Captura el formulario y crea un nuevo producto."""
        id = self.InputCodigo.text()
        nombre = self.InputNombre.text()
        precio_compra = self.InputPrecioCompra.text()
        cantidad = self.InputCantidad.text()
        cantidad_min = self.InputCantidadMin.text()
        marca = self.InputMarca.text()
        categoria = self.InputCategoria.text()
        pv1 = self.InputPrecioVenta1.text() or self.InputPrecioVenta1.placeholderText()
        pv2 = self.InputPrecioVenta2.text() or self.InputPrecioVenta2.placeholderText()
        pv3 = self.InputPrecioVenta3.text() or pv1
        pv4 = self.InputPrecioVenta4.text() or pv2

        if not all([id, nombre, precio_compra, cantidad, cantidad_min, marca, categoria]):
            enviar_notificacion("Error", "Por favor, rellene todos los campos")
            return

        try:
            id = int(id)
            precio_compra = float(precio_compra)
            pv1 = float(pv1)
            pv2 = float(pv2)
            pv3 = float(pv3)
            pv4 = float(pv4)
            cantidad = int(cantidad)
            cantidad_min = int(cantidad_min)

            self.db = SessionLocal()
            id_marca = obtener_o_crear_marca(self.db, marca)
            id_categoria = obtener_o_crear_categoria(self.db, categoria)

            configurar_autocompletado(self.InputMarca, obtener_marcas, "Nombre", self.db)
            configurar_autocompletado(self.InputCategoria, obtener_categorias, "Nombre", self.db)

            if obtener_producto_por_id(self.db, id):
                enviar_notificacion("Error", "El producto ya existe en la base de datos")
                return

            crear_producto(
                self.db, id, nombre, precio_compra,
                cantidad, cantidad_min,
                pv1, pv2, id_marca, id_categoria, pv3, pv4,
            )
            enviar_notificacion("Éxito", "Producto registrado exitosamente")
            self._post_operacion()

        except ValueError:
            enviar_notificacion("Error", "Por favor, ingrese valores numéricos")
        except Exception as e:
            enviar_notificacion("Error", f"Error: {e}")
        finally:
            if hasattr(self, "db") and self.db:
                self.db.close()

    def editar_producto(self):
        """Edita el producto seleccionado tras confirmación."""
        id = self.InputCodigo.text()
        nombre = self.InputNombre.text()
        precio_compra = self.InputPrecioCompra.text()
        cantidad = self.InputCantidad.text()
        cantidad_min = self.InputCantidadMin.text()
        marca = self.InputMarca.text()
        categoria = self.InputCategoria.text()
        pv1 = self.InputPrecioVenta1.text()
        pv2 = self.InputPrecioVenta2.text()
        pv3 = self.InputPrecioVenta3.text()
        pv4 = self.InputPrecioVenta4.text()

        if not all([id, nombre, precio_compra, cantidad, cantidad_min, marca, categoria]):
            enviar_notificacion("Error", "Por favor, rellene todos los campos")
            return

        reply = QMessageBox.question(
            self,
            "Confirmación",
            "¿Desea guardar los cambios?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.db = SessionLocal()
                id_marca = obtener_o_crear_marca(self.db, marca)
                id_categoria = obtener_o_crear_categoria(self.db, categoria)

                producto_actualizado = actualizar_producto(
                    self.db,
                    int(id),
                    nombre=nombre,
                    precio_costo=float(precio_compra),
                    stock_actual=int(cantidad),
                    stock_min=int(cantidad_min),
                    id_marca=id_marca,
                    id_categoria=id_categoria,
                    precio_venta_1=float(pv1) if pv1 else None,
                    precio_venta_2=float(pv2) if pv2 else None,
                    precio_venta_3=float(pv3) if pv3 else None,
                    precio_venta_4=float(pv4) if pv4 else None,
                )

                if producto_actualizado:
                    enviar_notificacion("Éxito", "Producto actualizado correctamente")
                    self._post_operacion()
                else:
                    enviar_notificacion("Error", "Hubo un problema al actualizar el producto")
                self.db.close()

            except Exception as e:
                enviar_notificacion("Error", f"Error: {e}")

    def limpiar_formulario(self):
        codigo_blocker = QtCore.QSignalBlocker(self.InputCodigo)
        for inp in [
            self.InputCodigo, self.InputNombre, self.InputPrecioCompra,
            self.InputCantidad, self.InputCantidadMin,
            self.InputMarca, self.InputCategoria,
            self.InputPrecioVenta1, self.InputPrecioVenta2,
            self.InputPrecioVenta3, self.InputPrecioVenta4,
            self.InputGanancia1, self.InputGanancia2,
            self.InputGanancia3, self.InputGanancia4,
        ]:
            inp.setText("")
        del codigo_blocker
        self.InputEstado.setCurrentIndex(0)
        # Volver al modo NUEVO
        self._set_modo_nuevo()
    def limpiar_formulario_codigo(self):
        for inp in [
            self.InputNombre, self.InputPrecioCompra,
            self.InputCantidad, self.InputCantidadMin,
            self.InputMarca, self.InputCategoria,
            self.InputPrecioVenta1, self.InputPrecioVenta2,
            self.InputPrecioVenta3, self.InputPrecioVenta4,
            self.InputGanancia1, self.InputGanancia2,
            self.InputGanancia3, self.InputGanancia4,
        ]:
            inp.setText("")

    def eliminar_productos(self):
        ids = self.obtener_ids_seleccionados()
        if not ids:
            enviar_notificacion("Advertencia", "No se seleccionaron productos para eliminar.")
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar {len(ids)} producto(s)?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )

        if respuesta == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.db = SessionLocal()
                for id_producto in ids:
                    eliminar_producto(self.db, id_producto)
                self.db.commit()
                enviar_notificacion("Éxito", "Producto(s) eliminado(s) correctamente.")
                self.limpiar_tabla_productos()
                self.mostrar_productos()
                self.limpiar_formulario()
            except Exception as e:
                enviar_notificacion("Error", f"Error al eliminar productos: {e}")
            finally:
                self.db.close()
            self.InputBuscador.setFocus()

    # ─── Interno ─────────────────────────────────────────────────────────────────

    def _post_operacion(self):
        """Acciones comunes tras ingresar/editar un producto."""
        self.limpiar_formulario()
        self.limpiar_tabla_productos()
        self.mostrar_productos()
        self.Contenido.setCurrentWidget(self.PanelListado)
        self.InputBuscador.setFocus()
        self.db = SessionLocal()
        configurar_autocompletado(self.InputMarca, obtener_marcas, "Nombre", self.db)
        configurar_autocompletado(self.InputCategoria, obtener_categorias, "Nombre", self.db)
        self.db.close()
