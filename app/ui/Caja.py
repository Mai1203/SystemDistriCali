from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta

class Ui_Caja(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1430, 997)
        Form.setStyleSheet("background-color: #F5F0F4;") # _BG

        self.main_layout = QtWidgets.QVBoxLayout(Form)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Header Card
        self.header_card = QtWidgets.QFrame(parent=Form)
        self.header_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)
        self.header_layout = QtWidgets.QVBoxLayout(self.header_card)
        self.header_layout.setContentsMargins(20, 20, 20, 20)
        self.header_layout.setSpacing(15)

        self.title_layout = QtWidgets.QHBoxLayout()
        self.LabelCaja = QtWidgets.QLabel("Caja", parent=self.header_card)
        self.LabelCaja.setObjectName("LabelCaja")
        self.LabelCaja.setStyleSheet("font-size: 28px; font-weight: bold; color: #201A24; background-color: transparent;")
        self.title_layout.addWidget(self.LabelCaja)
        
        self.label_9 = QtWidgets.QLabel("Nota: ¡Recuerda abrir la caja antes de generar cualquier venta!", parent=self.header_card)
        self.label_9.setObjectName("label_9")
        self.label_9.setStyleSheet("font-size: 14px; color: #7B737F; font-style: italic; background-color: transparent;")
        self.title_layout.addWidget(self.label_9)
        self.title_layout.addStretch()
        self.header_layout.addLayout(self.title_layout)

        self.controls_layout = QtWidgets.QHBoxLayout()
        
        # Search Box
        self.InputBuscador = QtWidgets.QLineEdit(parent=self.header_card)
        self.InputBuscador.setObjectName("InputBuscador")
        self.InputBuscador.setPlaceholderText("Buscar...")
        self.InputBuscador.setMinimumHeight(45)
        self.InputBuscador.setStyleSheet("""
            QLineEdit {
                background-color: #F5F0F4;
                border: 1px solid #E0DCE0;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 16px;
                color: #201A24;
            }
            QLineEdit:focus {
                border: 1px solid #862D6D;
                background-color: #FFFFFF;
            }
        """)
        search_action = self.InputBuscador.addAction(qta.icon('fa5s.search', color='#7B737F'), QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.controls_layout.addWidget(self.InputBuscador, stretch=1)

        # Monto Caja
        self.InputMontoCaja = QtWidgets.QLineEdit(parent=self.header_card)
        self.InputMontoCaja.setObjectName("InputMontoCaja")
        self.InputMontoCaja.setPlaceholderText("Monto apertura...")
        self.InputMontoCaja.setMinimumHeight(45)
        self.InputMontoCaja.setMaximumWidth(200)
        self.InputMontoCaja.setStyleSheet("""
            QLineEdit {
                background-color: #F5F0F4;
                border: 1px solid #E0DCE0;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 16px;
                color: #201A24;
            }
            QLineEdit:focus {
                border: 1px solid #862D6D;
                background-color: #FFFFFF;
            }
        """)
        self.controls_layout.addWidget(self.InputMontoCaja)

        # Apertura
        self.BtnCajaApertura = QtWidgets.QPushButton("  Abrir Caja", parent=self.header_card)
        self.BtnCajaApertura.setObjectName("BtnCajaApertura")
        self.BtnCajaApertura.setMinimumHeight(45)
        self.BtnCajaApertura.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnCajaApertura.setIcon(qta.icon('fa5s.unlock', color='#FFFFFF'))
        self.BtnCajaApertura.setIconSize(QtCore.QSize(20, 20))
        self.BtnCajaApertura.setStyleSheet("""
            QPushButton {
                background-color: #862D6D;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 5px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6C2458;
            }
        """)
        self.controls_layout.addWidget(self.BtnCajaApertura)

        # Cierre
        self.BtnCajaCierre = QtWidgets.QPushButton("  Cerrar Caja", parent=self.header_card)
        self.BtnCajaCierre.setObjectName("BtnCajaCierre")
        self.BtnCajaCierre.setMinimumHeight(45)
        self.BtnCajaCierre.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnCajaCierre.setIcon(qta.icon('fa5s.lock', color='#FFFFFF'))
        self.BtnCajaCierre.setIconSize(QtCore.QSize(20, 20))
        self.BtnCajaCierre.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 5px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.controls_layout.addWidget(self.BtnCajaCierre)

        self.header_layout.addLayout(self.controls_layout)
        self.main_layout.addWidget(self.header_card)

        # Content Split
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setSpacing(18)

        # Left Column - Historial de cajas
        self.left_column = QtWidgets.QVBoxLayout()
        self.left_column.setContentsMargins(0, 0, 0, 0)

        self.cajas_card = QtWidgets.QFrame(parent=Form)
        self.cajas_card.setObjectName("TablaCard")
        self.cajas_card.setStyleSheet("""
            QFrame#TablaCard {
                background-color: #FFFFFF;
                border: 1px solid #E6DDE4;
                border-radius: 12px;
            }
            QLabel#TituloTabla {
                color: #201A24;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
            QLabel#SubtituloTabla {
                color: #7B737F;
                font-size: 12px;
                background: transparent;
            }
        """)
        cajas_layout = QtWidgets.QVBoxLayout(self.cajas_card)
        cajas_layout.setContentsMargins(16, 14, 16, 16)
        cajas_layout.setSpacing(10)

        cajas_header = QtWidgets.QHBoxLayout()
        cajas_title_col = QtWidgets.QVBoxLayout()
        cajas_title_col.setSpacing(2)
        self.LabelHistorialCajas = QtWidgets.QLabel("Historial de cajas", parent=self.cajas_card)
        self.LabelHistorialCajas.setObjectName("TituloTabla")
        cajas_subtitle = QtWidgets.QLabel("Selecciona una caja para ver sus movimientos.", parent=self.cajas_card)
        cajas_subtitle.setObjectName("SubtituloTabla")
        cajas_title_col.addWidget(self.LabelHistorialCajas)
        cajas_title_col.addWidget(cajas_subtitle)
        cajas_header.addLayout(cajas_title_col)
        cajas_header.addStretch()
        cajas_layout.addLayout(cajas_header)

        self.TablaCaja = QtWidgets.QTableWidget(parent=self.cajas_card)
        self.TablaCaja.setObjectName("TablaCaja")
        self.TablaCaja.setColumnCount(9)
        self.TablaCaja.setHorizontalHeaderLabels([
            "ID", "Usuario", "Base", "Apertura", "Cierre", "Efectivo", "Transfer.", "Total", "Estado"
        ])
        caja_header = self.TablaCaja.horizontalHeader()
        caja_header.setStretchLastSection(False)
        caja_header.setMinimumSectionSize(40)
        caja_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        for column, width in enumerate([42, 86, 100, 120, 120, 84, 90, 90, 100]):
            self.TablaCaja.setColumnWidth(column, width)
        self.TablaCaja.verticalHeader().setVisible(False)
        self.TablaCaja.setAlternatingRowColors(True)
        self.TablaCaja.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaCaja.setShowGrid(False)
        self.TablaCaja.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.TablaCaja.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.TablaCaja.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                color: #201A24;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F5F0F4;
            }
            QTableWidget::item:selected {
                background-color: #F0EAF0;
                color: #862D6D;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #FFFFFF;
                color: #7B737F;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #F5F0F4;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        cajas_layout.addWidget(self.TablaCaja, stretch=1)
        self.left_column.addWidget(self.cajas_card)
        self.content_layout.addLayout(self.left_column, stretch=2)

        # Right Column - Movimientos de Turno & Resumen
        self.right_column = QtWidgets.QVBoxLayout()
        self.right_column.setContentsMargins(0, 0, 0, 0)
        self.right_column.setSpacing(18)

        # Tabla Movimientos
        self.movimientos_card = QtWidgets.QFrame(parent=Form)
        self.movimientos_card.setObjectName("TablaCard")
        self.movimientos_card.setStyleSheet(self.cajas_card.styleSheet())
        movimientos_layout = QtWidgets.QVBoxLayout(self.movimientos_card)
        movimientos_layout.setContentsMargins(16, 14, 16, 16)
        movimientos_layout.setSpacing(10)

        movimientos_header = QtWidgets.QHBoxLayout()
        movimientos_title_col = QtWidgets.QVBoxLayout()
        movimientos_title_col.setSpacing(2)
        self.LabelMovimientos = QtWidgets.QLabel("Movimientos del turno", parent=self.movimientos_card)
        self.LabelMovimientos.setObjectName("TituloTabla")
        movimientos_subtitle = QtWidgets.QLabel("Ingresos y egresos de la caja seleccionada.", parent=self.movimientos_card)
        movimientos_subtitle.setObjectName("SubtituloTabla")
        movimientos_title_col.addWidget(self.LabelMovimientos)
        movimientos_title_col.addWidget(movimientos_subtitle)
        movimientos_header.addLayout(movimientos_title_col)
        movimientos_header.addStretch()
        movimientos_layout.addLayout(movimientos_header)

        self.TablaIngresos = QtWidgets.QTableWidget(parent=self.movimientos_card)
        self.TablaIngresos.setObjectName("TablaIngresos")
        self.TablaIngresos.setColumnCount(3)
        self.TablaIngresos.setHorizontalHeaderLabels([
            "Concepto", "Efectivo", "Transfer."
        ])
        ingresos_header = self.TablaIngresos.horizontalHeader()
        ingresos_header.setStretchLastSection(False)
        ingresos_header.setMinimumSectionSize(60)
        ingresos_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        for column, width in enumerate([160, 105, 135]):
            self.TablaIngresos.setColumnWidth(column, width)
        self.TablaIngresos.verticalHeader().setVisible(False)
        self.TablaIngresos.setAlternatingRowColors(True)
        self.TablaIngresos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaIngresos.setShowGrid(False)
        self.TablaIngresos.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.TablaIngresos.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.TablaIngresos.setStyleSheet(self.TablaCaja.styleSheet())
        movimientos_layout.addWidget(self.TablaIngresos, stretch=1)
        self.right_column.addWidget(self.movimientos_card, stretch=3)

        # Summary Card
        self.summary_card = QtWidgets.QFrame(parent=Form)
        self.summary_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)
        self.summary_layout = QtWidgets.QGridLayout(self.summary_card)
        self.summary_layout.setContentsMargins(20, 20, 20, 20)
        self.summary_layout.setSpacing(15)

        resumen_titulo = QtWidgets.QLabel("Resumen de caja", parent=self.summary_card)
        resumen_titulo.setStyleSheet("font-size: 16px; color: #201A24; font-weight: bold; background-color: transparent;")
        self.summary_layout.addWidget(resumen_titulo, 0, 0, 1, 2)

        label_style = "font-size: 16px; color: #7B737F; font-weight: bold; background-color: transparent;"
        value_style = "font-size: 18px; color: #201A24; font-weight: bold; background-color: #F5F0F4; border-radius: 6px; padding: 8px;"
        
        lbl_efectivo = QtWidgets.QLabel("Efectivo:", parent=self.summary_card)
        lbl_efectivo.setStyleSheet(label_style)
        self.summary_layout.addWidget(lbl_efectivo, 1, 0)
        
        self.OutEfectivo = QtWidgets.QLabel("$ 0.00", parent=self.summary_card)
        self.OutEfectivo.setObjectName("OutEfectivo")
        self.OutEfectivo.setStyleSheet(value_style)
        self.OutEfectivo.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.summary_layout.addWidget(self.OutEfectivo, 1, 1)

        lbl_transf = QtWidgets.QLabel("Transferencia:", parent=self.summary_card)
        lbl_transf.setStyleSheet(label_style)
        self.summary_layout.addWidget(lbl_transf, 2, 0)

        self.OutTransferencia = QtWidgets.QLabel("$ 0.00", parent=self.summary_card)
        self.OutTransferencia.setObjectName("OutTransferencia")
        self.OutTransferencia.setStyleSheet(value_style)
        self.OutTransferencia.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.summary_layout.addWidget(self.OutTransferencia, 2, 1)

        lbl_total = QtWidgets.QLabel("Total:", parent=self.summary_card)
        lbl_total.setStyleSheet("font-size: 18px; color: #862D6D; font-weight: bold; background-color: transparent;")
        self.summary_layout.addWidget(lbl_total, 3, 0)

        self.OutTotal = QtWidgets.QLabel("$ 0.00", parent=self.summary_card)
        self.OutTotal.setObjectName("OutTotal")
        self.OutTotal.setStyleSheet("font-size: 22px; color: #862D6D; font-weight: bold; background-color: #F0EAF0; border-radius: 6px; padding: 8px;")
        self.OutTotal.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.summary_layout.addWidget(self.OutTotal, 3, 1)

        self.BtnCajaImprimir = QtWidgets.QPushButton("  Imprimir", parent=self.summary_card)
        self.BtnCajaImprimir.setObjectName("BtnCajaImprimir")
        self.BtnCajaImprimir.setMinimumHeight(45)
        self.BtnCajaImprimir.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnCajaImprimir.setIcon(qta.icon('fa5s.print', color='#FFFFFF'))
        self.BtnCajaImprimir.setIconSize(QtCore.QSize(20, 20))
        self.BtnCajaImprimir.setStyleSheet("""
            QPushButton {
                background-color: #201A24;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 5px 20px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #382D3F;
            }
        """)
        self.summary_layout.addWidget(self.BtnCajaImprimir, 4, 0, 1, 2)

        self.right_column.addWidget(self.summary_card, stretch=2)
        
        self.content_layout.addLayout(self.right_column, stretch=1)
        self.main_layout.addLayout(self.content_layout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        pass
