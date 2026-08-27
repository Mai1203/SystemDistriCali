from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
    QMessageBox,
)


class Mensajes(QMessageBox):
    """
    Mantiene compatibilidad para preguntas/confirmaciones modales (ej: QMessageBox.question).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(360, 360)
        self.setTextFormat(QtCore.Qt.PlainText)

    @staticmethod
    def _mostrar(parent, titulo, mensaje, icono, botones, boton_predeterminado=None):
        dialogo = Mensajes(parent)
        dialogo.setWindowTitle(titulo)
        dialogo.setText(mensaje)
        dialogo.setTextFormat(QtCore.Qt.PlainText)
        for etiqueta in dialogo.findChildren(QLabel):
            etiqueta.setWordWrap(True)
            etiqueta.setAlignment(QtCore.Qt.AlignCenter)
        dialogo.setIcon(icono)
        dialogo.setStandardButtons(botones)
        if boton_predeterminado is not None:
            dialogo.setDefaultButton(boton_predeterminado)
        return dialogo.exec_()

    @staticmethod
    def information(parent, titulo, mensaje, botones=QMessageBox.Ok, boton_predeterminado=None):
        return Mensajes._mostrar(parent, titulo, mensaje, QMessageBox.Information, botones, boton_predeterminado)

    @staticmethod
    def warning(parent, titulo, mensaje, botones=QMessageBox.Ok, boton_predeterminado=None):
        return Mensajes._mostrar(parent, titulo, mensaje, QMessageBox.Warning, botones, boton_predeterminado)

    @staticmethod
    def critical(parent, titulo, mensaje, botones=QMessageBox.Ok, boton_predeterminado=None):
        return Mensajes._mostrar(parent, titulo, mensaje, QMessageBox.Critical, botones, boton_predeterminado)

    @staticmethod
    def question(parent, titulo, mensaje, botones=QMessageBox.Yes | QMessageBox.No, boton_predeterminado=QMessageBox.No):
        return Mensajes._mostrar(parent, titulo, mensaje, QMessageBox.Question, botones, boton_predeterminado)


class ToastNotification(QWidget):
    """
    Widget flotante no bloqueante para notificaciones temporales (Toast).
    """
    _instancias_activas = []

    def __init__(
        self,
        titulo: str,
        mensaje: str,
        tipo: str = "info",
        duracion_ms: int = 3000,
        parent=None,
    ):
        super().__init__(parent)
        self.duracion_ms = duracion_ms
        self.tipo = tipo

        # Registrar instancia activa
        ToastNotification._instancias_activas.append(self)

        # Configuración de ventana flotante sin marco
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.ToolTip
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self._setup_ui(titulo, mensaje)
        self._posicionar()
        self._setup_animaciones()

    def _setup_ui(self, titulo: str, mensaje: str):
        config_tipos = {
            "exito": {
                "bg": "#2E7D32",
                "icono": "✓",
                "borde": "#4CAF50",
            },
            "error": {
                "bg": "#C62828",
                "icono": "✕",
                "borde": "#EF5350",
            },
            "warning": {
                "bg": "#EF6C00",
                "icono": "!",
                "borde": "#FFA726",
            },
            "info": {
                "bg": "#1565C0",
                "icono": "ℹ",
                "borde": "#42A5F5",
            },
        }

        estilo = config_tipos.get(self.tipo, config_tipos["info"])

        # Contenedor principal con estilo redondeado
        self.contenedor = QWidget(self)
        self.contenedor.setObjectName("ToastContainer")
        self.contenedor.setStyleSheet(
            f"""
            #ToastContainer {{
                background-color: {estilo["bg"]};
                border: 1.5px solid {estilo["borde"]};
                border-radius: 10px;
            }}
        """
        )

        layout_principal = QHBoxLayout(self.contenedor)
        layout_principal.setContentsMargins(18, 14, 18, 14)
        layout_principal.setSpacing(15)

        # Icono circular
        lbl_icono = QLabel(estilo["icono"])
        lbl_icono.setFixedSize(36, 36)
        lbl_icono.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icono.setStyleSheet(
            """
            background-color: rgba(255, 255, 255, 0.22);
            color: #FFFFFF;
            font-size: 18px;
            font-weight: bold;
            border-radius: 18px;
        """
        )
        layout_principal.addWidget(lbl_icono, alignment=QtCore.Qt.AlignTop)

        # Textos (Título y Mensaje)
        layout_texto = QVBoxLayout()
        layout_texto.setSpacing(4)
        layout_texto.setContentsMargins(0, 0, 0, 0)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(
            """
            color: #FFFFFF;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """
        )
        lbl_titulo.setWordWrap(True)

        lbl_mensaje = QLabel(mensaje)
        lbl_mensaje.setStyleSheet(
            """
            color: #F8F9FA;
            font-size: 13.5px;
            line-height: 1.3;
            background: transparent;
        """
        )
        lbl_mensaje.setWordWrap(True)

        layout_texto.addWidget(lbl_titulo)
        layout_texto.addWidget(lbl_mensaje)
        layout_principal.addLayout(layout_texto, stretch=1)

        # Botón de cerrar
        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(24, 24)
        btn_cerrar.setCursor(QtCore.Qt.PointingHandCursor)
        btn_cerrar.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.75);
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                color: #FFFFFF;
            }
        """
        )
        btn_cerrar.clicked.connect(self.close)
        layout_principal.addWidget(btn_cerrar, alignment=QtCore.Qt.AlignTop)

        # Layout raíz con margen para sombra
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.addWidget(self.contenedor)

        # Efecto de sombra
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(18)
        sombra.setColor(QtGui.QColor(0, 0, 0, 90))
        sombra.setOffset(0, 4)
        self.contenedor.setGraphicsEffect(sombra)

        # Ancho fijo uniforme para todas las notificaciones (evita que unas se vean más cortas que otras)
        self.setFixedWidth(430)
        self.adjustSize()

    def _posicionar(self):
        pantalla = QtWidgets.QDesktopWidget().availableGeometry()
        
        # Apilar notificaciones si hay varias activas simultáneamente
        index = len(ToastNotification._instancias_activas) - 1
        offset_y = index * (self.sizeHint().height() + 8)

        x = pantalla.width() - self.width() - 25
        y = pantalla.height() - self.height() - 25 - offset_y

        self.move(x, max(20, y))

    def _setup_animaciones(self):
        # Animación de entrada suave
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(220)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_in.start()

        # Temporizador de autodestrucción
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._iniciar_salida)
        self.timer.start(self.duracion_ms)

    def _iniciar_salida(self):
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.InCubic)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()

    def mousePressEvent(self, event):
        self.close()

    def closeEvent(self, event):
        if self in ToastNotification._instancias_activas:
            ToastNotification._instancias_activas.remove(self)
        event.accept()


def enviar_notificacion(titulo: str, mensaje: str, duracion_ms: int = None):
    """
    Muestra una notificación flotante (Toast) temporal y no bloqueante.
    """
    titulo_norm = titulo.lower()
    if "error" in titulo_norm:
        tipo = "error"
        tiempo = duracion_ms if duracion_ms is not None else 4000
    elif "advertencia" in titulo_norm or "warning" in titulo_norm:
        tipo = "warning"
        tiempo = duracion_ms if duracion_ms is not None else 3500
    elif any(k in titulo_norm for k in ["éxito", "exito", "bienvenido", "correcto"]):
        tipo = "exito"
        tiempo = duracion_ms if duracion_ms is not None else 3000
    else:
        tipo = "info"
        tiempo = duracion_ms if duracion_ms is not None else 3000

    toast = ToastNotification(titulo, mensaje, tipo=tipo, duracion_ms=tiempo)
    toast.show()

