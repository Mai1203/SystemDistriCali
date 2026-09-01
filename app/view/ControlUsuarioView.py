from PyQt6.QtWidgets import (
    QWidget,
    QMessageBox,
    QComboBox,
    QLabel,
)

from PyQt6.QtGui import (
    QStandardItem,
    QStandardItemModel,
)

from ..utils.enviar_notifi import Mensajes as QMessageBox

from PyQt6 import (
    QtWidgets,
    QtGui,
    QtCore,
)

from PyQt6.QtCore import (
    Qt,
    QTimer,
)

import qtawesome as qta

from ..ui import Ui_ControlUsuario
from ..configuracion import PERMISOS_VISTAS
from ..database.database import SessionLocal
from ..controllers.usuario_crud import *
from ..utils import *


class ControlUsuario_View(
    QWidget,
    Ui_ControlUsuario
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setupUi(
            self
        )


        self.permisos_vistas = PERMISOS_VISTAS


        # ============================================================
        # COMBO DE PERMISOS
        # ============================================================

        self.comboPermisos = QComboBox(
            self.widget_3
        )

        self.comboPermisos.setObjectName(
            "comboPermisos"
        )


        self.comboPermisos.setEditable(
            True
        )

        self.comboPermisos.lineEdit().setReadOnly(
            True
        )


        self.comboPermisos.setMinimumHeight(
            28
        )


        self.comboPermisos.setPlaceholderText(
            "Seleccionar permisos"
        )


        # ============================================================
        # MODELO DE PERMISOS
        # ============================================================

        self.modelo_permisos = QStandardItemModel(
            self.comboPermisos
        )


        self.icon_check = qta.icon(
            "fa5s.check-circle",
            color="#862D6D"
        )


        self.icon_uncheck = QtGui.QIcon()


        for nombre in self.permisos_vistas:

            item = QStandardItem(
                nombre
            )


            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                |
                Qt.ItemFlag.ItemIsUserCheckable
            )


            item.setData(
                Qt.CheckState.Unchecked,
                Qt.CheckStateRole
            )


            item.setIcon(
                self.icon_uncheck
            )


            self.modelo_permisos.appendRow(
                item
            )


        self.comboPermisos.setModel(
            self.modelo_permisos
        )


        self.modelo_permisos.itemChanged.connect(
            self._on_permiso_changed
        )


        # ============================================================
        # NUEVA UBICACIÓN DE PERMISOS
        #
        # LABEL:
        # fila 4
        # columna 1
        #
        # COMBO:
        # fila 5
        # columna 1
        #
        # ============================================================

        self.labelPermisos = QLabel(
            "Permisos",
            self.widget_3
        )

        self.labelPermisos.setObjectName(
            "labelPermisos"
        )


        self.gridFormulario.addWidget(
            self.labelPermisos,
            4,
            1
        )


        self.gridFormulario.addWidget(
            self.comboPermisos,
            5,
            1
        )


        # ============================================================
        # CONFIGURACIÓN INICIAL
        # ============================================================

        QTimer.singleShot(
            0,
            self.InputIdUser.setFocus
        )


        self.BtnEliminar.setCursor(
            QtGui.QCursor(
                Qt.CursorShape.PointingHandCursor
            )
        )


        self.BtnRegistrarUser.setCursor(
            QtGui.QCursor(
                Qt.CursorShape.PointingHandCursor
            )
        )


        self.BtnRolUser.setText(
            "ASESOR"
        )


        # ============================================================
        # BUSCADOR
        # ============================================================

        self.lineEdit.textChanged.connect(
            self.buscar_usuarios
        )


        self.lineEdit.setPlaceholderText(
            "Buscar por Nombre o ID"
        )


        # ============================================================
        # PLACEHOLDERS
        # ============================================================

        self.InputIdUser.setPlaceholderText(
            "Ej: # Cedula"
        )


        self.InputNombreUser.setPlaceholderText(
            "Ej: Pepito Perez"
        )


        self.InputUser.setPlaceholderText(
            "Ej: pepito123"
        )


        self.InputPasswordUser.setPlaceholderText(
            "Ej: pepito789"
        )


        self.InputIdUser.textChanged.connect(
            self.verififcarInput
        )


        # ============================================================
        # VALIDADORES
        # ============================================================

        configurar_validador_numerico(
            self.InputIdUser
        )


        configurar_validador_texto(
            self.InputNombreUser
        )


        # ============================================================
        # BOTONES
        # ============================================================

        self.BtnRegistrarUser.clicked.connect(
            self.ingresar_usuario
        )


        self.BtnEliminar.clicked.connect(
            self.eliminar_usuarios
        )


        # ============================================================
        # ENTER PARA EDITAR
        # ============================================================

        self.InputIdUser.returnPressed.connect(
            self.editar_usuario
        )

        self.InputNombreUser.returnPressed.connect(
            self.editar_usuario
        )

        self.InputUser.returnPressed.connect(
            self.editar_usuario
        )

        self.InputPasswordUser.returnPressed.connect(
            self.editar_usuario
        )


        # ============================================================
        # TABLA
        # ============================================================

        self.TablaUser.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )


        self.TablaUser.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )


        self.TablaUser.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )


        self.TablaUser.cellClicked.connect(
            self.cargar_datos_fila
        )


    # ================================================================
    # EVENTOS
    # ================================================================

    def showEvent(
        self,
        event
    ):

        super().showEvent(
            event
        )


        self.limpiar_formulario()

        self.limpiar_tabla_usuarios()

        self.mostrar_usuarios()


    # ================================================================
    # VALIDAR INPUT
    # ================================================================

    def verififcarInput(self):

        if not self.InputIdUser.text().strip():

            self.limpiar_formulario()


    # ================================================================
    # TECLADO
    # ================================================================

    def keyPressEvent(
        self,
        event
    ):

        if event.key() == Qt.Key.Key_Up:

            self.navegar_widgets()


        elif event.key() == Qt.Key.Key_Down:

            self.navegar_widgets_atras()


        super().keyPressEvent(
            event
        )


    # ================================================================
    # NAVEGACIÓN
    # ================================================================

    def navegar_widgets(self):

        if self.focusWidget() == self.InputIdUser:

            self.InputNombreUser.setFocus()


        elif self.focusWidget() == self.InputNombreUser:

            self.InputUser.setFocus()


        elif self.focusWidget() == self.InputUser:

            self.InputPasswordUser.setFocus()


        elif self.focusWidget() == self.InputPasswordUser:

            self.InputIdUser.setFocus()


    def navegar_widgets_atras(self):

        if self.focusWidget() == self.InputPasswordUser:

            self.InputUser.setFocus()


        elif self.focusWidget() == self.InputUser:

            self.InputNombreUser.setFocus()


        elif self.focusWidget() == self.InputNombreUser:

            self.InputIdUser.setFocus()


        elif self.focusWidget() == self.InputIdUser:

            self.InputPasswordUser.setFocus()


    # ================================================================
    # INGRESAR USUARIO
    # ================================================================

    def ingresar_usuario(self):

        id_user = self.InputIdUser.text().strip()

        nombre = self.InputNombreUser.text().strip()

        usuario = self.InputUser.text().strip()

        contraseña = self.InputPasswordUser.text().strip()


        if not id_user or not usuario or not contraseña:

            enviar_notificacion(
                "Error",
                "Por favor, rellena todos los campos"
            )

            return


        try:

            self.db = SessionLocal()


            usuario_existente = obtener_usuario_por_id(
                self.db,
                id_user
            )


            if usuario_existente:

                enviar_notificacion(
                    "Error",
                    "El usuario ya existe en la base de datos"
                )

                return


            crear_usuario(
                self.db,
                id_user,
                nombre,
                usuario,
                contraseña,
                True,
                2,
                self.permisos_seleccionados(),
            )


            enviar_notificacion(
                "Éxito",
                "Usuario registrado exitosamente"
            )


            self.BtnRolUser.setText(
                "ASESOR"
            )


            self.limpiar_formulario()

            self.limpiar_tabla_usuarios()

            self.mostrar_usuarios()


        except Exception as e:

            print(
                f"Error: {e}"
            )


            enviar_notificacion(
                "Error",
                f"Error: {e}"
            )


        finally:

            if hasattr(
                self,
                "db"
            ) and self.db:

                self.db.close()


        self.InputIdUser.setFocus()


    # ================================================================
    # LIMPIAR FORMULARIO
    # ================================================================

    def limpiar_formulario(self):

        self.InputIdUser.clear()

        self.InputNombreUser.clear()

        self.InputUser.clear()

        self.InputPasswordUser.clear()


        self.seleccionar_permisos(
            ()
        )


    # ================================================================
    # PERMISOS
    # ================================================================

    def permisos_seleccionados(self):

        return ",".join(

            nombre

            for indice, nombre
            in enumerate(
                self.permisos_vistas
            )

            if self.modelo_permisos.item(
                indice
            ).checkState()
            ==
            Qt.CheckState.Checked
        )


    def seleccionar_permisos(
        self,
        permisos
    ):

        permisos = set(
            permisos
        )


        self.modelo_permisos.blockSignals(
            True
        )


        for indice, nombre in enumerate(
            self.permisos_vistas
        ):

            estado = (

                Qt.CheckState.Checked

                if nombre in permisos

                else Qt.CheckState.Unchecked
            )


            self.modelo_permisos.item(
                indice
            ).setCheckState(
                estado
            )


        self.modelo_permisos.blockSignals(
            False
        )


        for indice in range(
            len(self.permisos_vistas)
        ):

            self._actualizar_icono_check(
                self.modelo_permisos.item(
                    indice
                )
            )


        self.actualizar_texto_permisos()


    def _on_permiso_changed(
        self,
        item
    ):

        self._actualizar_icono_check(
            item
        )


        self.actualizar_texto_permisos()


    def _actualizar_icono_check(
        self,
        item
    ):

        self.modelo_permisos.blockSignals(
            True
        )


        icon = (

            self.icon_check

            if item.checkState()
            ==
            Qt.CheckState.Checked

            else self.icon_uncheck
        )


        item.setIcon(
            icon
        )


        self.modelo_permisos.blockSignals(
            False
        )


    def actualizar_texto_permisos(self):

        seleccionados = [

            nombre

            for indice, nombre
            in enumerate(
                self.permisos_vistas
            )

            if self.modelo_permisos.item(
                indice
            ).checkState()
            ==
            Qt.CheckState.Checked
        ]


        self.comboPermisos.setEditText(

            ", ".join(
                seleccionados
            )

            or
            "Seleccionar permisos"
        )


    # ================================================================
    # MOSTRAR USUARIOS
    # ================================================================

    def mostrar_usuarios(self):

        self.db = SessionLocal()


        try:

            usuarios = obtener_usuarios(
                self.db
            )


            self.actualizar_tabla_usuarios(
                usuarios
            )


        finally:

            self.db.close()


    # ================================================================
    # ACTUALIZAR TABLA
    # ================================================================

    def actualizar_tabla_usuarios(
        self,
        usuarios
    ):

        if not usuarios:

            self.TablaUser.setRowCount(
                0
            )

            self.TablaUser.setColumnCount(
                6
            )

            return


        self.TablaUser.setRowCount(
            len(usuarios)
        )

        self.TablaUser.setColumnCount(
            6
        )


        for row_idx, row in enumerate(
            usuarios
        ):

            id_item = QtWidgets.QTableWidgetItem(
                str(row.ID_Usuario)
            )


            nombre_item = QtWidgets.QTableWidgetItem(
                str(row.Nombre)
            )


            usuario_item = QtWidgets.QTableWidgetItem(
                str(row.Usuario)
            )


            contrasena_item = QtWidgets.QTableWidgetItem(
                str(row.Contrasena)
            )


            rol_item = QtWidgets.QTableWidgetItem(
                str(row.rol)
            )


            estado_item = QtWidgets.QTableWidgetItem(
                str(row.Estado)
            )


            items = [
                id_item,
                nombre_item,
                usuario_item,
                contrasena_item,
                rol_item,
                estado_item,
            ]


            for column, item in enumerate(
                items
            ):

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )


                self.TablaUser.setItem(
                    row_idx,
                    column,
                    item
                )


    # ================================================================
    # LIMPIAR TABLA
    # ================================================================

    def limpiar_tabla_usuarios(self):

        self.TablaUser.setRowCount(
            0
        )

        self.TablaUser.setColumnCount(
            6
        )


    # ================================================================
    # ELIMINAR USUARIOS
    # ================================================================

    def eliminar_usuarios(self):

        ids = self.obtener_ids_seleccionados()


        if not ids:

            enviar_notificacion(
                "Advertencia",
                "No se seleccionaron usuarios para eliminar."
            )

            return


        self.db = SessionLocal()


        try:

            for id_usuario in ids:

                usuario = obtener_usuario_por_id(
                    self.db,
                    id_usuario
                )


                if usuario and usuario.rol == "ADMINISTRADOR":

                    enviar_notificacion(
                        "Advertencia",
                        "No se puede eliminar un administrador."
                    )

                    return


            respuesta = QMessageBox.question(

                self,

                "Confirmar Eliminación",

                f"¿Está seguro de que desea eliminar "
                f"{len(ids)} usuario(s)?",

                QMessageBox.Yes
                |
                QMessageBox.No,
            )


            if respuesta == QMessageBox.Yes:

                for id_usuario in ids:

                    eliminar_usuario(
                        self.db,
                        id_usuario
                    )


                self.db.commit()


                enviar_notificacion(
                    "Éxito",
                    "Usuario(s) eliminado(s) correctamente."
                )


                self.limpiar_tabla_usuarios()

                self.mostrar_usuarios()

                self.limpiar_formulario()


        except Exception as e:

            enviar_notificacion(
                "Error",
                f"Error al eliminar usuarios: {e}"
            )


            print(e)


        finally:

            self.db.close()


        self.InputIdUser.setFocus()


    # ================================================================
    # OBTENER IDS SELECCIONADOS
    # ================================================================

    def obtener_ids_seleccionados(self):

        filas_seleccionadas = (

            self.TablaUser
            .selectionModel()
            .selectedRows()
        )


        ids = []


        for fila in filas_seleccionadas:

            id_usuario = (

                self.TablaUser
                .item(
                    fila.row(),
                    0
                )
                .text()
            )


            ids.append(
                int(id_usuario)
            )


        return ids


    # ================================================================
    # CARGAR DATOS
    # ================================================================

    def cargar_datos_fila(self):

        fila_seleccionada = (
            self.TablaUser.currentRow()
        )


        if fila_seleccionada < 0:

            return


        datos_fila = []


        for columna in range(
            self.TablaUser.columnCount()
        ):

            item = self.TablaUser.item(
                fila_seleccionada,
                columna
            )


            datos_fila.append(
                item.text()
                if item
                else ""
            )


        self.InputIdUser.setText(
            datos_fila[0]
        )


        self.InputNombreUser.setText(
            datos_fila[1]
        )


        self.InputUser.setText(
            datos_fila[2]
        )


        self.InputPasswordUser.setText(
            datos_fila[3]
        )


        db = SessionLocal()


        try:

            usuario = obtener_usuario_por_id(
                db,
                datos_fila[0]
            )


            if usuario:

                self.seleccionar_permisos(

                    (
                        usuario.Permisos
                        or ""
                    ).split(",")
                )


        finally:

            db.close()


    # ================================================================
    # EDITAR USUARIO
    # ================================================================

    def editar_usuario(self):

        id_usuario = self.InputIdUser.text()

        nombre = self.InputNombreUser.text()

        usuario = self.InputUser.text()

        contrasena = self.InputPasswordUser.text()

        permisos = self.permisos_seleccionados()


        if (
            not id_usuario
            or not nombre
            or not usuario
            or not contrasena
        ):

            enviar_notificacion(
                "Error",
                "Por favor, rellene todos los campos"
            )

            return


        reply = QMessageBox.question(

            self,

            "Confirmación",

            "¿Desea guardar los cambios?",

            QMessageBox.Yes
            |
            QMessageBox.No,

            QMessageBox.No,
        )


        if reply == QMessageBox.Yes:

            try:

                self.db = SessionLocal()


                usuario_actualizado = actualizar_usuario(

                    self.db,

                    id_usuario,

                    nombre,

                    usuario,

                    contrasena,

                    permisos=permisos
                )


                if usuario_actualizado:

                    enviar_notificacion(
                        "Éxito",
                        "Usuario actualizado correctamente"
                    )


                    self.limpiar_formulario()

                    self.limpiar_tabla_usuarios()

                    self.mostrar_usuarios()


                else:

                    enviar_notificacion(
                        "Error",
                        "Hubo un problema al actualizar el usuario"
                    )


            except Exception as e:

                QMessageBox.critical(

                    self,

                    "Error",

                    f"Error: {e}"
                )


            finally:

                if (
                    hasattr(self, "db")
                    and self.db
                ):

                    self.db.close()


        else:

            print(
                "Edición cancelada"
            )


    # ================================================================
    # BUSCAR USUARIOS
    # ================================================================

    def buscar_usuarios(self):

        buscar = self.lineEdit.text().strip()


        if not buscar:

            self.mostrar_usuarios()

            return

        self.db = SessionLocal()

        try:

            usuarios = buscar_usuarios(
                self.db,
                buscar
            )

            self.actualizar_tabla_usuarios(
                usuarios
            )

        finally:

            self.db.close()