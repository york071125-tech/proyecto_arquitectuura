# 07 · Matriz de trazabilidad normativa (SUNAT ↔ UBL 2.1 ↔ Dominio ↔ DTO)

> Cada dato que exige SUNAT se rastrea de punta a punta: **norma/catálogo → XPath UBL → entidad de dominio → campo del DTO → regla de negocio**.
> Fuente de verdad: [`tests/trazabilidad/generar-matriz.mjs`](../tests/trazabilidad/generar-matriz.mjs). De ahí salen este cuadro y el [CSV](07-matriz-trazabilidad.csv) (abrible en Excel).

## Cómo leerla

| Columna | Significado |
|---|---|
| **XPath UBL 2.1** | Ruta en el XML (`cbc:` básicos, `cac:` agregados, `ext:` extensiones, `sac:` extensiones SUNAT) según `UBL-Invoice-2.1.xsd` y la guía SUNAT. |
| **Card.** | Cardinalidad **según la guía SUNAT** (el XSD de OASIS es más laxo: SUNAT restringe). |
| **Oblig.** | M = mandatorio · C = condicional. |
| **Cat.** | Catálogo SUNAT que gobierna los valores permitidos (**08 = sistema de cálculo del ISC**). |
| **Estado** | `Cubierto` (entra por DTO) · `Calculado` (lo calcula el dominio) · `Fuera de alcance fase 1` · `⚠ Verificar guía vigente`. |
| **Fuente** | `G-FAC` verificado contra la *Guía de elaboración XML Factura UBL 2.1*; `ANEXO` verificado contra el Anexo de catálogos RS 245-2017; `NO-EST` **no contrastado** en esta sesión (conocimiento general) → revisar antes de implementar. |

## Verificación automática

```bash
npm install
npm run matriz          # regenera docs/07-matriz-trazabilidad.csv y la tabla de este archivo
npm run verificar-matriz -- ruta/guia-factura.txt
```
Comprueba que (1) toda `RN-xxx` citada esté definida y (2) cada fila `G-FAC` exista en la guía SUNAT. Sin `guia.txt` el script sólo valida las RN. La corrida con el texto de la guía (`pdftotext`, no incluida en el repo) dio: **80 filas · 62 contrastadas · 15 sin contrastar · 0 errores**.

## Hallazgos de la trazabilidad (útiles para la exposición)

1. **Catálogo 08 → `cbc:TierRange`** dentro de `InvoiceLine/TaxTotal/TaxSubtotal/TaxCategory` (TR-056). Es **condicional**: sólo aparece cuando el tributo del ítem es ISC (`2000`). El mismo `TaxCategory` también lleva `cbc:Percent` con la tasa del ISC (el ejemplo oficial usa 20.00 con `TaxTypeCode = EXC`).
2. **Dos niveles de tributos**: cabecera (`/Invoice/cac:TaxTotal`) agrupa por tributo; cada línea (`InvoiceLine/cac:TaxTotal`) detalla. El dominio calcula por línea y **deriva** la cabecera (RN-022).
3. **Notas 07/08 no son `Invoice`**: usan raíces `CreditNote` / `DebitNote` (otros XSD) y líneas `CreditNoteLine`/`DebitNoteLine`. El generador UBL debe tener 3 plantillas, no 1 (TR-067…071).
4. **Boleta = `Invoice` con `InvoiceTypeCode=03`**, pero se informa por Resumen Diario (`SummaryDocuments`) y los XSD de resumen/baja son otros (TR-072…078).
5. **El RUC de ejemplo de la guía SUNAT (20100113612) no pasa el módulo 11**: es ficticio. Los tests no deben usarlo como válido (ver `tests/contratos/validar-contratos.mjs`).
6. **Estructura de partes**: la guía estudiada (2017) usa `cac:PartyTaxScheme`; versiones posteriores pueden usar `PartyIdentification`/`PartyLegalEntity`. Contrastar con la guía vigente antes de codificar el generador.

## Cobertura por catálogo → contrato

