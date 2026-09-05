import sqlite3
import os
from pathlib import Path

app_data_dir = Path(os.getenv("APPDATA") or os.path.expanduser("~/.local/share")) / "SystemDistriMagik"
db_path = app_data_dir / "systemdistrimagik.db"

def migrate():
    print(f"Migrando BD en: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Renombrar tabla vieja
    cursor.execute("ALTER TABLE PRODUCTOS RENAME TO PRODUCTOS_OLD")

    # 2. Crear nueva tabla
    cursor.execute("""
    CREATE TABLE PRODUCTOS (
        ID_Producto INTEGER NOT NULL PRIMARY KEY,
        Nombre VARCHAR NOT NULL,
        Precio_costo FLOAT NOT NULL,
        Precio_venta_1 FLOAT NOT NULL,
        Precio_venta_2 FLOAT NOT NULL,
        Precio_venta_3 FLOAT NOT NULL,
        Precio_venta_4 FLOAT NOT NULL,
        Ganancia_1 FLOAT NOT NULL,
        Ganancia_2 FLOAT NOT NULL,
        Ganancia_3 FLOAT NOT NULL,
        Ganancia_4 FLOAT NOT NULL,
        Stock_actual INTEGER NOT NULL,
        Stock_min INTEGER NOT NULL,
        Stock_max INTEGER NOT NULL,
        Estado BOOLEAN NOT NULL,
        ID_Marca INTEGER,
        ID_Categoria INTEGER,
        FOREIGN KEY(ID_Marca) REFERENCES MARCAS (ID_Marca),
        FOREIGN KEY(ID_Categoria) REFERENCES CATEGORIAS (ID_Categoria)
    )
    """)
    
    # 3. Copiar datos viejos a la tabla nueva mapeando
    # Antiguos: Precio_venta_normal, Precio_venta_mayor, Precio_venta_1, Precio_venta_2
    # Ganancias: Ganancia_Producto_normal, Ganancia_Producto_mayor
    cursor.execute("""
    INSERT INTO PRODUCTOS (
        ID_Producto, Nombre, Precio_costo,
        Precio_venta_1, Precio_venta_2, Precio_venta_3, Precio_venta_4,
        Ganancia_1, Ganancia_2, Ganancia_3, Ganancia_4,
        Stock_actual, Stock_min, Stock_max, Estado, ID_Marca, ID_Categoria
    )
    SELECT
        ID_Producto, Nombre, Precio_costo,
        Precio_venta_normal, Precio_venta_mayor, Precio_venta_1, Precio_venta_2,
        Ganancia_Producto_normal, Ganancia_Producto_mayor, Ganancia_Producto_mayor, Ganancia_Producto_mayor,
        Stock_actual, Stock_min, Stock_max, Estado, ID_Marca, ID_Categoria
    FROM PRODUCTOS_OLD
    """)

    # 4. Eliminar tabla vieja
    cursor.execute("DROP TABLE PRODUCTOS_OLD")

    conn.commit()
    conn.close()
    print("Migración de PRODUCTOS completada exitosamente.")

if __name__ == "__main__":
    migrate()
