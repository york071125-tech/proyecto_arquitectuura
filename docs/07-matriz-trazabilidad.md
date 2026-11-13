# 07 · Matriz de trazabilidad normativa (SUNAT ↔ UBL 2.1 ↔ Dominio ↔ DTO)

> Cada dato que exige SUNAT se rastrea de punta a punta: **norma/catálogo → XPath UBL → entidad de dominio → campo del DTO → regla de negocio**.
> Fuente de verdad: [`tests/trazabilidad/generar-matriz.mjs`](../tests/trazabilidad/generar-matriz.mjs). De ahí salen este cuadro y el [CSV](07-matriz-trazabilidad.csv) (abrible en Excel).

## Cómo leerla

| Columna | Significado |
|---|---|
| **XPath UBL 2.1** | Ruta en el XML (`cbc:` básicos, `cac:` agregados, `ext:` extensiones, `sac:` extensiones SUNAT). Los atributos se escriben `ruta@atributo`, igual que el estándar de SUNAT. |
| **Card.** | Cardinalidad **según el estándar SUNAT** (el XSD de OASIS es más laxo: SUNAT restringe). |
| **Oblig.** | M = mandatorio · C = condicional. |
| **Cat.** | Catálogo SUNAT que gobierna los valores permitidos (**08 = sistema de cálculo del ISC**). |
| **Estado** | `Cubierto` (entra por DTO) · `Calculado` (lo calcula el dominio) · `Retirado` (ya no figura en el estándar vigente; se comprueba su ausencia) · `Fuera de alcance fase 1` · `⚠ Verificar`. |
| **Fuente** | `G-VIG`: la **ruta completa** se verificó automáticamente contra el estándar vigente de SUNAT (ver abajo) · `NO-EST`: **no contrastado** (no figura en los anexos consultados) → revisar antes de implementar. |

## Fuentes oficiales (consultadas el 06-11-2026)

La primera entrega se basó en la guía XML de **2017**, ya superada. Esta versión usa el estándar vigente:

| Fuente | Cubre | Documento |
|---|---|---|
| Anexo 9-A «Estándar UBL 2.1» (RS 114-2019/SUNAT, Anexo VII) | Factura, nota de crédito y nota de débito | <https://www.sunat.gob.pe/legislacion/superin/2019/anexoVII-114-2019.pdf> |
| RS 114-2019/SUNAT, Anexo X | Resumen diario (`SummaryDocuments`) | <https://www.sunat.gob.pe/legislacion/superin/2019/anexoX-114-2019.pdf> |
| RS 193-2020/SUNAT, Anexo IV | **Forma de pago** obligatoria (`PaymentTerms`) | <https://www.sunat.gob.pe/legislacion/superin/2020/anexo4-193-2020.pdf> |
| RS 361-2015/SUNAT, Anexo 1 (mod. RS 042-2021) | Formato 14.1, Registro de Ventas e Ingresos | <https://www.sunat.gob.pe/legislacion/superin/2015/anexo1-361-2015.pdf> |
| RS 042-2018/SUNAT, Anexo 2 | Formato 12.1, Inventario Permanente en Unidades Físicas | <https://www.sunat.gob.pe/legislacion/superin/2018/anexo-042-2018.pdf> |
| RS 169-2015/SUNAT, Anexo 3 | Tablas del PLE (5, 6, 10, 12, 13…) | <https://www.sunat.gob.pe/legislacion/superin/2015/anexo3-rs169-2015.pdf> |

⚠ Estos anexos son los que se encontraron en el portal de SUNAT; SUNAT los modifica con frecuencia. Antes de implementar, confirmar en <https://cpe.sunat.gob.pe> que siguen vigentes.

## Verificación automática

