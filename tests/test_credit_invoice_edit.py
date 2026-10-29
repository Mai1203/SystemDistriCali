from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.models.detalle_facturas import DetalleFacturas
from app.models.facturas import Facturas
from app.view.VentasCreditoView import VentasCredito_View


def test_credit_invoice_edit_saves_updated_and_new_product_prices():
    existing_detail = SimpleNamespace(
        ID_Producto=10,
        ID_Lote=None,
        Cantidad=2,
        Precio_unitario=100.0,
        Subtotal=200.0,
    )
    invoice = SimpleNamespace()
    db = MagicMock()
    details_query = MagicMock()
    details_query.filter.return_value = details_query
    details_query.all.return_value = [existing_detail]
    details_query.first.return_value = existing_detail
    invoice_query = MagicMock()
    invoice_query.filter.return_value = invoice_query
    invoice_query.first.return_value = invoice
    db.query.side_effect = lambda model: {
        DetalleFacturas: details_query,
        Facturas: invoice_query,
    }[model]
    view_state = SimpleNamespace(invoice_number=42, id_venta_credito=7)
    new_product_data = []

    def capture_new_detail(detail):
        new_product_data.append(detail)

    db.add.side_effect = capture_new_detail

    with (
        patch(
            "app.view.VentasCreditoView.obtener_ventaCredito_id",
            return_value=[SimpleNamespace(Total_Deuda=200.0, Saldo_Pendiente=200.0)],
        ),
        patch("app.view.VentasCreditoView.actualizar_venta_credito"),
        patch("app.view.VentasCreditoView.crear_historial_modificacion"),
        patch("app.view.VentasCreditoView.descontar_stock_lote"),
    ):
        VentasCredito_View.actualizar_factura(
            view_state,
            db,
            42,
            [
                (10, 2, 150.0, None),
                (20, 1, 250.0, 5),
            ],
            "user-1",
            550.0,
            0.0,
            None,
        )

    assert existing_detail.Precio_unitario == 150.0
    assert existing_detail.Subtotal == 300.0
    assert len(new_product_data) == 1
    assert new_product_data[0].Precio_unitario == 250.0
    assert new_product_data[0].Subtotal == 250.0
    assert view_state.invoice_number == 42
    assert view_state.id_venta_credito == 7
