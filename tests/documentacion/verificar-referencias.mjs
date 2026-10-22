// Verifica la coherencia de la documentación: (1) enlaces relativos existentes; (2) toda referencia a RN, EP, PT, CU, ADR y T-NNNN-nn
// apunta a algo definido. Uso: npm run docs
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ignorar = new Set(["node_modules", ".git"]);
function listar(dir, ext, out = []) {
  for (const n of readdirSync(dir)) {
    if (ignorar.has(n)) continue;
    const p = path.join(dir, n);
    statSync(p).isDirectory() ? listar(p, ext, out) : ext.some(e => n.endsWith(e)) && out.push(p);
  }
  return out;
}
const rel = p => path.relative(raiz, p).replace(/\\/g, "/");
const mds = listar(raiz, [".md"]);
const leer = p => readFileSync(p, "utf8");
let errores = 0;
const err = (m) => { errores++; console.log("✗", m); };

// 1) Enlaces relativos
for (const f of mds) {
  const t = leer(f).replace(/```[\s\S]*?```/g, "");
  for (const m of t.matchAll(/\]\(([^)\s]+)\)/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|#)/.test(href)) continue;
    const destino = path.resolve(path.dirname(f), decodeURIComponent(href.split("#")[0]));
    if (!existsSync(destino)) err(`${rel(f)}: enlace roto → ${href}`);
  }
}

// 2) Definiciones
const todo = mds.map(f => ({ f, t: leer(f) }));
const yaml = leer(path.join(raiz, "specs/contracts/abc-facturacion-api.yaml"));
const docs = n => leer(path.join(raiz, "docs", n));
const defRN = new Set([...(docs("01-contexto-normativo.md") + docs("03-modelo-dominio.md")).matchAll(/^\|\s*(RN-\d{3})\s*\|/gm)].map(m => m[1]));
const defEP = new Set(yaml.match(/EP-\d{2}/g));
const defPT = new Set([...docs("04-arquitectura.md").matchAll(/^\|\s*(PT-\d{2})\s*\|/gm)].map(m => m[1]));
const defCU = new Set([...docs("02-casos-de-uso.md").matchAll(/^\|\s*\**(CU-\d{2})\**\s*\|/gm)].map(m => m[1]));
const defADR = new Set(readdirSync(path.join(raiz, "specs/adr")).map(n => n.match(/^(ADR-\d{2})/)?.[1]).filter(Boolean));
const defT = new Set();
for (const { f, t } of todo) if (f.endsWith("tasks.md") && rel(f).startsWith("specs/features/")) for (const m of t.matchAll(/^\|\s*(T-\d{4}-\d{2})\s/gm)) defT.add(m[1]);

const excluidos = ["specs/templates/", "docs/07-matriz-trazabilidad.md"]; // plantillas y tabla generada (ya verificada por verificar-matriz)
const rangos = /(RN|CU|T-\d{4})-(\d{2,3})\s*…\s*(?:RN-|CU-|T-\d{4}-)?(\d{2,3})/g; // "RN-020…RN-024": se comprueban extremos
function expandir(t) { // en un rango "RN-020…RN-042" sólo se comprueban los extremos (puede haber huecos legítimos)
  return t.replace(rangos, (m, pre, a, b) => `${pre}-${a} ${pre}-${b}`);
}
for (const { f, t } of todo) {
  if (excluidos.some(e => rel(f).startsWith(e))) continue;
  const txt = expandir(t);
  const chequea = (re, def, nombre) => { for (const id of new Set(txt.match(re) ?? [])) if (!def.has(id)) err(`${rel(f)}: ${nombre} no definido → ${id}`); };
  chequea(/\bRN-\d{3}\b/g, defRN, "RN");
  chequea(/\bEP-\d{2}\b/g, defEP, "EP");
  chequea(/\bPT-\d{2}\b/g, defPT, "PT");
  chequea(/\bCU-\d{2}\b/g, defCU, "CU");
  chequea(/\bADR-\d{2}\b/g, defADR, "ADR");
  chequea(/\bT-\d{4}-\d{2}\b/g, defT, "tarea");
}
console.log(`md=${mds.length}  RN=${defRN.size}  EP=${defEP.size}  PT=${defPT.size}  CU=${defCU.size}  ADR=${defADR.size}  tareas=${defT.size}  errores=${errores}`);
process.exit(errores ? 1 : 0);
