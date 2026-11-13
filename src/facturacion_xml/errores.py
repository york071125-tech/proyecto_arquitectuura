"""Errores propios del generador de facturas XML."""
from pathlib import Path


class FacturaInvalidaError(ValueError):
    """Un dato del dominio incumple una regla (RUC, serie, cantidad, unidad...)."""


class XmlInvalidoError(ValueError):
    """El XML generado no cumple el XSD de Invoice UBL 2.1."""

    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__("El XML no es válido contra el XSD:\n" + "\n".join(errores))


class XsdNoEncontradoError(FileNotFoundError):
    """No está el archivo XSD: sin él no se puede afirmar que el XML sea válido."""

    def __init__(self, ruta: Path):
        super().__init__(f"No se encontró el XSD en {ruta}. Ver specs/contracts/ubl-2.1/README.md")
