"""Genera el XML Invoice UBL 2.1 de una factura.

El XML se construye como un ÁRBOL de elementos (lxml), nunca concatenando texto: la biblioteca
escapa los caracteres especiales y respeta los espacios de nombres (ADR-07, RN-088).
Los elementos se agregan en el orden que exige el XSD de Invoice.
"""
from decimal import Decimal

from lxml import etree

from .calculo import TotalesFactura, calcular_totales, validar_forma_pago
from .catalogos import TIPO_DOC_IDENTIDAD_RUC, TIPO_DOCUMENTO_FACTURA, URI_CATALOGO
from .dominio import Factura, TipoAfectacion
from .monto_en_letras import monto_en_letras
from .validador_xsd import ValidadorXsd, validador_invoice

NS_INVOICE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
NS_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
NS_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NS_EXT = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NSMAP = {None: NS_INVOICE, "cac": NS_CAC, "cbc": NS_CBC, "ext": NS_EXT, "ds": NS_DS}

ORGANISMO_ONU = "United Nations Economic Commission for Europe"


def formatear_importe(valor: Decimal) -> str:
    """Importe con exactamente 2 decimales: 1200.00"""
    return f"{valor:.2f}"


def formatear_decimal(valor: Decimal) -> str:
    """Cantidad o precio: mínimo 2 y máximo 10 decimales, sin ceros sobrantes."""
    texto = f"{valor.quantize(Decimal('0.0000000001')):f}".rstrip("0")
    entero, _, decimales = texto.partition(".")
    return f"{entero}.{decimales.ljust(2, '0')}"


def _elemento(padre, prefijo, nombre, texto=None, **atributos):
    ns = NS_CAC if prefijo == "cac" else NS_CBC
    elemento = etree.SubElement(padre, f"{{{ns}}}{nombre}")
    if texto is not None:
        elemento.text = str(texto)
    for clave, valor in atributos.items():
        elemento.set(clave, valor)
    return elemento


def _cbc(padre, nombre, texto=None, **atributos):
    return _elemento(padre, "cbc", nombre, texto, **atributos)


def _cac(padre, nombre):
    return _elemento(padre, "cac", nombre)


