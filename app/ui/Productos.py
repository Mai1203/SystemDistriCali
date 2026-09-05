from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

# ─── TOKENS DE COLOR (Design System Lady Nail Shop) ───────────────────────────
_PRIMARY        = "#862D6D"
_PRIMARY_HOVER  = "#6E2259"
_PRIMARY_PRESSED= "#551443"
_BG             = "#F5F0F4"
_CARD_BG        = "#FFFFFF"
_FOCUS_BG       = "#FFFAFE"
_DIVIDER        = "#E2DAE1"
_TEXT           = "#201A24"
_MUTED          = "#7B737F"
_PLACEHOLDER    = "#9C94A0"
_BORDER         = "#D8C8D5"
_BORDER_HOVER   = "#A97099"
_BORDER_FOCUS   = "#862D6D"
_CARD_BORDER    = "#EAE0E8"
_DANGER         = "#C0392B"
_DANGER_HOVER   = "#96281B"
_SUCCESS        = "#27AE60"
_WARNING_BG     = "#FFF3CD"
_WARNING_FG     = "#856404"

_STYLESHEET = f"""
/* ── Fondo general ── */
QWidget#formPanel {{
    background-color: {_BG};
}}

/* ── Card principal ── */
QFrame#Card {{
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 16px;
}}

/* ── Encabezados de sección ── */
QLabel#SectionTitle {{
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 700;
    color: {_PRIMARY};
    letter-spacing: 1.5px;
}}

/* ── Título de página ── */
QLabel#PageTitle {{
    font-family: 'Segoe UI';
    font-size: 22px;
    font-weight: 700;
    color: {_TEXT};
}}
QLabel#PageSubtitle {{
    font-family: 'Segoe UI';
    font-size: 13px;
    font-weight: 400;
    color: {_MUTED};
}}

/* ── Labels de campo ── */
QLabel#FieldLabel {{
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
    color: {_MUTED};
    padding: 0px;
    margin: 0px;
}}

/* ── Inputs ── */
QLineEdit, QComboBox {{
    font-family: 'Segoe UI';
    font-size: 13px;
    color: {_TEXT};
    background-color: {_CARD_BG};
    border: 1.5px solid {_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 36px;
    selection-background-color: {_PRIMARY};
}}
QLineEdit:hover, QComboBox:hover {{
    border-color: {_BORDER_HOVER};
}}
QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {_BORDER_FOCUS};
    background-color: {_FOCUS_BG};
}}
QLineEdit:read-only {{
    background-color: {_BG};
    color: {_MUTED};
    border-color: {_DIVIDER};
}}
QLineEdit::placeholder {{
    color: {_PLACEHOLDER};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 12px;
}}

/* ── Botón primario ── */
QPushButton#BtnPrimary {{
    font-family: 'Segoe UI';
    font-weight: 600;
    color: #FFFFFF;
    background-color: {_PRIMARY};
    border: none;
    border-radius: 8px;
    padding: 0 16px;
    min-height: 40px;
    text-align: center;
}}
QPushButton#BtnPrimary:hover {{
    background-color: {_PRIMARY_HOVER};
}}

/* ── Botón peligro ── */
QPushButton#BtnDanger {{
    font-family: 'Segoe UI';
    font-weight: 600;
    color: #FFFFFF;
    background-color: {_DANGER};
    border: none;
    border-radius: 8px;
    padding: 0 16px;
    min-height: 40px;
    text-align: center;
}}
QPushButton#BtnDanger:hover {{
    background-color: {_DANGER_HOVER};
}}

/* ── Botón secundario (outline) ── */
QPushButton#BtnSecondary {{
    font-family: 'Segoe UI';
    font-weight: 600;
    color: {_PRIMARY};
    background-color: transparent;
    border: 1.5px solid {_PRIMARY};
    border-radius: 8px;
    padding: 0 16px;
    min-height: 40px;
    text-align: center;
}}
QPushButton#BtnSecondary:hover {{
    background-color: rgba(134,45,109,0.06);
}}

/* ── Buscador ── */
QLineEdit#Buscador {{
    font-family: 'Segoe UI';
    font-size: 13px;
    background-color: {_CARD_BG};
    border: 1.5px solid {_BORDER};
    border-radius: 10px;
    padding: 8px 12px 8px 38px;
    min-height: 38px;
    color: {_TEXT};
}}
QLineEdit#Buscador:focus {{
    border-color: {_BORDER_FOCUS};
    background-color: {_FOCUS_BG};
}}

/* ── Tabla ── */
QTableWidget {{
    font-family: 'Segoe UI';
    font-size: 13px;
    background-color: {_CARD_BG};
    border: 1px solid {_CARD_BORDER};
    border-radius: 12px;
    gridline-color: {_DIVIDER};
    color: {_TEXT};
    outline: 0;
}}
QTableWidget::item {{
    padding: 8px 12px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: rgba(134,45,109,0.10);
    color: {_TEXT};
}}
QTableWidget::item:hover {{
    background-color: rgba(134,45,109,0.05);
}}
QHeaderView::section {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 700;
    color: {_MUTED};
    background-color: {_BG};
    border: none;
    border-bottom: 1px solid {_DIVIDER};
    padding: 10px 12px;
    letter-spacing: 0.8px;
}}
QTableCornerButton::section {{
    background-color: {_BG};
    border: none;
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {_BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_BORDER_HOVER};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {_BORDER};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ── Frame divisor ── */
QFrame#Divider {{
    background-color: {_DIVIDER};
    border: none;
    max-height: 1px;
}}

/* ── Label Total ── */
QLabel#LabelTotal {{
    font-family: 'Segoe UI';
    font-size: 20px;
    font-weight: 700;
    color: {_PRIMARY};
}}
QLabel#LabelTotalText {{
    font-family: 'Segoe UI';
    font-size: 12px;
    font-weight: 600;
    color: {_MUTED};
    letter-spacing: 0.8px;
}}

/* ── Badge de modo ── */
QLabel#BadgeNuevo {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 700;
    color: #FFFFFF;
    background-color: {_SUCCESS};
    border-radius: 10px;
    padding: 3px 12px;
    letter-spacing: 1px;
}}
QLabel#BadgeEditando {{
    font-family: 'Segoe UI';
    font-size: 11px;
    font-weight: 700;
    color: #FFFFFF;
    background-color: {_PRIMARY};
    border-radius: 10px;
    padding: 3px 12px;
    letter-spacing: 1px;
}}

/* ── Botón actualizar ── */
QPushButton#BtnActualizar {{
    font-family: 'Segoe UI';
    font-weight: 600;
    color: #FFFFFF;
    background-color: #2980B9;
    border: none;
    border-radius: 8px;
    padding: 0 16px;
    min-height: 40px;
    text-align: center;
}}
QPushButton#BtnActualizar:hover {{
    background-color: #1F6391;
}}
"""


