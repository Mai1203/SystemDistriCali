from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

from ..ui import Ui_Login


class Login_View(QWidget, Ui_Login):
    """
    Vista de Login — responsiva al 100%.

    UX/UI aplicado:
    · resizeEvent → adapt_to_size() en cada redimensionado.
    · Tab order: usuario → contraseña → botón.
    · Enter en usuario mueve foco a contraseña.
    · Enter en contraseña dispara login (conectado en main.py).
    · Toggle ojo cambia ícono con feedback visual inmediato.
    · Link ¿Olvidaste? muestra mensaje de contacto.
    """

    def __init__(self, parent=None):
        super(Login_View, self).__init__(parent)

        self.setupUi(self)
        self.ojo_abierto = False

        # Focus inicial sin bloquear el event loop
        QTimer.singleShot(0, self.InputNombreUsuario.setFocus)

        # Seguridad: contraseña oculta por defecto
        self.InputPassword.setEchoMode(QLineEdit.EchoMode.Password)

        # Compatibilidad con main.py: BtnRol invisible pero conectado
        self.BtnRol.clicked.connect(self.Cambiar_Rol)

        # Toggle contraseña: acción nativa del QLineEdit (ojo trailing)
        self.toolButton.clicked.connect(self.mostrar_contrasena)
        if hasattr(self, "passAction"):
            self.passAction.triggered.connect(self.mostrar_contrasena)

        # Enter en usuario → foco a contraseña (flujo natural)
        self.InputNombreUsuario.returnPressed.connect(
            self.InputPassword.setFocus
        )
        # Enter en contraseña → login (conectado en main.py)

        # Link ¿Olvidaste?
        self.lblOlvidaste.mousePressEvent = self._on_olvido_contrasena

        # Adapt inicial con delay para que la geometría esté lista
        QTimer.singleShot(50, self._adapt_current)

    # ── Responsividad ──────────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adapt_current()

    def _adapt_current(self):
        w, h = self.width(), self.height()
        if w > 0 and h > 0:
            self.adapt_to_size(w, h)

    # ── ¿Olvidaste tu contraseña? ──────────────────────────────────
    def _on_olvido_contrasena(self, event):
        QMessageBox.information(
            self,
            "Recuperar Contraseña",
            (
                "Para restablecer tu contraseña o solicitar acceso,\n"
                "comunícate con el administrador del sistema."
            ),
            QMessageBox.StandardButton.Ok,
        )

    # ── Navegación con teclado ─────────────────────────────────────
    def keyPressEvent(self, event):
        key = event.key()
        focused = self.focusWidget()
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            if focused == self.InputNombreUsuario:
                self.InputPassword.setFocus()
            elif focused == self.InputPassword:
                self.InputNombreUsuario.setFocus()
        super().keyPressEvent(event)

    # ── Cambio de rol (invisible, compatibilidad main.py) ──────────
    def Cambiar_Rol(self):
        self.BtnRol.setText(
            "ASESOR" if self.BtnRol.text() == "ADMINISTRADOR"
            else "ADMINISTRADOR"
        )

    # ── Toggle contraseña ──────────────────────────────────────────
    def mostrar_contrasena(self):
        self._cambiar_icono_ojo()
        if self.InputPassword.echoMode() == QLineEdit.EchoMode.Password:
            self.InputPassword.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.InputPassword.setEchoMode(QLineEdit.EchoMode.Password)

    def _cambiar_icono_ojo(self):
        self.ojo_abierto = not self.ojo_abierto
        path = (
            "assets/iconos/eye_open.svg"
            if self.ojo_abierto
            else "assets/iconos/eye_closed.svg"
        )
        icon = QIcon(path)
        self.toolButton.setIcon(icon)
        if hasattr(self, "passAction"):
            self.passAction.setIcon(icon)

    # Alias legacy
    def cambiar_icono(self):
        self._cambiar_icono_ojo()
