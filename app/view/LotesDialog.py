from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta
from ..database.database import SessionLocal
from ..controllers.lote_crud import (
    crear_lote,
    obtener_lotes_por_producto,
    actualizar_lote,
    eliminar_lote,
    sincronizar_producto_con_lotes,
)
from ..controllers.producto_crud import obtener_producto_por_id, redondear_a_cientos
from ..utils.enviar_notifi import Mensajes as QMessageBox
from ..utils import (
    configurar_validador_numerico,
    configurar_validador_texto_y_numeros,
    enviar_notificacion,
)

_PRIMARY = "#862D6D"
_PRIMARY_HOVER = "#6E2259"
_PRIMARY_PRESSED = "#551443"
_BG = "#F5F0F4"
_CARD_BG = "#FFFFFF"
_DIVIDER = "#E2DAE1"
_TEXT = "#201A24"
_MUTED = "#7B737F"
_BORDER = "#D8C8D5"
_BORDER_FOCUS = "#862D6D"
_CARD_BORDER = "#EAE0E8"
_DANGER = "#C0392B"
_SUCCESS = "#27AE60"

_DIALOG_STYLE = f"""
QDialog {{
    background-color: {_BG};
}}
QFrame#Card {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 12px;
}}
QLabel#Title {{
    font-family: 'Segoe UI';
    font-size: 18px;
    font-weight: 700;
    color: {_TEXT};
}}
QLabel#Subtitle {{
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {_MUTED};
}}
QLabel#SectionTitle {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 700;
    color: {_PRIMARY};
    letter-spacing: 1px;
}}
QLabel#FieldLabel {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 600;
    color: {_MUTED};
}}
QLineEdit, QComboBox {{
    background-color: {_CARD_BG};
    border: 1.5px solid {_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {_TEXT};
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {_BORDER_FOCUS};
    background-color: #FFFAFE;
}}
QLineEdit[readOnly="true"] {{
    background-color: #F0EAF0;
    color: {_MUTED};
}}
QPushButton#BtnPrimary {{
    background-color: {_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#BtnPrimary:hover {{
    background-color: {_PRIMARY_HOVER};
}}
QPushButton#BtnSecondary {{
    background-color: transparent;
    color: {_PRIMARY};
    border: 1.5px solid {_PRIMARY};
    border-radius: 6px;
    padding: 6px 14px;
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#BtnSecondary:hover {{
    background-color: #F8EDF5;
}}
QPushButton#BtnDanger {{
    background-color: {_DANGER};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 600;
}}
QTableWidget {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 8px;
    gridline-color: #F0EAF0;
    font-family: 'Segoe UI';
    font-size: 12px;
    color: {_TEXT};
    selection-background-color: #F2E4EE;
    selection-color: {_PRIMARY};
}}
QHeaderView::section {{
    background-color: #EDE3EB;
    color: {_PRIMARY};
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 700;
    border: none;
    padding: 6px;
}}
"""


