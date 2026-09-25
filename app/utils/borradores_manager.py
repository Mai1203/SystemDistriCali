import os
import json
import time
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
BORRADORES_FILE = os.path.join(DATA_DIR, "borradores.json")


def _asegurar_directorio():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BORRADORES_FILE):
        with open(BORRADORES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def cargar_borradores(solo_credito=None):
    """
    Carga los borradores guardados.
    :param solo_credito:
        - True: devuelve solo borradores de Ventas a Crédito (tipo_venta == 4)
        - False: devuelve solo borradores de Ventas de Contado (tipo_venta != 4)
        - None: devuelve todos los borradores
    """
    _asegurar_directorio()
    try:
        with open(BORRADORES_FILE, "r", encoding="utf-8") as f:
            borradores = json.load(f)
            if solo_credito is True:
                return [b for b in borradores if b.get("tipo_venta") == 4]
            elif solo_credito is False:
                return [b for b in borradores if b.get("tipo_venta") != 4]
            return borradores
    except Exception:
        return []


def guardar_borrador(referencia: str, cliente_data: dict, items: list, domicilio: float = 0.0, descuento: float = 0.0, tipo_venta: int = 0):
    _asegurar_directorio()
    borradores = cargar_borradores(solo_credito=None)
    
    nuevo_borrador = {
        "id": f"draft_{int(time.time() * 1000)}",
        "fecha": datetime.now().strftime("%d/%m/%Y %I:%M %p"),
        "referencia": referencia or (cliente_data.get("nombre") if cliente_data else "Venta sin nombre"),
        "tipo_venta": tipo_venta,
        "cliente": cliente_data or {},
        "items": items,
        "domicilio": domicilio,
        "descuento": descuento,
    }
    
    borradores.insert(0, nuevo_borrador)  # El más reciente primero
    with open(BORRADORES_FILE, "w", encoding="utf-8") as f:
        json.dump(borradores, f, ensure_ascii=False, indent=2)
    return nuevo_borrador


def eliminar_borrador(borrador_id: str):
    _asegurar_directorio()
    borradores = cargar_borradores(solo_credito=None)
    borradores_filtrados = [b for b in borradores if b.get("id") != borrador_id]
    with open(BORRADORES_FILE, "w", encoding="utf-8") as f:
        json.dump(borradores_filtrados, f, ensure_ascii=False, indent=2)
    return len(borradores) != len(borradores_filtrados)


def obtener_borrador_por_id(borrador_id: str):
    borradores = cargar_borradores(solo_credito=None)
    for b in borradores:
        if b.get("id") == borrador_id:
            return b
    return None
