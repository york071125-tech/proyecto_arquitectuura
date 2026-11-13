"""Validación del XML contra el XSD oficial Invoice UBL 2.1 (OASIS).

El XSD valida la ESTRUCTURA (nombres, orden, cardinalidad, tipos). Las reglas tributarias de SUNAT
(cálculos, catálogos) se comprueban en el dominio y en las pruebas, no aquí.
"""
from functools import lru_cache
from pathlib import Path

from lxml import etree

from .errores import XmlInvalidoError, XsdNoEncontradoError

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_XSD_INVOICE = RAIZ_PROYECTO / "specs" / "contracts" / "ubl-2.1" / "xsd" / "maindoc" / "UBL-Invoice-2.1.xsd"

# Parser seguro: sin red y sin entidades externas.
_PARSER = etree.XMLParser(no_network=True, resolve_entities=False)


class ValidadorXsd:
    def __init__(self, ruta_xsd: Path = RUTA_XSD_INVOICE):
        if not Path(ruta_xsd).is_file():
            raise XsdNoEncontradoError(Path(ruta_xsd))
        self._esquema = etree.XMLSchema(etree.parse(str(ruta_xsd), _PARSER))

    def errores(self, xml: bytes) -> list[str]:
        """Lista de errores; vacía si el XML es válido."""
        try:
            documento = etree.fromstring(xml, _PARSER)
        except etree.XMLSyntaxError as error:
            return [f"XML mal formado: {error}"]
        self._esquema.validate(documento)
        return [f"línea {e.line}: {e.message}" for e in self._esquema.error_log]

    def es_valido(self, xml: bytes) -> bool:
        return not self.errores(xml)

    def exigir_valido(self, xml: bytes) -> None:
        errores = self.errores(xml)
        if errores:
            raise XmlInvalidoError(errores)


@lru_cache(maxsize=1)
def validador_invoice() -> ValidadorXsd:
    """Carga el XSD una sola vez (pesa 2,8 MB y tarda en compilarse)."""
    return ValidadorXsd()
