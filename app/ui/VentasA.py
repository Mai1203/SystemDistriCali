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
"""

_LABEL_QSS = f"font-size: 12px; color: {_TEXT}; font-weight: 500; font-family: 'Segoe UI';"

class Ui_VentasA(object):
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
        
        self.LabelVentasA = QtWidgets.QLabel("Ventas", Form)
        self.LabelVentasA.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {_TEXT};")
        titleTextLayout.addWidget(self.LabelVentasA)
        
        self.lblSubtitle = QtWidgets.QLabel("Registra los productos de la venta", Form)
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
        inputLayout.addWidget(self._mk_lbl("Precio por Mayor"), 0, 4)

        # Inputs Row 1
        self.InputCodigo = QtWidgets.QLineEdit(self.inputCard)
        self.InputCodigo.setMinimumHeight(40)
        self.InputCodigo.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputCodigo, 1, 0)

        self.InputNombre = QtWidgets.QLineEdit(self.inputCard)
        self.InputNombre.setMinimumHeight(40)
        self.InputNombre.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputNombre, 1, 1)

        self.InputMarca = QtWidgets.QLineEdit(self.inputCard) # New field visually
        self.InputMarca.setMinimumHeight(40)
        self.InputMarca.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputMarca, 1, 2)

        self.InputCantidad = QtWidgets.QLineEdit(self.inputCard)
        self.InputCantidad.setMinimumHeight(40)
        self.InputCantidad.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputCantidad, 1, 3)

        self.InputPrecioUnitario = QtWidgets.QLineEdit(self.inputCard)
        self.InputPrecioUnitario.setMinimumHeight(40)
        self.InputPrecioUnitario.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputPrecioUnitario, 1, 4)

        self.BtnAgregar = QtWidgets.QPushButton(" Agregar Producto", self.inputCard)
        self.BtnAgregar.setIcon(qta.icon('fa5s.plus', color='white'))
        self.BtnAgregar.setMinimumHeight(40)
        self.BtnAgregar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnAgregar.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        inputLayout.addWidget(self.BtnAgregar, 1, 5)

        # Row 2
        inputLayout.addWidget(self._mk_lbl("Valor Domicilio"), 2, 0)
        
        self.InputDomicilio = QtWidgets.QLineEdit(self.inputCard)
        self.InputDomicilio.setMinimumHeight(40)
        self.InputDomicilio.setStyleSheet(_INPUT_QSS)
        inputLayout.addWidget(self.InputDomicilio, 3, 0)

        self.BtnEliminar = QtWidgets.QPushButton(" Eliminar Seleccionado", self.inputCard)
        self.BtnEliminar.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.BtnEliminar.setMinimumHeight(40)
        self.BtnEliminar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnEliminar.setStyleSheet(f"background-color: {_DANGER}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        inputLayout.addWidget(self.BtnEliminar, 3, 5, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        self.rootLayout.addWidget(self.inputCard)

        # ── TABLE CARD ──
        self.tableCard = QtWidgets.QWidget(Form)
        self.tableCard.setStyleSheet(f"QWidget#tableCard {{ background-color: {_CARD_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.tableCard.setObjectName("tableCard")
        tableLayout = QtWidgets.QVBoxLayout(self.tableCard)
        
        self.tableWidget = QtWidgets.QTableWidget(self.tableCard)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(["Código", "Producto", "Marca", "Categoría", "Cantidad", "PAM", "Total"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setStyleSheet(f"QTableWidget {{ border: none; background-color: {_CARD_BG}; }} QHeaderView::section {{ background-color: {_CARD_BG}; font-weight: bold; border: none; border-bottom: 1px solid {_DIVIDER}; padding: 8px; }} QTableWidget::item:selected {{ background-color: {_PINK_BG}; color: {_TEXT}; }}")
        tableLayout.addWidget(self.tableWidget)

        # Hidden old buttons to avoid breaking VentasAView.py logic
        self.BtnFacturaA = QtWidgets.QPushButton(Form)
        self.BtnFacturaB = QtWidgets.QPushButton(Form)
        self.BtnFacturaA.hide()
        self.BtnFacturaB.hide()

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
        
        lblIconCli = QtWidgets.QLabel()
        lblIconCli.setPixmap(qta.icon('fa5s.user', color=_PRIMARY).pixmap(16, 16))
        lblIconCli.setFixedSize(16, 16)
        
        lblTitleCli = QtWidgets.QLabel("Cliente")
        lblTitleCli.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_PRIMARY};")
        
        titleCliLayout.addWidget(lblIconCli)
        titleCliLayout.addWidget(lblTitleCli)
        titleCliLayout.addStretch()
        clienteLayout.addLayout(titleCliLayout)
        
        gridCli = QtWidgets.QGridLayout()
        gridCli.setContentsMargins(0, 0, 0, 0)
        gridCli.setSpacing(12)
        gridCli.addWidget(self._mk_lbl("Cédula de Ciudadanía"), 0, 0)
        gridCli.addWidget(self._mk_lbl("Nombre y Apellido"), 0, 1)
        
        self.InputCedula = QtWidgets.QLineEdit(self.clienteCard)
        self.InputCedula.setMinimumHeight(40)
        self.InputCedula.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputCedula, 1, 0)
        
        self.InputNombreCli = QtWidgets.QLineEdit(self.clienteCard)
        self.InputNombreCli.setMinimumHeight(40)
        self.InputNombreCli.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputNombreCli, 1, 1)
        
        gridCli.addWidget(self._mk_lbl("Teléfono"), 2, 0)
        gridCli.addWidget(self._mk_lbl("Dirección"), 2, 1)
        
        self.InputTelefonoCli = QtWidgets.QLineEdit(self.clienteCard)
        self.InputTelefonoCli.setMinimumHeight(40)
        self.InputTelefonoCli.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputTelefonoCli, 3, 0)
        
        self.InputDireccion = QtWidgets.QLineEdit(self.clienteCard)
        self.InputDireccion.setMinimumHeight(40)
        self.InputDireccion.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputDireccion, 3, 1)
        
        gridCli.addWidget(self._mk_lbl("Descuento Global"), 4, 0)
        self.InputDescuento = QtWidgets.QLineEdit(self.clienteCard)
        self.InputDescuento.setMinimumHeight(40)
        self.InputDescuento.setStyleSheet(_INPUT_QSS)
        gridCli.addWidget(self.InputDescuento, 5, 0)
        
        self.BtnCrearCliente = QtWidgets.QPushButton(" Registrar Cliente", self.clienteCard)
        self.BtnCrearCliente.setIcon(qta.icon('fa5s.user-plus', color='white'))
        self.BtnCrearCliente.setMinimumHeight(40)
        self.BtnCrearCliente.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnCrearCliente.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-weight: 600; padding: 0 16px; text-align: center;")
        gridCli.addWidget(self.BtnCrearCliente, 5, 1)
        
        clienteLayout.addLayout(gridCli)
        bottomLayout.addWidget(self.clienteCard)

        # PAGO CARD
        self.pagoCard = QtWidgets.QWidget(Form)
        self.pagoCard.setObjectName("pagoCard")
        self.pagoCard.setStyleSheet(f"QWidget#pagoCard {{ background-color: {_CARD_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        pagoLayout = QtWidgets.QVBoxLayout(self.pagoCard)
        pagoLayout.setContentsMargins(20, 20, 20, 20)
        pagoLayout.setSpacing(14)

        titlePagoLayout = QtWidgets.QHBoxLayout()
        lblIconPago = QtWidgets.QLabel()
        lblIconPago.setPixmap(qta.icon("fa5s.credit-card", color=_PRIMARY).pixmap(16, 16))
        lblIconPago.setStyleSheet("border: none;")
        lblTitlePago = QtWidgets.QLabel("M\u00e9todo de Pago")
        lblTitlePago.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_PRIMARY}; border: none;")
        titlePagoLayout.addWidget(lblIconPago)
        titlePagoLayout.addWidget(lblTitlePago)
        titlePagoLayout.addStretch()
        # QComboBox oculto para compatibilidad con VentasAView.py
        self.MetodoPagoBox = QtWidgets.QComboBox(self.pagoCard)
        self.MetodoPagoBox.setObjectName("MetodoPagoBox")
        self.MetodoPagoBox.hide()

        # Pill buttons de m\u00e9todo
        pillWidget = QtWidgets.QWidget(self.pagoCard)
        pillWidget.setStyleSheet("background: transparent; border: none;")
        pillLayout = QtWidgets.QHBoxLayout(pillWidget)
        pillLayout.setContentsMargins(0, 0, 0, 0)
        pillLayout.setSpacing(8)

        self._pill_group = QtWidgets.QButtonGroup(pillWidget)
        self._pill_group.setExclusive(True)
        self._pill_buttons = {}

        for _ico, _lbl in [("fa5s.money-bill-wave", "Efectivo"), ("fa5s.exchange-alt", "Mixto"), ("fa5s.university", "Transferencia")]:
            pb = QtWidgets.QPushButton(f"  {_lbl}", pillWidget)
            pb.setIcon(qta.icon(_ico, color=_TEXT))
            pb.setCheckable(True)
            pb.setStyleSheet(
                f"QPushButton {{ border: 1.5px solid {_DIVIDER}; border-radius: 20px; padding: 8px 16px; "
                f"font-size: 13px; font-weight: 500; background: {_CARD_BG}; color: {_TEXT}; }}"
                f"QPushButton:hover {{ border-color: {_PRIMARY}; color: {_PRIMARY}; background: #FDF0F6; }}"
                f"QPushButton:checked {{ background: {_PRIMARY}; color: white; border-color: {_PRIMARY}; font-weight: 700; }}"
            )
            pb.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self._pill_group.addButton(pb)
            pillLayout.addWidget(pb)
            self._pill_buttons[_lbl] = pb

            def _toggled_fn(checked, b=pb, ico=_ico):
                b.setIcon(qta.icon(ico, color="#FFFFFF" if checked else _TEXT))
            pb.toggled.connect(_toggled_fn)

        pillLayout.addStretch()
        pagoLayout.addWidget(pillWidget)

        # Monto efectivo
        self._lblEfectivo = QtWidgets.QLabel("Monto recibido (permite vuelto si es mayor)")
        self._lblEfectivo.setStyleSheet(f"color: {_MUTED}; font-size: 12px; border: none;")
        pagoLayout.addWidget(self._lblEfectivo)

        self.InputPago = QtWidgets.QLineEdit(self.pagoCard)
        self.InputPago.setMinimumHeight(44)
        self.InputPago.setPlaceholderText("$ 0.00")
        self.InputPago.setStyleSheet(_INPUT_QSS)
        pagoLayout.addWidget(self.InputPago)

        # Monto transferencia (solo en Mixto)
        self._lblTransferencia = QtWidgets.QLabel("Monto en Transferencia")
        self._lblTransferencia.setStyleSheet(f"color: {_MUTED}; font-size: 12px; border: none;")
        self._lblTransferencia.hide()
        pagoLayout.addWidget(self._lblTransferencia)

        self.InputPagoTransferencia = QtWidgets.QLineEdit(self.pagoCard)
        self.InputPagoTransferencia.setMinimumHeight(44)
        self.InputPagoTransferencia.setPlaceholderText("$ 0.00")
        self.InputPagoTransferencia.setStyleSheet(_INPUT_QSS)
        self.InputPagoTransferencia.hide()
        pagoLayout.addWidget(self.InputPagoTransferencia)

        self.lblPagoInfo = QtWidgets.QLabel("")
        self.lblPagoInfo.setStyleSheet(f"color: {_MUTED}; font-size: 11px; border: none; font-style: italic;")
        pagoLayout.addWidget(self.lblPagoInfo)
        pagoLayout.addStretch()

        bottomLayout.addWidget(self.pagoCard)

        # RESUMEN CARD
        self.resumenCard = QtWidgets.QWidget(Form)
        self.resumenCard.setStyleSheet(f"QWidget#resumenCard {{ background-color: {_PINK_BG}; border-radius: 12px; border: 1px solid {_DIVIDER}; }}")
        self.resumenCard.setObjectName("resumenCard")
        resumenLayout = QtWidgets.QVBoxLayout(self.resumenCard)
        
        titleResumenLayout = QtWidgets.QHBoxLayout()
        lblIconResumen = QtWidgets.QLabel()
        lblIconResumen.setPixmap(qta.icon('fa5s.chart-bar', color=_PRIMARY).pixmap(16, 16))
        lblTitleResumen = QtWidgets.QLabel("Resumen de Venta")
        lblTitleResumen.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {_PRIMARY};")
        titleResumenLayout.addWidget(lblIconResumen)
        titleResumenLayout.addWidget(lblTitleResumen)
        titleResumenLayout.addStretch()
        resumenLayout.addLayout(titleResumenLayout)
        
        resumenLayout.addSpacing(16)
        
        # We will need standard labels for the view to update if necessary, or just rely on the view logic updating specific labels.
        # Let's define the labels the view might look for, or just general ones.
        self.LabelSubtotal = QtWidgets.QLabel("$ 0")
        self.LabelSubtotal.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self._add_row(resumenLayout, "Subtotal Ítems", self.LabelSubtotal)
        
        self.lblResumenDescuento = QtWidgets.QLabel("- $ 0")
        self.lblResumenDescuento.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.lblResumenDescuento.setStyleSheet("color: red;")
        self._add_row(resumenLayout, "Descuento Global", self.lblResumenDescuento)
        
        self._add_row(resumenLayout, "Subtotal", QtWidgets.QLabel("$ 0", alignment=QtCore.Qt.AlignmentFlag.AlignRight))
        
        self.lblTotalTitle = QtWidgets.QLabel("Total")
        self.lblTotalTitle.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {_TEXT};")
        self.LabelTotal = QtWidgets.QLabel("$ 0")
        self.LabelTotal.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {_PRIMARY};")
        self.LabelTotal.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        totLayout = QtWidgets.QHBoxLayout()
        totLayout.addWidget(self.lblTotalTitle)
        totLayout.addWidget(self.LabelTotal)
        resumenLayout.addLayout(totLayout)
        
        resumenLayout.addStretch()

        self.BtnGenerarVenta = QtWidgets.QPushButton(" Generar Venta", self.resumenCard)
        self.BtnGenerarVenta.setIcon(qta.icon('fa5s.file-invoice-dollar', color='white'))
        self.BtnGenerarVenta.setIconSize(QtCore.QSize(18, 18))
        self.BtnGenerarVenta.setMinimumHeight(48)
        self.BtnGenerarVenta.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnGenerarVenta.setStyleSheet(f"background-color: {_PRIMARY}; color: white; border-radius: 8px; font-size: 16px; font-weight: 600; text-align: center;")
        resumenLayout.addWidget(self.BtnGenerarVenta)

        bottomLayout.addWidget(self.resumenCard)
        
        # Proportions for bottom cards
        bottomLayout.setStretch(0, 3)
        bottomLayout.setStretch(1, 3)
        bottomLayout.setStretch(2, 3)

        self.rootLayout.addLayout(bottomLayout)

        QtCore.QMetaObject.connectSlotsByName(Form)

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
