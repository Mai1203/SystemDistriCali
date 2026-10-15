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
        f"Nombre: {cliente.get('Nombre', '')} {cliente.get('Apellido', '')}".strip(),
        f"Identificación: {cliente.get('ID_Cliente', '')}",
        f"Teléfono: {cliente.get('Teléfono') or cliente.get('telefono') or 'No registrado'}",
        f"Dirección: {cliente.get('Direccion') or cliente.get('direccion') or 'No registrada'}",
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

    subtotal = sum(detalle.get("Subtotal", 0) for detalle in detalles)
    descuento = float(factura.get("Descuento", 0) or 0)
    total = subtotal - descuento
    lineas.extend([
        "",
        f"Subtotal: ${formatear_numero(subtotal)}",
        f"Descuento: ${formatear_numero(descuento)}",
        f"TOTAL: ${formatear_numero(total)}",
    ])

    if credito:
        fecha_lim = credito.get('Fecha_Limite', '') if isinstance(credito, dict) else getattr(credito, 'Fecha_Limite', '')
        if hasattr(fecha_lim, "strftime"):
            fecha_lim = fecha_lim.strftime("%d/%m/%Y")
        total_deuda = credito.get('Total_Deuda', 0) if isinstance(credito, dict) else getattr(credito, 'Total_Deuda', 0)
        saldo_pend = credito.get('Saldo_Pendiente', 0) if isinstance(credito, dict) else getattr(credito, 'Saldo_Pendiente', 0)
        lineas.extend([
            "",
            "CRÉDITO",
            "-" * 42,
            f"Total deuda: ${formatear_numero(total_deuda)}",
            f"Saldo pendiente: ${formatear_numero(saldo_pend)}",
            f"Fecha límite: {fecha_lim}",
        ])
        if pagos:
            lineas.extend(["", "ABONOS", "-" * 42])
            for pago in pagos:
                fecha_pago = getattr(pago, "Fecha_Registro", None) if not isinstance(pago, dict) else pago.get("Fecha_Registro")
                if hasattr(fecha_pago, "strftime"):
                    fecha_pago = fecha_pago.strftime("%d/%m/%Y %H:%M")
                monto = getattr(pago, "Monto", 0) if not isinstance(pago, dict) else pago.get("Monto", 0)
                metodo = getattr(pago, "metodopago", "") if not isinstance(pago, dict) else pago.get("metodopago", "")
                tipo = getattr(pago, "tipopago", "") if not isinstance(pago, dict) else pago.get("tipopago", "")
                lineas.append(
                    f"{fecha_pago} | ${formatear_numero(monto)} | "
                    f"{metodo} | {tipo}"
                )

    return "\n".join(lineas)
