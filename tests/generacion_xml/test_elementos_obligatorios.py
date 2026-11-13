"""Aspecto 3: existen los elementos obligatorios del Invoice de SUNAT."""
from .base import PruebaXml


class PruebasElementosObligatorios(PruebaXml):
    def test_cabecera_del_documento(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, "cbc:UBLVersionID"), "2.1")
        self.assertEqual(self.texto(raiz, "cbc:CustomizationID"), "2.0")
        self.assertEqual(self.texto(raiz, "cbc:ID"), "F001-00000001")
        self.assertEqual(self.texto(raiz, "cbc:IssueDate"), "2026-11-06")
        self.assertEqual(self.texto(raiz, "cbc:IssueTime"), "10:30:00")
        self.assertEqual(self.texto(raiz, "cbc:DocumentCurrencyCode"), "PEN")

    def test_tipo_de_documento_y_tipo_de_operacion(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, "cbc:InvoiceTypeCode"), "01")             # catálogo 01: factura
        self.assertEqual(self.atributo(raiz, "cbc:InvoiceTypeCode", "listID"), "0101")  # catálogo 51: venta interna

    def test_leyenda_1000_con_el_monto_en_letras(self):
        _, raiz = self.generar()
        leyenda = self.uno(raiz, "cbc:Note[@languageLocaleID='1000']")
        self.assertEqual(leyenda.text, "SON: MIL QUINIENTOS SESENTA Y SIETE CON 50/100 SOLES")

    def test_estan_los_bloques_principales(self):
        _, raiz = self.generar()
        for ruta in ("cac:Signature", "cac:AccountingSupplierParty", "cac:AccountingCustomerParty", "cac:PaymentTerms",
                     "cac:TaxTotal", "cac:LegalMonetaryTotal"):
            self.uno(raiz, ruta)

    def test_toda_linea_tiene_sus_elementos_obligatorios(self):
        _, raiz = self.generar()
        lineas = self.elementos(raiz, "cac:InvoiceLine")
        self.assertGreaterEqual(len(lineas), 1)
        for linea in lineas:
            for ruta in ("cbc:ID", "cbc:InvoicedQuantity", "cbc:LineExtensionAmount",
                         "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount",
                         "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode",
                         "cac:TaxTotal/cbc:TaxAmount", "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID",
                         "cac:Item/cbc:Description", "cac:Item/cac:SellersItemIdentification/cbc:ID", "cac:Price/cbc:PriceAmount"):
                self.assertEqual(len(self.elementos(linea, ruta)), 1, f"línea {linea[0].text}: falta {ruta}")

    def test_toda_cantidad_importe_lleva_su_moneda(self):
        _, raiz = self.generar()
        for nodo in self.elementos(raiz, "//cbc:TaxAmount | //cbc:TaxableAmount | //cbc:LineExtensionAmount | //cbc:PayableAmount"):
            self.assertEqual(nodo.get("currencyID"), "PEN")
