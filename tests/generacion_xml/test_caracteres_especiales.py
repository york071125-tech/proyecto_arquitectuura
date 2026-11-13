"""Aspecto 8: los caracteres especiales del español se manejan correctamente (UTF-8 y escape XML)."""
import tempfile
from decimal import Decimal
from pathlib import Path

from lxml import etree

from facturacion_xml import DetalleFactura, Emisor
from facturacion_xml.ejemplo import emisor_ejemplo, factura_ejemplo

from .base import PruebaXml

DESCRIPCION = "Ñandú “premium” — ¿mañana? <1 kg> & más: áéíóú ü N°5 100% 'sal'"


class PruebasCaracteresEspeciales(PruebaXml):
    def _factura_con_descripcion(self, descripcion=DESCRIPCION):
        detalle = DetalleFactura("ESP-1", descripcion, "NIU", Decimal("1"), Decimal("10.00"))
        return factura_ejemplo(detalles=(detalle,))

    def test_el_texto_se_conserva_identico_al_leer_el_xml(self):
        _, raiz = self.generar(self._factura_con_descripcion())
        self.assertEqual(self.texto(self.linea(raiz, 1), "cac:Item/cbc:Description"), DESCRIPCION)

    def test_la_razon_social_con_ampersand_y_enie_se_conserva(self):
        _, raiz = self.generar()
        nombre = self.texto(raiz, "cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName")
        self.assertEqual(nombre, "Distribuidora Peña & Cañete S.A.C.")

    def test_los_caracteres_reservados_se_escapan(self):
        xml, _ = self.generar(self._factura_con_descripcion())
        self.assertIn(b"&lt;1 kg&gt;", xml)
        self.assertIn(b"&amp; m\xc3\xa1s", xml)   # «& más»: & escapado y la á en UTF-8
        self.assertNotIn(b"<1 kg>", xml)

    def test_las_letras_estan_en_utf8_y_no_como_entidades(self):
        xml, _ = self.generar()
        self.assertIn("Abarrotes Ñandú".encode("utf-8"), xml)   # bytes C3 91 ... C3 BA
        self.assertNotIn(b"&#209;", xml)
        self.assertNotIn(b"&#xD1;", xml)

    def test_no_hay_mojibake(self):
        xml, _ = self.generar()
        texto = xml.decode("utf-8")
        for basura in ("Ã±", "Ã¡", "Ã³", "â€œ", "â€“", "Ã‘"):
            self.assertNotIn(basura, texto)

    def test_el_archivo_escrito_y_leido_conserva_los_caracteres(self):
        xml, _ = self.generar()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "factura.xml"
            ruta.write_bytes(xml)
            texto = ruta.read_text(encoding="utf-8")
        self.assertIn("Jr. Progreso N° 123 – Tingo María", texto)
        self.assertIn("HUÁNUCO", texto)

    def test_el_xml_con_caracteres_especiales_pasa_el_xsd(self):
        xml, _ = self.generar(self._factura_con_descripcion())   # generar() ya valida; se confirma con un validador aparte
        self.assertEqual(self.generador._validador.errores(xml), [])

    def test_un_emisor_con_caracteres_chinos_o_emoji_tambien_se_conserva(self):
        # No es un caso de negocio habitual, pero UTF-8 debe soportarlo igual
        base = emisor_ejemplo()
        emisor = Emisor(**{**base.__dict__, "nombre_comercial": "Tienda 福 ☕"})
        _, raiz = self.generar(factura_ejemplo(emisor=emisor))
        self.assertEqual(self.texto(raiz, "cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name"), "Tienda 福 ☕")

    def test_la_declaracion_xml_indica_utf8(self):
        xml, _ = self.generar()
        cabecera = etree.fromstring(xml).getroottree().docinfo
        self.assertEqual(cabecera.encoding.upper(), "UTF-8")
