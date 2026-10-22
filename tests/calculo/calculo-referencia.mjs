// Prueba de la ESPECIFICACIÓN de cálculo (RN-020…RN-045): calcula con fórmulas independientes y compara con cada
// caso dorado `examples/*.totales-esperados.json` (entrada = mismo nombre sin `.totales-esperados`).
// No es el código de producción: es el oráculo que éste deberá igualar.
// Parámetros de ejemplo (⚠ en producción vienen de ParametroTributario, ADR-05): IGV 18 %, ICBPER S/ 0.50 por bolsa.
// Aritmética decimal exacta con BigInt (ADR-04): con float, el half-up de RN-021 falla en ~18 % de los bordes x.xx5
// (p. ej. IGV de 13.25 = 2.385 → daba 2.38 en vez de 2.39; lo fijan boleta-inafecta y factura-descuento-global).
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ej = path.join(raiz, "specs", "contracts", "examples");
const sch = path.join(raiz, "specs", "contracts", "schemas");
const leer = f => JSON.parse(readFileSync(f, "utf8"));

// Decimal exacto { v: BigInt, s: escala } = v / 10^s. Los números JSON llegan con ≤ 10 decimales (n(12,10), RN-024).
const dec = x => { const [e, f = ""] = (typeof x === "number" ? x.toFixed(10) : x).split("."); return { v: BigInt(e + f), s: f.length }; };
const pct = x => { const d = dec(x); return { v: d.v, s: d.s + 2 }; };                  // tasa en % → fracción
const esc = (a, s) => a.v * 10n ** BigInt(s - a.s);
const suma = (a, b) => { const s = Math.max(a.s, b.s); return { v: esc(a, s) + esc(b, s), s }; };
const resta = (a, b) => suma(a, { v: -b.v, s: b.s });
const mul = (a, b) => ({ v: a.v * b.v, s: a.s + b.s });
const r2 = a => { if (a.s <= 2) return { v: esc(a, 2), s: 2 };                           // half-up por línea (RN-021)
  const d = 10n ** BigInt(a.s - 2), sg = a.v < 0n ? -1n : 1n; return { v: sg * ((sg * a.v * 2n + d) / (2n * d)), s: 2 }; };
const num = a => Number(r2(a).v) / 100;
const CERO = dec(0);

const P = { igv: dec("0.18"), icbper: dec("0.50") };
const GRAV = ["10","11","12","13","14","15","16","17"], EXON = ["20","21"], INAF = ["30","31","32","33","34","35","36"], GRATIS = ["11","12","13","14","15","16","21","31","32","33","34","35","36"];
const SUMAN = ["gravadas", "exoneradas", "inafectas", "exportacion", "igv", "isc", "icbper", "otrosCargos"]; // RN-022

export function calcular(req) {
  const t = Object.fromEntries([...SUMAN, "gratuitas", "descuentosGlobales", "anticipos"].map(k => [k, CERO]));
  for (const it of req.items) {
    const cant = dec(it.cantidad);
    const valor = r2(resta(mul(cant, dec(it.valorUnitario)), dec(it.descuento ?? 0)));    // RN-021
    let isc = CERO;
    if (it.sistemaIsc === "01") isc = r2(mul(valor, pct(it.tasaIsc)));                   // RN-040 al valor
    if (it.sistemaIsc === "02") isc = r2(mul(cant, dec(it.montoFijoIsc)));               // RN-040 monto fijo
    if (it.sistemaIsc === "03") throw new Error("ISC sistema 03 (PVP): ⚠ fórmula pendiente de verificar (RN-040)");
    const baseIgv = suma(valor, isc);                                                     // RN-041
    if (GRATIS.includes(it.afectacionIgv)) { t.gratuitas = suma(t.gratuitas, valor); continue; } // RN-031: no suma al total
    if (GRAV.includes(it.afectacionIgv)) { t.gravadas = suma(t.gravadas, valor); t.igv = suma(t.igv, r2(mul(baseIgv, P.igv))); } // RN-020
    else if (EXON.includes(it.afectacionIgv)) t.exoneradas = suma(t.exoneradas, valor);
    else if (INAF.includes(it.afectacionIgv)) t.inafectas = suma(t.inafectas, valor);
    else if (it.afectacionIgv === "40") t.exportacion = suma(t.exportacion, valor);
    t.isc = suma(t.isc, isc);
    if (it.bolsasIcbper) t.icbper = suma(t.icbper, r2(mul(dec(it.bolsasIcbper), P.icbper))); // RN-042
  }
  t.descuentosGlobales = (req.descuentosGlobales ?? []).reduce((a, d) => suma(a, dec(d.monto)), CERO);
  t.anticipos = (req.anticipos ?? []).reduce((a, d) => suma(a, dec(d.monto)), CERO);
  t.importeTotal = resta(resta(SUMAN.reduce((a, k) => suma(a, t[k]), CERO), t.descuentosGlobales), t.anticipos); // RN-022
  return Object.fromEntries(Object.entries(t).map(([k, v]) => [k, num(v)]));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ajv = new Ajv2020({ strict: false, allErrors: true }); addFormats(ajv);
  for (const f of readdirSync(sch).filter(f => f.endsWith(".schema.json"))) ajv.addSchema(leer(path.join(sch, f)));
  const validaTotales = ajv.getSchema("https://abc-software.example/schemas/comprobante.schema.json#/$defs/Totales");
  let fallos = 0;
  const casos = readdirSync(ej).filter(f => f.endsWith(".totales-esperados.json")).map(f => [f.replace(".totales-esperados", ""), f]);
  for (const [entrada, esperado] of casos) {
    const obtenido = calcular(leer(path.join(ej, entrada))), esp = leer(path.join(ej, esperado));
    if (!validaTotales(esp)) { fallos++; console.log(`FAIL esquema Totales de ${esperado}`, validaTotales.errors); }
    const cuadre = num(resta(resta(SUMAN.reduce((a, k) => suma(a, dec(esp[k])), CERO), dec(esp.descuentosGlobales)), dec(esp.anticipos)));
    if (cuadre !== esp.importeTotal) { fallos++; console.log(`FAIL ${esperado}: importeTotal=${esp.importeTotal} no cuadra con RN-022 (${cuadre})`); }
    const difs = Object.keys(esp).filter(k => Math.abs(obtenido[k] - esp[k]) >= 0.005);
    fallos += difs.length;
    console.log(`${difs.length ? "FAIL" : "OK  "} ${entrada} · ${Object.keys(esp).length - difs.length}/${Object.keys(esp).length} totales · importeTotal=${obtenido.importeTotal}`);
    for (const k of difs) console.log(`     ${k}: calculado=${obtenido[k]} esperado=${esp[k]}`);
  }
  // Flujo A2 de la spec 0001: el ISC por PVP (cat. 08 = 03) NO se calcula hasta cerrar su ⚠ VERIFICAR (T-0001-05).
  try { const t = calcular({ items: [{ cantidad: 1, valorUnitario: 10, afectacionIgv: "10", sistemaIsc: "03", tasaIsc: 30 }] });
        fallos++; console.log(`FAIL ISC sistema 03 calculó isc=${t.isc}: la fórmula aún no está verificada`); }
  catch (e) { const ok = /fórmula pendiente/.test(e.message); if (!ok) fallos++; console.log(`${ok ? "OK  " : "FAIL"} ISC sistema 03 → ${e.message}`); }
  console.log(`casos=${casos.length}  fallos=${fallos}`);
  process.exit(fallos ? 1 : 0);
}
