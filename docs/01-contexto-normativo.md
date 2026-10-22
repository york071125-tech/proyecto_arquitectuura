# 01 · Contexto normativo

## 1. Normas citadas en el enunciado

| Norma | Qué regula (verificado) | Impacto en el sistema |
|---|---|---|
| **RS 097-2012/SUNAT** | Crea el **SEE – Sistema de Emisión Electrónica desarrollado desde los sistemas del contribuyente**: factura, boleta, notas, resumen diario, comunicación de baja, guía; envío a SUNAT o a un **OSE**. Modificada varias veces (p. ej. RS 003-2023 sobre plazos de envío). | Define el modo de emisión, el envío, la constancia (CDR) y los plazos. Base de `EP-` de envío y de ADR-03. |
| **RS 234-2006/SUNAT** | **Libros y registros vinculados a asuntos tributarios** (Registro de Ventas, Compras, **Inventario Permanente**, etc.). Modificada por RS 226-2013 y RS 045-2017. | **Pista clave para el legado**: las fichas de almacén (fecha, ingreso, salida, producto, nro. documento) equivalen a un *kardex*/Inventario Permanente. La migración debe producir un registro con trazabilidad. |
| "Normativas de masificación de comprobantes electrónicos" | Hacen obligatoria la emisión electrónica por rubros/umbrales; RS 133-2019 exige **sólo UBL 2.1** desde 01-07-2019. | UBL 2.1 es el único formato permitido. |
| Estándar **UBL 2.1** (OASIS, ISO/IEC 19845:2015) | Esquema XSD `UBL-Invoice-2.1.xsd` (`urn:oasis:names:specification:ubl:schema:xsd:Invoice-2`). | Define la estructura del XML. |

> ⚠ En el enunciado, RS 234-2006 aparece junto a la comprobación electrónica; en realidad es la norma de **libros/registros**. Se usa para el *registro de inventario permanente / ventas*, no para el formato del XML. Esta precisión se debe justificar en la exposición.

## 2. Catálogos SUNAT relevantes (extraídos del Anexo RS 245-2017)

| Cat. | Contenido | Campo UBL | Valores clave |
|---|---|---|---|
| 01 | Tipo de documento | `cbc:InvoiceTypeCode` | 01 Factura · 03 Boleta · 07 N. Crédito · 08 N. Débito · 09 GR remitente · 31 GR transportista |
| 02 | Moneda | `cbc:DocumentCurrencyCode` | ISO 4217 (PEN, USD) |
| 03 | Unidad de medida | `@unitCode` | UN/ECE Rec. 20 (NIU, KGM, CS, BX, …) |
| 05 | Tipos de tributo | `cac:TaxScheme/cbc:ID`, `cbc:Name`, `cbc:TaxTypeCode` | 1000 IGV (VAT) · 2000 ISC (EXC) · 9995 Exportación (FRE) · 9996 Gratuito (FRE) · 9997 Exonerado (VAT) · 9998 Inafecto (FRE) · 9999 Otros (OTH) · 7152 ICBPER (OTH)¹ |
| 06 | Documento de identidad | `cbc:CompanyID/@schemeID` | 0 sin RUC · 1 DNI · 4 C. extranjería · 6 RUC · 7 Pasaporte · A, B, C, D |
| 07 | Afectación IGV | `cbc:TaxExemptionReasonCode` | 10–17 Gravado · 20–21 Exonerado · 30–36 Inafecto · 40 Exportación |
| **08** | **Sistema de cálculo del ISC** | **`cbc:TierRange`** | **01 Sistema al valor · 02 Monto fijo · 03 Precio de venta al público** (Apéndice IV, lit. A/B/C del TUO IGV e ISC) |
| 09 | Tipo de nota de crédito | `cbc:ResponseCode` | 01 Anulación · 02 Error RUC · 03 Error descripción · 04 Dscto global · 05 Dscto ítem · 06 Devol. total · 07 Devol. ítem · 08 Bonificación · 09 Disminución valor · 10 Otros |
| 10 | Tipo de nota de débito | `cbc:ResponseCode` | 01 Intereses mora · 02 Aumento valor · 03 Penalidades |
| 13 | UBIGEO | `cbc:ID` (dirección) | Catálogo INEI |
| 16 | Tipo de precio unitario | `cbc:PriceTypeCode` | 01 Precio unitario (incl. IGV) · 02 Valor referencial (no onerosa) |
| 17 / 51 | Tipo de operación / de factura | `cbc:ProfileID` | 0101 Venta interna · 0102 Exportación · 0103 No domiciliados · 0104 Anticipos … |
| 52 | Leyendas | `cbc:Note/@languageLocaleID` | 1000 monto en letras · 1002 transferencia gratuita · 2001 Amazonía bienes · 2006 detracción … |
| 53 | Cargos/descuentos | `cbc:AllowanceChargeReasonCode` | (ver anexo vigente) |

