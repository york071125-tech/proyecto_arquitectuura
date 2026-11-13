"""Monto en letras para la leyenda 1000 de la factura: «SON: MIL CON 50/100 SOLES» (RN-045)."""
from decimal import Decimal

from .calculo import redondear
from .catalogos import MONEDAS

_BASICOS = [
    "CERO", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ", "ONCE", "DOCE",
    "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUNO",
    "VEINTIDÓS", "VEINTITRÉS", "VEINTICUATRO", "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE",
]
_DECENAS = {3: "TREINTA", 4: "CUARENTA", 5: "CINCUENTA", 6: "SESENTA", 7: "SETENTA", 8: "OCHENTA", 9: "NOVENTA"}
_CENTENAS = {1: "CIENTO", 2: "DOSCIENTOS", 3: "TRESCIENTOS", 4: "CUATROCIENTOS", 5: "QUINIENTOS",
             6: "SEISCIENTOS", 7: "SETECIENTOS", 8: "OCHOCIENTOS", 9: "NOVECIENTOS"}


def _menor_de_mil(n: int) -> str:
    if n == 100:
        return "CIEN"
    partes = []
    centenas, resto = divmod(n, 100)
    if centenas:
        partes.append(_CENTENAS[centenas])
    if 0 < resto < 30:
        partes.append(_BASICOS[resto])
    elif resto >= 30:
        decenas, unidad = divmod(resto, 10)
        partes.append(_DECENAS[decenas] + (f" Y {_BASICOS[unidad]}" if unidad else ""))
    return " ".join(partes)


def _apocopar(texto: str) -> str:
    """«UNO» antes de MIL o MILLONES se dice «UN» (VEINTIÚN MIL, TREINTA Y UN MIL)."""
    if texto.endswith("VEINTIUNO"):
        return texto[: -len("VEINTIUNO")] + "VEINTIÚN"
    return texto[:-1] if texto.endswith("UNO") else texto


def entero_en_letras(n: int) -> str:
    if n < 0 or n >= 10**12:
        raise ValueError("El monto debe estar entre 0 y 999 999 999 999")
    if n == 0:
        return "CERO"
    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1000)
    partes = []
    if millones:
        partes.append("UN MILLÓN" if millones == 1 else f"{_apocopar(entero_en_letras(millones))} MILLONES")
    if miles:
        partes.append("MIL" if miles == 1 else f"{_apocopar(_menor_de_mil(miles))} MIL")
    if unidades:
        partes.append(_menor_de_mil(unidades))
    return " ".join(partes)


def monto_en_letras(importe: Decimal, moneda: str = "PEN") -> str:
    importe = redondear(importe)
    enteros, centavos = divmod(int(importe * 100), 100)
    return f"SON: {entero_en_letras(enteros)} CON {centavos:02d}/100 {MONEDAS[moneda]}"
