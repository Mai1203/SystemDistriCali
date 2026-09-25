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
            stock_producto = p.Stock_actual or 0
            
            # Obtener suma de stock en lotes
            total_lotes = db.query(func.coalesce(func.sum(LoteProducto.Stock_actual), 0)).filter(LoteProducto.ID_Producto == p.ID_Producto).scalar()
            
            if stock_producto != total_lotes:
                diferencia = stock_producto - total_lotes
                print(f"Producto {p.ID_Producto} ({p.Nombre}): Stock_Producto={stock_producto}, Total_Lotes={total_lotes}. Diferencia={diferencia}")
                
                if diferencia != 0:
                    # Buscar el lote más reciente
                    lote_objetivo = db.query(LoteProducto).filter(LoteProducto.ID_Producto == p.ID_Producto).order_by(desc(LoteProducto.ID_Lote)).first()
                    
                    if lote_objetivo:
                        # Aplicarle la diferencia al lote
                        nuevo_stock_lote = max(0, lote_objetivo.Stock_actual + diferencia)
                        lote_objetivo.Stock_actual = nuevo_stock_lote
                        lote_objetivo.Estado = nuevo_stock_lote > 0
                        print(f"  -> Actualizando lote {lote_objetivo.ID_Lote} (Lote: {lote_objetivo.Numero_Lote}) a {nuevo_stock_lote}")
                    else:
                        # Crear lote nuevo
                        nuevo_lote = LoteProducto(
                            ID_Producto=p.ID_Producto,
                            Numero_Lote="LOTE-RECONCILIACION",
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
                        print(f"  -> Creando nuevo lote para cubrir {stock_producto}")
                    
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
