from PyQt6 import QtCore, QtGui, QtWidgets
import qtawesome as qta


PRIMARY = "#862D6D"
PRIMARY_HOVER = "#6E2259"
BACKGROUND = "#F5F0F4"
CARD = "#FFFFFF"
TEXT = "#201A24"
MUTED = "#7B737F"
BORDER = "#EAE0E8"
DIVIDER = "#D8C8D5"
FONT = "'Segoe UI', Arial, sans-serif"


def field_style():
    return f"""
        QLineEdit, QComboBox {{
            background: {CARD}; border: 1px solid {DIVIDER};
            border-radius: 8px; padding: 7px 10px;
            color: {TEXT}; font: 13px {FONT}; min-height: 28px;
        }}
        QLineEdit:focus, QComboBox:focus {{ border: 2px solid {PRIMARY}; }}
    """


def button_style(color=PRIMARY):
    return f"""
        QToolButton {{ background: {color}; color: white; border: none;
            border-radius: 8px; padding: 7px 13px; font: 600 13px {FONT}; }}
        QToolButton:hover {{ background: {PRIMARY_HOVER}; }}
    """


class Ui_ControlUsuario(object):
    def setupUi(self, Form):
        Form.setObjectName("ControlUsuario")
        Form.setMinimumSize(900, 600)
        Form.setStyleSheet(f"background: {BACKGROUND};")

        root = QtWidgets.QGridLayout(Form)
        root.setContentsMargins(0, 0, 0, 0)
        self.Contenedor = QtWidgets.QWidget(Form)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Contenedor)
        self.horizontalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.Contenido = QtWidgets.QStackedWidget(self.Contenedor)
        self.Contenido.setStyleSheet("background: transparent; border: none;")
        self.horizontalLayout_2.addWidget(self.Contenido)
        root.addWidget(self.Contenedor)

        self.ContenidoPage1 = QtWidgets.QWidget()
        self.Contenido.addWidget(self.ContenidoPage1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.ContenidoPage1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(18)

        self.build_header()
        self.build_stats()
        self.build_form()
        self.build_search()
        self.build_table()
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def build_header(self):
        self.headerWidget = QtWidgets.QWidget(self.ContenidoPage1)
        layout = QtWidgets.QHBoxLayout(self.headerWidget)
        layout.setContentsMargins(4, 0, 4, 0)
        text = QtWidgets.QVBoxLayout()
        text.setSpacing(2)

        self.LabelTituloUsuarios = QtWidgets.QLabel("Control de Usuarios")
        self.LabelTituloUsuarios.setStyleSheet(f"color: {PRIMARY}; font: 700 28px {FONT};")
        self.LabelSubtituloUsuarios = QtWidgets.QLabel(
            "Administra los usuarios del sistema y sus permisos de acceso."
        )
        self.LabelSubtituloUsuarios.setStyleSheet(f"color: {MUTED}; font: 13px {FONT};")
        text.addWidget(self.LabelTituloUsuarios)
        text.addWidget(self.LabelSubtituloUsuarios)
        layout.addLayout(text)
        layout.addStretch()
        self.BtnNuevoUsuario = self.make_button(
            "BtnNuevoUsuario", "Nuevo Usuario", "fa5s.user-plus"
        )
        layout.addWidget(self.BtnNuevoUsuario)
        self.verticalLayout_2.addWidget(self.headerWidget)

    def build_stats(self):
        self.statsWidget = QtWidgets.QWidget(self.ContenidoPage1)
        layout = QtWidgets.QHBoxLayout(self.statsWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        self.statLabels = {}
        stats = (
            ("total", "Total Usuarios", "0", PRIMARY),
            ("active", "Usuarios Activos", "0", "#35A853"),
            ("roles", "Roles Asignados", "0", "#6A35C2"),
            ("access", "Ultimo Acceso", "Hoy", "#E53935"),
            ("security", "Seguridad", "Alta", "#35A853"),
        )
        for key, title, value, color in stats:
            card = QtWidgets.QFrame(self.statsWidget)
            card.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}")
            card_layout = QtWidgets.QVBoxLayout(card)
            card_layout.setContentsMargins(14, 9, 14, 9)
            title_label = QtWidgets.QLabel(title)
            title_label.setStyleSheet(f"color: {MUTED}; font: 11px {FONT}; border: none;")
            value_label = QtWidgets.QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font: 700 22px {FONT}; border: none;")
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            layout.addWidget(card, 1)
            self.statLabels[key] = value_label
        self.verticalLayout_2.addWidget(self.statsWidget)

    def build_form(self):
        self.widget_3 = QtWidgets.QFrame(self.ContenidoPage1)
        self.widget_3.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}")
        self.widget_3.setVisible(False)
        self.gridLayout = QtWidgets.QGridLayout(self.widget_3)
        self.gridLayout.setContentsMargins(20, 16, 20, 16)
        self.gridFormulario = QtWidgets.QGridLayout()
        self.gridFormulario.setHorizontalSpacing(12)
        self.gridFormulario.setVerticalSpacing(6)
        self.gridLayout.addLayout(self.gridFormulario, 0, 0)

        self.BtnVolverUsuarios = QtWidgets.QToolButton()
        self.BtnVolverUsuarios.setObjectName("BtnVolverUsuarios")
        self.BtnVolverUsuarios.setToolTip("Volver a usuarios")
        self.BtnVolverUsuarios.setIcon(qta.icon("fa5s.arrow-left", color=PRIMARY))
        self.BtnVolverUsuarios.setIconSize(QtCore.QSize(18, 18))
        self.BtnVolverUsuarios.setFixedSize(34, 34)
        self.BtnVolverUsuarios.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.BtnVolverUsuarios.setStyleSheet(
            f"QToolButton {{ background: transparent; border: none; border-radius: 6px; }}"
            f"QToolButton:hover {{ background: #F3E6EF; }}"
        )
        self.gridFormulario.addWidget(self.BtnVolverUsuarios, 0, 0)

        self.LabelVentasA = QtWidgets.QLabel("Usuario")
        self.LabelVentasA.setStyleSheet(f"color: {PRIMARY}; font: 700 20px {FONT}; border: none;")
        self.gridFormulario.addWidget(self.LabelVentasA, 0, 1, 1, 4)

        fields = (
            ("label_3", "ID:", "InputIdUser", "fa5s.id-badge"),
            ("label_5", "Nombre:", "InputNombreUser", "fa5s.user"),
            ("label_7", "Usuario:", "InputUser", "fa5s.user"),
            ("label", "Contrasena:", "InputPasswordUser", "fa5s.lock"),
        )
        for column, (label_name, label_text, field_name, icon_name) in enumerate(fields):
            label = QtWidgets.QLabel(label_text)
            label.setObjectName(label_name)
            label.setStyleSheet(f"color: {MUTED}; font: 600 11px {FONT}; border: none;")
            field = self.make_field(field_name, icon_name)
            setattr(self, label_name, label)
            setattr(self, field_name, field)
            self.gridFormulario.addWidget(label, 1, column)
            self.gridFormulario.addWidget(field, 2, column)

        self.label_6 = QtWidgets.QLabel("Rol:")
        self.label_6.setStyleSheet(f"color: {MUTED}; font: 600 11px {FONT}; border: none;")
        self.gridFormulario.addWidget(self.label_6, 3, 0)
        self.BtnRolUser = self.make_button("BtnRolUser", "ASESOR", "fa5s.user-tag", outlined=True)
        self.gridFormulario.addWidget(self.BtnRolUser, 4, 0)

        self.BtnRegistrarUser = self.make_button("BtnRegistrarUser", "Registrar Usuario", "fa5s.user-plus")
        self.BtnEliminar = self.make_button("BtnEliminar", "Eliminar Usuario", "fa5s.trash-alt", color="#C0392B")
        self.gridFormulario.addWidget(self.BtnRegistrarUser, 4, 3)
        self.gridFormulario.addWidget(self.BtnEliminar, 4, 4)
        self.verticalLayout_2.addWidget(self.widget_3)

    def build_search(self):
        self.widget_2 = QtWidgets.QFrame(self.ContenidoPage1)
        self.widget_2.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}")
        layout = QtWidgets.QHBoxLayout(self.widget_2)
        layout.setContentsMargins(14, 8, 14, 8)
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setPixmap(qta.icon("fa5s.search", color=PRIMARY).pixmap(18, 18))
        layout.addWidget(self.label_2)
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("Buscar por nombre, usuario o ID...")
        self.lineEdit.setStyleSheet(field_style())
        layout.addWidget(self.lineEdit)
        self.verticalLayout_2.addWidget(self.widget_2)

    def build_table(self):
        self.widget = QtWidgets.QWidget(self.ContenidoPage1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.TablaUser = QtWidgets.QTableWidget(0, 6)
        self.TablaUser.setObjectName("TablaUser")
        self.TablaUser.setMinimumHeight(280)
        self.TablaUser.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.TablaUser.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.TablaUser.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.TablaUser.setShowGrid(False)
        self.TablaUser.verticalHeader().setVisible(False)
        self.TablaUser.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.TablaUser.setStyleSheet(f"""
            QTableWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; color: {TEXT}; font: 13px {FONT}; }}
            QTableWidget::item {{ padding: 8px; border-bottom: 1px solid {BORDER}; }}
            QTableWidget::item:selected {{ background: #F3E6EF; color: {TEXT}; }}
            QHeaderView::section {{ background: #FBEFF7; color: {PRIMARY}; border: none; padding: 10px; font: 600 12px {FONT}; }}
        """)
        self.verticalLayout_3.addWidget(self.TablaUser)
        self.verticalLayout_2.addWidget(self.widget, 1)

    def make_field(self, name, icon_name):
        field = QtWidgets.QLineEdit()
        field.setObjectName(name)
        field.setStyleSheet(field_style())
        field.addAction(qta.icon(icon_name, color=PRIMARY), QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        if name == "InputPasswordUser":
            field.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        return field

    def make_button(self, name, text, icon_name, color=PRIMARY, outlined=False):
        button = QtWidgets.QToolButton()
        button.setObjectName(name)
        button.setText(text)
        button.setIcon(qta.icon(icon_name, color=PRIMARY if outlined else "#FFFFFF"))
        button.setIconSize(QtCore.QSize(16, 16))
        button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        if outlined:
            button.setStyleSheet(f"QToolButton {{ background: {CARD}; color: {PRIMARY}; border: 1px solid {PRIMARY}; border-radius: 8px; padding: 7px 13px; font: 600 13px {FONT}; }}")
        else:
            button.setStyleSheet(button_style(color))
        return button

    def retranslateUi(self, Form):
        Form.setWindowTitle("Control de Usuarios")
        self.TablaUser.setHorizontalHeaderLabels(["ID", "Nombre", "Usuario", "Contrasena", "Rol", "Estado"])
