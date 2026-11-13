"""Utilidades comunes de las pruebas: genera el XML y consulta elementos por XPath."""
import unittest

from lxml import etree

from facturacion_xml import GeneradorFacturaXml
from facturacion_xml.ejemplo import factura_ejemplo

NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


class PruebaXml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generador = GeneradorFacturaXml()   # carga y compila el XSD una sola vez

    def generar(self, factura=None):
        """Devuelve (bytes del XML, raíz parseada)."""
        xml = self.generador.generar(factura or factura_ejemplo())
        return xml, etree.fromstring(xml)

    def elementos(self, nodo, xpath):
        return nodo.xpath(xpath, namespaces=NS)

    def uno(self, nodo, xpath):
        """El único elemento que cumple el XPath; falla si hay 0 o más de 1."""
        encontrados = self.elementos(nodo, xpath)
        self.assertEqual(len(encontrados), 1, f"{xpath}: se esperaba 1 elemento y hay {len(encontrados)}")
        return encontrados[0]

    def texto(self, nodo, xpath):
        return self.uno(nodo, xpath).text

    def atributo(self, nodo, xpath, nombre):
        return self.uno(nodo, xpath).get(nombre)

    def linea(self, raiz, numero):
        """La línea de factura número `numero` (desde 1)."""
        return self.uno(raiz, f"cac:InvoiceLine[cbc:ID='{numero}']")
