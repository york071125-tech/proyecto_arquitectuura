// Fuente única de la matriz de trazabilidad. Genera docs/07-matriz-trazabilidad.csv y reescribe la tabla de docs/07-matriz-trazabilidad.md (entre marcadores).
// Uso: npm run matriz
// fuente: G-FAC = Guía XML Factura UBL 2.1 (SUNAT, estudiada); ANEXO = Anexo catálogos RS 245-2017 (estudiado);
//         NO-EST = conocimiento general NO contrastado en esta sesión → verificar antes de implementar.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const I = "/Invoice";
const SUP = `${I}/cac:AccountingSupplierParty/cac:Party`;
const CUS = `${I}/cac:AccountingCustomerParty/cac:Party`;
const L = `${I}/cac:InvoiceLine`;
const LT = `${L}/cac:TaxTotal/cac:TaxSubtotal`;

// [grupo, dato SUNAT, xpath UBL, card., formato, catálogo, oblig., dominio, DTO, reglas, estado, fuente]
export const filas = [
  // ── Cabecera
  ["Cabecera", "Firma digital", `${I}/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature`, "0..1", "XMLDSig", "", "M", "Comprobante.xmlFirmado", "(generado: PT-12)", "RN-053", "Cubierto", "G-FAC"],
  ["Cabecera", "Versión del UBL", `${I}/cbc:UBLVersionID`, "0..1", '"2.1"', "", "M", "constante", "(generado)", "RS 133-2019", "Cubierto", "G-FAC"],
  ["Cabecera", "Versión estructura del documento", `${I}/cbc:CustomizationID`, "0..1", '"2.0"', "", "M", "constante", "(generado)", "", "Cubierto", "G-FAC"],
  ["Cabecera", "Tipo de operación", `${I}/cbc:ProfileID`, "1", "an4", "51", "M", "Comprobante.tipoOperacion", "tipoOperacion", "RN-032, RN-033", "Cubierto", "G-FAC"],
  ["Cabecera", "Serie y correlativo", `${I}/cbc:ID`, "1", "F###-NNNNNNNN", "", "M", "Comprobante.serie + correlativo", "serie (+correlativo asignado)", "RN-001, RN-002", "Cubierto", "G-FAC"],
  ["Cabecera", "Fecha de emisión", `${I}/cbc:IssueDate`, "1", "YYYY-MM-DD", "", "M", "Comprobante.fechaEmision", "fechaEmision", "RN-006", "Cubierto", "G-FAC"],
  ["Cabecera", "Hora de emisión", `${I}/cbc:IssueTime`, "0..1", "hh:mm:ss", "", "C", "Comprobante.horaEmision", "horaEmision", "", "Cubierto", "G-FAC"],
  ["Cabecera", "Fecha de vencimiento", `${I}/cbc:DueDate`, "0..1", "YYYY-MM-DD", "", "C", "Comprobante.fechaVencimiento", "fechaVencimiento", "", "Cubierto", "G-FAC"],
  ["Cabecera", "Tipo de documento", `${I}/cbc:InvoiceTypeCode`, "1", "an2", "01", "M", "Comprobante.tipo", "tipoDocumento", "RN-001", "Cubierto", "G-FAC"],
  ["Cabecera", "Leyendas (monto en letras, gratuitas…)", `${I}/cbc:Note/@languageLocaleID`, "0..n", "an..100", "52 (15 en 2017)", "M (1000)", "Comprobante.leyendas[]", "(generado) Leyenda{codigo,texto}", "RN-045, RN-031", "Cubierto", "G-FAC"],
  ["Cabecera", "Moneda", `${I}/cbc:DocumentCurrencyCode`, "1", "an3", "02", "M", "Comprobante.moneda", "moneda", "RN-036", "Cubierto", "G-FAC"],
  ["Cabecera", "Cantidad de ítems", `${I}/cbc:LineCountNumeric`, "0..1", "n3", "", "C", "count(items)", "(calculado)", "", "Calculado", "G-FAC"],
  ["Cabecera", "Orden de compra", `${I}/cac:OrderReference/cbc:ID`, "0..1", "an..20", "", "C", "—", "—", "", "Fuera de alcance fase 1", "G-FAC"],
  ["Cabecera", "Guía de remisión relacionada", `${I}/cac:DespatchDocumentReference/cbc:ID`, "0..n", "an..", "01/12", "C", "—", "—", "", "Fuera de alcance fase 1", "G-FAC"],
  ["Cabecera", "Documento relacionado (anticipos, otros)", `${I}/cac:AdditionalDocumentReference/cbc:ID`, "0..n", "an..30", "12", "C", "—", "—", "", "Fuera de alcance fase 1", "G-FAC"],
  // ── Emisor
  ["Emisor", "Nombre comercial del emisor", `${SUP}/cac:PartyName/cbc:Name`, "1..1", "an..100", "", "M", "Emisor.nombreComercial", "EmisorRequest.nombreComercial", "", "Cubierto", "G-FAC"],
  ["Emisor", "RUC del emisor", `${SUP}/cac:PartyTaxScheme/cbc:CompanyID`, "0..1", "n11", "", "M", "Emisor.ruc", "EmisorRequest.ruc", "RN-010", "Cubierto", "G-FAC"],
  ["Emisor", "Tipo de documento del emisor (=6)", `${SUP}/cac:PartyTaxScheme/cbc:CompanyID/@schemeID`, "0..1", "an1", "06", "M", "constante '6'", "(generado)", "RN-010", "Cubierto", "G-FAC"],
  ["Emisor", "Razón social del emisor", `${SUP}/cac:PartyTaxScheme/cbc:RegistrationName`, "0..1", "an..100", "", "M", "Emisor.razonSocial", "EmisorRequest.razonSocial", "", "Cubierto", "G-FAC"],
  ["Emisor", "Código de domicilio fiscal / local anexo", `${SUP}/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:AddressTypeCode`, "0..1", "n4", "", "M", "Direccion.codigoEstablecimiento", "Direccion.codigoEstablecimiento", "", "Cubierto", "G-FAC"],
  ["Emisor", "UBIGEO del domicilio fiscal", `${SUP}/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID`, "0..1", "n6", "13", "C", "Direccion.ubigeo", "Direccion.ubigeo", "RN-013", "Cubierto", "ANEXO"],
  // ── Adquirente
  ["Adquirente", "Tipo de documento de identidad del cliente", `${CUS}/cac:PartyTaxScheme/cbc:CompanyID/@schemeID`, "0..1", "an1", "06", "M", "Cliente.tipoDocIdentidad", "cliente.tipoDocIdentidad", "RN-012", "Cubierto", "G-FAC"],
  ["Adquirente", "Número de documento del cliente", `${CUS}/cac:PartyTaxScheme/cbc:CompanyID`, "0..1", "n11 / según tipo", "", "M", "Cliente.numeroDoc", "cliente.numeroDocumento", "RN-010, RN-011", "Cubierto", "G-FAC"],
  ["Adquirente", "Nombre o razón social del cliente", `${CUS}/cac:PartyTaxScheme/cbc:RegistrationName`, "0..1", "an..100", "", "M", "Cliente.nombre", "cliente.nombre", "", "Cubierto", "G-FAC"],
  // ── Descuentos / anticipos / pago
  ["Globales", "Indicador cargo/descuento global", `${I}/cac:AllowanceCharge/cbc:ChargeIndicator`, "1", "true/false", "53", "M", "DescuentoGlobal (false)", "descuentosGlobales[]", "RN-034", "Cubierto", "G-FAC"],
  ["Globales", "Motivo del descuento global", `${I}/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode`, "0..1", "an..2", "53", "C", "DescuentoGlobal.codigo", "descuentosGlobales[].codigo", "RN-034", "Cubierto", "G-FAC"],
  ["Globales", "Monto del descuento global", `${I}/cac:AllowanceCharge/cbc:Amount`, "1", "n(12,2)", "", "M", "DescuentoGlobal.monto", "descuentosGlobales[].monto", "RN-022", "Cubierto", "G-FAC"],
  ["Globales", "Base del descuento global", `${I}/cac:AllowanceCharge/cbc:BaseAmount`, "1", "n(12,2)", "", "C", "DescuentoGlobal.base", "descuentosGlobales[].base", "RN-034", "Cubierto", "G-FAC"],
  ["Globales", "Anticipo · serie-número", `${I}/cac:PrepaidPayment/cbc:ID`, "0..1", "F###-NNNNNNNN", "12", "C", "Anticipo.serieNumero", "anticipos[].serieNumero", "RN-033", "Cubierto", "G-FAC"],
  ["Globales", "Anticipo · monto", `${I}/cac:PrepaidPayment/cbc:PaidAmount`, "0..1", "n(15,2)", "", "C", "Anticipo.monto", "anticipos[].monto", "RN-033", "Cubierto", "G-FAC"],
  ["Globales", "Forma de pago al crédito / cuotas", `${I}/cac:PaymentTerms`, "0..n", "—", "", "C", "FormaPago", "formaPago", "", "⚠ Verificar guía vigente", "NO-EST"],
  // ── Totales por tributo
  ["Totales", "Total de tributos del comprobante", `${I}/cac:TaxTotal/cbc:TaxAmount`, "1", "n(12,2)", "", "M", "Totales.igv + isc + icbper", "(calculado) totales", "RN-022", "Calculado", "G-FAC"],
  ["Totales", "Base imponible por tributo", `${I}/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount`, "0..1", "n(12,2)", "", "C", "Totales.gravadas/exoneradas/inafectas…", "(calculado)", "RN-035", "Calculado", "G-FAC"],
  ["Totales", "Monto por tributo", `${I}/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount`, "1", "n(12,2)", "", "M", "Totales.igv / isc / icbper", "(calculado)", "RN-020, RN-040, RN-042", "Calculado", "G-FAC"],
  ["Totales", "Código del tributo", `${I}/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID`, "0..1", "an..3", "05", "M", "TributoLinea.codigo", "(calculado)", "RN-030", "Cubierto", "G-FAC"],
  ["Totales", "Nombre del tributo (IGV, ISC, ICBPER…)", `${I}/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name`, "0..1", "an..6", "05", "M", "derivado de codigo", "(generado)", "", "Cubierto", "G-FAC"],
  ["Totales", "Código internacional del tributo (VAT, EXC…)", `${I}/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode`, "0..1", "an..6", "05", "M", "derivado de codigo", "(generado)", "", "Cubierto", "G-FAC"],
  ["Totales", "Total valor de venta", `${I}/cac:LegalMonetaryTotal/cbc:LineExtensionAmount`, "0..1", "n(12,2)", "", "C", "Σ valorVenta de ítems", "(calculado)", "RN-022", "Calculado", "G-FAC"],
  ["Totales", "Total precio de venta (incluye impuestos)", `${I}/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount`, "0..1", "n(12,2)", "", "C", "Totales", "(calculado)", "RN-022", "Calculado", "G-FAC"],
  ["Totales", "Total descuentos globales", `${I}/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount`, "0..1", "n(12,2)", "", "C", "Totales.descuentosGlobales", "totales.descuentosGlobales", "RN-022", "Calculado", "G-FAC"],
  ["Totales", "Total otros cargos", `${I}/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount`, "0..1", "n(12,2)", "", "C", "Totales.otrosCargos", "totales.otrosCargos", "RN-022", "Calculado", "G-FAC"],
  ["Totales", "Total anticipos", `${I}/cac:LegalMonetaryTotal/cbc:PrepaidAmount`, "0..1", "n(12,2)", "", "C", "Totales.anticipos", "totales.anticipos", "RN-033", "Calculado", "G-FAC"],
  ["Totales", "Importe total a pagar", `${I}/cac:LegalMonetaryTotal/cbc:PayableAmount`, "1", "n(12,2)", "", "M", "Totales.importeTotal", "totales.importeTotal", "RN-022", "Calculado", "G-FAC"],
  // ── Líneas
  ["Ítem", "Número de orden del ítem", `${L}/cbc:ID`, "1", "n..3", "", "M", "ItemComprobante.numero", "(asignado)", "", "Calculado", "G-FAC"],
  ["Ítem", "Cantidad", `${L}/cbc:InvoicedQuantity`, "0..1", "n(12,10)", "", "M", "ItemComprobante.cantidad", "items[].cantidad", "RN-024", "Cubierto", "G-FAC"],
  ["Ítem", "Unidad de medida", `${L}/cbc:InvoicedQuantity/@unitCode`, "0..1", "an..3", "03", "M", "ItemComprobante.unidad", "items[].unidad", "", "Cubierto", "G-FAC"],
  ["Ítem", "Valor de venta del ítem", `${L}/cbc:LineExtensionAmount`, "1", "n(12,2)", "", "M", "ItemComprobante.valorVenta", "ItemResponse.valorVenta", "RN-021", "Calculado", "G-FAC"],
  ["Ítem", "Precio de venta unitario / valor referencial", `${L}/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount`, "1", "n(12,10)", "", "M", "ItemComprobante.precioUnitario", "ItemResponse.precioUnitario", "RN-023", "Calculado", "G-FAC"],
  ["Ítem", "Tipo de precio", `${L}/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode`, "0..1", "an2", "16", "M", "ItemComprobante.tipoPrecio", "items[].tipoPrecio", "RN-031", "Cubierto", "G-FAC"],
  ["Ítem", "Cargo/descuento del ítem", `${L}/cac:AllowanceCharge/cbc:Amount`, "1", "n(12,2)", "53", "C", "ItemComprobante.descuento", "items[].descuento", "RN-034", "Cubierto", "G-FAC"],
  ["Ítem", "Monto de tributos del ítem", `${L}/cac:TaxTotal/cbc:TaxAmount`, "1", "n(12,2)", "", "M", "Σ TributoLinea.monto", "ItemResponse.tributos", "RN-020", "Calculado", "G-FAC"],
  ["Ítem · IGV", "Base de cada tributo del ítem", `${LT}/cbc:TaxableAmount`, "0..1", "n(12,2)", "", "M", "TributoLinea.baseImponible", "TributoLinea.baseImponible", "RN-041", "Calculado", "G-FAC"],
  ["Ítem · IGV", "Monto de cada tributo del ítem", `${LT}/cbc:TaxAmount`, "1", "n(12,2)", "", "M", "TributoLinea.monto", "TributoLinea.monto", "RN-020, RN-040, RN-042", "Calculado", "G-FAC"],
  ["Ítem · IGV", "Tasa del tributo (%)", `${LT}/cac:TaxCategory/cbc:Percent`, "0..1", "n(3,5)", "", "M", "TributoLinea.tasa", "TributoLinea.tasa", "RN-020", "Cubierto", "G-FAC"],
  ["Ítem · IGV", "Afectación al IGV", `${LT}/cac:TaxCategory/cbc:TaxExemptionReasonCode`, "0..1", "an2", "07", "M", "ItemComprobante.afectacionIgv", "items[].afectacionIgv", "RN-030", "Cubierto", "G-FAC"],
  ["Ítem · ISC", "**Sistema de cálculo del ISC**", `${LT}/cac:TaxCategory/cbc:TierRange`, "0..1", "an2", "**08**", "C (si ISC)", "TributoLinea.tierRange / Producto.sistemaIsc", "items[].sistemaIsc · TributoLinea.tierRange", "RN-040, RN-041, RN-043", "Cubierto", "G-FAC"],
  ["Ítem · ISC", "Tasa / monto del ISC", `${LT}/cac:TaxCategory/cbc:Percent`, "0..1", "n(3,5)", "08", "C", "Producto.tasaIsc / montoFijoIsc", "items[].tasaIsc / montoFijoIsc", "RN-040", "Cubierto", "G-FAC"],
  ["Ítem · ICBPER", "Cantidad de bolsas (ICBPER)", `${LT}/cbc:BaseUnitMeasure`, "0..1", "n", "05 (7152)", "C", "ItemComprobante.bolsasIcbper", "items[].bolsasIcbper", "RN-042", "⚠ Verificar guía vigente", "NO-EST"],
  ["Ítem · ICBPER", "Monto unitario del ICBPER", `${LT}/cac:TaxCategory/cbc:PerUnitAmount`, "0..1", "n(12,2)", "05 (7152)", "C", "parámetro tarifaIcbper", "(parámetro)", "RN-042", "⚠ Verificar guía vigente", "NO-EST"],
  ["Ítem", "Código del tributo del ítem", `${LT}/cac:TaxCategory/cac:TaxScheme/cbc:ID`, "0..1", "an..3", "05", "M", "TributoLinea.codigo", "TributoLinea.codigo", "RN-030", "Cubierto", "G-FAC"],
  ["Ítem", "Nombre del tributo del ítem", `${LT}/cac:TaxCategory/cac:TaxScheme/cbc:Name`, "0..1", "an..6", "05", "M", "derivado de codigo", "(generado)", "", "Cubierto", "G-FAC"],
  ["Ítem", "Código internacional del tributo del ítem", `${LT}/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode`, "0..1", "an4", "05", "M", "derivado de codigo", "(generado)", "", "Cubierto", "G-FAC"],
  ["Ítem", "Descripción del ítem", `${L}/cac:Item/cbc:Description`, "0..n", "an..250", "", "M", "ItemComprobante.descripcion", "items[].descripcion", "", "Cubierto", "G-FAC"],
  ["Ítem", "Código de producto del vendedor", `${L}/cac:Item/cac:SellersItemIdentification/cbc:ID`, "0..1", "an..30", "", "C", "Producto.codigoInterno", "items[].codigoInterno", "", "Cubierto", "G-FAC"],
  ["Ítem", "Código de producto SUNAT (UNSPSC)", `${L}/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode`, "1", "n8", "25", "C", "Producto.codigoSunat", "items[].codigoSunat", "", "Cubierto", "G-FAC"],
  ["Ítem", "Valor unitario (sin impuestos)", `${L}/cac:Price/cbc:PriceAmount`, "1", "n(12,10)", "", "M", "ItemComprobante.valorUnitario", "items[].valorUnitario", "RN-024", "Cubierto", "G-FAC"],
  // ── Notas de crédito / débito (raíces distintas)
  ["Nota 07/08", "Documento que se modifica · serie-número", "/CreditNote|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", "1", "F###-N…", "", "M", "DocumentoModificado.serie + correlativo", "documentoModificado.serie/correlativo", "RN-004", "Cubierto", "NO-EST"],
  ["Nota 07/08", "Documento que se modifica · tipo", "/CreditNote|DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode", "1", "an2", "01", "M", "DocumentoModificado.tipoDocumento", "documentoModificado.tipoDocumento", "RN-004", "Cubierto", "NO-EST"],
  ["Nota 07/08", "Motivo (tipo de nota)", "/CreditNote|DebitNote/cac:DiscrepancyResponse/cbc:ResponseCode", "1", "an2", "09 / 10", "M", "DocumentoModificado.motivoCodigo", "documentoModificado.motivoCodigo", "RN-004", "Cubierto", "ANEXO"],
  ["Nota 07/08", "Sustento", "/CreditNote|DebitNote/cac:DiscrepancyResponse/cbc:Description", "1", "an..250", "", "M", "DocumentoModificado.sustento", "documentoModificado.sustento", "RN-004", "Cubierto", "NO-EST"],
  ["Nota 07/08", "Cantidad de la línea (NC / ND)", "/CreditNote/cac:CreditNoteLine/cbc:CreditedQuantity · /DebitNote/cac:DebitNoteLine/cbc:DebitedQuantity", "1", "n(12,10)", "03", "M", "ItemComprobante.cantidad", "items[].cantidad", "", "Cubierto", "NO-EST"],
  // ── Lotes
  ["Resumen diario", "Identificador del resumen (RC-AAAAMMDD-n)", "/SummaryDocuments/cbc:ID", "1", "RC-\\d{8}-\\d{1,5}", "", "M", "ResumenDiario.id", "LoteEnvioResponse.id", "RN-006", "Cubierto", "NO-EST"],
  ["Resumen diario", "Fecha de emisión de los documentos", "/SummaryDocuments/cbc:ReferenceDate", "1", "YYYY-MM-DD", "", "M", "ResumenDiario.fechaReferencia", "ResumenDiarioRequest.fechaReferencia", "RN-006", "Cubierto", "NO-EST"],
  ["Resumen diario", "Estado del ítem (adicionar/modificar/anular)", "/SummaryDocuments/sac:SummaryDocumentsLine/cac:Status/cbc:ConditionCode", "1", "n1", "19", "M", "derivado de Estado", "(generado)", "RN-006", "Cubierto", "ANEXO"],
  ["Baja", "Identificador de la baja (RA-AAAAMMDD-n)", "/VoidedDocuments/cbc:ID", "1", "RA-\\d{8}-\\d{1,5}", "", "M", "ComunicacionBaja.id", "LoteEnvioResponse.id", "RN-007", "Cubierto", "NO-EST"],
  ["Baja", "Serie del documento dado de baja", "/VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentSerialID", "1", "an4", "", "M", "documentos[].serie", "ComunicacionBajaRequest.documentos[].serie", "RN-007", "Cubierto", "NO-EST"],
  ["Baja", "Correlativo del documento dado de baja", "/VoidedDocuments/sac:VoidedDocumentsLine/sac:DocumentNumberID", "1", "n..8", "", "M", "documentos[].correlativo", "ComunicacionBajaRequest.documentos[].correlativo", "RN-007", "Cubierto", "NO-EST"],
  ["Baja", "Motivo de la baja", "/VoidedDocuments/sac:VoidedDocumentsLine/sac:VoidReasonDescription", "1", "an..100", "", "M", "documentos[].motivo", "ComunicacionBajaRequest.documentos[].motivo", "RN-007", "Cubierto", "NO-EST"],
  // ── Respuesta
  ["CDR", "Código de respuesta de SUNAT/OSE", "/ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:ResponseCode", "1", "an..", "", "M", "EnvioSunat.codigoRespuesta", "ResultadoSunat.codigoRespuesta", "§4 de 01-…", "Cubierto", "NO-EST"],
  ["CDR", "Mensaje / descripción de la respuesta", "/ApplicationResponse/cac:DocumentResponse/cac:Response/cbc:Description", "1", "an..", "", "M", "EnvioSunat.mensaje", "ResultadoSunat.descripcion", "", "Cubierto", "NO-EST"],
];

