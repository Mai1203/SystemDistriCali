from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QApplication,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from app.view import (
    Navbar_View,
    Respaldo_View,
    ControlUsuario_View,
    VentasCredito_View,
    Facturas_View,
    CrediFactura_View,
    VentasA_View,
    Caja_View,
    Egreso_View,
    Productos_View,
    Reportes_View,
    PagoCredito_View,
    Cliente_View,
)
from app.configuracion import TIPOS_VENTA, obtener_tipo_venta


class MainApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configurar la ventana principal
        self.setWindowTitle("System Distri Cali")
        self.setWindowIcon(QIcon("assets/Favicon.ico"))
        self.resize(800, 600)
        screen = QApplication.primaryScreen().availableGeometry()
        self.setMaximumSize(screen.width(), screen.height())

        self.setStyleSheet("background-color: white;")

        # Widget central que contiene el diseño principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Crear el Navbar
        self.navbar = Navbar_View()
        layout.addWidget(self.navbar)

        # Crear el QStackedWidget para el contenido
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Crear y agregar vistas al QStackedWidget
        self.caja = Caja_View()
        self.ventas = VentasA_View()
        self.ventasCredito = VentasCredito_View()
        self.facturas = Facturas_View()
        self.egreso = Egreso_View()
        self.productos = Productos_View()
        self.respaldo_view = Respaldo_View()
        self.control_usuario_view = ControlUsuario_View()
        self.reportes = Reportes_View()
        self.crediFactura = CrediFactura_View()
        self.pagoCredito = PagoCredito_View()
        self.Clientes = Cliente_View()

        self.stacked_widget.addWidget(self.caja)
        self.stacked_widget.addWidget(self.ventas)
        self.stacked_widget.addWidget(self.ventasCredito)
        self.stacked_widget.addWidget(self.facturas)
        self.stacked_widget.addWidget(self.crediFactura)
        self.stacked_widget.addWidget(self.egreso)
        self.stacked_widget.addWidget(self.productos)
        self.stacked_widget.addWidget(self.respaldo_view)
        self.stacked_widget.addWidget(self.control_usuario_view)
        self.stacked_widget.addWidget(self.reportes)
        self.stacked_widget.addWidget(self.pagoCredito)
        self.stacked_widget.addWidget(self.Clientes)

        # Conectar los botones del Navbar
        self.navbar.comboVentas.activated.connect(self.cambiar_tipo_venta)
        self.cambiar_tipo_venta(0)
        self.navbar.BtnCaja.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.caja)
        )
        self.navbar.BtnCredito.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.ventasCredito)
        )
        self.navbar.BtnEgreso.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.egreso)
        )
        self.navbar.BtnRespaldo.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.respaldo_view)
        )
        self.navbar.BtnProductos.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.productos)
        )
        self.navbar.BtnCrediFactura.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.crediFactura)
        )
        self.navbar.BtnFacturas.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.facturas)
        )
        self.navbar.BtnReportes.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.reportes)
        )
        self.navbar.BtnControlUsuario.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.control_usuario_view)
        )
        self.navbar.BtnClientes.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.Clientes)
        )

        self.facturas.enviar_facturas_A.connect(self.cambiar_a_ventasA)
        self.facturas.enviar_facturas_B.connect(self.cambiar_a_ventasB)
        self.facturas.enviar_facturas_C.connect(self.cambiar_a_ventasA)
        self.facturas.enviar_facturas_D.connect(self.cambiar_a_ventasA)
        self.facturas.enviar_facturas_Credito.connect(self.cambiar_a_ventasCredito)
        self.crediFactura.enviar_facturas_Credito.connect(self.cambiar_a_ventasCredito)
        self.crediFactura.enviar_ventaCredito.connect(self.cambiar_a_pagoCredito)

    def cambiar_tipo_venta(self, indice):
        if (
            self.ventas.en_edicion
            and self.ventas.tipo_venta_original is not None
            and indice != self.ventas.tipo_venta_original
        ):
            QMessageBox.warning(
                self,
                "Edición de factura",
                "Se está editando una factura y no se puede cambiar el tipo de factura.",
            )
            self.navbar.comboVentas.blockSignals(True)
            self.navbar.comboVentas.setCurrentIndex(self.ventas.tipo_venta_original)
            self.navbar.comboVentas.blockSignals(False)
            return

        tipo_venta = obtener_tipo_venta(indice)["nombre"]
        self.ventas.configurar_tipo_venta(indice)
        self.ventas.LabelVentasA.setText(tipo_venta)
        self.stacked_widget.setCurrentWidget(self.ventas)

    def seleccionar_tipo_por_factura(self, factura_completa):
        tipo_factura = factura_completa["Factura"]["TipoFactura"]
        for indice, tipo in TIPOS_VENTA.items():
            if tipo["factura"] == tipo_factura:
                self.navbar.comboVentas.setCurrentIndex(indice)
                tipo_venta = tipo["nombre"]
                self.ventas.configurar_tipo_venta(indice)
                self.ventas.LabelVentasA.setText(tipo_venta)
                return

    def cambiar_a_ventasA(self, factura_completa):
        try:
            self.seleccionar_tipo_por_factura(factura_completa)
            self.stacked_widget.setCurrentWidget(self.ventas)
            self.ventas.cargar_información(factura_completa)
        except Exception as e:
            print(f"Error al cargar datos VentasA: {e}")

    def cambiar_a_ventasB(self, factura_completa):
        try:
            self.seleccionar_tipo_por_factura(factura_completa)
            self.stacked_widget.setCurrentWidget(self.ventas)
            self.ventas.cargar_información(factura_completa)
        except Exception as e:
            print(f"Error al cargar datos VentasB: {e}")

    def cambiar_a_ventasCredito(self, factura_completa, id_venta_credito=None):
        try:
            self.stacked_widget.setCurrentWidget(self.ventasCredito)
            self.ventasCredito.cargar_información(factura_completa, id_venta_credito)
        except Exception as e:
            print(f"Error al cargar datos VentasCredito: {e}")

    def cambiar_a_pagoCredito(self, id_ventaCredito):
        print(f"[DEBUG] cambiar_a_pagoCredito llamado con id={id_ventaCredito}")
        try:
            self.stacked_widget.setCurrentWidget(self.pagoCredito)
            print(f"[DEBUG] cambiado a pagoCredito, llamando cargar_informacion")
            self.pagoCredito.cargar_informacion(id_ventaCredito)
        except Exception as e:
            print(f"[DEBUG] Error al cargar datos PagoCredito: {e}")

