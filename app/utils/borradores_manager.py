"""
borradores_manager.py
Gestiona los borradores de ventas de forma independiente por tipo:
  - tipo = 'normal'  -> borradores de Ventas Normales (Contado)
  - tipo = 'credito' -> borradores de Ventas a Credito
Los borradores se almacenan como archivos JSON en la carpeta `borradores/`
dentro del directorio raiz de la aplicacion.
"""

import os
import json
import uuid
from datetime import datetime

# Carpeta base donde se guardan los archivos de borradores
_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "borradores"
)


def _asegurar_carpeta(tipo: str) -> str:
    """Devuelve la ruta de la carpeta para el tipo dado, creandola si no existe."""
    carpeta = os.path.join(_BASE_DIR, tipo)
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def guardar_borrador(tipo: str, datos: dict) -> str:
    """
    Guarda un borrador de venta.
    :param tipo: 'normal' o 'credito'
    :param datos: dict con la informacion de la venta en curso
    :return: ID unico del borrador guardado
    """
    carpeta = _asegurar_carpeta(tipo)
    borrador_id = str(uuid.uuid4())
    datos_guardados = {
        "id": borrador_id,
        "tipo": tipo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "datos": datos,
    }
    ruta = os.path.join(carpeta, f"{borrador_id}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos_guardados, f, ensure_ascii=False, indent=2)
    return borrador_id


def cargar_borradores(tipo: str) -> list:
    """
    Carga todos los borradores de un tipo especifico.
    :param tipo: 'normal' o 'credito'
    :return: Lista de dicts con los borradores, ordenados por fecha descendente
    """
    carpeta = _asegurar_carpeta(tipo)
    borradores = []
    for nombre_archivo in os.listdir(carpeta):
        if nombre_archivo.endswith(".json"):
            ruta = os.path.join(carpeta, nombre_archivo)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    b = json.load(f)
                    borradores.append(b)
            except (json.JSONDecodeError, KeyError):
                pass  # Ignorar archivos corruptos
    # Ordenar por fecha descendente (mas reciente primero)
    borradores.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    return borradores


def eliminar_borrador(borrador_id: str) -> bool:
    """
    Elimina un borrador por su ID buscando en ambas carpetas (normal y credito).
    :param borrador_id: ID unico del borrador
    :return: True si se elimino, False si no se encontro
    """
    for tipo in ("normal", "credito"):
        carpeta = os.path.join(_BASE_DIR, tipo)
        if not os.path.isdir(carpeta):
            continue
        ruta = os.path.join(carpeta, f"{borrador_id}.json")
        if os.path.isfile(ruta):
            os.remove(ruta)
            return True
    return False


def contar_borradores(tipo: str) -> int:
    """
    Cuenta cuantos borradores hay para el tipo dado.
    :param tipo: 'normal' o 'credito'
    :return: Numero de borradores
    """
    carpeta = _asegurar_carpeta(tipo)
    return sum(1 for f in os.listdir(carpeta) if f.endswith(".json"))