const cols = ["ID", "Grupo", "Dato SUNAT", "XPath UBL 2.1", "Card.", "Formato", "Cat.", "Oblig.", "Dominio", "DTO (specs/contracts/schemas)", "Reglas", "Estado", "Fuente"];
const rows = filas.map((f, i) => [`TR-${String(i + 1).padStart(3, "0")}`, ...f]);

const docs = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "docs");
const csv = [cols, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(";")).join("\n");
writeFileSync(path.join(docs, "07-matriz-trazabilidad.csv"), "﻿" + csv, "utf8");

const md = [
  `| ${cols.join(" | ")} |`,
  `|${cols.map(() => "---").join("|")}|`,
  ...rows.map(r => `| ${r.map(c => String(c).replace(/\|/g, "\\|")).join(" | ")} |`),
].join("\n");
const mdPath = path.join(docs, "07-matriz-trazabilidad.md");
const doc = readFileSync(mdPath, "utf8");
const ini = "<!-- MATRIZ:INICIO", fin = "<!-- MATRIZ:FIN -->";
const a = doc.indexOf(ini), b = doc.indexOf(fin);
if (a < 0 || b < 0) throw new Error("Faltan marcadores MATRIZ:INICIO/FIN en " + mdPath);
const marcaIni = doc.slice(a, doc.indexOf("\n", a) + 1);
writeFileSync(mdPath, doc.slice(0, a) + marcaIni + md + "\n" + doc.slice(b), "utf8");
console.log(`${rows.length} filas`);
