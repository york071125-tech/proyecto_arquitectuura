"""Aspecto 6: los importes y totales son correctos.

Los valores esperados están escritos a mano (no se calculan con el mismo código que se prueba).
Línea 1: 10 × 120.00 = 1200.00 · línea 2: 50.00 · gravado 1250.00 · IGV 18 % = 225.00 · inafecto 30.00 ·
exonerado 62.50 · gratuito 7.00 (valor referencial, no suma) · total = 1250.00 + 30.00 + 62.50 + 225.00 = 1567.50
"""
from datetime import date
from decimal import Decimal

from facturacion_xml import DetalleFactura, Factura, TipoAfectacion, calcular_totales
from facturacion_xml.ejemplo import emisor_ejemplo, factura_ejemplo, receptor_ejemplo

from .base import PruebaXml


class PruebasTotales(PruebaXml):
    def test_totales_calculados_por_el_dominio(self):
        t = calcular_totales(factura_ejemplo())
        self.assertEqual(t.total_gravado, Decimal("1250.00"))
        self.assertEqual(t.total_igv, Decimal("225.00"))
        self.assertEqual(t.total_inafecto, Decimal("30.00"))
        self.assertEqual(t.total_exonerado, Decimal("62.50"))
        self.assertEqual(t.total_gratuito, Decimal("7.00"))
        self.assertEqual(t.importe_total, Decimal("1567.50"))

    def test_los_importes_son_decimal_nunca_float(self):
        t = calcular_totales(factura_ejemplo())
        for valor in (t.total_gravado, t.total_igv, t.total_inafecto, t.total_exonerado, t.total_gratuito, t.importe_total):
            self.assertIsInstance(valor, Decimal)

    def test_totales_en_el_xml(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, "cac:TaxTotal/cbc:TaxAmount"), "225.00")
        self.assertEqual(self.texto(raiz, "cac:LegalMonetaryTotal/cbc:LineExtensionAmount"), "1342.50")  # 1250 + 30 + 62.50
        self.assertEqual(self.texto(raiz, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount"), "1567.50")
        self.assertEqual(self.texto(raiz, "cac:LegalMonetaryTotal/cbc:PayableAmount"), "1567.50")

    def test_igv_de_cada_linea_gravada(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(self.linea(raiz, 1), "cac:TaxTotal/cbc:TaxAmount"), "216.00")   # 18 % de 1200.00
        self.assertEqual(self.texto(self.linea(raiz, 2), "cac:TaxTotal/cbc:TaxAmount"), "9.00")     # 18 % de 50.00

    def test_el_gratuito_no_suma_al_importe_total(self):
        sin_gratuito = factura_ejemplo(detalles=factura_ejemplo().detalles[:4])
        self.assertEqual(calcular_totales(sin_gratuito).importe_total, calcular_totales(factura_ejemplo()).importe_total)

    def test_redondeo_half_up_por_linea(self):
        # 1 × 13.25 al 18 % = 2.385 → 2.39 (mitad hacia arriba), no 2.38
        detalle = DetalleFactura("R-1", "Redondeo", "NIU", Decimal("1"), Decimal("13.25"))
        self.assertEqual(calcular_totales(factura_ejemplo(detalles=(detalle,))).total_igv, Decimal("2.39"))

    def test_el_igv_total_es_la_suma_de_los_igv_de_cada_linea(self):
        # Dos líneas de 0.25: IGV por línea 0.045 → 0.05 y 0.05; total 0.10 (no 0.09, que saldría de redondear la suma)
        lineas = tuple(DetalleFactura(f"C-{i}", "Caramelo", "NIU", Decimal("1"), Decimal("0.25")) for i in (1, 2))
        totales = calcular_totales(factura_ejemplo(detalles=lineas))
        self.assertEqual(totales.total_igv, Decimal("0.10"))
        self.assertEqual(totales.importe_total, Decimal("0.60"))

    def test_la_tasa_por_defecto_es_18_por_ciento(self):
        detalle = DetalleFactura("T-1", "Producto", "NIU", Decimal("1"), Decimal("100.00"))
        self.assertEqual(calcular_totales(factura_ejemplo(detalles=(detalle,))).total_igv, Decimal("18.00"))

    def test_otra_tasa_solo_se_aplica_si_se_pasa_expresamente(self):
        detalle = DetalleFactura("T-1", "Almuerzo", "ZZ", Decimal("1"), Decimal("100.00"))
        factura = factura_ejemplo(detalles=(detalle,), tasa_igv=Decimal("10"))
        self.assertEqual(calcular_totales(factura).total_igv, Decimal("10.00"))
        _, raiz = self.generar(factura)
        self.assertEqual(self.texto(self.linea(raiz, 1), "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent"), "10.00")

    def test_factura_con_una_sola_linea_inafecta_no_tiene_igv(self):
        detalle = DetalleFactura("I-1", "Servicio inafecto", "ZZ", Decimal("2"), Decimal("45.00"), TipoAfectacion.INAFECTO)
        totales = calcular_totales(factura_ejemplo(detalles=(detalle,)))
        self.assertEqual((totales.total_igv, totales.importe_total), (Decimal("0.00"), Decimal("90.00")))

    def test_importe_en_dolares(self):
        detalle = DetalleFactura("D-1", "Exportación menor", "NIU", Decimal("1"), Decimal("100.00"))
        _, raiz = self.generar(factura_ejemplo(detalles=(detalle,), moneda="USD"))
        self.assertEqual(self.atributo(raiz, "cac:LegalMonetaryTotal/cbc:PayableAmount", "currencyID"), "USD")
        self.assertEqual(self.texto(raiz, "cbc:Note[@languageLocaleID='1000']"), "SON: CIENTO DIECIOCHO CON 00/100 DÓLARES AMERICANOS")

    def test_fecha_de_vencimiento_opcional(self):
        _, raiz = self.generar(factura_ejemplo(fecha_vencimiento=date(2026, 12, 6)))
        self.assertEqual(self.texto(raiz, "cbc:DueDate"), "2026-12-06")
        _, sin = self.generar()
        self.assertEqual(self.elementos(sin, "cbc:DueDate"), [])
