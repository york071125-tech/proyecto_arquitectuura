"""Modelo de dominio de la factura electrónica, con los nombres del negocio.

Las clases validan sus datos al crearse: una `Factura` que existe es una factura coherente.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal, InvalidOperation
from enum import Enum

from .catalogos import (MONEDAS, MOTIVOS_GRATUITO, TIPO_DOC_IDENTIDAD_RUC, TIPO_OPERACION_VENTA_INTERNA,
                        UNIDADES_MEDIDA)
from .errores import FacturaInvalidaError


class TipoAfectacion(Enum):
    """Los cuatro tipos de afectación. Valor: (código, tributo cat. 05, nombre, tipo internacional, categoría, afectación cat. 07)."""

    GRAVADO = ("1001", "1000", "IGV", "VAT", "S", "10")
    INAFECTO = ("1002", "9998", "INA", "FRE", "O", "30")
    EXONERADO = ("1003", "9997", "EXO", "VAT", "E", "20")
    GRATUITO = ("1004", "9996", "GRA", "FRE", "Z", "21")

    def __init__(self, codigo, id_tributo, nombre_tributo, tipo_internacional, categoria, codigo_afectacion_igv):
        self.codigo = codigo
        self.id_tributo = id_tributo
        self.nombre_tributo = nombre_tributo
        self.tipo_internacional = tipo_internacional
        self.categoria = categoria
        self.codigo_afectacion_igv = codigo_afectacion_igv

    @classmethod
    def desde_codigo(cls, codigo: str) -> "TipoAfectacion":
        for tipo in cls:
            if tipo.codigo == codigo:
                return tipo
        raise FacturaInvalidaError(f"Tipo de afectación desconocido: {codigo!r} (use 1001, 1002, 1003 o 1004)")


def a_decimal(valor, campo: str) -> Decimal:
    """Convierte a Decimal. Rechaza float: los importes se manejan con decimales exactos (ADR-04)."""
    if isinstance(valor, float):
        raise FacturaInvalidaError(f"{campo}: use Decimal, int o str; un float no es exacto")
    try:
        return valor if isinstance(valor, Decimal) else Decimal(str(valor))
    except InvalidOperation:
        raise FacturaInvalidaError(f"{campo}: no es un número decimal: {valor!r}") from None


def ruc_valido(ruc: str) -> bool:
    """RUC de 11 dígitos con prefijo 10, 15, 16, 17 o 20 y dígito verificador módulo 11 (RN-010)."""
    if not re.fullmatch(r"(10|15|16|17|20)[0-9]{9}", ruc):
        return False
    pesos = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
    suma = sum(int(d) * p for d, p in zip(ruc[:10], pesos))
    verificador = 11 - suma % 11
    verificador = {10: 0, 11: 1}.get(verificador, verificador)
    return verificador == int(ruc[10])


@dataclass(frozen=True)
class Emisor:
    ruc: str
    razon_social: str
    nombre_comercial: str
    direccion: str
    ubigeo: str
    departamento: str
    provincia: str
    distrito: str
    codigo_establecimiento: str = "0000"

    def __post_init__(self):
        if not ruc_valido(self.ruc):
            raise FacturaInvalidaError(f"RUC del emisor inválido: {self.ruc!r}")
        if not self.razon_social.strip():
            raise FacturaInvalidaError("La razón social del emisor es obligatoria")
        if not re.fullmatch(r"[0-9]{6}", self.ubigeo):
            raise FacturaInvalidaError(f"UBIGEO inválido (6 dígitos): {self.ubigeo!r}")
        if not re.fullmatch(r"[0-9]{4}", self.codigo_establecimiento):
            raise FacturaInvalidaError("El código de establecimiento tiene 4 dígitos")


@dataclass(frozen=True)
class Receptor:
    """Adquirente. En una factura debe identificarse con RUC (RN-012)."""

    numero_documento: str
    razon_social: str
    tipo_documento: str = TIPO_DOC_IDENTIDAD_RUC
    direccion: str | None = None

    def __post_init__(self):
        if self.tipo_documento != TIPO_DOC_IDENTIDAD_RUC:
            raise FacturaInvalidaError("Una factura exige receptor con RUC (tipo de documento 6)")
        if not ruc_valido(self.numero_documento):
            raise FacturaInvalidaError(f"RUC del receptor inválido: {self.numero_documento!r}")
        if not self.razon_social.strip():
            raise FacturaInvalidaError("La razón social del receptor es obligatoria")


@dataclass(frozen=True)
class DetalleFactura:
    """Una línea de la factura: un producto o servicio."""

    codigo: str
    descripcion: str
    unidad: str
    cantidad: Decimal
    valor_unitario: Decimal            # sin impuestos; en un gratuito es el valor referencial
    tipo_afectacion: TipoAfectacion = TipoAfectacion.GRAVADO
    motivo_gratuito: str | None = None  # catálogo 07; solo para TipoAfectacion.GRATUITO

    def __post_init__(self):
        object.__setattr__(self, "cantidad", a_decimal(self.cantidad, "cantidad"))
        object.__setattr__(self, "valor_unitario", a_decimal(self.valor_unitario, "valor_unitario"))
        if not self.descripcion.strip():
            raise FacturaInvalidaError("La descripción del producto es obligatoria")
        if self.unidad not in UNIDADES_MEDIDA:
            raise FacturaInvalidaError(f"Unidad de medida fuera del catálogo 03: {self.unidad!r}")
        if self.cantidad <= 0:
            raise FacturaInvalidaError("La cantidad debe ser mayor que cero")
        if self.valor_unitario < 0:
            raise FacturaInvalidaError("El valor unitario no puede ser negativo")
        if self.tipo_afectacion is TipoAfectacion.GRATUITO:
            motivo = self.motivo_gratuito or self.tipo_afectacion.codigo_afectacion_igv
            if motivo not in MOTIVOS_GRATUITO:
                raise FacturaInvalidaError(f"Motivo de transferencia gratuita inválido: {motivo!r}")
            object.__setattr__(self, "motivo_gratuito", motivo)
        elif self.motivo_gratuito is not None:
            raise FacturaInvalidaError("motivo_gratuito solo aplica a la afectación 1004 (gratuito)")

    @property
    def codigo_afectacion_igv(self) -> str:
        return self.motivo_gratuito or self.tipo_afectacion.codigo_afectacion_igv


@dataclass(frozen=True)
class Cuota:
    monto: Decimal
    fecha_vencimiento: date

    def __post_init__(self):
        object.__setattr__(self, "monto", a_decimal(self.monto, "monto de la cuota"))
        if self.monto <= 0:
            raise FacturaInvalidaError("El monto de una cuota debe ser mayor que cero")


@dataclass(frozen=True)
class FormaPago:
    """Obligatoria en toda factura: contado o crédito con cuotas (RS 193-2020)."""

    cuotas: tuple[Cuota, ...] = ()

    @property
    def es_credito(self) -> bool:
        return bool(self.cuotas)


@dataclass(frozen=True)
class Factura:
    emisor: Emisor
    receptor: Receptor
    serie: str
    correlativo: int
    fecha_emision: date
    hora_emision: time
    detalles: tuple[DetalleFactura, ...]
    moneda: str = "PEN"
    forma_pago: FormaPago = field(default_factory=FormaPago)
    tasa_igv: Decimal = Decimal("18.00")   # parámetro explícito: 10 % (restaurantes y hoteles) solo si se pasa expresamente
    tipo_operacion: str = TIPO_OPERACION_VENTA_INTERNA
    fecha_vencimiento: date | None = None

    def __post_init__(self):
        object.__setattr__(self, "tasa_igv", a_decimal(self.tasa_igv, "tasa_igv"))
        object.__setattr__(self, "detalles", tuple(self.detalles))
        if not re.fullmatch(r"F[A-Z0-9]{3}", self.serie):
            raise FacturaInvalidaError(f"Serie de factura inválida (F + 3 caracteres): {self.serie!r}")
        if not 1 <= self.correlativo <= 99_999_999:
            raise FacturaInvalidaError("El correlativo va de 1 a 99 999 999")
        if not self.detalles:
            raise FacturaInvalidaError("La factura necesita al menos un detalle")
        if self.moneda not in MONEDAS:
            raise FacturaInvalidaError(f"Moneda no soportada: {self.moneda!r}")
        if not Decimal("0") <= self.tasa_igv <= Decimal("100"):
            raise FacturaInvalidaError("La tasa del IGV debe estar entre 0 y 100")
        if self.fecha_vencimiento and self.fecha_vencimiento < self.fecha_emision:
            raise FacturaInvalidaError("La fecha de vencimiento no puede ser anterior a la emisión")

    @property
    def numero(self) -> str:
        """Serie y correlativo: F001-00000001."""
        return f"{self.serie}-{self.correlativo:08d}"