```bash
npm install
npm run matriz                        # regenera docs/07-matriz-trazabilidad.csv y la tabla de este archivo
# Opcional (contrastar las rutas con los anexos oficiales; los PDF no se guardan en el repo):
pdftotext -raw anexoVII-114-2019.pdf anexo9A.txt
pdftotext -raw anexoX-114-2019.pdf   anexoX.txt
pdftotext -raw anexo4-193-2020.pdf   anexo193.txt
npm run verificar-matriz -- anexo9A.txt anexoX.txt anexo193.txt
```
Sin anexos, el script solo comprueba que toda `RN-xxx` citada esté definida. Con los anexos compara la **ruta completa** de cada fila `G-VIG` y exige que las filas `Retirado` **no** aparezcan. Resultado de la última corrida (06-11-2026): **83 filas · 74 contrastadas · 1 retirada (ausencia comprobada) · 8 `NO-EST` · 0 errores**.

## Qué cambió respecto a la entrega anterior (corrección del ingeniero)

| Antes (guía 2017) | Ahora (estándar vigente) |
|---|---|
| Emisor y adquirente en `cac:PartyTaxScheme/cbc:CompanyID` y `…/cbc:RegistrationName` (TR-017…024) | `cac:PartyIdentification/cbc:ID@schemeID` para el documento y `cac:PartyLegalEntity/cbc:RegistrationName` para la razón social |
| Tipo de operación en `cbc:ProfileID` (TR-004) | `cbc:InvoiceTypeCode@listID` (catálogo 51) |
| `cbc:LineCountNumeric` (TR-012) | **Retirado**: ya no figura en el estándar |
| Forma de pago «NO-EST / verificar» (TR-031) | **Obligatoria** desde 2021 (RS 193-2020): `PaymentTerms` con `FormaPago`, `Contado`/`Credito` y cuotas (TR-031, TR-081…083) |
| Notas de crédito/débito, resumen diario: «NO-EST» | Contrastados con los anexos (TR-067…074) |
| Atributos como `ruta/@atributo` | `ruta@atributo` (notación del estándar) |

## Hallazgos de la trazabilidad (útiles para la exposición)

