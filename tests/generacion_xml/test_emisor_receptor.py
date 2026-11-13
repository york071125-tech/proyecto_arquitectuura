"""Aspecto 4: los datos del emisor y del receptor se generan correctamente."""
from .base import PruebaXml

EMISOR = "cac:AccountingSupplierParty/cac:Party"
RECEPTOR = "cac:AccountingCustomerParty/cac:Party"


class PruebasEmisor(PruebaXml):
    def test_ruc_y_tipo_de_documento_de_identidad(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, f"{EMISOR}/cac:PartyIdentification/cbc:ID"), "20123456786")
        self.assertEqual(self.atributo(raiz, f"{EMISOR}/cac:PartyIdentification/cbc:ID", "schemeID"), "6")  # catálogo 06: RUC

    def test_razon_social_y_nombre_comercial(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, f"{EMISOR}/cac:PartyLegalEntity/cbc:RegistrationName"),
                         "Distribuidora Peña & Cañete S.A.C.")
        self.assertEqual(self.texto(raiz, f"{EMISOR}/cac:PartyName/cbc:Name"), "Abarrotes Ñandú")

    def test_domicilio_fiscal(self):
        _, raiz = self.generar()
        direccion = f"{EMISOR}/cac:PartyLegalEntity/cac:RegistrationAddress"
        self.assertEqual(self.texto(raiz, f"{direccion}/cbc:ID"), "100901")                 # UBIGEO
        self.assertEqual(self.texto(raiz, f"{direccion}/cbc:AddressTypeCode"), "0000")      # domicilio fiscal
        self.assertEqual(self.texto(raiz, f"{direccion}/cbc:CountrySubentity"), "HUÁNUCO")
        self.assertEqual(self.texto(raiz, f"{direccion}/cbc:CityName"), "LEONCIO PRADO")
        self.assertEqual(self.texto(raiz, f"{direccion}/cbc:District"), "RUPA-RUPA")
        self.assertEqual(self.texto(raiz, f"{direccion}/cac:AddressLine/cbc:Line"), "Jr. Progreso N° 123 – Tingo María")
        self.assertEqual(self.texto(raiz, f"{direccion}/cac:Country/cbc:IdentificationCode"), "PE")

    def test_la_firma_referencia_al_emisor(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, "cac:Signature/cac:SignatoryParty/cac:PartyIdentification/cbc:ID"), "20123456786")


class PruebasReceptor(PruebaXml):
    def test_ruc_y_tipo_de_documento_de_identidad(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, f"{RECEPTOR}/cac:PartyIdentification/cbc:ID"), "20456789014")
        self.assertEqual(self.atributo(raiz, f"{RECEPTOR}/cac:PartyIdentification/cbc:ID", "schemeID"), "6")

    def test_razon_social(self):
        _, raiz = self.generar()
        self.assertEqual(self.texto(raiz, f"{RECEPTOR}/cac:PartyLegalEntity/cbc:RegistrationName"), "Bodega “El Sol” E.I.R.L.")

    def test_emisor_y_receptor_son_partes_distintas(self):
        _, raiz = self.generar()
        emisor = self.texto(raiz, f"{EMISOR}/cac:PartyIdentification/cbc:ID")
        receptor = self.texto(raiz, f"{RECEPTOR}/cac:PartyIdentification/cbc:ID")
        self.assertNotEqual(emisor, receptor)
