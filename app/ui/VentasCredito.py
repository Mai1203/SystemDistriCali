from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

_PRIMARY = "#862D6D"
_PRIMARY_HOVER = "#6E2259"
_BG = "#F5F0F4"
_CARD_BG = "#FFFFFF"
_TEXT = "#201A24"
_MUTED = "#7B737F"
_DIVIDER = "#E2DAE1"
_DANGER = "#F44336"
_PINK_BG = "#FDF0F6"

_INPUT_QSS = f"""
    QLineEdit, QSpinBox, QComboBox, QTextEdit {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {_TEXT};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
        border: 1.5px solid {_PRIMARY};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: 1px solid {_DIVIDER};
    }}
    QComboBox QAbstractItemView {{
        background-color: {_CARD_BG};
        border: 1px solid {_DIVIDER};
        selection-background-color: {_PINK_BG};
        selection-color: {_PRIMARY};
        border-radius: 4px;
        padding: 4px;
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 28px;
        padding-left: 8px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {_PINK_BG};
        color: {_PRIMARY};
    }}
"""

_LABEL_QSS = f"font-size: 12px; color: {_TEXT}; font-weight: 500; font-family: 'Segoe UI';"

class Ui_VentasCredito(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet(f"background-color: {_BG};")

        self.rootLayout = QtWidgets.QVBoxLayout(Form)
        self.rootLayout.setContentsMargins(24, 24, 24, 24)
        self.rootLayout.setSpacing(16)

        # ── HEADER ──
        self.headerWidget = QtWidgets.QWidget(Form)
        headerLayout = QtWidgets.QHBoxLayout(self.headerWidget)
        headerLayout.setContentsMargins(0,0,0,0)
        headerLayout.addStretch()
        
        # Tools (Notifications, etc)
        self.btnNotif = QtWidgets.QToolButton(self.headerWidget)
        self.btnNotif.setIcon(qta.icon('fa5s.bell', color=_MUTED))
        self.btnNotif.setStyleSheet("border: none; background: transparent;")
        headerLayout.addWidget(self.btnNotif)

        self.rootLayout.addWidget(self.headerWidget)

        # ── TITLE ──
        titleLayout = QtWidgets.QHBoxLayout()
        
        titleTextLayout = QtWidgets.QVBoxLayout()
        titleTextLayout.setSpacing(4)
        
        self.LabelVentasA = QtWidgets.QLabel("Ventas a Crédito", Form)
        self.LabelVentasA.setObjectName("LabelVentasA")
        self.LabelVentasA.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {_TEXT};")
        titleTextLayout.addWidget(self.LabelVentasA)
        
        self.lblSubtitle = QtWidgets.QLabel("Registra los productos para ventas a crédito", Form)
        self.lblSubtitle.setStyleSheet(f"font-size: 13px; color: {_MUTED};")
        titleTextLayout.addWidget(self.lblSubtitle)
        
        titleLayout.addLayout(titleTextLayout)
        titleLayout.addStretch()
        self.rootLayout.addLayout(titleLayout)

        # ── PRODUCT INPUT CARD ──
        self.inputCard = QtWidgets.QWidget(Form)
        self.inputCard.setStyleSheet(f"QWidget#inputCard {{ background-color: {_CARD_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.inputCard.setObjectName("inputCard")
        inputLayout = QtWidgets.QGridLayout(self.inputCard)
        inputLayout.setContentsMargins(20, 20, 20, 20)
        inputLayout.setSpacing(12)

        # Labels Row 0
        inputLayout.addWidget(self._mk_lbl("Código"), 0, 0)
        inputLayout.addWidget(self._mk_lbl("Nombre del Producto"), 0, 1)
        inputLayout.addWidget(self._mk_lbl("Marca"), 0, 2)
        inputLayout.addWidget(self._mk_lbl("Cantidad"), 0, 3)
        inputLayout.addWidget(self._mk_lbl("Precio"), 0, 4)
        inputLayout.addWidget(self._mk_lbl("Tipo Precio"), 0, 5)

        # Inputs Row 1
        self.InputCodigo = QtWidgets.QLineEdit(self.inputCard)
        self.InputCodigo.setObjectName("InputCodigo")
        self.InputCodigo.setMinimumHeight(40)
        self.InputCodigo.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputCodigo, 1, 0)

        self.InputNombre = QtWidgets.QLineEdit(self.inputCard)
        self.InputNombre.setObjectName("InputNombre")
        self.InputNombre.setMinimumHeight(40)
        self.InputNombre.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputNombre, 1, 1)

        self.InputMarca = QtWidgets.QLineEdit(self.inputCard)
        self.InputMarca.setObjectName("InputMarca")
        self.InputMarca.setMinimumHeight(40)
        self.InputMarca.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputMarca, 1, 2)

        self.InputCantidad = QtWidgets.QLineEdit(self.inputCard)
        self.InputCantidad.setObjectName("InputCantidad")
        self.InputCantidad.setMinimumHeight(40)
        self.InputCantidad.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputCantidad, 1, 3)

        self.InputPrecioUnitario = QtWidgets.QLineEdit(self.inputCard)
        self.InputPrecioUnitario.setObjectName("InputPrecioUnitario")
        self.InputPrecioUnitario.setMinimumHeight(40)
        self.InputPrecioUnitario.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputPrecioUnitario, 1, 4)
        
        self.comboBoxPrecio = QtWidgets.QComboBox(self.inputCard)
        self.comboBoxPrecio.setObjectName("comboBoxPrecio")
        self.comboBoxPrecio.setMinimumHeight(40)
        self.comboBoxPrecio.setStyleSheet(_INPUT_QSS)
        self.comboBoxPrecio.addItems(["PV-01", "PV-02", "PV-03", "PV-04"])
        inputLayout.addWidget(self.comboBoxPrecio, 1, 5)

        self.BtnAgregar = QtWidgets.QPushButton(" Agregar Producto", self.inputCard)
        self.BtnAgregar.setIcon(qta.icon('fa5s.plus', color='white'))
        self.BtnAgregar.setMinimumHeight(40)
        self.BtnAgregar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnAgregar.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        inputLayout.addWidget(self.BtnAgregar, 1, 6)

        self.BtnEliminar = QtWidgets.QPushButton(" Eliminar Seleccionado", self.inputCard)
        self.BtnEliminar.setObjectName("BtnEliminar")
        self.BtnEliminar.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.BtnEliminar.setMinimumHeight(40)
        self.BtnEliminar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnEliminar.setStyleSheet(f"background-color: {_DANGER}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        # Posicionarlo en una nueva fila, alineado a la derecha
        inputLayout.addWidget(self.BtnEliminar, 2, 6, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        self.rootLayout.addWidget(self.inputCard)

        # ── TABLE CARD ──
        self.tableCard = QtWidgets.QWidget(Form)
        self.tableCard.setStyleSheet(f"QWidget#tableCard {{ background-color: {_CARD_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.tableCard.setObjectName("tableCard")
        tableLayout = QtWidgets.QVBoxLayout(self.tableCard)
        
        self.TablaVentasCredito = QtWidgets.QTableWidget(self.tableCard)
        self.TablaVentasCredito.setObjectName("TablaVentasCredito")
        self.TablaVentasCredito.setColumnCount(7)
        self.TablaVentasCredito.setHorizontalHeaderLabels(["Código", "Producto", "Marca", "Categoría", "Cantidad", "Precio", "Total"])
        self.TablaVentasCredito.horizontalHeader().setStretchLastSection(True)
        self.TablaVentasCredito.verticalHeader().setVisible(False)
        self.TablaVentasCredito.setShowGrid(False)
        self.TablaVentasCredito.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.TablaVentasCredito.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaVentasCredito.setStyleSheet(f"QTableWidget {{ border: none; background-color: {_CARD_BG}; }} QHeaderView::section {{ background-color: {_CARD_BG}; font-weight: bold; border: none; border-bottom: 1px solid {_DIVIDER}; padding: 8px; }} QTableWidget::item:selected {{ background-color: {_PINK_BG}; color: {_TEXT}; }}")
        tableLayout.addWidget(self.TablaVentasCredito)

        self.rootLayout.addWidget(self.tableCard)

        # ── BOTTOM CARDS ──
        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.setSpacing(16)

        # CLIENTE CARD
        self.clienteCard = QtWidgets.QWidget(Form)
        self.clienteCard.setStyleSheet(f"QWidget#clienteCard {{ background-color: {_CARD_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.clienteCard.setObjectName("clienteCard")
        clienteLayout = QtWidgets.QVBoxLayout(self.clienteCard)
        clienteLayout.setContentsMargins(16, 16, 16, 16)
        clienteLayout.setSpacing(12)
        
        titleCliLayout = QtWidgets.QHBoxLayout()
        titleCliLayout.setContentsMargins(0, 0, 0, 0)
        titleCliLayout.setSpacing(8)
        titleCliLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        lblIconCli = QtWidgets.QLabel()
        lblIconCli.setPixmap(qta.icon('fa5s.user', color=_PRIMARY).pixmap(18, 18))
        lblIconCli.setFixedSize(18, 18)
        lblIconCli.setStyleSheet("background: transparent; border: none;")
        
        lblTitleCli = QtWidgets.QLabel("Datos del Cliente")
        lblTitleCli.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_PRIMARY}; border: none;")
        
        titleCliLayout.addWidget(lblIconCli)
        titleCliLayout.addWidget(lblTitleCli)
        titleCliLayout.addStretch()
        clienteLayout.addLayout(titleCliLayout)
        
        gridCli = QtWidgets.QGridLayout()
        gridCli.setContentsMargins(0, 0, 0, 0)
        gridCli.setSpacing(12)
        gridCli.addWidget(self._mk_lbl("Cédula de Ciudadanía"), 0, 0)
        gridCli.addWidget(self._mk_lbl("Nombres"), 0, 1)
        gridCli.addWidget(self._mk_lbl("Apellidos"), 0, 2)
        
        self.InputCedula = QtWidgets.QLineEdit(self.clienteCard)
        self.InputCedula.setObjectName("InputCedula")
        self.InputCedula.setMinimumHeight(40)
        self.InputCedula.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputCedula, 1, 0)
        
        self.InputNombreCli = QtWidgets.QLineEdit(self.clienteCard)
        self.InputNombreCli.setObjectName("InputNombreCli")
        self.InputNombreCli.setMinimumHeight(40)
        self.InputNombreCli.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputNombreCli, 1, 1)

        self.InputApellidoCli = QtWidgets.QLineEdit(self.clienteCard)
        self.InputApellidoCli.setObjectName("InputApellidoCli")
        self.InputApellidoCli.setMinimumHeight(40)
        self.InputApellidoCli.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputApellidoCli, 1, 2)
        
        gridCli.addWidget(self._mk_lbl("Teléfono"), 2, 0)
        gridCli.addWidget(self._mk_lbl("Dirección"), 2, 1)
        gridCli.addWidget(self._mk_lbl("Límite de Pago"), 2, 2)
        
        self.InputTelefonoCli = QtWidgets.QLineEdit(self.clienteCard)
        self.InputTelefonoCli.setObjectName("InputTelefonoCli")
        self.InputTelefonoCli.setMinimumHeight(40)
        self.InputTelefonoCli.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputTelefonoCli, 3, 0)
        
        self.InputDireccion = QtWidgets.QLineEdit(self.clienteCard)
        self.InputDireccion.setObjectName("InputDireccion")
        self.InputDireccion.setMinimumHeight(40)
        self.InputDireccion.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputDireccion, 3, 1)
        
        self.LimitePagoBox = QtWidgets.QComboBox(self.clienteCard)
        self.LimitePagoBox.setObjectName("LimitePagoBox")
        self.LimitePagoBox.setMinimumHeight(40)
        self.LimitePagoBox.setStyleSheet(_INPUT_QSS)
        self.LimitePagoBox.addItems(["15 días", "30 días", "45 días", "60 días"])
        gridCli.addWidget(self.LimitePagoBox, 3, 2)
        
        clienteLayout.addLayout(gridCli)
        bottomLayout.addWidget(self.clienteCard)

        # RESUMEN CARD
        self.resumenCard = QtWidgets.QWidget(Form)
        self.resumenCard.setStyleSheet(f"QWidget#resumenCard {{ background-color: {_PINK_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.resumenCard.setObjectName("resumenCard")
        resumenLayout = QtWidgets.QVBoxLayout(self.resumenCard)
        
        titleResumenLayout = QtWidgets.QHBoxLayout()
        titleResumenLayout.setContentsMargins(0, 0, 0, 0)
        titleResumenLayout.setSpacing(8)
        titleResumenLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        lblIconResumen = QtWidgets.QLabel()
        lblIconResumen.setPixmap(qta.icon('fa5s.chart-bar', color=_PRIMARY).pixmap(18, 18))
        lblIconResumen.setFixedSize(18, 18)
        lblIconResumen.setStyleSheet("background: transparent; border: none;")
        
        lblTitleResumen = QtWidgets.QLabel("Resumen de Venta")
        lblTitleResumen.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_PRIMARY}; border: none;")
        
        titleResumenLayout.addWidget(lblIconResumen)
        titleResumenLayout.addWidget(lblTitleResumen)
        titleResumenLayout.addStretch()
        resumenLayout.addLayout(titleResumenLayout)
        
        resumenLayout.addSpacing(16)
        
        # ── Caja destacada: Subtotal Ítems (Protagonista) ──
        self.subtotalBox = QtWidgets.QFrame(self.resumenCard)
        self.subtotalBox.setStyleSheet(f"""
            QFrame {{
                background-color: {_CARD_BG};
                border: 1.5px solid {_PRIMARY};
                border-radius: 8px;
                padding: 6px 10px;
            }}
        """)
        subtotalBoxLayout = QtWidgets.QHBoxLayout(self.subtotalBox)
        subtotalBoxLayout.setContentsMargins(4, 4, 4, 4)
        
        lblSubtotalTitleLayout = QtWidgets.QVBoxLayout()
        lblSubtotalTitleLayout.setSpacing(2)
        lblSubtotalHeader = QtWidgets.QLabel("Subtotal Ítems")
        lblSubtotalHeader.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {_TEXT};")
        lblSubtotalSub = QtWidgets.QLabel("(Valor productos)")
        lblSubtotalSub.setStyleSheet(f"font-size: 10px; color: {_MUTED};")
        lblSubtotalTitleLayout.addWidget(lblSubtotalHeader)
        lblSubtotalTitleLayout.addWidget(lblSubtotalSub)
        subtotalBoxLayout.addLayout(lblSubtotalTitleLayout)
        
        subtotalBoxLayout.addStretch()
        self.LabelSubtotal = QtWidgets.QLabel("$ 0")
        self.LabelSubtotal.setObjectName("LabelSubtotal")
        self.LabelSubtotal.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {_PRIMARY};")
        self.LabelSubtotal.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        subtotalBoxLayout.addWidget(self.LabelSubtotal)
        resumenLayout.addWidget(self.subtotalBox)
        
        # ── Total General ──
        self.lblTotalTitle = QtWidgets.QLabel("Total")
        self.lblTotalTitle.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_TEXT};")
        self.LabelTotal = QtWidgets.QLabel("$ 0")
        self.LabelTotal.setObjectName("LabelTotal")
        self.LabelTotal.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {_TEXT};")
        self.LabelTotal.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        totLayout = QtWidgets.QHBoxLayout()
        totLayout.addWidget(self.lblTotalTitle)
        totLayout.addWidget(self.LabelTotal)
        resumenLayout.addLayout(totLayout)
        
        # ── Nota informativa sobre el pago ──
        self.lblNotaPago = QtWidgets.QLabel(
            "ℹ️ El valor a cobrar corresponde al Subtotal de Ítems.\n(El domicilio no se registra en la base de datos).",
            self.resumenCard
        )
        self.lblNotaPago.setWordWrap(True)
        self.lblNotaPago.setStyleSheet(
            f"background-color: #FFFFFF; color: {_MUTED}; font-size: 10px; font-style: italic; "
            f"border: 1px dashed {_DIVIDER}; border-radius: 6px; padding: 6px 8px;"
        )
        resumenLayout.addWidget(self.lblNotaPago)
        
        resumenLayout.addStretch()

        self.BtnGenerarVentaCredito = QtWidgets.QPushButton(" Generar Venta a Crédito", self.resumenCard)
        self.BtnGenerarVentaCredito.setObjectName("BtnGenerarVentaCredito")
        self.BtnGenerarVentaCredito.setIcon(qta.icon('fa5s.file-invoice-dollar', color='white'))
        self.BtnGenerarVentaCredito.setIconSize(QtCore.QSize(18, 18))
        self.BtnGenerarVentaCredito.setMinimumHeight(48)
        self.BtnGenerarVentaCredito.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-size: 16px; font-weight: 600; text-align: center;")
        resumenLayout.addWidget(self.BtnGenerarVentaCredito)

        bottomLayout.addWidget(self.resumenCard)
        
        # Proportions for bottom cards
        bottomLayout.setStretch(0, 7)
        bottomLayout.setStretch(1, 3)

        self.rootLayout.addLayout(bottomLayout)

    def _mk_lbl(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(_LABEL_QSS)
        return lbl

    def _add_row(self, parent_layout, label_text, value_widget):
        lyt = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label_text)
        lbl.setStyleSheet(f"color: {_MUTED}; font-size: 13px;")
        lyt.addWidget(lbl)
        lyt.addWidget(value_widget)
        parent_layout.addLayout(lyt)