1. **Catálogo 08 → `cbc:TierRange`** dentro de `InvoiceLine/TaxTotal/TaxSubtotal/TaxCategory` (TR-056). Es **condicional**: solo aparece cuando el tributo del ítem es ISC (`2000`). El mismo `TaxCategory` lleva `cbc:Percent` con la tasa del ISC.
2. **Dos niveles de tributos**: cabecera (`/Invoice/cac:TaxTotal`) agrupa por tributo; cada línea (`InvoiceLine/cac:TaxTotal`) detalla. El dominio calcula por línea y **deriva** la cabecera (RN-022).
3. **Notas 07/08 no son `Invoice`**: usan las raíces `CreditNote` / `DebitNote` (otros XSD) y líneas `CreditNoteLine`/`DebitNoteLine` (TR-067…071). Un **único** `UblXmlAdapter` genera los tres documentos desde sus XSD (ADR-07); no hay «una plantilla por documento».
4. **Boleta = `Invoice` con `InvoiceTypeCode=03`**, pero se informa por Resumen Diario (`SummaryDocuments`, TR-072…074). La baja (`VoidedDocuments`, TR-075…078) sigue sin contrastar.
5. **El RUC de ejemplo de la guía SUNAT (20100113612) no pasa el módulo 11**: es ficticio. Los tests no deben usarlo como válido.
6. **Filas sin contrastar (8)**: ICBPER (TR-058, TR-059), baja (TR-075…078) y CDR (TR-079, TR-080) no figuran en los anexos consultados. No se afirma nada sobre ellas.

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
| TR-001 | Cabecera | Firma digital | /Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature | 0..1 | XMLDSig |  | M | Comprobante.xmlFirmado | (generado: PT-12) | RN-053 | Cubierto | G-VIG |
| TR-002 | Cabecera | Versión del UBL | /Invoice/cbc:UBLVersionID | 0..1 | "2.1" |  | M | constante | (generado) | RS 133-2019 | Cubierto | G-VIG |
| TR-003 | Cabecera | Versión estructura del documento | /Invoice/cbc:CustomizationID | 0..1 | "2.0" |  | M | constante | (generado) |  | Cubierto | G-VIG |
| TR-004 | Cabecera | Tipo de operación (listID del tipo de documento) | /Invoice/cbc:InvoiceTypeCode@listID | 1 | an4 | 51 | M | Comprobante.tipoOperacion | tipoOperacion | RN-032, RN-033 | Cubierto | G-VIG |
| TR-005 | Cabecera | Serie y correlativo | /Invoice/cbc:ID | 1 | F###-NNNNNNNN |  | M | Comprobante.serie + correlativo | serie (+correlativo asignado) | RN-001, RN-002 | Cubierto | G-VIG |
| TR-006 | Cabecera | Fecha de emisión | /Invoice/cbc:IssueDate | 1 | YYYY-MM-DD |  | M | Comprobante.fechaEmision | fechaEmision | RN-006 | Cubierto | G-VIG |
| TR-007 | Cabecera | Hora de emisión | /Invoice/cbc:IssueTime | 0..1 | hh:mm:ss |  | C | Comprobante.horaEmision | horaEmision |  | Cubierto | G-VIG |
| TR-008 | Cabecera | Fecha de vencimiento | /Invoice/cbc:DueDate | 0..1 | YYYY-MM-DD |  | C | Comprobante.fechaVencimiento | fechaVencimiento |  | Cubierto | G-VIG |
| TR-009 | Cabecera | Tipo de documento | /Invoice/cbc:InvoiceTypeCode | 1 | an2 | 01 | M | Comprobante.tipo | tipoDocumento | RN-001 | Cubierto | G-VIG |
| TR-010 | Cabecera | Leyendas (monto en letras, gratuitas…) | /Invoice/cbc:Note@languageLocaleID | 0..n | an..100 | 52 (15 en 2017) | M (1000) | Comprobante.leyendas[] | (generado) Leyenda{codigo,texto} | RN-045, RN-031 | Cubierto | G-VIG |
| TR-011 | Cabecera | Moneda | /Invoice/cbc:DocumentCurrencyCode | 1 | an3 | 02 | M | Comprobante.moneda | moneda | RN-036 | Cubierto | G-VIG |
| TR-012 | Cabecera | Cantidad de ítems | /Invoice/cbc:LineCountNumeric | 0..1 | n3 |  | C | count(items) | (calculado) |  | Retirado: no figura en el estándar vigente | G-VIG |
| TR-013 | Cabecera | Orden de compra | /Invoice/cac:OrderReference/cbc:ID | 0..1 | an..20 |  | C | — | — |  | Fuera de alcance fase 1 | G-VIG |
| TR-014 | Cabecera | Guía de remisión relacionada | /Invoice/cac:DespatchDocumentReference/cbc:ID | 0..n | an.. | 01/12 | C | — | — |  | Fuera de alcance fase 1 | G-VIG |
| TR-015 | Cabecera | Documento relacionado (anticipos, otros) | /Invoice/cac:AdditionalDocumentReference/cbc:ID | 0..n | an..30 | 12 | C | — | — |  | Fuera de alcance fase 1 | G-VIG |
| TR-016 | Emisor | Nombre comercial del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name | 1..1 | an..100 |  | M | Emisor.nombreComercial | EmisorRequest.nombreComercial |  | Cubierto | G-VIG |
| TR-017 | Emisor | RUC del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID | 0..1 | n11 |  | M | Emisor.ruc | EmisorRequest.ruc | RN-010 | Cubierto | G-VIG |
| TR-018 | Emisor | Tipo de documento del emisor (=6) | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID@schemeID | 0..1 | an1 | 06 | M | constante '6' | (generado) | RN-010 | Cubierto | G-VIG |
| TR-019 | Emisor | Razón social del emisor | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName | 0..1 | an..100 |  | M | Emisor.razonSocial | EmisorRequest.razonSocial |  | Cubierto | G-VIG |
| TR-020 | Emisor | Código de domicilio fiscal / local anexo | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:AddressTypeCode | 0..1 | n4 |  | M | Direccion.codigoEstablecimiento | Direccion.codigoEstablecimiento |  | Cubierto | G-VIG |
| TR-021 | Emisor | UBIGEO del domicilio fiscal | /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID | 0..1 | n6 | 13 | C | Direccion.ubigeo | Direccion.ubigeo | RN-013 | Cubierto | G-VIG |
| TR-022 | Adquirente | Tipo de documento de identidad del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID@schemeID | 0..1 | an1 | 06 | M | Cliente.tipoDocIdentidad | cliente.tipoDocIdentidad | RN-012 | Cubierto | G-VIG |
| TR-023 | Adquirente | Número de documento del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID | 0..1 | n11 / según tipo |  | M | Cliente.numeroDoc | cliente.numeroDocumento | RN-010, RN-011 | Cubierto | G-VIG |
| TR-024 | Adquirente | Nombre o razón social del cliente | /Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName | 0..1 | an..100 |  | M | Cliente.nombre | cliente.nombre |  | Cubierto | G-VIG |
| TR-025 | Globales | Indicador cargo/descuento global | /Invoice/cac:AllowanceCharge/cbc:ChargeIndicator | 1 | true/false | 53 | M | DescuentoGlobal (false) | descuentosGlobales[] | RN-034 | Cubierto | G-VIG |
| TR-026 | Globales | Motivo del descuento global | /Invoice/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode | 0..1 | an..2 | 53 | C | DescuentoGlobal.codigo | descuentosGlobales[].codigo | RN-034 | Cubierto | G-VIG |
| TR-027 | Globales | Monto del descuento global | /Invoice/cac:AllowanceCharge/cbc:Amount | 1 | n(12,2) |  | M | DescuentoGlobal.monto | descuentosGlobales[].monto | RN-022 | Cubierto | G-VIG |
| TR-028 | Globales | Base del descuento global | /Invoice/cac:AllowanceCharge/cbc:BaseAmount | 1 | n(12,2) |  | C | DescuentoGlobal.base | descuentosGlobales[].base | RN-034 | Cubierto | G-VIG |
| TR-029 | Globales | Anticipo · serie-número | /Invoice/cac:PrepaidPayment/cbc:ID | 0..1 | F###-NNNNNNNN | 12 | C | Anticipo.serieNumero | anticipos[].serieNumero | RN-033 | Cubierto | G-VIG |
| TR-030 | Globales | Anticipo · monto | /Invoice/cac:PrepaidPayment/cbc:PaidAmount | 0..1 | n(15,2) |  | C | Anticipo.monto | anticipos[].monto | RN-033 | Cubierto | G-VIG |
| TR-031 | Globales | Forma de pago · indicador «FormaPago» | /Invoice/cac:PaymentTerms/cbc:ID | 1 | an9 |  | M | FormaPago | formaPago | RN-080 | Cubierto | G-VIG |
| TR-032 | Totales | Total de tributos del comprobante | /Invoice/cac:TaxTotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Totales.igv + isc + icbper | (calculado) totales | RN-022 | Calculado | G-VIG |
| TR-033 | Totales | Base imponible por tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount | 0..1 | n(12,2) |  | C | Totales.gravadas/exoneradas/inafectas… | (calculado) | RN-035 | Calculado | G-VIG |
| TR-034 | Totales | Monto por tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Totales.igv / isc / icbper | (calculado) | RN-020, RN-040, RN-042 | Calculado | G-VIG |
| TR-035 | Totales | Código del tributo | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID | 0..1 | an..3 | 05 | M | TributoLinea.codigo | (calculado) | RN-030 | Cubierto | G-VIG |
| TR-036 | Totales | Nombre del tributo (IGV, ISC, ICBPER…) | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-VIG |
| TR-037 | Totales | Código internacional del tributo (VAT, EXC…) | /Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-VIG |
| TR-038 | Totales | Total valor de venta | /Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount | 0..1 | n(12,2) |  | C | Σ valorVenta de ítems | (calculado) | RN-022 | Calculado | G-VIG |
| TR-039 | Totales | Total precio de venta (incluye impuestos) | /Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount | 0..1 | n(12,2) |  | C | Totales | (calculado) | RN-022 | Calculado | G-VIG |
| TR-040 | Totales | Total descuentos globales | /Invoice/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount | 0..1 | n(12,2) |  | C | Totales.descuentosGlobales | totales.descuentosGlobales | RN-022 | Calculado | G-VIG |
| TR-041 | Totales | Total otros cargos | /Invoice/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount | 0..1 | n(12,2) |  | C | Totales.otrosCargos | totales.otrosCargos | RN-022 | Calculado | G-VIG |
| TR-042 | Totales | Total anticipos | /Invoice/cac:LegalMonetaryTotal/cbc:PrepaidAmount | 0..1 | n(12,2) |  | C | Totales.anticipos | totales.anticipos | RN-033 | Calculado | G-VIG |
| TR-043 | Totales | Importe total a pagar | /Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount | 1 | n(12,2) |  | M | Totales.importeTotal | totales.importeTotal | RN-022 | Calculado | G-VIG |
| TR-044 | Ítem | Número de orden del ítem | /Invoice/cac:InvoiceLine/cbc:ID | 1 | n..3 |  | M | ItemComprobante.numero | (asignado) |  | Calculado | G-VIG |
| TR-045 | Ítem | Cantidad | /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity | 0..1 | n(12,10) |  | M | ItemComprobante.cantidad | items[].cantidad | RN-024 | Cubierto | G-VIG |
| TR-046 | Ítem | Unidad de medida | /Invoice/cac:InvoiceLine/cbc:InvoicedQuantity@unitCode | 0..1 | an..3 | 03 | M | ItemComprobante.unidad | items[].unidad |  | Cubierto | G-VIG |
| TR-047 | Ítem | Valor de venta del ítem | /Invoice/cac:InvoiceLine/cbc:LineExtensionAmount | 1 | n(12,2) |  | M | ItemComprobante.valorVenta | ItemResponse.valorVenta | RN-021 | Calculado | G-VIG |
| TR-048 | Ítem | Precio de venta unitario / valor referencial | /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount | 1 | n(12,10) |  | M | ItemComprobante.precioUnitario | ItemResponse.precioUnitario | RN-023 | Calculado | G-VIG |
| TR-049 | Ítem | Tipo de precio | /Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode | 0..1 | an2 | 16 | M | ItemComprobante.tipoPrecio | items[].tipoPrecio | RN-031 | Cubierto | G-VIG |
| TR-050 | Ítem | Cargo/descuento del ítem | /Invoice/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount | 1 | n(12,2) | 53 | C | ItemComprobante.descuento | items[].descuento | RN-034 | Cubierto | G-VIG |
| TR-051 | Ítem | Monto de tributos del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount | 1 | n(12,2) |  | M | Σ TributoLinea.monto | ItemResponse.tributos | RN-020 | Calculado | G-VIG |
| TR-052 | Ítem · IGV | Base de cada tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount | 0..1 | n(12,2) |  | M | TributoLinea.baseImponible | TributoLinea.baseImponible | RN-041 | Calculado | G-VIG |
| TR-053 | Ítem · IGV | Monto de cada tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount | 1 | n(12,2) |  | M | TributoLinea.monto | TributoLinea.monto | RN-020, RN-040, RN-042 | Calculado | G-VIG |
| TR-054 | Ítem · IGV | Tasa del tributo (%) | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent | 0..1 | n(3,5) |  | M | TributoLinea.tasa | TributoLinea.tasa | RN-020 | Cubierto | G-VIG |
| TR-055 | Ítem · IGV | Afectación al IGV | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode | 0..1 | an2 | 07 | M | ItemComprobante.afectacionIgv | items[].afectacionIgv | RN-030 | Cubierto | G-VIG |
| TR-056 | Ítem · ISC | **Sistema de cálculo del ISC** | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange | 0..1 | an2 | **08** | C (si ISC) | TributoLinea.tierRange / Producto.sistemaIsc | items[].sistemaIsc · TributoLinea.tierRange | RN-040, RN-041, RN-043 | Cubierto | G-VIG |
| TR-057 | Ítem · ISC | Tasa / monto del ISC | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent | 0..1 | n(3,5) | 08 | C | Producto.tasaIsc / montoFijoIsc | items[].tasaIsc / montoFijoIsc | RN-040 | Cubierto | G-VIG |
| TR-058 | Ítem · ICBPER | Cantidad de bolsas (ICBPER) | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:BaseUnitMeasure | 0..1 | n | 05 (7152) | C | ItemComprobante.bolsasIcbper | items[].bolsasIcbper | RN-042 | ⚠ Verificar guía vigente | NO-EST |
| TR-059 | Ítem · ICBPER | Monto unitario del ICBPER | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:PerUnitAmount | 0..1 | n(12,2) | 05 (7152) | C | parámetro tarifaIcbper | (parámetro) | RN-042 | ⚠ Verificar guía vigente | NO-EST |
| TR-060 | Ítem | Código del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID | 0..1 | an..3 | 05 | M | TributoLinea.codigo | TributoLinea.codigo | RN-030 | Cubierto | G-VIG |
| TR-061 | Ítem | Nombre del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name | 0..1 | an..6 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-VIG |
| TR-062 | Ítem | Código internacional del tributo del ítem | /Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode | 0..1 | an4 | 05 | M | derivado de codigo | (generado) |  | Cubierto | G-VIG |
| TR-063 | Ítem | Descripción del ítem | /Invoice/cac:InvoiceLine/cac:Item/cbc:Description | 0..n | an..250 |  | M | ItemComprobante.descripcion | items[].descripcion |  | Cubierto | G-VIG |
| TR-064 | Ítem | Código de producto del vendedor | /Invoice/cac:InvoiceLine/cac:Item/cac:SellersItemIdentification/cbc:ID | 0..1 | an..30 |  | C | Producto.codigoInterno | items[].codigoInterno |  | Cubierto | G-VIG |
| TR-065 | Ítem | Código de producto SUNAT (UNSPSC) | /Invoice/cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode | 1 | n8 | 25 | C | Producto.codigoSunat | items[].codigoSunat |  | Cubierto | G-VIG |
| TR-066 | Ítem | Valor unitario (sin impuestos) | /Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount | 1 | n(12,10) |  | M | ItemComprobante.valorUnitario | items[].valorUnitario | RN-024 | Cubierto | G-VIG |
| TR-067 | Nota 07/08 | Documento que se modifica · serie-número | /CreditNote\|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID | 1 | F###-N… |  | M | DocumentoModificado.serie + correlativo | documentoModificado.serie/correlativo | RN-004 | Cubierto | G-VIG |
| TR-068 | Nota 07/08 | Documento que se modifica · tipo | /CreditNote\|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode | 1 | an2 | 01 | M | DocumentoModificado.tipoDocumento | documentoModificado.tipoDocumento | RN-004 | Cubierto | G-VIG |
| TR-069 | Nota 07/08 | Motivo (tipo de nota) | /CreditNote\|DebitNote/cac:DiscrepancyResponse/cbc:ResponseCode | 1 | an2 | 09 / 10 | M | DocumentoModificado.motivoCodigo | documentoModificado.motivoCodigo | RN-004 | Cubierto | G-VIG |
| TR-070 | Nota 07/08 | Sustento | /CreditNote\|DebitNote/cac:DiscrepancyResponse/cbc:Description | 1 | an..250 |  | M | DocumentoModificado.sustento | documentoModificado.sustento | RN-004 | Cubierto | G-VIG |
| TR-071 | Nota 07/08 | Cantidad de la línea (NC / ND) | /CreditNote/cac:CreditNoteLine/cbc:CreditedQuantity · /DebitNote/cac:DebitNoteLine/cbc:DebitedQuantity | 1 | n(12,10) | 03 | M | ItemComprobante.cantidad | items[].cantidad |  | Cubierto | G-VIG |
| TR-072 | Resumen diario | Identificador del resumen (RC-AAAAMMDD-n) | /SummaryDocuments/cbc:ID | 1 | RC-\d{8}-\d{1,5} |  | M | ResumenDiario.id | LoteEnvioResponse.id | RN-006 | Cubierto | G-VIG |
| TR-073 | Resumen diario | Fecha de emisión de los documentos | /SummaryDocuments/cbc:ReferenceDate | 1 | YYYY-MM-DD |  | M | ResumenDiario.fechaReferencia | ResumenDiarioRequest.fechaReferencia | RN-006 | Cubierto | G-VIG |
| TR-074 | Resumen diario | Estado del ítem (adicionar/modificar/anular) | /SummaryDocuments/sac:SummaryDocumentsLine/cac:Status/cbc:ConditionCode | 1 | n1 | 19 | M | derivado de Estado | (generado) | RN-006 | Cubierto | G-VIG |
| TR-075 | Baja | Identificador de la baja (RA-AAAAMMDD-n) | /VoidedDocuments/cbc:ID | 1 | RA-\d{8}-\d{1,5} |  | M | ComunicacionBaja.id | LoteEnvioResponse.id | RN-007 | Cubierto | NO-EST |
| TR-076 | Baja | Serie del documento dado de baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentSerialID | 1 | an4 |  | M | documentos[].serie | ComunicacionBajaRequest.documentos[].serie | RN-007 | Cubierto | NO-EST |
| TR-077 | Baja | Correlativo del documento dado de baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentNumberID | 1 | n..8 |  | M | documentos[].correlativo | ComunicacionBajaRequest.documentos[].correlativo | RN-007 | Cubierto | NO-EST |
| TR-078 | Baja | Motivo de la baja | /VoidedDocuments/sac:VoidedDocumentsLine/sac:VoidReasonDescription | 1 | an..100 |  | M | documentos[].motivo | ComunicacionBajaRequest.documentos[].motivo | RN-007 | Cubierto | NO-EST |
| TR-079 | CDR | Código de respuesta de SUNAT/OSE | /ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:ResponseCode | 1 | an.. |  | M | EnvioSunat.codigoRespuesta | ResultadoSunat.codigoRespuesta | §4 de 01-… | Cubierto | NO-EST |
| TR-080 | CDR | Mensaje / descripción de la respuesta | /ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:Description | 1 | an.. |  | M | EnvioSunat.mensaje | ResultadoSunat.descripcion |  | Cubierto | NO-EST |
| TR-081 | Forma de pago | Forma de pago: Contado / Credito / Cuota### | /Invoice/cac:PaymentTerms/cbc:PaymentMeansID | 1..n | an..8 |  | M | FormaPago.tipo / Cuota.numero | formaPago.tipo / cuotas[] | RN-080, RN-081 | Cubierto | G-VIG |
| TR-082 | Forma de pago | Monto neto pendiente (crédito) o monto de cada cuota | /Invoice/cac:PaymentTerms/cbc:Amount | 0..n | n(12,2) | 02 | C | FormaPago.montoPendiente / Cuota.monto | formaPago.montoPendiente / cuotas[].monto | RN-081 | Cubierto | G-VIG |
| TR-083 | Forma de pago | Fecha de vencimiento de la cuota | /Invoice/cac:PaymentTerms/cbc:PaymentDueDate | 0..n | YYYY-MM-DD |  | C | Cuota.fechaVencimiento | cuotas[].fechaVencimiento | RN-081 | Cubierto | G-VIG |
<!-- MATRIZ:FIN -->
