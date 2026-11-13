"""Coherencia del generador con el resto del proyecto: catálogos del contrato JSON y XML de ejemplo versionado."""
import json
import unittest

from lxml import etree

from facturacion_xml import GeneradorFacturaXml
from facturacion_xml.catalogos import MONEDAS, MOTIVOS_GRATUITO, UNIDADES_MEDIDA
from facturacion_xml.ejemplo import factura_ejemplo
from facturacion_xml.validador_xsd import RAIZ_PROYECTO

ESQUEMAS = RAIZ_PROYECTO / "specs" / "contracts" / "schemas"


class PruebasCatalogos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comun = json.loads((ESQUEMAS / "common.schema.json").read_text(encoding="utf-8"))["$defs"]

    def test_las_unidades_de_medida_son_las_del_contrato_json(self):
        self.assertEqual(UNIDADES_MEDIDA, set(self.comun["UnidadMedida"]["enum"]))

    def test_las_monedas_son_las_del_contrato_json(self):
        self.assertEqual(set(MONEDAS), set(self.comun["Moneda"]["enum"]))

    def test_los_motivos_gratuitos_existen_en_el_catalogo_07_del_contrato(self):
        self.assertTrue(MOTIVOS_GRATUITO <= set(self.comun["AfectacionIgv"]["enum"]))


class PruebaEjemploVersionado(unittest.TestCase):
    def test_el_xml_de_ejemplo_del_repositorio_esta_al_dia(self):
        """Si cambia el generador, hay que volver a ejecutar `python -m facturacion_xml` y versionar el XML."""
        archivo = RAIZ_PROYECTO / "specs" / "contracts" / "examples" / "xml" / "factura-ejemplo.xml"
        self.assertTrue(archivo.is_file(), "falta el XML de ejemplo: ejecute python -m facturacion_xml")
        generado = GeneradorFacturaXml().generar(factura_ejemplo())
        canonico = lambda datos: etree.tostring(etree.fromstring(datos), method="c14n")
        self.assertEqual(canonico(archivo.read_bytes()), canonico(generado))
