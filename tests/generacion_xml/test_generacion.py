"""Aspectos 1 y 2: se genera un XML y tiene la estructura esperada."""
from lxml import etree

from facturacion_xml.ejemplo import factura_ejemplo
from facturacion_xml.generador_invoice import NS_INVOICE

from .base import PruebaXml


class PruebasGeneracion(PruebaXml):
    def test_se_genera_un_xml_en_bytes_utf8(self):
        xml, _ = self.generar()
        self.assertIsInstance(xml, bytes)
        self.assertTrue(xml.startswith(b"<?xml"), "debe empezar con la declaración XML")
        self.assertIn(b"UTF-8", xml[:80], "la declaración debe indicar UTF-8")
        xml.decode("utf-8")   # no debe lanzar UnicodeDecodeError

    def test_es_xml_bien_formado_con_raiz_invoice(self):
        _, raiz = self.generar()
        self.assertEqual(raiz.tag, f"{{{NS_INVOICE}}}Invoice")

    def test_los_hijos_de_la_raiz_siguen_el_orden_esperado(self):
        _, raiz = self.generar()
        nombres = [etree.QName(hijo).localname for hijo in raiz]
        esperado = ["UBLVersionID", "CustomizationID", "ID", "IssueDate", "IssueTime", "InvoiceTypeCode", "Note", "Note",
                    "DocumentCurrencyCode", "Signature", "AccountingSupplierParty", "AccountingCustomerParty",
                    "PaymentTerms", "TaxTotal", "LegalMonetaryTotal"] + ["InvoiceLine"] * 5
        self.assertEqual(nombres, esperado)

    def test_se_genera_una_linea_por_cada_detalle(self):
        factura = factura_ejemplo()
        _, raiz = self.generar(factura)
        self.assertEqual(len(self.elementos(raiz, "cac:InvoiceLine")), len(factura.detalles))

    def test_la_misma_factura_produce_siempre_el_mismo_xml(self):
        primero, _ = self.generar()
        segundo, _ = self.generar()
        self.assertEqual(primero, segundo)

    def test_un_xml_sin_gratuitos_no_lleva_la_leyenda_1002(self):
        solo_gravados = factura_ejemplo().detalles[:2]
        _, raiz = self.generar(factura_ejemplo(detalles=solo_gravados))
        leyendas = [n.get("languageLocaleID") for n in self.elementos(raiz, "cbc:Note")]
        self.assertEqual(leyendas, ["1000"])
