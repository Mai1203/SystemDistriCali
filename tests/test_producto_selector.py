from app.utils.autocomplementado import extraer_codigo_y_nombre_producto


def test_extraer_codigo_y_nombre_producto_con_codigo_y_nombre():
    codigo, nombre = extraer_codigo_y_nombre_producto("100 - Esmalte Muna")

    assert codigo == "100"
    assert nombre == "Esmalte Muna"


def test_extraer_codigo_y_nombre_producto_sin_codigo():
    codigo, nombre = extraer_codigo_y_nombre_producto("Esmalte Muna")

    assert codigo is None
    assert nombre == "Esmalte Muna"
