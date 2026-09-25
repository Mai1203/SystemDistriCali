import os
import sys

# Agregar el directorio raíz al path para poder importar la app
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.database import SessionLocal
from app.models.productos import Productos
from app.models.lotes import LoteProducto
from sqlalchemy import func, desc

def arreglar_stock():
    db = SessionLocal()
    try:
        productos = db.query(Productos).all()
        arreglados = 0
        
        for p in productos:
            lotes_existentes = db.query(LoteProducto).filter(LoteProducto.ID_Producto == p.ID_Producto).all()
            if not lotes_existentes:
                stock_producto = p.Stock_actual or 0
                nuevo_lote = LoteProducto(
                    ID_Producto=p.ID_Producto,
                    Numero_Lote="LOTE-001",
                    Stock_inicial=stock_producto,
                    Stock_actual=stock_producto,
                    Precio_costo=p.Precio_costo or 0,
                    Precio_venta_1=p.Precio_venta_1 or 0,
                    Precio_venta_2=p.Precio_venta_2 or 0,
                    Precio_venta_3=p.Precio_venta_3 or 0,
                    Precio_venta_4=p.Precio_venta_4 or 0,
                    Ganancia_1=p.Ganancia_1 or 0,
                    Ganancia_2=p.Ganancia_2 or 0,
                    Ganancia_3=p.Ganancia_3 or 0,
                    Ganancia_4=p.Ganancia_4 or 0,
                    Estado=stock_producto > 0,
                    Proveedor="Ajuste automático",
                    Notas="Lote creado para arreglar desincronización antigua"
                )
                db.add(nuevo_lote)
                print(f"Producto {p.ID_Producto} ({p.Nombre}): Sin lotes. Creando lote inicial con stock={stock_producto}")
                arreglados += 1
            else:
                total_lotes = sum(l.Stock_actual or 0 for l in lotes_existentes)
                if p.Stock_actual != total_lotes:
                    print(f"Producto {p.ID_Producto} ({p.Nombre}): Stock_Producto={p.Stock_actual} -> Total_Lotes={total_lotes} (ajustando producto)")
                    p.Stock_actual = total_lotes
                    p.Estado = total_lotes > 0
                    arreglados += 1
                
        db.commit()
        print(f"\nSe arreglaron {arreglados} productos con diferencias.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    arreglar_stock()
