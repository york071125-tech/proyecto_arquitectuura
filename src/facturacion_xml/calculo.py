"""Cálculo de importes de la factura con Decimal exacto (ADR-04).

Reglas: redondeo half-up a 2 decimales por línea (RN-021) y totales como suma de líneas (RN-022).
"""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .dominio import DetalleFactura, Factura, TipoAfectacion
from .errores import FacturaInvalidaError

CENTAVOS = Decimal("0.01")
CERO = Decimal("0.00")


def redondear(importe: Decimal) -> Decimal:
    """Redondea a 2 decimales, mitad hacia arriba."""
    return importe.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ImportesLinea:
    detalle: DetalleFactura
    valor_venta: Decimal        # LineExtensionAmount; en un gratuito es 0.00
    valor_referencial: Decimal  # solo gratuitos: cantidad × valor unitario
    base_igv: Decimal           # monto sobre el que se declara el tributo de la línea
    igv: Decimal
    precio_unitario: Decimal    # con IGV si es gravado; valor referencial unitario si es gratuito


@dataclass(frozen=True)
class TotalesFactura:
    lineas: tuple[ImportesLinea, ...]
    total_gravado: Decimal
    total_inafecto: Decimal
    total_exonerado: Decimal
    total_gratuito: Decimal      # valor referencial; no suma al importe total
    total_igv: Decimal
    importe_total: Decimal

    @property
    def valor_venta_total(self) -> Decimal:
        """Total valor de venta de las operaciones onerosas (sin impuestos)."""
        return self.total_gravado + self.total_inafecto + self.total_exonerado


def calcular_linea(detalle: DetalleFactura, tasa_igv: Decimal) -> ImportesLinea:
    bruto = detalle.cantidad * detalle.valor_unitario
    tipo = detalle.tipo_afectacion
    if tipo is TipoAfectacion.GRATUITO:
        referencial = redondear(bruto)
        return ImportesLinea(detalle, CERO, referencial, referencial, CERO, detalle.valor_unitario)
    valor_venta = redondear(bruto)
    if tipo is TipoAfectacion.GRAVADO:
        factor = tasa_igv / 100
        precio = (detalle.valor_unitario * (1 + factor)).quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP)
        return ImportesLinea(detalle, valor_venta, CERO, valor_venta, redondear(valor_venta * factor), precio)
    return ImportesLinea(detalle, valor_venta, CERO, valor_venta, CERO, detalle.valor_unitario)


def calcular_totales(factura: Factura) -> TotalesFactura:
    lineas = tuple(calcular_linea(d, factura.tasa_igv) for d in factura.detalles)

    def suma(tipo, campo="valor_venta"):
        return sum((getattr(l, campo) for l in lineas if l.detalle.tipo_afectacion is tipo), CERO)

    gravado = suma(TipoAfectacion.GRAVADO)
    inafecto = suma(TipoAfectacion.INAFECTO)
    exonerado = suma(TipoAfectacion.EXONERADO)
    gratuito = suma(TipoAfectacion.GRATUITO, "valor_referencial")
    igv = sum((l.igv for l in lineas), CERO)
    return TotalesFactura(lineas, gravado, inafecto, exonerado, gratuito, igv, gravado + inafecto + exonerado + igv)


def validar_forma_pago(factura: Factura, totales: TotalesFactura) -> None:
    """RN-081: en un crédito, las cuotas suman el importe total y sus fechas no retroceden."""
    if not factura.forma_pago.es_credito:
        return
    cuotas = factura.forma_pago.cuotas
    if sum((c.monto for c in cuotas), CERO) != totales.importe_total:
        raise FacturaInvalidaError("Las cuotas no suman el importe total de la factura")
    previa = factura.fecha_emision
    for cuota in cuotas:
        if cuota.fecha_vencimiento < previa:
            raise FacturaInvalidaError("Las fechas de vencimiento de las cuotas no pueden retroceder")
        previa = cuota.fecha_vencimiento
