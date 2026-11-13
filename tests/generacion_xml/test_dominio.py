"""Reglas del dominio: una factura con datos incorrectos no llega a generar XML."""
import unittest
from datetime import date, time
from decimal import Decimal

from facturacion_xml import DetalleFactura, Emisor, Factura, FacturaInvalidaError, Receptor, ruc_valido
from facturacion_xml.ejemplo import detalles_ejemplo, emisor_ejemplo, factura_ejemplo, receptor_ejemplo


def detalle(**cambios):
    datos = dict(codigo="P-1", descripcion="Producto", unidad="NIU", cantidad=Decimal("1"), valor_unitario=Decimal("10.00"))
    datos.update(cambios)
    return DetalleFactura(**datos)


class PruebasRuc(unittest.TestCase):
    def test_rucs_validos(self):
        for ruc in ("20123456786", "20456789014", "20100047218"):   # el último es un RUC público real de ejemplo
            with self.subTest(ruc=ruc):
                self.assertTrue(ruc_valido(ruc))

    def test_rucs_invalidos(self):
        casos = {"20123456787": "dígito verificador", "12345678901": "prefijo", "2012345678": "10 dígitos",
                 "201234567860": "12 dígitos", "2012345678A": "letra", "": "vacío",
                 "20100113612": "RUC del ejemplo de la guía SUNAT: es ficticio"}
        for ruc, motivo in casos.items():
            with self.subTest(motivo=motivo):
                self.assertFalse(ruc_valido(ruc))


class PruebasEmisorReceptor(unittest.TestCase):
    def test_emisor_con_ruc_invalido(self):
        with self.assertRaises(FacturaInvalidaError):
            Emisor(**{**emisor_ejemplo().__dict__, "ruc": "20123456787"})

    def test_emisor_con_ubigeo_invalido(self):
        with self.assertRaises(FacturaInvalidaError):
            Emisor(**{**emisor_ejemplo().__dict__, "ubigeo": "10090"})

    def test_receptor_de_factura_debe_tener_ruc(self):
        with self.assertRaises(FacturaInvalidaError):
            Receptor(numero_documento="12345678", razon_social="Juan Pérez", tipo_documento="1")

    def test_receptor_con_ruc_invalido(self):
        with self.assertRaises(FacturaInvalidaError):
            Receptor(numero_documento="20456789015", razon_social="X")


class PruebasDetalle(unittest.TestCase):
    def test_cantidad_cero_o_negativa(self):
        for cantidad in (Decimal("0"), Decimal("-1")):
            with self.subTest(cantidad=cantidad), self.assertRaises(FacturaInvalidaError):
                detalle(cantidad=cantidad)

    def test_unidad_fuera_del_catalogo_03(self):
        with self.assertRaises(FacturaInvalidaError):
            detalle(unidad="XX")

    def test_valor_unitario_negativo(self):
        with self.assertRaises(FacturaInvalidaError):
            detalle(valor_unitario=Decimal("-0.01"))

    def test_float_se_rechaza_porque_no_es_exacto(self):
        with self.assertRaises(FacturaInvalidaError):
            detalle(valor_unitario=0.1)

    def test_texto_no_numerico(self):
        with self.assertRaises(FacturaInvalidaError):
            detalle(cantidad="diez")

    def test_acepta_int_y_str_como_decimales_exactos(self):
        d = detalle(cantidad=3, valor_unitario="0.10")
        self.assertEqual((d.cantidad, d.valor_unitario), (Decimal("3"), Decimal("0.10")))

    def test_descripcion_vacia(self):
        with self.assertRaises(FacturaInvalidaError):
            detalle(descripcion="  ")


class PruebasFactura(unittest.TestCase):
    def test_serie_invalida(self):
        for serie in ("B001", "F01", "F0001", "f001", "FF-1"):
            with self.subTest(serie=serie), self.assertRaises(FacturaInvalidaError):
                factura_ejemplo(serie=serie)

    def test_series_validas(self):
        for serie in ("F001", "FA01", "F9Z9"):
            with self.subTest(serie=serie):
                self.assertEqual(factura_ejemplo(serie=serie).serie, serie)

    def test_correlativo_fuera_de_rango(self):
        for correlativo in (0, -1, 100_000_000):
            with self.subTest(correlativo=correlativo), self.assertRaises(FacturaInvalidaError):
                factura_ejemplo(correlativo=correlativo)

    def test_numero_con_ceros_a_la_izquierda(self):
        self.assertEqual(factura_ejemplo(correlativo=15).numero, "F001-00000015")
        self.assertEqual(factura_ejemplo(correlativo=99_999_999).numero, "F001-99999999")

    def test_sin_detalles(self):
        with self.assertRaises(FacturaInvalidaError):
            factura_ejemplo(detalles=())

    def test_moneda_no_soportada(self):
        with self.assertRaises(FacturaInvalidaError):
            factura_ejemplo(moneda="EUR")

    def test_tasa_igv_fuera_de_rango(self):
        for tasa in (Decimal("-1"), Decimal("101")):
            with self.subTest(tasa=tasa), self.assertRaises(FacturaInvalidaError):
                factura_ejemplo(tasa_igv=tasa)

    def test_vencimiento_anterior_a_la_emision(self):
        with self.assertRaises(FacturaInvalidaError):
            factura_ejemplo(fecha_vencimiento=date(2026, 11, 5))

    def test_los_datos_son_inmutables(self):
        factura = factura_ejemplo()
        with self.assertRaises(Exception):
            factura.serie = "F999"
