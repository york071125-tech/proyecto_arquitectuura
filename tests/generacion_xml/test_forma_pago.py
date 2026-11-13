"""Forma de pago obligatoria en la factura (RS 193-2020): Contado o Crédito con cuotas."""
from datetime import date
from decimal import Decimal

from facturacion_xml import Cuota, FacturaInvalidaError, FormaPago
from facturacion_xml.ejemplo import factura_ejemplo

from .base import PruebaXml


class PruebasFormaPago(PruebaXml):
    def test_contado(self):
        _, raiz = self.generar()
        terminos = self.elementos(raiz, "cac:PaymentTerms")
        self.assertEqual(len(terminos), 1)
        self.assertEqual(self.texto(terminos[0], "cbc:ID"), "FormaPago")
        self.assertEqual(self.texto(terminos[0], "cbc:PaymentMeansID"), "Contado")

    def test_credito_con_dos_cuotas(self):
        credito = FormaPago((Cuota(Decimal("1000.00"), date(2026, 12, 6)), Cuota(Decimal("567.50"), date(2027, 1, 6))))
        _, raiz = self.generar(factura_ejemplo(forma_pago=credito))
        terminos = self.elementos(raiz, "cac:PaymentTerms")
        self.assertEqual(len(terminos), 3)   # el crédito y una fila por cuota
        medios = [self.texto(t, "cbc:PaymentMeansID") for t in terminos]
        self.assertEqual(medios, ["Credito", "Cuota001", "Cuota002"])
        self.assertEqual(self.texto(terminos[0], "cbc:Amount"), "1567.50")      # monto neto pendiente
        self.assertEqual(self.texto(terminos[1], "cbc:Amount"), "1000.00")
        self.assertEqual(self.texto(terminos[1], "cbc:PaymentDueDate"), "2026-12-06")
        self.assertEqual(self.texto(terminos[2], "cbc:Amount"), "567.50")
        self.assertEqual(self.texto(terminos[2], "cbc:PaymentDueDate"), "2027-01-06")
        self.assertEqual(self.atributo(terminos[0], "cbc:Amount", "currencyID"), "PEN")

    def test_las_cuotas_deben_sumar_el_importe_total(self):
        incompleto = FormaPago((Cuota(Decimal("1000.00"), date(2026, 12, 6)),))
        with self.assertRaises(FacturaInvalidaError):
            self.generador.generar(factura_ejemplo(forma_pago=incompleto))

    def test_las_fechas_de_las_cuotas_no_pueden_retroceder(self):
        al_reves = FormaPago((Cuota(Decimal("1000.00"), date(2027, 1, 6)), Cuota(Decimal("567.50"), date(2026, 12, 6))))
        with self.assertRaises(FacturaInvalidaError):
            self.generador.generar(factura_ejemplo(forma_pago=al_reves))

    def test_una_cuota_no_puede_vencer_antes_de_la_emision(self):
        vencida = FormaPago((Cuota(Decimal("1567.50"), date(2026, 11, 5)),))
        with self.assertRaises(FacturaInvalidaError):
            self.generador.generar(factura_ejemplo(forma_pago=vencida))

    def test_monto_de_cuota_cero(self):
        with self.assertRaises(FacturaInvalidaError):
            Cuota(Decimal("0"), date(2026, 12, 6))
