// Valida (1) que todos los JSON Schema compilan, (2) que los ejemplos válidos pasan y los INVALIDO-* fallan,
// (3) las respuestas sintéticas de SUNAT/OSE de `examples/respuestas-sunat/` (T-0002-04).
// Además implementa RN-010 (RUC módulo 11) como referencia ejecutable de las reglas que JSON Schema no expresa.
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const base = path.join(raiz, "specs", "contracts", "schemas");
const ejemplos = path.join(raiz, "specs", "contracts", "examples");
const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);
for (const f of readdirSync(base).filter(f => f.endsWith(".schema.json"))) {
  ajv.addSchema(JSON.parse(readFileSync(path.join(base, f), "utf8")));
}
const esquema = ref => ajv.getSchema(`https://abc-software.example/schemas/${ref}`);
// El esquema de cada ejemplo sale del prefijo de su nombre (sin `INVALIDO-`); el resto son comprobantes.
const esquemaPorPrefijo = {
  "resumen-diario": "operaciones.schema.json#/$defs/ResumenDiarioRequest",
  "comunicacion-baja": "operaciones.schema.json#/$defs/ComunicacionBajaRequest",
  "movimiento": "almacen-migracion.schema.json#/$defs/MovimientoInventario",
};
const esquemaDe = f => Object.entries(esquemaPorPrefijo).find(([p]) => f.replace(/^INVALIDO-/, "").startsWith(p))?.[1]
  ?? "comprobante.schema.json#/$defs/ComprobanteEmitirRequest";
let fallos = 0;

for (const f of readdirSync(ejemplos).filter(f => f.endsWith(".json") && !f.includes(".totales-esperados"))) {
  const data = JSON.parse(readFileSync(path.join(ejemplos, f), "utf8"));
  const ref = esquemaDe(f), validate = esquema(ref);
  const ok = validate(data);
  const esperado = !f.startsWith("INVALIDO-");
  const pasa = ok === esperado;
  if (!pasa) fallos++;
  console.log(`${pasa ? "OK  " : "FAIL"} ${f}  (valido=${ok}, esperado=${esperado}) · ${ref.split("/").pop()}`);
  if (!ok && esperado) console.log(JSON.stringify(validate.errors, null, 2));
}

// Respuestas del envío (mock de IEnvioComprobantePort): resultado-* = CDR → ResultadoSunat; problema-* = caída → Problema.
// Son sintéticas: llevan `_nota` y sus códigos sólo como rango de docs/01 §4 ("0", "2xxx"/"3xxx", observaciones "4xxx").
const respuestas = path.join(ejemplos, "respuestas-sunat");
const esquemaRespuesta = { "resultado-": "comprobante.schema.json#/$defs/ResultadoSunat", "problema-": "operaciones.schema.json#/$defs/Problema" };
for (const f of readdirSync(respuestas).filter(f => f.endsWith(".json"))) {
  const data = JSON.parse(readFileSync(path.join(respuestas, f), "utf8"));
  const prefijo = Object.keys(esquemaRespuesta).find(p => f.startsWith(p));
  const v = prefijo && esquema(esquemaRespuesta[prefijo]);
  const errores = [
    !v && "nombre sin prefijo resultado-/problema-",
    v && !v(data) && ajv.errorsText(v.errors),
    data._nota !== "ejemplo sintético, no oficial" && "falta _nota",
    !(data.codigoRespuesta === undefined || /^(0|[23]xxx)$/.test(data.codigoRespuesta)) && `codigoRespuesta concreto (${data.codigoRespuesta}): usar rango`,
    !(data.observaciones ?? []).every(o => /^4xxx\b/.test(o)) && "observación sin rango 4xxx",
  ].filter(Boolean);
  if (errores.length) fallos++;
  console.log(`${errores.length ? "FAIL" : "OK  "} respuestas-sunat/${f}  (${errores.length ? errores.join(" · ") : esquemaRespuesta[prefijo].split("/").pop()})`);
}

// RN-010 · RUC módulo 11
export function rucValido(ruc) {
  if (!/^(10|15|16|17|20)\d{9}$/.test(ruc)) return false;
  const w = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
  const s = w.reduce((a, p, i) => a + p * Number(ruc[i]), 0);
  let d = 11 - (s % 11); if (d === 10) d = 0; if (d === 11) d = 1;
  return d === Number(ruc[10]);
}
const casosRuc = [["20123456786", true], ["20100047218", true], ["20100113612", false], ["20123456787", false], ["12345678901", false]]; // 20100113612 = RUC del ejemplo de la guía SUNAT: NO pasa módulo 11 (es ficticio)
for (const [r, esp] of casosRuc) {
  const ok = rucValido(r) === esp; if (!ok) fallos++;
  console.log(`${ok ? "OK  " : "FAIL"} RUC ${r} esperado=${esp}`);
}
process.exit(fallos ? 1 : 0);