class LotesDialog(QtWidgets.QDialog):
    def __init__(self, id_producto: int, parent=None):
        super().__init__(parent)
        self.id_producto = id_producto
        self.editando_lote_id = None
        self.setWindowTitle(f"Gestión de Lotes — Producto #{id_producto}")
        self.resize(960, 680)
        self.setStyleSheet(_DIALOG_STYLE)

        self._setup_ui()
        self._cargar_datos_producto()
        self._cargar_lotes()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # ── Header ──
        header_frame = QtWidgets.QFrame()
        header_frame.setObjectName("Card")
        hf_layout = QtWidgets.QHBoxLayout(header_frame)
        hf_layout.setContentsMargins(16, 12, 16, 12)

        title_vbox = QtWidgets.QVBoxLayout()
        self.label_titulo = QtWidgets.QLabel(f"Lotes de Producto #{self.id_producto}")
        self.label_titulo.setObjectName("Title")
        self.label_subtitulo = QtWidgets.QLabel("Cargando detalles...")
        self.label_subtitulo.setObjectName("Subtitle")
        title_vbox.addWidget(self.label_titulo)
        title_vbox.addWidget(self.label_subtitulo)
        hf_layout.addLayout(title_vbox)
        hf_layout.addStretch()

        # Resumen stock
        self.label_stock_total = QtWidgets.QLabel("Stock Total: 0")
        self.label_stock_total.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {_PRIMARY}; "
            f"background: #F8EDF5; border-radius: 8px; padding: 6px 14px;"
        )
        hf_layout.addWidget(self.label_stock_total)

        main_layout.addWidget(header_frame)

        # ── Formulario de Lote (Card) ──
        form_frame = QtWidgets.QFrame()
        form_frame.setObjectName("Card")
        ff_layout = QtWidgets.QVBoxLayout(form_frame)
        ff_layout.setContentsMargins(16, 12, 16, 12)
        ff_layout.setSpacing(10)

        self.label_modo_form = QtWidgets.QLabel("NUEVO LOTE")
        self.label_modo_form.setObjectName("SectionTitle")
        ff_layout.addWidget(self.label_modo_form)

        # Grid 1: Lote #, Stock Inicial, P. Costo, Vencimiento, Proveedor
        grid1 = QtWidgets.QGridLayout()
        grid1.setSpacing(8)

        self.input_numero_lote = QtWidgets.QLineEdit()
        self.input_numero_lote.setPlaceholderText("Ej: LOTE-002 o Factura #")
        self.input_stock = QtWidgets.QLineEdit()
        self.input_stock.setPlaceholderText("Ej: 20")
        self.input_precio_costo = QtWidgets.QLineEdit()
        self.input_precio_costo.setPlaceholderText("Ej: 3000")
        self.input_vencimiento = QtWidgets.QLineEdit()
        self.input_vencimiento.setPlaceholderText("AAAA-MM-DD (opcional)")
        self.input_proveedor = QtWidgets.QLineEdit()
        self.input_proveedor.setPlaceholderText("Proveedor / Distribuidor")

        configurar_validador_numerico(self.input_stock)
        configurar_validador_numerico(self.input_precio_costo)

        cols1 = [
            ("N° Lote / Referencia", self.input_numero_lote),
            ("Stock de Entrada", self.input_stock),
            ("Precio Costo", self.input_precio_costo),
            ("Fecha Vencimiento", self.input_vencimiento),
            ("Proveedor", self.input_proveedor),
        ]
        for col_idx, (lbl, w) in enumerate(cols1):
            l = QtWidgets.QLabel(lbl)
            l.setObjectName("FieldLabel")
            grid1.addWidget(l, 0, col_idx)
            grid1.addWidget(w, 1, col_idx)

        ff_layout.addLayout(grid1)

        # Grid 2: Precios de Venta 1..4 y Ganancias
        grid2 = QtWidgets.QGridLayout()
        grid2.setSpacing(8)

        self.input_pv1 = QtWidgets.QLineEdit()
        self.input_pv2 = QtWidgets.QLineEdit()
        self.input_pv3 = QtWidgets.QLineEdit()
        self.input_pv4 = QtWidgets.QLineEdit()
        self.input_g1 = QtWidgets.QLineEdit()
        self.input_g2 = QtWidgets.QLineEdit()
        self.input_g3 = QtWidgets.QLineEdit()
        self.input_g4 = QtWidgets.QLineEdit()

        for g_inp in (self.input_g1, self.input_g2, self.input_g3, self.input_g4):
            g_inp.setReadOnly(True)
            g_inp.setPlaceholderText("Auto")

        for pv_inp in (self.input_pv1, self.input_pv2, self.input_pv3, self.input_pv4):
            configurar_validador_numerico(pv_inp)
            pv_inp.textChanged.connect(self._calcular_ganancias_lote)

        self.input_precio_costo.textChanged.connect(self._sugerir_precios)
        self.input_precio_costo.textChanged.connect(self._calcular_ganancias_lote)

        cols2 = [
            ("PV-1 (Precio 1)", self.input_pv1, "G-1", self.input_g1),
            ("PV-2 (Precio 2)", self.input_pv2, "G-2", self.input_g2),
            ("PV-3 (Precio 3)", self.input_pv3, "G-3", self.input_g3),
            ("PV-4 (Precio 4)", self.input_pv4, "G-4", self.input_g4),
        ]
        for col_idx, (lbl_pv, w_pv, lbl_g, w_g) in enumerate(cols2):
            lpv = QtWidgets.QLabel(lbl_pv)
            lpv.setObjectName("FieldLabel")
            lg = QtWidgets.QLabel(lbl_g)
            lg.setObjectName("FieldLabel")
            grid2.addWidget(lpv, 0, col_idx * 2)
            grid2.addWidget(w_pv, 1, col_idx * 2)
            grid2.addWidget(lg, 0, col_idx * 2 + 1)
            grid2.addWidget(w_g, 1, col_idx * 2 + 1)

        ff_layout.addLayout(grid2)

        # Botones del formulario
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.setSpacing(8)

        self.btn_guardar_lote = QtWidgets.QPushButton("  Guardar Lote")
        self.btn_guardar_lote.setObjectName("BtnPrimary")
        self.btn_guardar_lote.setIcon(qta.icon("fa5s.save", color="#FFFFFF"))
        self.btn_guardar_lote.clicked.connect(self._guardar_lote)

        self.btn_cancelar_edicion = QtWidgets.QPushButton("  Cancelar")
        self.btn_cancelar_edicion.setObjectName("BtnSecondary")
        self.btn_cancelar_edicion.clicked.connect(self._reset_formulario)
        self.btn_cancelar_edicion.setVisible(False)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_cancelar_edicion)
        btn_box.addWidget(self.btn_guardar_lote)
        ff_layout.addLayout(btn_box)

        main_layout.addWidget(form_frame)

        # ── Tabla de Lotes ──
        tabla_frame = QtWidgets.QFrame()
        tabla_frame.setObjectName("Card")
        tf_layout = QtWidgets.QVBoxLayout(tabla_frame)
        tf_layout.setContentsMargins(12, 12, 12, 12)
        tf_layout.setSpacing(8)

        tb_header = QtWidgets.QHBoxLayout()
        lbl_tbl = QtWidgets.QLabel("HISTORIAL DE LOTES REGISTRADOS")
        lbl_tbl.setObjectName("SectionTitle")
        tb_header.addWidget(lbl_tbl)
        tb_header.addStretch()

        self.btn_eliminar_lote = QtWidgets.QPushButton("  Eliminar Lote")
        self.btn_eliminar_lote.setObjectName("BtnDanger")
        self.btn_eliminar_lote.setIcon(qta.icon("fa5s.trash", color="#FFFFFF"))
        self.btn_eliminar_lote.clicked.connect(self._eliminar_lote_seleccionado)
        tb_header.addWidget(self.btn_eliminar_lote)

        tf_layout.addLayout(tb_header)

        self.tabla_lotes = QtWidgets.QTableWidget()
        self.tabla_lotes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_lotes.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_lotes.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_lotes.verticalHeader().setVisible(False)
        self.tabla_lotes.cellDoubleClicked.connect(self._editar_lote_fila)

        headers = [
            "ID", "N° Lote", "F. Entrada", "Vencimiento", "Proveedor",
            "Stock Inicial", "Stock Actual", "P. Costo",
            "PV-1", "PV-2", "PV-3", "PV-4", "Estado"
        ]
        self.tabla_lotes.setColumnCount(len(headers))
        for i, h in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(h)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.tabla_lotes.setHorizontalHeaderItem(i, item)

        self.tabla_lotes.horizontalHeader().setStretchLastSection(True)
        tf_layout.addWidget(self.tabla_lotes, stretch=1)

        main_layout.addWidget(tabla_frame, stretch=1)

        # ── Botón Cerrar ──
        close_box = QtWidgets.QHBoxLayout()
        self.btn_cerrar = QtWidgets.QPushButton("  Cerrar")
        self.btn_cerrar.setObjectName("BtnSecondary")
        self.btn_cerrar.clicked.connect(self.accept)
        close_box.addStretch()
        close_box.addWidget(self.btn_cerrar)
        main_layout.addLayout(close_box)

    def _cargar_datos_producto(self):
        db = SessionLocal()
        try:
            prod_rows = obtener_producto_por_id(db, self.id_producto)
            if prod_rows:
                prod = prod_rows[0]
                self.label_titulo.setText(f"Lotes de Producto: {prod.Nombre}")
                self.label_subtitulo.setText(
                    f"Código: #{prod.ID_Producto} · Marca: {prod.marcas} · Categoría: {prod.categorias} · Stock Mín: {prod.Stock_min}"
                )
                self.label_stock_total.setText(f"Stock Total: {prod.Stock_actual}")
        finally:
            db.close()

    def _sugerir_precios(self):
        costo_txt = self.input_precio_costo.text().strip()
        if not costo_txt:
            self.input_pv1.setPlaceholderText("PV-1")
            self.input_pv2.setPlaceholderText("PV-2")
            return
        try:
            costo = float(costo_txt)
            pv1 = redondear_a_cientos(costo + costo * 0.50)
            pv2 = redondear_a_cientos(costo + costo * 0.35)
            self.input_pv1.setPlaceholderText(f"{pv1}")
            self.input_pv2.setPlaceholderText(f"{pv2}")
        except ValueError:
            pass

    def _calcular_ganancias_lote(self):
        try:
            costo = float(self.input_precio_costo.text() or 0)
            for inp_pv, inp_g in [
                (self.input_pv1, self.input_g1),
                (self.input_pv2, self.input_g2),
                (self.input_pv3, self.input_g3),
                (self.input_pv4, self.input_g4),
            ]:
                txt = inp_pv.text().strip()
                if txt:
                    ganancia = float(txt) - costo
                    inp_g.setText(f"{ganancia:,.0f}")
                else:
                    inp_g.setText("")
        except ValueError:
            pass

    def _cargar_lotes(self):
        db = SessionLocal()
        try:
            lotes = obtener_lotes_por_producto(db, self.id_producto)
            self.tabla_lotes.setRowCount(len(lotes))

            for row_idx, lote in enumerate(lotes):
                estado_str = "Activo" if lote.Stock_actual > 0 and lote.Estado else "Agotado"
                fecha_str = lote.Fecha_Entrada.strftime("%Y-%m-%d %H:%M") if lote.Fecha_Entrada else ""

                vals = [
                    str(lote.ID_Lote),
                    str(lote.Numero_Lote or f"LOTE-{lote.ID_Lote}"),
                    fecha_str,
                    str(lote.Fecha_Vencimiento or "-"),
                    str(lote.Proveedor or "-"),
                    str(lote.Stock_inicial),
                    str(lote.Stock_actual),
                    f"{lote.Precio_costo:,.2f}",
                    f"{lote.Precio_venta_1:,.2f}",
                    f"{lote.Precio_venta_2:,.2f}",
                    f"{lote.Precio_venta_3:,.2f}",
                    f"{lote.Precio_venta_4:,.2f}",
                    estado_str,
                ]

                for col_idx, val in enumerate(vals):
                    item = QtWidgets.QTableWidgetItem(val)
                    if col_idx in (5, 6, 7, 8, 9, 10, 11):
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    else:
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                    if lote.Stock_actual <= 0:
                        item.setForeground(QtGui.QColor(150, 150, 150))
                    self.tabla_lotes.setItem(row_idx, col_idx, item)
        finally:
            db.close()

    def _guardar_lote(self):
        numero_lote = self.input_numero_lote.text().strip()
        stock_txt = self.input_stock.text().strip()
        costo_txt = self.input_precio_costo.text().strip()
        pv1_txt = self.input_pv1.text().strip() or self.input_pv1.placeholderText()
        pv2_txt = self.input_pv2.text().strip() or self.input_pv2.placeholderText()
        pv3_txt = self.input_pv3.text().strip() or pv1_txt
        pv4_txt = self.input_pv4.text().strip() or pv2_txt
        vencimiento = self.input_vencimiento.text().strip() or None
        proveedor = self.input_proveedor.text().strip() or None

        if not stock_txt or not costo_txt:
            enviar_notificacion("Error", "Por favor ingrese al menos el stock y el precio de costo.")
            return

        try:
            stock = int(stock_txt)
            costo = float(costo_txt)
            pv1 = float(pv1_txt) if pv1_txt else costo * 1.5
            pv2 = float(pv2_txt) if pv2_txt else costo * 1.35
            pv3 = float(pv3_txt) if pv3_txt else pv1
            pv4 = float(pv4_txt) if pv4_txt else pv2

            db = SessionLocal()
            try:
                if self.editando_lote_id:
                    # Actualizar lote existente
                    actualizar_lote(
                        db,
                        self.editando_lote_id,
                        numero_lote=numero_lote,
                        precio_costo=costo,
                        precio_venta_1=pv1,
                        precio_venta_2=pv2,
                        precio_venta_3=pv3,
                        precio_venta_4=pv4,
                        stock_actual=stock,
                        fecha_vencimiento=vencimiento,
                        proveedor=proveedor,
                    )
                    enviar_notificacion("Éxito", "Lote actualizado correctamente.")
                else:
                    # Crear nuevo lote
                    if not numero_lote:
                        # Auto-generar nombre de lote basado en cantidad existente
                        total_lotes = len(obtener_lotes_por_producto(db, self.id_producto))
                        numero_lote = f"LOTE-{total_lotes + 1:03d}"

                    crear_lote(
                        db,
                        id_producto=self.id_producto,
                        numero_lote=numero_lote,
                        precio_costo=costo,
                        stock_inicial=stock,
                        precio_venta_1=pv1,
                        precio_venta_2=pv2,
                        precio_venta_3=pv3,
                        precio_venta_4=pv4,
                        fecha_vencimiento=vencimiento,
                        proveedor=proveedor,
                    )
                    enviar_notificacion("Éxito", "Nuevo lote registrado exitosamente.")
            finally:
                db.close()

            self._reset_formulario()
            self._cargar_datos_producto()
            self._cargar_lotes()

        except ValueError:
            enviar_notificacion("Error", "Los valores de stock y precios deben ser numéricos.")
        except Exception as e:
            enviar_notificacion("Error", f"Error al guardar el lote: {e}")

    def _editar_lote_fila(self, row, col):
        id_item = self.tabla_lotes.item(row, 0)
        if not id_item:
            return
        id_lote = int(id_item.text())

        db = SessionLocal()
        try:
            from ..controllers.lote_crud import obtener_lote_por_id
            lote = obtener_lote_por_id(db, id_lote)
            if not lote:
                return

            self.editando_lote_id = lote.ID_Lote
            self.label_modo_form.setText(f"✎ EDITANDO LOTE #{lote.ID_Lote} ({lote.Numero_Lote or ''})")
            self.btn_guardar_lote.setText("  Actualizar Lote")
            self.btn_cancelar_edicion.setVisible(True)

            self.input_numero_lote.setText(lote.Numero_Lote or "")
            self.input_stock.setText(str(lote.Stock_actual))
            self.input_precio_costo.setText(str(lote.Precio_costo))
            self.input_pv1.setText(str(lote.Precio_venta_1))
            self.input_pv2.setText(str(lote.Precio_venta_2))
            self.input_pv3.setText(str(lote.Precio_venta_3))
            self.input_pv4.setText(str(lote.Precio_venta_4))
            self.input_vencimiento.setText(str(lote.Fecha_Vencimiento or ""))
            self.input_proveedor.setText(str(lote.Proveedor or ""))
            self._calcular_ganancias_lote()
        finally:
            db.close()

    def _reset_formulario(self):
        self.editando_lote_id = None
        self.label_modo_form.setText("NUEVO LOTE")
        self.btn_guardar_lote.setText("  Guardar Lote")
        self.btn_cancelar_edicion.setVisible(False)

        self.input_numero_lote.clear()
        self.input_stock.clear()
        self.input_precio_costo.clear()
        self.input_pv1.clear()
        self.input_pv2.clear()
        self.input_pv3.clear()
        self.input_pv4.clear()
        self.input_g1.clear()
        self.input_g2.clear()
        self.input_g3.clear()
        self.input_g4.clear()
        self.input_vencimiento.clear()
        self.input_proveedor.clear()

    def _eliminar_lote_seleccionado(self):
        row = self.tabla_lotes.currentRow()
        if row < 0:
            enviar_notificacion("Advertencia", "Seleccione un lote de la tabla para eliminar.")
            return

        id_item = self.tabla_lotes.item(row, 0)
        num_lote = self.tabla_lotes.item(row, 1).text() if self.tabla_lotes.item(row, 1) else ""
        if not id_item:
            return
        id_lote = int(id_item.text())

        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el lote '{num_lote}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            db = SessionLocal()
            try:
                ok, msg = eliminar_lote(db, id_lote)
                if ok:
                    enviar_notificacion("Éxito", msg)
                    self._cargar_datos_producto()
                    self._cargar_lotes()
                    if self.editando_lote_id == id_lote:
                        self._reset_formulario()
                else:
                    enviar_notificacion("Error", msg)
            finally:
                db.close()
