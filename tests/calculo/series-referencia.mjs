// Oráculo de la regla RN-082/RN-083 (series exclusivas por dispositivo) y de su efecto en la numeración (RN-002, RN-051).
// Cada dispositivo (caja MSI/APK) tiene su propia base SQLite y emite sin conexión: si dos cajas compartieran F001 se
// duplicarían correlativos. JSON Schema no puede expresar «una serie pertenece a un solo dispositivo»; por eso hay un oráculo.
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const dir = path.join(raiz, "specs", "contracts", "examples", "series");
const sch = path.join(raiz, "specs", "contracts", "schemas");
const leer = f => JSON.parse(readFileSync(f, "utf8"));
const error = codigo => Object.assign(new Error(codigo), { codigo });

export function crearEmisor(dispositivos) {
  const duenoDe = new Map(), correlativos = new Map();   // (tipo|serie) → dispositivoId ; (dispositivo|tipo|serie) → último correlativo
  for (const d of dispositivos) for (const s of d.series) {
    const k = `${s.tipoDocumento}|${s.serie}`;
    if (duenoDe.has(k) && duenoDe.get(k) !== d.dispositivoId) throw error("SERIE_DUPLICADA");   // RN-083
    duenoDe.set(k, d.dispositivoId);
    correlativos.set(`${d.dispositivoId}|${k}`, s.correlativoInicial ?? 0);
  }
  return {
    emitir({ dispositivoId, tipoDocumento, serie }) {
      const k = `${tipoDocumento}|${serie}`;
      if (duenoDe.get(k) !== dispositivoId) throw error("SERIE_NO_ASIGNADA");                  // RN-082
      const n = correlativos.get(`${dispositivoId}|${k}`) + 1;                                  // RN-002: consecutivo por (dispositivo, serie)
      correlativos.set(`${dispositivoId}|${k}`, n);
      return `${serie}-${String(n).padStart(8, "0")}`;
    },
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ajv = new Ajv2020({ strict: false, allErrors: true }); addFormats(ajv);
  for (const f of readdirSync(sch).filter(f => f.endsWith(".schema.json"))) ajv.addSchema(leer(path.join(sch, f)));
  const vDisp = ajv.getSchema("https://abc-software.example/schemas/maestros.schema.json#/$defs/DispositivoRequest");
  let fallos = 0, casos = 0;
  for (const f of readdirSync(dir).filter(f => f.endsWith(".json"))) {
    const e = leer(path.join(dir, f)); casos++;
    const errores = e.dispositivos.flatMap(d => vDisp(d) ? [] : [`${d.dispositivoId}: ${ajv.errorsText(vDisp.errors)}`]);
    let emisor = null;
    try { emisor = crearEmisor(e.dispositivos); if (e.esperadoErrorAlRegistrar) errores.push("debió rechazar el registro"); }
    catch (x) { if (x.codigo !== e.esperadoErrorAlRegistrar) errores.push(`registro: ${x.codigo ?? x.message}`); }
    for (const [i, m] of (emisor ? e.emisiones ?? [] : []).entries()) {
      try { const r = emisor.emitir(m); if (r !== m.esperado) errores.push(`#${i + 1}: obtuvo ${r}, esperado ${m.esperado ?? m.esperadoError}`); }
      catch (x) { if (x.codigo !== m.esperadoError) errores.push(`#${i + 1}: ${x.codigo ?? x.message}, esperado ${m.esperadoError ?? m.esperado}`); }
    }
    if (errores.length) fallos++;
    console.log(`${errores.length ? "FAIL" : "OK  "} series/${f}${errores.length ? "  " + errores.join(" · ") : ""}`);
  }
  console.log(`escenarios=${casos}  fallos=${fallos}`);
  process.exit(fallos ? 1 : 0);
}