def _make_label(parent, text, obj_name="FieldLabel"):
    lbl = QtWidgets.QLabel(text, parent=parent)
    lbl.setObjectName(obj_name)
    return lbl


def _make_input(parent, obj_name, placeholder="", read_only=False):
    inp = QtWidgets.QLineEdit(parent=parent)
    inp.setObjectName(obj_name)
    inp.setPlaceholderText(placeholder)
    inp.setReadOnly(read_only)
    return inp


def _section_header(parent, text):
    """Devuelve un QLabel de encabezado de sección con línea decorativa."""
    container = QtWidgets.QWidget(parent=parent)
    layout = QtWidgets.QHBoxLayout(container)
    layout.setContentsMargins(0, 8, 0, 4)
    layout.setSpacing(10)

    lbl = QtWidgets.QLabel(text.upper(), parent=container)
    lbl.setObjectName("SectionTitle")

    line = QtWidgets.QFrame(parent=container)
    line.setObjectName("Divider")
    line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    sp = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    line.setSizePolicy(sp)

    layout.addWidget(lbl)
    layout.addWidget(line)
    return container


class Ui_Productos(object):
    def setupUi(self, Productos):
        Productos.setObjectName("Productos")
        Productos.setStyleSheet(_STYLESHEET)

        # ── Contenedor de vistas ──────────────────────────────────────────────
        root = QtWidgets.QVBoxLayout(Productos)
        root.setContentsMargins(0, 0, 0, 0)

        self.Contenido = QtWidgets.QStackedWidget(parent=Productos)
        self.Contenido.setObjectName("Contenido")
        root.addWidget(self.Contenido)

        # ═══════════════════════ Listado de productos ═══════════════════════
        self.PanelListado = QtWidgets.QWidget(parent=self.Contenido)
        listado = QtWidgets.QVBoxLayout(self.PanelListado)
        listado.setContentsMargins(24, 20, 24, 20)
        listado.setSpacing(16)

        header_row = QtWidgets.QHBoxLayout()
        header_row.setSpacing(10)

        title_col = QtWidgets.QVBoxLayout()
        title_col.setSpacing(2)
        self.LabelVentasA = _make_label(self.PanelListado, "Productos", "PageTitle")
        subtitle = _make_label(self.PanelListado, "Gestión de inventario · Distri Magik", "PageSubtitle")
        title_col.addWidget(self.LabelVentasA)
        title_col.addWidget(subtitle)

        header_row.addLayout(title_col)
        header_row.addStretch()

        self.BtnRegistrarProducto = QtWidgets.QPushButton("  Registrar producto", parent=self.PanelListado)
        self.BtnRegistrarProducto.setObjectName("BtnPrimary")
        self.BtnRegistrarProducto.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnRegistrarProducto.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        header_row.addWidget(self.BtnRegistrarProducto)

        self.BtnEliminar = QtWidgets.QPushButton("  Eliminar seleccionados", parent=self.PanelListado)
        self.BtnEliminar.setObjectName("BtnDanger")
        self.BtnEliminar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        trash_icon = qta.icon("fa5s.trash-alt", color="#FFFFFF")
        self.BtnEliminar.setIcon(trash_icon)
        header_row.addWidget(self.BtnEliminar)

        listado.addLayout(header_row)

        # ── Barra de búsqueda ────────────────────────────────────────────────
        search_container = QtWidgets.QWidget(parent=self.PanelListado)
        search_container.setStyleSheet("background: transparent;")
        search_row = QtWidgets.QHBoxLayout(search_container)
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(12)

        # Buscador con icono incrustado usando QHBoxLayout
        search_frame = QtWidgets.QFrame(parent=search_container)
        search_frame.setObjectName("Card")
        search_frame.setFixedHeight(44)
        sf_layout = QtWidgets.QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(12, 0, 12, 0)
        sf_layout.setSpacing(8)

        search_icon_lbl = QtWidgets.QLabel(parent=search_frame)
        search_icon_lbl.setPixmap(qta.icon("fa5s.search", color=_MUTED).pixmap(14, 14))
        search_icon_lbl.setFixedSize(16, 16)

        self.InputBuscador = QtWidgets.QLineEdit(parent=search_frame)
        self.InputBuscador.setObjectName("Buscador")
        self.InputBuscador.setPlaceholderText("Buscar por código, nombre, marca o categoría...")
        self.InputBuscador.setStyleSheet(
            f"border: none; background: transparent; font-size: 13px; color: {_TEXT}; "
            f"font-family: 'Segoe UI';"
        )

        sf_layout.addWidget(search_icon_lbl)
        sf_layout.addWidget(self.InputBuscador)
        search_frame.setStyleSheet(
            f"QFrame#Card {{ background: {_CARD_BG}; border: 1.5px solid {_BORDER}; "
            f"border-radius: 10px; }}"
            f"QFrame#Card:focus-within {{ border-color: {_BORDER_FOCUS}; }}"
        )

        # Label de total
        total_frame = QtWidgets.QFrame(parent=search_container)
        total_frame.setObjectName("Card")
        total_frame.setFixedHeight(44)
        tf_layout = QtWidgets.QHBoxLayout(total_frame)
        tf_layout.setContentsMargins(16, 0, 16, 0)
        tf_layout.setSpacing(8)

        total_text_lbl = _make_label(total_frame, "TOTAL CP", "LabelTotalText")
        self.LabelTotalCp = _make_label(total_frame, "$ 0.00", "LabelTotal")

        tf_layout.addWidget(total_text_lbl)
        tf_layout.addWidget(self.LabelTotalCp)

        search_row.addWidget(search_frame, stretch=3)
        search_row.addStretch()
        search_row.addWidget(total_frame)
        listado.addWidget(search_container)

        # ── Tabla de productos ───────────────────────────────────────────────
        self.TablaProductos = QtWidgets.QTableWidget(parent=self.PanelListado)
        self.TablaProductos.setObjectName("TablaProductos")
        self.TablaProductos.verticalHeader().setVisible(False)
        self.TablaProductos.setShowGrid(True)
        self.TablaProductos.setAlternatingRowColors(False)

        headers = [
            "Código", "Nombre", "Marca", "Categoría", "Stock", "C.Min",
            "P.Costo", "PV-1", "PV-2", "PV-3", "PV-4",
            "G-1", "G-2", "G-3", "G-4", "Estado",
        ]
        self.TablaProductos.setColumnCount(len(headers))
        self.TablaProductos.setRowCount(0)
        for i, h in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(h.upper())
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TablaProductos.setHorizontalHeaderItem(i, item)

        # Ajuste de columnas
        self.TablaProductos.horizontalHeader().setStretchLastSection(True)
        self.TablaProductos.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        listado.addWidget(self.TablaProductos, stretch=1)
        self.Contenido.addWidget(self.PanelListado)

        # ══════════════════════ Formulario de producto ══════════════════════
        self.PanelFormulario = QtWidgets.QWidget(parent=self.Contenido)
        formulario = QtWidgets.QVBoxLayout(self.PanelFormulario)
        formulario.setContentsMargins(24, 20, 24, 20)
        formulario.setSpacing(16)

        form_header = QtWidgets.QHBoxLayout()
        form_header.setSpacing(10)

        self.BtnVolver = QtWidgets.QPushButton("  Volver", parent=self.PanelFormulario)
        self.BtnVolver.setObjectName("BtnSecondary")
        self.BtnVolver.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnVolver.setIcon(qta.icon("fa5s.arrow-left", color=_PRIMARY))
        form_header.addWidget(self.BtnVolver)

        form_title_col = QtWidgets.QVBoxLayout()
        form_title_col.setSpacing(2)
        self.LabelTituloFormulario = _make_label(self.PanelFormulario, "Registrar producto", "PageTitle")
        form_subtitle = _make_label(
            self.PanelFormulario,
            "Completa la información del producto para guardarlo en el inventario.",
            "PageSubtitle",
        )
        form_title_col.addWidget(self.LabelTituloFormulario)
        form_title_col.addWidget(form_subtitle)
        form_header.addLayout(form_title_col)
        form_header.addStretch()

        self.BadgeModo = _make_label(self.PanelFormulario, "● NUEVO PRODUCTO", "BadgeNuevo")
        self.BadgeModo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        form_header.addWidget(self.BadgeModo)
        formulario.addLayout(form_header)

        self.FormularioScroll = QtWidgets.QScrollArea(parent=self.PanelFormulario)
        self.FormularioScroll.setObjectName("FormularioScroll")
        self.FormularioScroll.setWidgetResizable(True)
        self.FormularioScroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.FormularioScroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        form_content = QtWidgets.QWidget(parent=self.FormularioScroll)
        form_content.setObjectName("FormularioContenido")
        content_layout = QtWidgets.QVBoxLayout(form_content)
        content_layout.setContentsMargins(0, 0, 8, 0)
        content_layout.setSpacing(0)

        self.Card = QtWidgets.QFrame(parent=form_content)
        self.Card.setObjectName("Card")
        card_layout = QtWidgets.QVBoxLayout(self.Card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(8)

        # ·· Sección 1: Información Básica ····································
        card_layout.addWidget(_section_header(self.Card, "Información Básica"))
        grid1 = QtWidgets.QGridLayout()
        grid1.setSpacing(10)
        grid1.setColumnStretch(0, 1)
        grid1.setColumnStretch(1, 2)
        grid1.setColumnStretch(2, 1)
        grid1.setColumnStretch(3, 1)

        self.InputCodigo = _make_input(self.Card, "InputCodigo", "Ej: 1000")
        self.InputNombre = _make_input(self.Card, "InputNombre", "Ej: Esmalte Rosa Pastel")
        self.InputMarca = _make_input(self.Card, "InputMarca", "Ej: Predeterminado")
        self.InputCategoria = _make_input(self.Card, "InputCategoria", "Ej: Predeterminado")

        for col, (lbl, w) in enumerate([
            ("Código", self.InputCodigo),
            ("Nombre", self.InputNombre),
            ("Marca", self.InputMarca),
            ("Categoría", self.InputCategoria),
        ]):
            grid1.addWidget(_make_label(self.Card, lbl), 0, col)
            grid1.addWidget(w, 1, col)
        card_layout.addLayout(grid1)

        # ·· Sección 2: Stock ·················································
        card_layout.addWidget(_section_header(self.Card, "Stock"))
        grid2 = QtWidgets.QGridLayout()
        grid2.setSpacing(10)

        self.InputCantidad = _make_input(self.Card, "InputCantidad", "Ej: 10")
        self.InputCantidadMin = _make_input(self.Card, "InputCantidadMin", "Ej: 3")
        self.InputPrecioCompra = _make_input(self.Card, "InputPrecioCompra", "Ej: 2500")

        self.InputEstado = QtWidgets.QComboBox(parent=self.Card)
        self.InputEstado.setObjectName("InputEstado")
        self.InputEstado.addItems(["Activo", "Inactivo"])

        for col, (lbl, w) in enumerate([
            ("Stock Actual", self.InputCantidad),
            ("Stock Mínimo", self.InputCantidadMin),
            ("Precio Costo", self.InputPrecioCompra),
            ("Estado", self.InputEstado),
        ]):
            grid2.addWidget(_make_label(self.Card, lbl), 0, col)
            grid2.addWidget(w, 1, col)
        card_layout.addLayout(grid2)

        # ·· Sección 3: Precios de Venta ······································
        card_layout.addWidget(_section_header(self.Card, "Precios de Venta"))
        grid3 = QtWidgets.QGridLayout()
        grid3.setSpacing(10)

        self.InputPrecioVenta1 = _make_input(self.Card, "InputPrecioVenta1", "PV-1 (50% margen)")
        self.InputPrecioVenta2 = _make_input(self.Card, "InputPrecioVenta2", "PV-2 (35% margen)")
        self.InputPrecioVenta3 = _make_input(self.Card, "InputPrecioVenta3", "PV-3 opcional")
        self.InputPrecioVenta4 = _make_input(self.Card, "InputPrecioVenta4", "PV-4 opcional")

        for col, (lbl, w) in enumerate([
            ("Precio Venta 1", self.InputPrecioVenta1),
            ("Precio Venta 2", self.InputPrecioVenta2),
            ("Precio Venta 3", self.InputPrecioVenta3),
            ("Precio Venta 4", self.InputPrecioVenta4),
        ]):
            grid3.addWidget(_make_label(self.Card, lbl), 0, col)
            grid3.addWidget(w, 1, col)
        card_layout.addLayout(grid3)

        # ·· Sección 4: Ganancias (read-only) ··································
        card_layout.addWidget(_section_header(self.Card, "Ganancias Calculadas"))
        grid4 = QtWidgets.QGridLayout()
        grid4.setSpacing(10)

        self.InputGanancia1 = _make_input(self.Card, "InputGanancia1", "Auto", read_only=True)
        self.InputGanancia2 = _make_input(self.Card, "InputGanancia2", "Auto", read_only=True)
        self.InputGanancia3 = _make_input(self.Card, "InputGanancia3", "Auto", read_only=True)
        self.InputGanancia4 = _make_input(self.Card, "InputGanancia4", "Auto", read_only=True)

        for col, (lbl, w) in enumerate([
            ("Ganancia PV-1", self.InputGanancia1),
            ("Ganancia PV-2", self.InputGanancia2),
            ("Ganancia PV-3", self.InputGanancia3),
            ("Ganancia PV-4", self.InputGanancia4),
        ]):
            grid4.addWidget(_make_label(self.Card, lbl), 0, col)
            grid4.addWidget(w, 1, col)
        card_layout.addLayout(grid4)

        card_layout.addSpacing(8)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.BtnLimpiar = QtWidgets.QPushButton("  Cancelar", parent=self.Card)
        self.BtnLimpiar.setObjectName("BtnSecondary")
        self.BtnLimpiar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnLimpiar.setIcon(qta.icon("fa5s.times", color=_PRIMARY))

        self.BtnActualizar = QtWidgets.QPushButton("  Actualizar Producto", parent=self.Card)
        self.BtnActualizar.setObjectName("BtnActualizar")
        self.BtnActualizar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnActualizar.setIcon(qta.icon("fa5s.sync-alt", color="#FFFFFF"))
        self.BtnActualizar.setVisible(False)

        self.BtnIngresarProducto = QtWidgets.QPushButton("  Guardar Producto", parent=self.Card)
        self.BtnIngresarProducto.setObjectName("BtnPrimary")
        self.BtnIngresarProducto.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnIngresarProducto.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))

        btn_row.addWidget(self.BtnLimpiar)
        btn_row.addWidget(self.BtnActualizar)
        btn_row.addWidget(self.BtnIngresarProducto)
        card_layout.addLayout(btn_row)

        content_layout.addWidget(self.Card)
        content_layout.addStretch()
        self.FormularioScroll.setWidget(form_content)
        formulario.addWidget(self.FormularioScroll, stretch=1)
        self.Contenido.addWidget(self.PanelFormulario)
        self.Contenido.setCurrentWidget(self.PanelListado)

        QtCore.QMetaObject.connectSlotsByName(Productos)
