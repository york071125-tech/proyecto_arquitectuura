"""Aspecto 5: los productos y servicios se representan correctamente."""
from decimal import Decimal

from facturacion_xml import DetalleFactura, TipoAfectacion
from facturacion_xml.ejemplo import factura_ejemplo

from .base import PruebaXml


class PruebasDetalle(PruebaXml):
    def test_producto_gravado_con_unidad_bolsa(self):
        _, raiz = self.generar()
        linea = self.linea(raiz, 1)
        self.assertEqual(self.texto(linea, "cac:Item/cbc:Description"), "Arroz extra “Selecto” saco 50 kg")
        self.assertEqual(self.texto(linea, "cac:Item/cac:SellersItemIdentification/cbc:ID"), "ARR-001")
        self.assertEqual(self.texto(linea, "cbc:InvoicedQuantity"), "10.00")
        self.assertEqual(self.atributo(linea, "cbc:InvoicedQuantity", "unitCode"), "BG")
        self.assertEqual(self.texto(linea, "cac:Price/cbc:PriceAmount"), "120.00")                      # valor unitario sin IGV
        self.assertEqual(self.texto(linea, "cbc:LineExtensionAmount"), "1200.00")                      # 10 × 120.00
        self.assertEqual(self.texto(linea, "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount"), "141.60")  # con IGV
        self.assertEqual(self.texto(linea, "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode"), "01")

    def test_servicio_usa_la_unidad_zz(self):
        _, raiz = self.generar()
        linea = self.linea(raiz, 2)
        self.assertEqual(self.atributo(linea, "cbc:InvoicedQuantity", "unitCode"), "ZZ")
        self.assertEqual(self.texto(linea, "cbc:LineExtensionAmount"), "50.00")

    def test_producto_con_cantidad_decimal(self):
        _, raiz = self.generar()
        linea = self.linea(raiz, 3)   # 25 kg de plátano a 2.50
        self.assertEqual(self.atributo(linea, "cbc:InvoicedQuantity", "unitCode"), "KGM")
        self.assertEqual(self.texto(linea, "cbc:LineExtensionAmount"), "62.50")

    def test_cantidad_fraccionaria_se_conserva(self):
        detalle = DetalleFactura("AZU-1", "Azúcar a granel", "KGM", Decimal("2.5"), Decimal("4.00"))
        _, raiz = self.generar(factura_ejemplo(detalles=(detalle,)))
        linea = self.linea(raiz, 1)
        self.assertEqual(self.texto(linea, "cbc:InvoicedQuantity"), "2.50")
        self.assertEqual(self.texto(linea, "cbc:LineExtensionAmount"), "10.00")

    def test_las_lineas_se_numeran_desde_uno_en_orden(self):
        _, raiz = self.generar()
        numeros = [n.text for n in self.elementos(raiz, "cac:InvoiceLine/cbc:ID")]
        self.assertEqual(numeros, ["1", "2", "3", "4", "5"])

    def test_producto_gratuito_va_con_valor_referencial(self):
        _, raiz = self.generar()
        linea = self.linea(raiz, 5)   # 2 kg de azúcar, valor referencial 3.50 c/u
        self.assertEqual(self.texto(linea, "cbc:LineExtensionAmount"), "0.00")
        self.assertEqual(self.texto(linea, "cac:Price/cbc:PriceAmount"), "0.00")
        self.assertEqual(self.texto(linea, "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount"), "3.50")
        self.assertEqual(self.texto(linea, "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode"), "02")
        self.assertEqual(self.texto(linea, "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount"), "7.00")

    def test_precio_unitario_con_igv_conserva_decimales_del_calculo(self):
        detalle = DetalleFactura("X-1", "Precio con decimales", "NIU", Decimal("1"), Decimal("8.47"))
        _, raiz = self.generar(factura_ejemplo(detalles=(detalle,)))
        self.assertEqual(self.texto(self.linea(raiz, 1), "cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount"),
                         "9.99460000".rstrip("0"))   # 8.47 × 1.18 = 9.9946
        self.assertIs(detalle.tipo_afectacion, TipoAfectacion.GRAVADO)
