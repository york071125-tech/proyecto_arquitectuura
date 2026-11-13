"""Leyenda 1000: monto en letras en español."""
import unittest
from decimal import Decimal

from facturacion_xml.monto_en_letras import entero_en_letras, monto_en_letras


class PruebasMontoEnLetras(unittest.TestCase):
    def test_montos_conocidos_en_soles(self):
        casos = {
            "0.00": "SON: CERO CON 00/100 SOLES",
            "1.00": "SON: UNO CON 00/100 SOLES",
            "15.50": "SON: QUINCE CON 50/100 SOLES",
            "21.00": "SON: VEINTIUNO CON 00/100 SOLES",
            "100.00": "SON: CIEN CON 00/100 SOLES",
            "101.01": "SON: CIENTO UNO CON 01/100 SOLES",
            "118.00": "SON: CIENTO DIECIOCHO CON 00/100 SOLES",
            "1000.00": "SON: MIL CON 00/100 SOLES",
            "1567.50": "SON: MIL QUINIENTOS SESENTA Y SIETE CON 50/100 SOLES",
            "21000.00": "SON: VEINTIÚN MIL CON 00/100 SOLES",
            "31500.00": "SON: TREINTA Y UN MIL QUINIENTOS CON 00/100 SOLES",
            "999999.99": "SON: NOVECIENTOS NOVENTA Y NUEVE MIL NOVECIENTOS NOVENTA Y NUEVE CON 99/100 SOLES",
            "1000000.00": "SON: UN MILLÓN CON 00/100 SOLES",
            "2500000.00": "SON: DOS MILLONES QUINIENTOS MIL CON 00/100 SOLES",
            "21000000.00": "SON: VEINTIÚN MILLONES CON 00/100 SOLES",
        }
        for monto, esperado in casos.items():
            with self.subTest(monto=monto):
                self.assertEqual(monto_en_letras(Decimal(monto)), esperado)

    def test_dolares(self):
        self.assertEqual(monto_en_letras(Decimal("118.00"), "USD"), "SON: CIENTO DIECIOCHO CON 00/100 DÓLARES AMERICANOS")

    def test_los_centavos_se_redondean_half_up(self):
        self.assertEqual(monto_en_letras(Decimal("10.005")), "SON: DIEZ CON 01/100 SOLES")

    def test_los_numeros_del_16_al_29_llevan_tilde(self):
        self.assertEqual(entero_en_letras(16), "DIECISÉIS")
        self.assertEqual(entero_en_letras(22), "VEINTIDÓS")
        self.assertEqual(entero_en_letras(23), "VEINTITRÉS")
        self.assertEqual(entero_en_letras(26), "VEINTISÉIS")

    def test_fuera_de_rango(self):
        for n in (-1, 10**12):
            with self.subTest(n=n), self.assertRaises(ValueError):
                entero_en_letras(n)