| Catálogo | Contrato que lo materializa |
|---|---|
| 01 Tipo de documento | `common#TipoDocumento` |
| 02 Moneda | `common#Moneda` |
| 03 Unidad | `common#UnidadMedida` |
| 05 Tributos | `common#CodigoTributo` |
| 06 Doc. identidad | `common#TipoDocIdentidad` |
| 07 Afectación IGV | `common#AfectacionIgv` |
| **08 Sistema ISC** | **`common#SistemaIsc`** (+ `productos`, `items[]`, `TributoLinea.tierRange`) |
| 09/10 Motivos NC/ND | `comprobante#DocumentoModificado.motivoCodigo` (+ regla ND ⇒ 01-03) |
| 13 UBIGEO | `common#Ubigeo` |
| 16 Tipo de precio | `common#TipoPrecio` |
| 51 Tipo de operación | `common#TipoOperacion` |
| 52 Leyendas | `common#Leyenda` |

## Matriz completa

<!-- MATRIZ:INICIO (generado por tests/trazabilidad/generar-matriz.mjs; no editar a mano) -->
| ID | Grupo | Dato SUNAT | XPath UBL 2.1 | Card. | Formato | Cat. | Oblig. | Dominio | DTO (specs/contracts/schemas) | Reglas | Estado | Fuente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TR-001 | Cabecera | Firma digital | /Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature | 0..1 | XMLDSig |  | M | Comprobante.xmlFirmado | (generado: PT-12) | RN-053 | Cubierto | G-FAC |
| TR-002 | Cabecera | Versión del UBL | /Invoice/cbc:UBLVersionID | 0..1 | "2.1" |  | M | constante | (generado) | RS 133-2019 | Cubierto | G-FAC |
| TR-003 | Cabecera | Versión estructura del documento | /Invoice/cbc:CustomizationID | 0..1 | "2.0" |  | M | constante | (generado) |  | Cubierto | G-FAC |
| TR-004 | Cabecera | Tipo de operación | /Invoice/cbc:ProfileID | 1 | an4 | 51 | M | Comprobante.tipoOperacion | tipoOperacion | RN-032, RN-033 | Cubierto | G-FAC |
| TR-005 | Cabecera | Serie y correlativo | /Invoice/cbc:ID | 1 | F###-NNNNNNNN |  | M | Comprobante.serie + correlativo | serie (+correlativo asignado) | RN-001, RN-002 | Cubierto | G-FAC |
| TR-006 | Cabecera | Fecha de emisión | /Invoice/cbc:IssueDate | 1 | YYYY-MM-DD |  | M | Comprobante.fechaEmision | fechaEmision | RN-006 | Cubierto | G-FAC |
| TR-007 | Cabecera | Hora de emisión | /Invoice/cbc:IssueTime | 0..1 | hh:mm:ss |  | C | Comprobante.horaEmision | horaEmision |  | Cubierto | G-FAC |
| TR-008 | Cabecera | Fecha de vencimiento | /Invoice/cbc:DueDate | 0..1 | YYYY-MM-DD |  | C | Comprobante.fechaVencimiento | fechaVencimiento |  | Cubierto | G-FAC |
| TR-009 | Cabecera | Tipo de documento | /Invoice/cbc:InvoiceTypeCode | 1 | an2 | 01 | M | Comprobante.tipo | tipoDocumento | RN-001 | Cubierto | G-FAC |
| TR-010 | Cabecera | Leyendas (monto en letras, gratuitas…) | /Invoice/cbc:Note/@languageLocaleID | 0..n | an..100 | 52 (15 en 2017) | M (1000) | Comprobante.leyendas[] | (generado) Leyenda{codigo,texto} | RN-045, RN-031 | Cubierto | G-FAC |
| TR-011 | Cabecera | Moneda | /Invoice/cbc:DocumentCurrencyCode | 1 | an3 | 02 | M | Comprobante.moneda | moneda | RN-036 | Cubierto | G-FAC |
| TR-012 | Cabecera | Cantidad de ítems | /Invoice/cbc:LineCountNumeric | 0..1 | n3 |  | C | count(items) | (calculado) |  | Calculado | G-FAC |
| TR-013 | Cabecera | Orden de compra | /Invoice/cac:OrderReference/cbc:ID | 0..1 | an..20 |  | C | — | — |  | Fuera de alcance fase 1 | G-FAC |
| TR-014 | Cabecera | Guía de remisión relacionada | /Invoice/cac:DespatchDocumentReference/cbc:ID | 0..n | an.. | 01/12 | C | — | — |  | Fuera de alcance fase 1 | G-FAC |
| TR-015 | Cabecera | Documento relacionado (anticipos, otros) | /Invoice/cac:AdditionalDocumentReference/cbc:ID | 0..n | an..30 | 12 | C | — | — |  | Fuera de alcance fase 1 | G-FAC |
| TR-016 | Emisor | Nombre comercial del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name | 1..1 | an..100 |  | M | Emisor.nombreComercial | EmisorRequest.nombreComercial |  | Cubierto | G-FAC |
| TR-017 | Emisor | RUC del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID | 0..1 | n11 |  | M | Emisor.ruc | EmisorRequest.ruc | RN-010 | Cubierto | G-FAC |
| TR-018 | Emisor | Tipo de documento del emisor (=6) | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID/@schemeID | 0..1 | an1 | 06 | M | constante '6' | (generado) | RN-010 | Cubierto | G-FAC |
| TR-019 | Emisor | Razón social del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName | 0..1 | an..100 |  | M | Emisor.razonSocial | EmisorRequest.razonSocial |  | Cubierto | G-FAC |
| TR-020 | Emisor | Código de domicilio fiscal / local anexo | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:AddressTypeCode | 0..1 | n4 |  | M | Direccion.codigoEstablecimiento | Direccion.codigoEstablecimiento |  | Cubierto | G-FAC |
| TR-021 | Emisor | UBIGEO del domicilio fiscal | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID | 0..1 | n6 | 13 | C | Direccion.ubigeo | Direccion.ubigeo | RN-013 | Cubierto | ANEXO |
| TR-022 | Adquirente | Tipo de documento de identidad del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID/@schemeID | 0..1 | an1 | 06 | M | Cliente.tipoDocIdentidad | cliente.tipoDocIdentidad | RN-012 | Cubierto | G-FAC |
| TR-023 | Adquirente | Número de documento del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID | 0..1 | n11 / según tipo |  | M | Cliente.numeroDoc | cliente.numeroDocumento | RN-010, RN-011 | Cubierto | G-FAC |
| TR-024 | Adquirente | Nombre o razón social del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName | 0..1 | an..100 |  | M | Cliente.nombre | cliente.nombre |  | Cubierto | G-FAC |
| TR-025 | Globales | Indicador cargo/descuento global | /Invoice/cac:AllowanceCharge/cbc:ChargeIndicator | 1 | true/false | 53 | M | DescuentoGlobal (false) | descuentosGlobales[] | RN-034 | Cubierto | G-FAC |
| TR-026 | Globales | Motivo del descuento global | /Invoice/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode | 0..1 | an..2 | 53 | C | DescuentoGlobal.codigo | descuentosGlobales[].codigo | RN-034 | Cubierto | G-FAC |
| TR-027 | Globales | Monto del descuento global | /Invoice/cac:AllowanceCharge/cbc:Amount | 1 | n(12,2) |  | M | DescuentoGlobal.monto | descuentosGlobales[].monto | RN-022 | Cubierto | G-FAC |
| TR-028 | Globales | Base del descuento global | /Invoice/cac:AllowanceCharge/cbc:BaseAmount | 1 | n(12,2) |  | C | DescuentoGlobal.base | descuentosGlobales[].base | RN-034 | Cubierto | G-FAC |
| TR-029 | Globales | Anticipo · serie-número | /Invoice/cac:PrepaidPayment/cbc:ID | 0..1 | F###-NNNNNNNN | 12 | C | Anticipo.serieNumero | anticipos[].serieNumero | RN-033 | Cubierto | G-FAC |
| TR-030 | Globales | Anticipo · monto | /Invoice/cac:PrepaidPayment/cbc:PaidAmount | 0..1 | n(15,2) |  | C | Anticipo.monto | anticipos[].monto | RN-033 | Cubierto | G-FAC |
| TR-031 | Globales | Forma de pago al crédito / cuotas | /Invoice/cac:PaymentTerms | 0..n | — |  | C | FormaPago | formaPago |  | ⚠ Verificar guía vigente | NO-EST |
| TR-032 | Totales | Total de tributos del comprobante | /Invoice/cac:TaxTotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Totales.igv + isc + icbper | (calculado) totales | RN-022 | Calculado | G-FAC |
| TR-033 | Totales | Base imponible por tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount | 0..1 | n(12,2) |  | C | Totales.gravadas/exoneradas/inafectas… | (calculado) | RN-035 | Calculado | G-FAC |
| TR-034 | Totales | Monto por tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Totales.igv / isc / icbper | (calculado) | RN-020, RN-040, RN-042 | Calculado | G-FAC |
| TR-035 | Totales | Código del tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID | 0..1 | an..3 | 05 | M | TributoLinea.codigo | (calculado) | RN-030 | Cubierto | G-FAC |
| TR-036 | Totales | Nombre del tributo (IGV, ISC, ICBPER…) | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-FAC |
| TR-037 | Totales | Código internacional del tributo (VAT, EXC…) | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-FAC |
| TR-038 | Totales | Total valor de venta | /Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount | 0..1 | n(12,2) |  | C | Σ valorVenta de ítems | (calculado) | RN-022 | Calculado | G-FAC |
| TR-039 | Totales | Total precio de venta (incluye impuestos) | /Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount | 0..1 | n(12,2) |  | C | Totales | (calculado) | RN-022 | Calculado | G-FAC |
| TR-040 | Totales | Total descuentos globales | /Invoice/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount | 0..1 | n(12,2) |  | C | Totales.descuentosGlobales | totales.descuentosGlobales | RN-022 | Calculado | G-FAC |
| TR-041 | Totales | Total otros cargos | /Invoice/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount | 0..1 | n(12,2) |  | C | Totales.otrosCargos | totales.otrosCargos | RN-022 | Calculado | G-FAC |
| TR-042 | Totales | Total anticipos | /Invoice/cac:LegalMonetaryTotal/cbc:PrepaidAmount | 0..1 | n(12,2) |  | C | Totales.anticipos | totales.anticipos | RN-033 | Calculado | G-FAC |
| TR-043 | Totales | Importe total a pagar | /Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount | 1 | n(12,2) |  | M | Totales.importeTotal | totales.importeTotal | RN-022 | Calculado | G-FAC |
| TR-044 | Ítem | Número de orden del ítem | /Invoice/cac:InvoiceLine/cbc:ID | 1 | n..3 |  | M | ItemComprobante.numero | (asignado) |  | Calculado | G-FAC |
| TR-045 | Ítem | Cantidad | /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity | 0..1 | n(12,10) |  | M | ItemComprobante.cantidad | items[].cantidad | RN-024 | Cubierto | G-FAC |
| TR-046 | Ítem | Unidad de medida | /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode | 0..1 | an..3 | 03 | M | ItemComprobante.unidad | items[].unidad |  | Cubierto | G-FAC |
| TR-047 | Ítem | Valor de venta del ítem | /Invoice/cac:InvoiceLine/cbc:LineExtensionAmount | 1 | n(12,2) |  | M | ItemComprobante.valorVenta | ItemResponse.valorVenta | RN-021 | Calculado | G-FAC |
| TR-048 | Ítem | Precio de venta unitario / valor referencial | /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount | 1 | n(12,10) |  | M | ItemComprobante.precioUnitario | ItemResponse.precioUnitario | RN-023 | Calculado | G-FAC |
| TR-049 | Ítem | Tipo de precio | /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode | 0..1 | an2 | 16 | M | ItemComprobante.tipoPrecio | items[].tipoPrecio | RN-031 | Cubierto | G-FAC |
| TR-050 | Ítem | Cargo/descuento del ítem | /Invoice/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount | 1 | n(12,2) | 53 | C | ItemComprobante.descuento | items[].descuento | RN-034 | Cubierto | G-FAC |
| TR-051 | Ítem | Monto de tributos del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Σ TributoLinea.monto | ItemResponse.tributos | RN-020 | Calculado | G-FAC |
| TR-052 | Ítem · IGV | Base de cada tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount | 0..1 | n(12,2) |  | M | TributoLinea.baseImponible | TributoLinea.baseImponible | RN-041 | Calculado | G-FAC |
| TR-053 | Ítem · IGV | Monto de cada tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount | 1 | n(12,2) |  | M | TributoLinea.monto | TributoLinea.monto | RN-020, RN-040, RN-042 | Calculado | G-FAC |
| TR-054 | Ítem · IGV | Tasa del tributo (%) | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent | 0..1 | n(3,5) |  | M | TributoLinea.tasa | TributoLinea.tasa | RN-020 | Cubierto | G-FAC |
| TR-055 | Ítem · IGV | Afectación al IGV | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode | 0..1 | an2 | 07 | M | ItemComprobante.afectacionIgv | items[].afectacionIgv | RN-030 | Cubierto | G-FAC |
| TR-056 | Ítem · ISC | **Sistema de cálculo del ISC** | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange | 0..1 | an2 | **08** | C (si ISC) | TributoLinea.tierRange / Producto.sistemaIsc | items[].sistemaIsc · TributoLinea.tierRange | RN-040, RN-041, RN-043 | Cubierto | G-FAC |
| TR-057 | Ítem · ISC | Tasa / monto del ISC | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent | 0..1 | n(3,5) | 08 | C | Producto.tasaIsc / montoFijoIsc | items[].tasaIsc / montoFijoIsc | RN-040 | Cubierto | G-FAC |
| TR-058 | Ítem · ICBPER | Cantidad de bolsas (ICBPER) | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:BaseUnitMeasure | 0..1 | n | 05 (7152) | C | ItemComprobante.bolsasIcbper | items[].bolsasIcbper | RN-042 | ⚠ Verificar guía vigente | NO-EST |
| TR-059 | Ítem · ICBPER | Monto unitario del ICBPER | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:PerUnitAmount | 0..1 | n(12,2) | 05 (7152) | C | parámetro tarifaIcbper | (parámetro) | RN-042 | ⚠ Verificar guía vigente | NO-EST |
| TR-060 | Ítem | Código del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID | 0..1 | an..3 | 05 | M | TributoLinea.codigo | TributoLinea.codigo | RN-030 | Cubierto | G-FAC |
| TR-061 | Ítem | Nombre del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-FAC |
| TR-062 | Ítem | Código internacional del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode | 0..1 | an4 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-FAC |
| TR-063 | Ítem | Descripción del ítem | /Invoice/cac:InvoiceLine/cac:Item/cbc:Description | 0..n | an..250 |  | M | ItemComprobante.descripcion | items[].descripcion |  | Cubierto | G-FAC |
| TR-064 | Ítem | Código de producto del vendedor | /Invoice/cac:InvoiceLine/cac:Item/cac:SellersItemIdentification/cbc:ID | 0..1 | an..30 |  | C | Producto.codigoInterno | items[].codigoInterno |  | Cubierto | G-FAC |
| TR-065 | Ítem | Código de producto SUNAT (UNSPSC) | /Invoice/cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode | 1 | n8 | 25 | C | Producto.codigoSunat | items[].codigoSunat |  | Cubierto | G-FAC |
| TR-066 | Ítem | Valor unitario (sin impuestos) | /Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount | 1 | n(12,10) |  | M | ItemComprobante.valorUnitario | items[].valorUnitario | RN-024 | Cubierto | G-FAC |
| TR-067 | Nota 07/08 | Documento que se modifica · serie-número | /CreditNote\|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID | 1 | F###-N… |  | M | DocumentoModificado.serie + correlativo | documentoModificado.serie/correlativo | RN-004 | Cubierto | NO-EST |
| TR-068 | Nota 07/08 | Documento que se modifica · tipo | /CreditNote\|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode | 1 | an2 | 01 | M | DocumentoModificado.tipoDocumento | documentoModificado.tipoDocumento | RN-004 | Cubierto | NO-EST |
| TR-069 | Nota 07/08 | Motivo (tipo de nota) | /CreditNote\|DebitNote/cac:DiscrepancyResponse/cbc:ResponseCode | 1 | an2 | 09 / 10 | M | DocumentoModificado.motivoCodigo | documentoModificado.motivoCodigo | RN-004 | Cubierto | ANEXO |
| TR-070 | Nota 07/08 | Sustento | /CreditNote\|DebitNote/cac:DiscrepancyResponse/cbc:Description | 1 | an..250 |  | M | DocumentoModificado.sustento | documentoModificado.sustento | RN-004 | Cubierto | NO-EST |
| TR-071 | Nota 07/08 | Cantidad de la línea (NC / ND) | /CreditNote/cac:CreditNoteLine/cbc:CreditedQuantity · /DebitNote/cac:DebitNoteLine/cbc:DebitedQuantity | 1 | n(12,10) | 03 | M | ItemComprobante.cantidad | items[].cantidad |  | Cubierto | NO-EST |
| TR-072 | Resumen diario | Identificador del resumen (RC-AAAAMMDD-n) | /SummaryDocuments/cbc:ID | 1 | RC-\d{8}-\d{1,5} |  | M | ResumenDiario.id | LoteEnvioResponse.id | RN-006 | Cubierto | NO-EST |
| TR-073 | Resumen diario | Fecha de emisión de los documentos | /SummaryDocuments/cbc:ReferenceDate | 1 | YYYY-MM-DD |  | M | ResumenDiario.fechaReferencia | ResumenDiarioRequest.fechaReferencia | RN-006 | Cubierto | NO-EST |
| TR-074 | Resumen diario | Estado del ítem (adicionar/modificar/anular) | /SummaryDocuments/sac:SummaryDocumentsLine/cac:Status/cbc:ConditionCode | 1 | n1 | 19 | M | derivado de Estado | (generado) | RN-006 | Cubierto | ANEXO |
| TR-075 | Baja | Identificador de la baja (RA-AAAAMMDD-n) | /VoidedDocuments/cbc:ID | 1 | RA-\d{8}-\d{1,5} |  | M | ComunicacionBaja.id | LoteEnvioResponse.id | RN-007 | Cubierto | NO-EST |
| TR-076 | Baja | Serie del documento dado de baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentSerialID | 1 | an4 |  | M | documentos[].serie | ComunicacionBajaRequest.documentos[].serie | RN-007 | Cubierto | NO-EST |
| TR-077 | Baja | Correlativo del documento dado de baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentNumberID | 1 | n..8 |  | M | documentos[].correlativo | ComunicacionBajaRequest.documentos[].correlativo | RN-007 | Cubierto | NO-EST |
| TR-078 | Baja | Motivo de la baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:VoidReasonDescription | 1 | an..100 |  | M | documentos[].motivo | ComunicacionBajaRequest.documentos[].motivo | RN-007 | Cubierto | NO-EST |
| TR-079 | CDR | Código de respuesta de SUNAT/OSE | /ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:ResponseCode | 1 | an.. |  | M | EnvioSunat.codigoRespuesta | ResultadoSunat.codigoRespuesta | §4 de 01-… | Cubierto | NO-EST |
| TR-080 | CDR | Mensaje / descripción de la respuesta | /ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:Description | 1 | an.. |  | M | EnvioSunat.mensaje | ResultadoSunat.descripcion |  | Cubierto | NO-EST |
<!-- MATRIZ:FIN -->
