// Prueba de la ESPECIFICACIÓN del kardex (feature 0005): valida cada movimiento de `examples/kardex/*.json` contra
// `MovimientoInventario` y recalcula el saldo acumulado tras cada paso (RN-063):
// saldo = Σ INGRESO + Σ AJUSTE AUMENTO − Σ SALIDA − Σ AJUSTE DISMINUCION. No es el código de producción: es el oráculo.
// Cantidades n(12,10) (RN-024) como enteros de 10⁻¹⁰ con BigInt: sin float (ADR-04).
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const dir = path.join(raiz, "specs", "contracts", "examples", "kardex");
const sch = path.join(raiz, "specs", "contracts", "schemas");
const leer = f => JSON.parse(readFileSync(f, "utf8"));
const u = x => BigInt(x.toFixed(10).replace(".", ""));                      // cantidad → unidades de 10⁻¹⁰
const txt = v => String(Number(v) / 1e10);

const SIGNO = { INGRESO: 1n, SALIDA: -1n, AUMENTO: 1n, DISMINUCION: -1n };
const signo = m => SIGNO[m.tipo === "AJUSTE" ? m.sentido : m.tipo];         // RN-063

const ajv = new Ajv2020({ strict: false, allErrors: true }); addFormats(ajv);
for (const f of readdirSync(sch).filter(f => f.endsWith(".schema.json"))) ajv.addSchema(leer(path.join(sch, f)));
const validaMov = ajv.getSchema("https://abc-software.example/schemas/almacen-migracion.schema.json#/$defs/MovimientoInventario");
let fallos = 0, pasos = 0;
const casos = readdirSync(dir).filter(f => f.endsWith(".json"));
for (const f of casos) {
  const caso = leer(path.join(dir, f));
  let saldo = u(caso.saldoInicial ?? 0), fechaPrevia = "";
  for (const [i, { movimiento: m, saldoEsperado }] of caso.pasos.entries()) {
    const errores = [];
    if (!validaMov(m)) errores.push(ajv.errorsText(validaMov.errors));
    if (m.productoId !== caso.productoId) errores.push("productoId distinto del caso");
    if (m.fecha < fechaPrevia) errores.push(`fecha ${m.fecha} anterior a ${fechaPrevia}`);
    const s = signo(m);
    if (s === undefined || typeof m.cantidad !== "number") errores.push("no se sabe cuánto suma o resta (tipo/sentido/cantidad)");
    else saldo += s * u(m.cantidad);
    if (saldo < 0n) errores.push("saldo negativo (RF-0005-06)");
    if (saldo !== u(saldoEsperado)) errores.push(`esperado=${saldoEsperado}`);
    fechaPrevia = m.fecha; pasos++;
    if (errores.length) fallos++;
    console.log(`${errores.length ? "FAIL" : "OK  "} ${f} · ${i + 1}. ${m.fecha} ${m.tipo}${m.sentido ? " " + m.sentido : ""} ${m.cantidad} → saldo ${txt(saldo)}`
      + (errores.length ? `  (${errores.join(" · ")})` : ""));
  }
}
console.log(`casos=${casos.length}  pasos=${pasos}  fallos=${fallos}`);
process.exit(fallos ? 1 : 0);
