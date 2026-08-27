def validar_campos_requeridos(valores):
    for nombre, valor in valores.items():
        if valor is None or not str(valor).strip():
            return f"El campo '{nombre}' es obligatorio."
    return None


def convertir_float(valor, nombre):
    try:
        return float(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"El campo '{nombre}' debe ser numérico.") from error
