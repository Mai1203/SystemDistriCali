from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox


class Mensajes(QMessageBox):
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


def enviar_notificacion(titulo, mensaje):
    """
    Muestra un mensaje dentro de la aplicación.
    """
    titulo_normalizado = titulo.lower()
    if "error" in titulo_normalizado:
        Mensajes.critical(None, titulo, mensaje)
    elif "advertencia" in titulo_normalizado or "warning" in titulo_normalizado:
        Mensajes.warning(None, titulo, mensaje)
    else:
        Mensajes.information(None, titulo, mensaje)
