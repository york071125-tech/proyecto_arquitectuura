"""Aspecto 7: los tipos de afectación 1001 (gravado), 1002 (inafecto), 1003 (exonerado) y 1004 (gratuito).

Tabla esperada (catálogos SUNAT 05 y 07):
  1001 gravado   → tributo 1000 IGV  VAT · categoría S · afectación 10
  1002 inafecto  → tributo 9998 INA  FRE · categoría O · afectación 30
  1003 exonerado → tributo 9997 EXO  VAT · categoría E · afectación 20
  1004 gratuito  → tributo 9996 GRA  FRE · categoría Z · afectación 21
"""
from decimal import Decimal

from facturacion_xml import DetalleFactura, FacturaInvalidaError, TipoAfectacion, calcular_totales
from facturacion_xml.ejemplo import factura_ejemplo

from .base import PruebaXml

TABLA = {
    TipoAfectacion.GRAVADO: ("1001", "1000", "IGV", "VAT", "S", "10"),
    TipoAfectacion.INAFECTO: ("1002", "9998", "INA", "FRE", "O", "30"),
    TipoAfectacion.EXONERADO: ("1003", "9997", "EXO", "VAT", "E", "20"),
    TipoAfectacion.GRATUITO: ("1004", "9996", "GRA", "FRE", "Z", "21"),
}
CATEGORIA = "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory"


def factura_de(tipo, **extra):
    detalle = DetalleFactura("P-1", "Producto de prueba", "NIU", Decimal("2"), Decimal("50.00"), tipo, **extra)
    return factura_ejemplo(detalles=(detalle,))


class PruebasAfectaciones(PruebaXml):
    def test_cada_tipo_tiene_su_codigo_del_enunciado(self):
        for tipo, (codigo, *_) in TABLA.items():
            with self.subTest(tipo=tipo.name):
                self.assertEqual(tipo.codigo, codigo)
                self.assertIs(TipoAfectacion.desde_codigo(codigo), tipo)

    def test_codigo_de_afectacion_desconocido_se_rechaza(self):
        with self.assertRaises(FacturaInvalidaError):
            TipoAfectacion.desde_codigo("9999")

    def test_cada_tipo_se_expresa_con_su_tributo_y_categoria_en_la_linea(self):
        for tipo, (_, id_tributo, nombre, internacional, categoria, afectacion) in TABLA.items():
            with self.subTest(tipo=tipo.name):
                _, raiz = self.generar(factura_de(tipo))
                linea = self.linea(raiz, 1)
                base = f"{CATEGORIA}"
                self.assertEqual(self.texto(linea, f"{base}/cbc:ID"), categoria)
                self.assertEqual(self.texto(linea, f"{base}/cac:TaxScheme/cbc:ID"), id_tributo)
                self.assertEqual(self.texto(linea, f"{base}/cac:TaxScheme/cbc:Name"), nombre)
                self.assertEqual(self.texto(linea, f"{base}/cac:TaxScheme/cbc:TaxTypeCode"), internacional)
                self.assertEqual(self.texto(linea, f"{base}/cbc:TaxExemptionReasonCode"), afectacion)

    def test_cada_tipo_aparece_en_los_impuestos_de_la_cabecera(self):
        _, raiz = self.generar()   # la factura de ejemplo tiene los cuatro tipos
        tributos = [n.text for n in self.elementos(raiz, f"{CATEGORIA}/cac:TaxScheme/cbc:ID")]
        self.assertEqual(tributos, ["1000", "9998", "9997", "9996"])

    def test_inafecto_y_exonerado_no_se_confunden(self):
        _, raiz_inafecto = self.generar(factura_de(TipoAfectacion.INAFECTO))
        _, raiz_exonerado = self.generar(factura_de(TipoAfectacion.EXONERADO))
        ruta = f"{CATEGORIA}/cac:TaxScheme/cbc:ID"
        self.assertEqual(self.texto(raiz_inafecto, ruta), "9998")
        self.assertEqual(self.texto(raiz_exonerado, ruta), "9997")
        self.assertNotEqual(self.texto(raiz_inafecto, f"{CATEGORIA}/cbc:ID"), self.texto(raiz_exonerado, f"{CATEGORIA}/cbc:ID"))

    def test_solo_el_gravado_paga_igv(self):
        for tipo in TipoAfectacion:
            with self.subTest(tipo=tipo.name):
                esperado = Decimal("18.00") if tipo is TipoAfectacion.GRAVADO else Decimal("0.00")   # 18 % de 100.00
                self.assertEqual(calcular_totales(factura_de(tipo)).total_igv, esperado)

    def test_importe_total_segun_la_afectacion(self):
        # 2 × 50.00 = 100.00 de base
        esperado = {TipoAfectacion.GRAVADO: "118.00", TipoAfectacion.INAFECTO: "100.00",
                    TipoAfectacion.EXONERADO: "100.00", TipoAfectacion.GRATUITO: "0.00"}
        for tipo, total in esperado.items():
            with self.subTest(tipo=tipo.name):
                self.assertEqual(calcular_totales(factura_de(tipo)).importe_total, Decimal(total))

    def test_el_gravado_declara_el_porcentaje_del_igv(self):
        _, raiz = self.generar(factura_de(TipoAfectacion.GRAVADO))
        self.assertEqual(self.texto(self.linea(raiz, 1), f"{CATEGORIA}/cbc:Percent"), "18.00")

    def test_el_gratuito_acepta_otros_motivos_del_catalogo_07(self):
        _, raiz = self.generar(factura_de(TipoAfectacion.GRATUITO, motivo_gratuito="13"))
        self.assertEqual(self.texto(self.linea(raiz, 1), f"{CATEGORIA}/cbc:TaxExemptionReasonCode"), "13")

    def test_motivo_gratuito_invalido_se_rechaza(self):
        with self.assertRaises(FacturaInvalidaError):
            factura_de(TipoAfectacion.GRATUITO, motivo_gratuito="10")   # 10 es «gravado oneroso», no gratuito

    def test_motivo_gratuito_en_una_afectacion_onerosa_se_rechaza(self):
        with self.assertRaises(FacturaInvalidaError):
            factura_de(TipoAfectacion.GRAVADO, motivo_gratuito="21")
