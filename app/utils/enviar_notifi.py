from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox


class Mensajes(QMessageBox):
    def __init__(self, parent=None):
        configurar_estilo_message_box()
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


def configurar_estilo_message_box():
    app = QApplication.instance()
    if app is None:
        return
    if app.property("message_box_style_configured"):
        return

    app.setStyleSheet(app.styleSheet() + """
        QMessageBox {
            background-color: #ffffff;
            border: 1px solid #d9dee7;
            border-radius: 0px;
        }
        QMessageBox QLabel {
            color: #1f2937;
            font-size: 14px;
            min-width: 0px;
            max-width: 300px;
            min-height: 0px;
            padding: 8px;
        }
        QMessageBox QPushButton {
            background-color: #1f6feb;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            min-width: 90px;
            padding: 8px 16px;
            font-size: 13px;
        }
        QMessageBox QPushButton:hover {
            background-color: #1558b0;
        }
        QMessageBox QPushButton:pressed {
            background-color: #0d3f80;
        }
    """)
    app.setProperty("message_box_style_configured", True)


def enviar_notificacion(titulo, mensaje):
    """
    Muestra un mensaje dentro de la aplicación.
    """
    configurar_estilo_message_box()
    titulo_normalizado = titulo.lower()
    if "error" in titulo_normalizado:
        Mensajes.critical(None, titulo, mensaje)
    elif "advertencia" in titulo_normalizado or "warning" in titulo_normalizado:
        Mensajes.warning(None, titulo, mensaje)
    else:
        Mensajes.information(None, titulo, mensaje)
