import sys
import traceback

from PyQt6.QtWidgets import QApplication

from app.view.PagoCreditoView import PagoCredito_View

app = QApplication(sys.argv)

try:
    ventana = PagoCredito_View()
    ventana.show()
    print("Ventana creada y show() llamado correctamente")
except Exception:
    traceback.print_exc()

sys.exit(app.exec())
