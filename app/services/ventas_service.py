class VentasService:
    @staticmethod
    def calcular_total(subtotal, domicilio=0.0, descuento=0.0):
        return (subtotal + domicilio) - descuento

    @staticmethod
    def validar_pago(metodo_pago, monto_pago, subtotal):
        return _validar_pago(metodo_pago, monto_pago, subtotal)


def calcular_total_venta(subtotal, domicilio=0.0, descuento=0.0):
    return VentasService.calcular_total(subtotal, domicilio, descuento)


def validar_pago(metodo_pago, monto_pago, subtotal):
    return VentasService.validar_pago(metodo_pago, monto_pago, subtotal)


def _validar_pago(metodo_pago, monto_pago, subtotal):
    if not monto_pago:
        return "El campo 'Pago' está vacío."

    try:
        if metodo_pago in ("Efectivo", "Transferencia"):
            if float(monto_pago) > subtotal:
                return "El monto pagado no puede ser mayor al subtotal."
            return None

        if metodo_pago == "Mixto":
            partes = monto_pago.split("/")
            if len(partes) != 2 or not partes[0] or not partes[1]:
                return "Ingrese efectivo y transferencia separados por '/'."
            efectivo = float(partes[0])
            transferencia = float(partes[1])
            if efectivo == 0 or transferencia == 0:
                return "Ingrese un valor mayor que cero para ambos pagos."
            if efectivo + transferencia > subtotal:
                return "El monto pagado no puede ser mayor al subtotal."
            return None

        return "Método de pago no válido."
    except (TypeError, ValueError):
        return "Ingrese un monto de pago válido."
