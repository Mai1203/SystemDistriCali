from PyQt6.QtWidgets import QCompleter
from PyQt6 import QtCore


def extraer_codigo_y_nombre_producto(texto):
    """Convierte un valor como '100 - Esmalte Muna' en (codigo, nombre)."""
    if texto is None:
        return None, ""

    valor = str(texto).strip()
    if not valor:
        return None, ""

    if " - " in valor:
        codigo, nombre = valor.split(" - ", 1)
        codigo = codigo.strip()
        nombre = nombre.strip()
        if codigo.isdigit():
            return codigo, nombre

    return None, valor


def configurar_autocompletado(
    input_widget, obtener_datos_func, columna, db_session, procesar_func=None
):
    """
    Configura el autocompletado de un campo de entrada.

    Args:
        input_widget (QLineEdit): El widget de entrada donde se configurará el autocompletado.
        obtener_datos_func (function): La función para obtener los datos de la base de datos.
        columna (str): La columna o atributo que se desea usar para el autocompletado.
        db_session (Session): Sesión activa de la base de datos.
    """
    items = []
    for item in obtener_datos_func(db_session):
        valor = getattr(item, columna) if hasattr(item, columna) else item
        if columna == "Nombre" and hasattr(item, "ID_Producto"):
            items.append(f"{item.ID_Producto} - {valor}")
        else:
            items.append(str(valor))

    completer = QCompleter(items)
    completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
    input_widget.setCompleter(completer)

    if procesar_func:
        completer.activated.connect(procesar_func)