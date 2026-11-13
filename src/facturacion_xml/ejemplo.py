"""Factura de ejemplo con los cuatro tipos de afectación y textos con caracteres especiales del español.

Todos los datos son ficticios. Sirve para la demostración (`python -m facturacion_xml`) y para las pruebas.
"""
from datetime import date, time
from decimal import Decimal

from .dominio import DetalleFactura, Emisor, Factura, FormaPago, Receptor, TipoAfectacion


def emisor_ejemplo() -> Emisor:
    return Emisor(ruc="20123456786", razon_social="Distribuidora Peña & Cañete S.A.C.",
                  nombre_comercial="Abarrotes Ñandú", direccion="Jr. Progreso N° 123 – Tingo María",
                  ubigeo="100901", departamento="HUÁNUCO", provincia="LEONCIO PRADO", distrito="RUPA-RUPA")


def receptor_ejemplo() -> Receptor:
    return Receptor(numero_documento="20456789014", razon_social="Bodega “El Sol” E.I.R.L.")


def detalles_ejemplo() -> tuple[DetalleFactura, ...]:
    return (
        DetalleFactura("ARR-001", "Arroz extra “Selecto” saco 50 kg", "BG", Decimal("10"), Decimal("120.00"),
                       TipoAfectacion.GRAVADO),
        DetalleFactura("SRV-001", "Servicio de transporte <local>", "ZZ", Decimal("1"), Decimal("50.00"),
                       TipoAfectacion.GRAVADO),
        DetalleFactura("PLA-001", "Plátano de seda (fruta fresca)", "KGM", Decimal("25"), Decimal("2.50"),
                       TipoAfectacion.EXONERADO),
        DetalleFactura("SRV-002", "Servicio de ejemplo inafecto", "ZZ", Decimal("1"), Decimal("30.00"),
                       TipoAfectacion.INAFECTO),
        DetalleFactura("MUE-001", "Muestra gratuita: azúcar rubia 1 kg", "KGM", Decimal("2"), Decimal("3.50"),
                       TipoAfectacion.GRATUITO),
    )


def factura_ejemplo(**cambios) -> Factura:
    """Factura F001-00000001 al contado. `cambios` reemplaza campos (p. ej. detalles=..., forma_pago=...)."""
    datos = dict(emisor=emisor_ejemplo(), receptor=receptor_ejemplo(), serie="F001", correlativo=1,
                 fecha_emision=date(2026, 11, 6), hora_emision=time(10, 30, 0), detalles=detalles_ejemplo(),
                 forma_pago=FormaPago())
    datos.update(cambios)
    return Factura(**datos)
