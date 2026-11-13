"""Aspecto 9: el XML generado pasa la validación contra Invoice XSD 2.1.

Además se comprueba que el validador NO es decorativo: rechaza XML con elementos faltantes, fuera de orden,
inexistentes, de otro espacio de nombres, mal formados o con un valor de tipo incorrecto.
"""
import copy
import hashlib
from pathlib import Path

from lxml import etree

from facturacion_xml import GeneradorFacturaXml, ValidadorXsd, XmlInvalidoError, XsdNoEncontradoError
from facturacion_xml.ejemplo import factura_ejemplo
from facturacion_xml.validador_xsd import RAIZ_PROYECTO, RUTA_XSD_INVOICE

from .base import NS, PruebaXml


def a_bytes(raiz):
    return etree.tostring(raiz, xml_declaration=True, encoding="UTF-8")


class PruebasValidacionXsd(PruebaXml):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.validador = ValidadorXsd()

    # ---- el XML generado es válido ----------------------------------------------------------------------------

    def test_el_xml_generado_pasa_la_validacion(self):
        xml, _ = self.generar()
        self.assertEqual(self.validador.errores(xml), [])
        self.assertTrue(self.validador.es_valido(xml))

    def test_validan_tambien_credito_dolares_y_cada_afectacion_por_separado(self):
        from decimal import Decimal
        from datetime import date
        from facturacion_xml import Cuota, DetalleFactura, FormaPago, TipoAfectacion
        casos = [factura_ejemplo(moneda="USD")]
        for tipo in TipoAfectacion:
            detalle = DetalleFactura("P-1", "Producto", "NIU", Decimal("3"), Decimal("7.50"), tipo)
            casos.append(factura_ejemplo(detalles=(detalle,)))
        credito = FormaPago((Cuota(Decimal("783.75"), date(2026, 12, 6)), Cuota(Decimal("783.75"), date(2027, 1, 6))))
        casos.append(factura_ejemplo(forma_pago=credito))
        for factura in casos:
            with self.subTest(moneda=factura.moneda, forma_pago=factura.forma_pago.es_credito):
                self.assertEqual(self.validador.errores(self.generador.generar(factura)), [])

    # ---- el validador rechaza XML incorrecto (no es decorativo) -----------------------------------------------

    def test_rechaza_un_xml_sin_un_elemento_obligatorio(self):
        _, raiz = self.generar()
        defectuoso = copy.deepcopy(raiz)
        defectuoso.remove(self.uno(defectuoso, "cbc:ID"))
        errores = self.validador.errores(a_bytes(defectuoso))
        self.assertTrue(errores, "el XSD debió rechazar un Invoice sin cbc:ID")

    def test_rechaza_elementos_fuera_de_orden(self):
        _, raiz = self.generar()
        defectuoso = copy.deepcopy(raiz)
        id_ = self.uno(defectuoso, "cbc:ID")
        fecha = self.uno(defectuoso, "cbc:IssueDate")
        defectuoso.remove(fecha)
        id_.addprevious(fecha)   # IssueDate antes de ID: el XSD exige otro orden
        self.assertTrue(self.validador.errores(a_bytes(defectuoso)))

    def test_rechaza_un_elemento_que_no_existe_en_el_esquema(self):
        _, raiz = self.generar()
        defectuoso = copy.deepcopy(raiz)
        etree.SubElement(defectuoso, f"{{{NS['cbc']}}}ElementoInventado").text = "x"
        errores = self.validador.errores(a_bytes(defectuoso))
        self.assertTrue(any("ElementoInventado" in e for e in errores), errores)

    def test_rechaza_un_nombre_de_etiqueta_mal_escrito(self):
        xml, _ = self.generar()
        defectuoso = xml.replace(b"IssueDate", b"IssueDat")   # abre y cierra con el error de tipeo
        self.assertTrue(self.validador.errores(defectuoso))

    def test_rechaza_otro_espacio_de_nombres(self):
        xml, _ = self.generar()
        defectuoso = xml.replace(b"Invoice-2", b"Invoice-9")
        self.assertTrue(self.validador.errores(defectuoso))

    def test_rechaza_un_valor_con_tipo_incorrecto(self):
        _, raiz = self.generar()
        defectuoso = copy.deepcopy(raiz)
        self.uno(defectuoso, "cbc:IssueDate").text = "ayer"
        self.assertTrue(self.validador.errores(a_bytes(defectuoso)))

    def test_rechaza_un_xml_mal_formado(self):
        errores = self.validador.errores(b"<Invoice><sin_cerrar></Invoice>")
        self.assertEqual(len(errores), 1)
        self.assertIn("mal formado", errores[0])

    def test_rechaza_un_documento_vacio_de_otro_tipo(self):
        self.assertTrue(self.validador.errores(b"<?xml version='1.0'?><Otro/>"))

    def test_el_error_indica_la_linea(self):
        _, raiz = self.generar()
        defectuoso = copy.deepcopy(raiz)
        defectuoso.remove(self.uno(defectuoso, "cbc:ID"))
        self.assertRegex(self.validador.errores(a_bytes(defectuoso))[0], r"^línea \d+:")

    # ---- el generador usa la validación -----------------------------------------------------------------------

    def test_el_generador_lanza_error_si_el_xsd_rechaza_el_resultado(self):
        class GeneradorDefectuoso(GeneradorFacturaXml):
            def _construir(self, factura, totales):
                raiz = super()._construir(factura, totales)
                raiz.remove(raiz.xpath("cbc:ID", namespaces=NS)[0])
                return raiz

        with self.assertRaises(XmlInvalidoError) as contexto:
            GeneradorDefectuoso().generar(factura_ejemplo())
        self.assertTrue(contexto.exception.errores)

    # ---- el XSD es el oficial y existe --------------------------------------------------------------------------

    def test_si_falta_el_xsd_se_avisa_en_vez_de_afirmar_que_es_valido(self):
        with self.assertRaises(XsdNoEncontradoError):
            ValidadorXsd(Path("no-existe") / "UBL-Invoice-2.1.xsd")

    def test_el_xsd_es_el_oficial_de_oasis_ubl_2_1(self):
        cabecera = RUTA_XSD_INVOICE.read_text(encoding="utf-8")[:1500]
        self.assertIn("OASIS Universal Business Language (UBL) 2.1 OS", cabecera)
        self.assertIn("urn:oasis:names:specification:ubl:schema:xsd:Invoice-2", cabecera)
        self.assertIn("xsd/maindoc/UBL-Invoice-2.1.xsd", cabecera)

    def test_los_xsd_no_han_sido_modificados(self):
        sumas = RAIZ_PROYECTO / "specs" / "contracts" / "ubl-2.1" / "xsd" / "SHA256SUMS.txt"
        verificados = 0
        for linea in sumas.read_text(encoding="utf-8").splitlines():
            esperado, _, nombre = linea.partition(" *")
            real = hashlib.sha256((sumas.parent / nombre).read_bytes()).hexdigest()
            self.assertEqual(real, esperado, f"{nombre} fue modificado")
            verificados += 1
        self.assertEqual(verificados, 14)