class GeneradorFacturaXml:
    """Convierte una `Factura` del dominio en el XML Invoice UBL 2.1 validado contra el XSD."""

    def __init__(self, validador: ValidadorXsd | None = None):
        self._validador = validador or validador_invoice()

    def generar(self, factura: Factura) -> bytes:
        """Devuelve el XML en UTF-8. Lanza XmlInvalidoError si no cumple el XSD."""
        totales = calcular_totales(factura)
        validar_forma_pago(factura, totales)
        xml = etree.tostring(self._construir(factura, totales), xml_declaration=True, encoding="UTF-8",
                             pretty_print=True, standalone=False)
        self._validador.exigir_valido(xml)
        return xml

    # ---- construcción del árbol, en el orden del XSD -----------------------------------------------------------

    def _construir(self, f: Factura, t: TotalesFactura):
        raiz = etree.Element(f"{{{NS_INVOICE}}}Invoice", nsmap=NSMAP)
        _cbc(raiz, "UBLVersionID", "2.1")
        _cbc(raiz, "CustomizationID", "2.0")
        _cbc(raiz, "ID", f.numero)
        _cbc(raiz, "IssueDate", f.fecha_emision.isoformat())
        _cbc(raiz, "IssueTime", f.hora_emision.strftime("%H:%M:%S"))
        if f.fecha_vencimiento:
            _cbc(raiz, "DueDate", f.fecha_vencimiento.isoformat())
        _cbc(raiz, "InvoiceTypeCode", TIPO_DOCUMENTO_FACTURA, listAgencyName="PE:SUNAT", listName="Tipo de Documento",
             listURI=URI_CATALOGO.format(1), listID=f.tipo_operacion, name="Tipo de Operacion",
             listSchemeURI=URI_CATALOGO.format(51))
        _cbc(raiz, "Note", monto_en_letras(t.importe_total, f.moneda), languageLocaleID="1000")
        if t.total_gratuito > 0:
            _cbc(raiz, "Note", "TRANSFERENCIA GRATUITA DE UN BIEN Y/O SERVICIO PRESTADO GRATUITAMENTE",
                 languageLocaleID="1002")
        _cbc(raiz, "DocumentCurrencyCode", f.moneda, listID="ISO 4217 Alpha", listName="Currency",
             listAgencyName=ORGANISMO_ONU)
        self._firma_referencia(raiz, f)
        self._parte(raiz, "AccountingSupplierParty", f.emisor.ruc, f.emisor.razon_social, f.emisor.nombre_comercial,
                    f.emisor)
        self._parte(raiz, "AccountingCustomerParty", f.receptor.numero_documento, f.receptor.razon_social)
        self._forma_pago(raiz, f)
        self._impuestos_cabecera(raiz, f, t)
        self._totales(raiz, f, t)
        for numero, linea in enumerate(t.lineas, start=1):
            self._linea(raiz, f, numero, linea)
        return raiz

    def _firma_referencia(self, raiz, f):
        """Referencia a la firma (cac:Signature). La firma digital en sí (ds:Signature) se agrega en otra fase."""
        firma = _cac(raiz, "Signature")
        _cbc(firma, "ID", f"SIGN-{f.emisor.ruc}")
        firmante = _cac(firma, "SignatoryParty")
        _cbc(_cac(firmante, "PartyIdentification"), "ID", f.emisor.ruc)
        _cbc(_cac(firmante, "PartyName"), "Name", f.emisor.razon_social)
        adjunto = _cac(_cac(firma, "DigitalSignatureAttachment"), "ExternalReference")
        _cbc(adjunto, "URI", f"#SIGN-{f.emisor.ruc}")

    def _parte(self, raiz, nombre_rol, documento, razon_social, nombre_comercial=None, emisor=None):
        party = _cac(_cac(raiz, nombre_rol), "Party")
        _cbc(_cac(party, "PartyIdentification"), "ID", documento, schemeID=TIPO_DOC_IDENTIDAD_RUC,
             schemeName="Documento de Identidad", schemeAgencyName="PE:SUNAT", schemeURI=URI_CATALOGO.format(6))
        if nombre_comercial:
            _cbc(_cac(party, "PartyName"), "Name", nombre_comercial)
        entidad = _cac(party, "PartyLegalEntity")
        _cbc(entidad, "RegistrationName", razon_social)
        if emisor:
            direccion = _cac(entidad, "RegistrationAddress")
            _cbc(direccion, "ID", emisor.ubigeo, schemeAgencyName="PE:INEI", schemeName="Ubigeos")
            _cbc(direccion, "AddressTypeCode", emisor.codigo_establecimiento, listAgencyName="PE:SUNAT",
                 listName="Establecimientos anexos")
            _cbc(direccion, "CityName", emisor.provincia)
            _cbc(direccion, "CountrySubentity", emisor.departamento)
            _cbc(direccion, "District", emisor.distrito)
            _cbc(_cac(direccion, "AddressLine"), "Line", emisor.direccion)
            _cbc(_cac(direccion, "Country"), "IdentificationCode", "PE", listID="ISO 3166-1",
                 listAgencyName=ORGANISMO_ONU, listName="Country")

    def _forma_pago(self, raiz, f):
        moneda = f.moneda
        pago = _cac(raiz, "PaymentTerms")
        _cbc(pago, "ID", "FormaPago")
        if not f.forma_pago.es_credito:
            _cbc(pago, "PaymentMeansID", "Contado")
            return
        _cbc(pago, "PaymentMeansID", "Credito")
        _cbc(pago, "Amount", formatear_importe(sum((c.monto for c in f.forma_pago.cuotas), Decimal("0"))),
             currencyID=moneda)
        for numero, cuota in enumerate(f.forma_pago.cuotas, start=1):
            detalle = _cac(raiz, "PaymentTerms")
            _cbc(detalle, "ID", "FormaPago")
            _cbc(detalle, "PaymentMeansID", f"Cuota{numero:03d}")
            _cbc(detalle, "Amount", formatear_importe(cuota.monto), currencyID=moneda)
            _cbc(detalle, "PaymentDueDate", cuota.fecha_vencimiento.isoformat())

    def _categoria(self, padre, tipo: TipoAfectacion, porcentaje=None, motivo=None):
        categoria = _cac(padre, "TaxCategory")
        _cbc(categoria, "ID", tipo.categoria, schemeID="UN/ECE 5305", schemeName="Tax Category Identifier",
             schemeAgencyName=ORGANISMO_ONU)
        if porcentaje is not None:
            _cbc(categoria, "Percent", formatear_importe(porcentaje))
        if motivo is not None:
            _cbc(categoria, "TaxExemptionReasonCode", motivo, listAgencyName="PE:SUNAT",
                 listName="Afectacion del IGV", listURI=URI_CATALOGO.format(7))
        esquema = _cac(categoria, "TaxScheme")
        _cbc(esquema, "ID", tipo.id_tributo, schemeID="UN/ECE 5153", schemeAgencyID="6")
        _cbc(esquema, "Name", tipo.nombre_tributo)
        _cbc(esquema, "TaxTypeCode", tipo.tipo_internacional)

    def _subtotal(self, padre, moneda, base, impuesto, tipo, porcentaje=None, motivo=None):
        subtotal = _cac(padre, "TaxSubtotal")
        _cbc(subtotal, "TaxableAmount", formatear_importe(base), currencyID=moneda)
        _cbc(subtotal, "TaxAmount", formatear_importe(impuesto), currencyID=moneda)
        self._categoria(subtotal, tipo, porcentaje, motivo)

    def _impuestos_cabecera(self, raiz, f, t):
        impuestos = _cac(raiz, "TaxTotal")
        _cbc(impuestos, "TaxAmount", formatear_importe(t.total_igv), currencyID=f.moneda)
        grupos = ((TipoAfectacion.GRAVADO, t.total_gravado, t.total_igv), (TipoAfectacion.INAFECTO, t.total_inafecto, 0),
                  (TipoAfectacion.EXONERADO, t.total_exonerado, 0), (TipoAfectacion.GRATUITO, t.total_gratuito, 0))
        for tipo, base, impuesto in grupos:
            if any(l.detalle.tipo_afectacion is tipo for l in t.lineas):
                self._subtotal(impuestos, f.moneda, base, Decimal(impuesto), tipo)

    def _totales(self, raiz, f, t):
        total = _cac(raiz, "LegalMonetaryTotal")
        _cbc(total, "LineExtensionAmount", formatear_importe(t.valor_venta_total), currencyID=f.moneda)
        _cbc(total, "TaxInclusiveAmount", formatear_importe(t.importe_total), currencyID=f.moneda)
        _cbc(total, "PayableAmount", formatear_importe(t.importe_total), currencyID=f.moneda)

    def _linea(self, raiz, f, numero, linea):
        detalle, tipo, moneda = linea.detalle, linea.detalle.tipo_afectacion, f.moneda
        item_linea = _cac(raiz, "InvoiceLine")
        _cbc(item_linea, "ID", numero)
        _cbc(item_linea, "InvoicedQuantity", formatear_decimal(detalle.cantidad), unitCode=detalle.unidad,
             unitCodeListID="UN/ECE rec 20", unitCodeListAgencyName=ORGANISMO_ONU)
        _cbc(item_linea, "LineExtensionAmount", formatear_importe(linea.valor_venta), currencyID=moneda)
        precio = _cac(_cac(item_linea, "PricingReference"), "AlternativeConditionPrice")
        _cbc(precio, "PriceAmount", formatear_decimal(linea.precio_unitario), currencyID=moneda)
        _cbc(precio, "PriceTypeCode", "02" if tipo is TipoAfectacion.GRATUITO else "01", listName="Tipo de Precio",
             listAgencyName="PE:SUNAT", listURI=URI_CATALOGO.format(16))
        impuestos = _cac(item_linea, "TaxTotal")
        _cbc(impuestos, "TaxAmount", formatear_importe(linea.igv), currencyID=moneda)
        porcentaje = f.tasa_igv if tipo is TipoAfectacion.GRAVADO else Decimal("0")
        self._subtotal(impuestos, moneda, linea.base_igv, linea.igv, tipo, porcentaje, detalle.codigo_afectacion_igv)
        item = _cac(item_linea, "Item")
        _cbc(item, "Description", detalle.descripcion)
        _cbc(_cac(item, "SellersItemIdentification"), "ID", detalle.codigo)
        _cbc(_cac(item_linea, "Price"), "PriceAmount", formatear_decimal(detalle.valor_unitario
             if tipo is not TipoAfectacion.GRATUITO else Decimal("0")), currencyID=moneda)
