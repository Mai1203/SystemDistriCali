def formatear_numero(total):
    """
    Formatea un número con miles y decimales según sea necesario.
    """
    if isinstance(total, str):
        # Si el valor es un string, conviértelo a float
        total = float(total)

    if total % 1 == 0:
        # Si es un número entero, formatear sin decimales
        return f"{total:,.0f}"
    else:
        # Si no es entero, mostrar con dos decimales
        return f"{total:,.2f}"


def formatear_numero_entero(total):
    """
    Formatea un número entero con miles.
    """
    return f"{total:,.0f}"


def formatear_numero_decimal(total, decimales=2):
    """
    Formatea un número decimal con miles y un número específico de decimales.
    """
    return f"{total:,.{decimales}f}"


def formatear_factura_completa(factura_completa, credito=None, pagos=None):
    factura = factura_completa["Factura"]
    cliente = factura_completa["Cliente"]
    detalles = factura_completa["Detalles"]

    fecha = factura["Fecha_Factura"]
    if hasattr(fecha, "strftime"):
        fecha = fecha.strftime("%d/%m/%Y %H:%M")

    lineas = [
        f"FACTURA #{factura['ID_Factura']}",
        "=" * 42,
        f"Fecha: {fecha}",
        f"Tipo: {factura['TipoFactura']}",
        f"Estado: {'Pagada' if factura['Estado'] else 'Pendiente'}",
        f"Método de pago: {factura['MetodoPago']}",
        "",
        "CLIENTE",
        "-" * 42,
        f"Nombre: {cliente['Nombre']} {cliente['Apellido']}",
        f"Identificación: {cliente['ID_Cliente']}",
        f"Teléfono: {cliente['Teléfono']}",
        f"Dirección: {cliente['Direccion']}",
        "",
        "PRODUCTOS",
        "-" * 42,
    ]

    for detalle in detalles:
        lineas.append(
            f"{detalle['Producto']} | Cant.: {detalle['Cantidad']} | "
            f"Precio: ${formatear_numero(detalle['Precio_Unitario'])} | "
            f"Subtotal: ${formatear_numero(detalle['Subtotal'])}"
        )

    subtotal = sum(detalle["Subtotal"] for detalle in detalles)
    lineas.extend([
        "",
        f"Subtotal: ${formatear_numero(subtotal)}",
        f"Descuento: ${formatear_numero(factura['Descuento'])}",
        f"TOTAL: ${formatear_numero(subtotal - factura['Descuento'])}",
    ])

    if credito:
        lineas.extend([
            "",
            "CRÉDITO",
            "-" * 42,
            f"Total deuda: ${formatear_numero(credito['Total_Deuda'])}",
            f"Saldo pendiente: ${formatear_numero(credito['Saldo_Pendiente'])}",
            f"Fecha límite: {credito['Fecha_Limite']}",
        ])
        if pagos:
            lineas.extend(["", "ABONOS", "-" * 42])
            for pago in pagos:
                fecha_pago = pago.Fecha_Registro
                if hasattr(fecha_pago, "strftime"):
                    fecha_pago = fecha_pago.strftime("%d/%m/%Y %H:%M")
                lineas.append(
                    f"{fecha_pago} | ${formatear_numero(pago.Monto)} | "
                    f"{pago.metodopago} | {pago.tipopago}"
                )

    return "\n".join(lineas)