¹ **7152 ICBPER** (impuesto al consumo de bolsas de plástico) se añadió después del anexo 2017; confirmar en el anexo vigente. El enunciado lo menciona (“IGV, ISC, ICBPER, etc.”).

### Por qué el Catálogo 8 es el “punto clave”
El **ISC** no se calcula igual para todos los productos. El catálogo 8 indica **cómo**:
- **01 · Al valor**: ISC = base × tasa %.
- **02 · Monto fijo**: ISC = cantidad (en la unidad que fija la norma) × monto fijo por unidad.
- **03 · Precio de venta al público (PVP)**: la base se deriva del PVP sugerido. ⚠ VERIFICAR la fórmula exacta (Apéndice IV, lit. C, TUO IGV/ISC) antes de implementar; se modela como *estrategia* intercambiable (RN-040).

Además el ISC **forma parte de la base imponible del IGV** (RN-041). Para abarrotes y mercadería de ABC, ISC aplica a bebidas alcohólicas, cigarrillos, gaseosas azucaradas, combustibles, etc. según Apéndices III–V.

## 3. Tipos de comprobante y reglas de numeración (RN)

| Regla | Detalle | Fuente |
|---|---|---|
| RN-001 | Serie Factura = `F` + 3 alfanum. (`F001`); Boleta = `B` + 3 alfanum. (`B001`). | Guía XML (“F###-NNNNNNNN”) |
| RN-002 | Correlativo: entero 1–99 999 999, **consecutivo por (RUC, tipo, serie)**. | Guía XML |
| RN-003 | Nombre de archivo: `RUC-TT-SERIE-CORRELATIVO.xml` (TT = cat. 01); se envía comprimido `.zip` del mismo nombre. | RS 097-2012 + guía de servicios web ⚠ VERIFICAR versión vigente |
| RN-004 | Notas (07/08) deben referenciar el documento modificado (`cac:BillingReference`) y llevar motivo (cat. 09/10). | Guía XML NC/ND |
| RN-005 | Factura exige adquirente con **RUC**; boleta puede ir sin identificar cuando el total no supere el umbral (S/ 700, parámetro). | Normativa de comprobantes de pago ⚠ VERIFICAR umbral vigente |
| RN-006 | Boletas se informan vía **Resumen Diario** (RC-AAAAMMDD-n) salvo que la norma vigente permita envío directo. | RS 097-2012 / RS 114-2019 ⚠ VERIFICAR |
| RN-007 | Anulaciones de facturas vía **Comunicación de Baja** (RA-AAAAMMDD-n). | SUNAT (nombres RA/RC verificados en anexos) |

## 4. Resultado del envío (CDR)

SUNAT/OSE responde con una **Constancia de Recepción (CDR)** = ZIP con `R-<archivo>.xml` (`ApplicationResponse`).
- `ResponseCode = 0` → **Aceptado** (puede traer observaciones 4xxx).
- Errores `0100–0999` → excepción técnica/credenciales (se reintenta); `2000–3999` → **rechazo** (se corrige y se reemite con **nuevo** correlativo si ya se consumió).
- Estados internos del sistema: `BORRADOR → FIRMADO → ENVIADO → ACEPTADO | ACEPTADO_CON_OBS | RECHAZADO | ANULADO`.

## 5. Impuestos y cálculo (referencia para el dominio)

| Impuesto | Código cat. 05 | Tasa/Monto | Base | Se suma al total |
|---|---|---|---|---|
| IGV | 1000 | 18 % (16 % IGV + 2 % IPM) ⚠ parámetro | valor de venta + ISC | Sí |
| ISC | 2000 | según cat. 08 | según cat. 08 | Sí |
| ICBPER | 7152 | S/ por bolsa (parámetro, S/ 0.50 desde 2023 ⚠ VERIFICAR) | nº de bolsas | Sí; **no** integra base de IGV |
| Operaciones gratuitas | 9996 | valor referencial | — | No suma al pagable |
| Exportación / Exonerado / Inafecto | 9995 / 9997 / 9998 | 0 % | — | — |

**Nota regional (UNAS – Selva):** las operaciones en la Amazonía pueden tener beneficio (leyendas 2001–2003, afectación exonerada). Se deja como *configuración del emisor* (`regimenAmazonia`), fuera del alcance de la fase 1.
