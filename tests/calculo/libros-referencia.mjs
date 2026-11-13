// Oráculo de la feature 0008: convierte la fila del DTO a la línea PLE y la compara con la línea escrita a mano
// (`examples/*.ple.txt`). Comprueba el orden de las columnas, el número de campos y el formato de fechas e importes.
//   14.1 Registro de Ventas (RS 361-2015, campos 1–34) · 12.1 Inventario Permanente en Unidades Físicas (RS 042-2018, campos 1–19)
// Los importes son cadenas decimales (ADR-04): no hay aritmética de coma flotante.
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ej = path.join(raiz, "specs", "contracts", "examples");
const sch = path.join(raiz, "specs", "contracts", "schemas");
const leer = f => JSON.parse(readFileSync(f, "utf8"));
const fecha = iso => (iso ? iso.split("-").reverse().join("/") : "");          // AAAA-MM-DD → DD/MM/AAAA

// Orden oficial de las columnas. «icbper» no tiene columna propia en la estructura de 2015: se suma al campo 23 (⚠).
const COLUMNAS_14_1 = [
  "periodo", "cuo", "correlativoAsiento", ["fechaEmision", fecha], ["fechaVencimiento", fecha], "tipoComprobante", "serie", "numero",
  "numeroFinal", "tipoDocIdentidadCliente", "numeroDocIdentidadCliente", "razonSocialCliente", "valorFacturadoExportacion",
  "baseImponibleGravada", "descuentoBaseImponible", "igvIpm", "descuentoIgvIpm", "importeExonerada", "importeInafecta", "isc",
  "baseImponibleArrozPilado", "impuestoArrozPilado", "campo23", "importeTotal", "moneda", "tipoCambio",
  ["fechaEmisionModificado", fecha], "tipoComprobanteModificado", "serieModificado", "numeroModificado", "contratoProyecto",
  "errorTipo1", "indicadorMedioPago", "estado",
];
const COLUMNAS_12_1 = [
  "periodo", "cuo", "correlativoAsiento", "codigoEstablecimiento", "codigoCatalogoPropio", "tipoExistencia", "codigoPropioExistencia",
  "codigoCatalogoUtilizado", "codigoExistenciaCatalogo", ["fechaDocumento", fecha], "tipoDocumento", "serieDocumento", "numeroDocumento",
  "tipoOperacion", "descripcionExistencia", "unidadMedida", "entradas", "salidas", "estado",
];

const centavos = s => BigInt((s ?? "0.00").replace(".", ""));
const aTexto = c => `${c < 0n ? "-" : ""}${(c < 0n ? -c : c) / 100n}.${String((c < 0n ? -c : c) % 100n).padStart(2, "0")}`;

export function lineaPle(fila, columnas) {
  const f = { ...fila };
  if ("icbper" in f || "otrosConceptos" in f) {                                  // campo 23 = otros conceptos + ICBPER
    const suma = centavos(f.otrosConceptos) + centavos(f.icbper);
    f.campo23 = f.otrosConceptos === undefined && f.icbper === undefined ? "" : aTexto(suma);
  }
  const campos = columnas.map(c => Array.isArray(c) ? c[1](f[c[0]]) : (f[c] ?? ""));
  campos.forEach((x, i) => { if (String(x).includes("|")) throw new Error(`el campo ${i + 1} contiene «|»`); });
  return campos.join("|") + "|";
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ajv = new Ajv2020({ strict: false, allErrors: true }); addFormats(ajv);
  for (const f of readdirSync(sch).filter(f => f.endsWith(".schema.json"))) ajv.addSchema(leer(path.join(sch, f)));
  const casos = [
    ["registro-ventas-fila-valida", "libros.schema.json#/$defs/RegistroVentasFila", COLUMNAS_14_1, 34],
    ["inventario-fisico-fila-valida", "libros.schema.json#/$defs/RegistroInventarioFisicoFila", COLUMNAS_12_1, 19],
  ];
  let fallos = 0;
  for (const [nombre, ref, columnas, nCampos] of casos) {
    const fila = leer(path.join(ej, `${nombre}.json`));
    const esperada = readFileSync(path.join(ej, `${nombre}.ple.txt`), "utf8").replace(/\n$/, "");
    const validar = ajv.getSchema(`https://abc-software.example/schemas/${ref}`);
    const errores = [];
    if (!validar(fila)) errores.push("la fila no valida contra el esquema: " + ajv.errorsText(validar.errors));
    const obtenida = lineaPle(fila, columnas);
    if (obtenida !== esperada) errores.push(`línea distinta:\n     obtenida: ${obtenida}\n     esperada: ${esperada}`);
    const campos = obtenida.split("|");
    if (campos.length - 1 !== nCampos) errores.push(`se esperaban ${nCampos} campos y hay ${campos.length - 1}`);
    if (!obtenida.endsWith("|")) errores.push("la línea debe terminar con «|»");
    if (errores.length) fallos++;
    console.log(`${errores.length ? "FAIL" : "OK  "} ${nombre} · ${nCampos} campos${errores.length ? "\n   " + errores.join("\n   ") : ""}`);
  }
  console.log(`casos=${casos.length}  fallos=${fallos}`);
  process.exit(fallos ? 1 : 0);
}
