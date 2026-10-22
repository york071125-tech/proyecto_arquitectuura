// Verifica la matriz: (1) toda RN-nnn citada está definida en 01-contexto-normativo.md (RN-001…007) o 03-modelo-dominio.md;
// (2) opcional: con la guía SUNAT convertida a texto (pdftotext), cada fila con fuente G-FAC existe en la guía (elemento hoja).
// Uso: node verificar-matriz.mjs [ruta/guia.txt]
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { filas } from "./generar-matriz.mjs";

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "docs");
const dominio = ["01-contexto-normativo.md", "03-modelo-dominio.md"].map(f => readFileSync(path.join(dir, f), "utf8")).join("\n");
const definidas = new Set([...dominio.matchAll(/\|\s*(RN-\d{3})\s*\|/g)].map(m => m[1]));
let errores = 0;

for (const [i, f] of filas.entries()) {
  const id = `TR-${String(i + 1).padStart(3, "0")}`;
  for (const rn of String(f[9]).match(/RN-\d{3}/g) ?? []) {
    if (!definidas.has(rn)) { console.log(`✗ ${id}: ${rn} no está definida en 01/03`); errores++; }
  }
}

const guiaPath = process.argv[2];
if (guiaPath) {
  const guia = readFileSync(guiaPath, "utf8");
  for (const [i, f] of filas.entries()) {
    if (f[11] !== "G-FAC") continue;
    const id = `TR-${String(i + 1).padStart(3, "0")}`;
    const hoja = f[2].split("/").pop().replace(/@.*/, "").replace(/^.*:/, "");
    const attr = f[2].includes("@") ? f[2].split("@").pop() : null;
    const buscar = attr ?? hoja;
    if (!guia.includes(buscar)) { console.log(`✗ ${id}: '${buscar}' no aparece en la guía (${f[2]})`); errores++; }
  }
}
const g = filas.filter(f => f[11] === "G-FAC").length, n = filas.filter(f => f[11] === "NO-EST").length;
console.log(`filas=${filas.length}  verificadas-en-guía=${g}  no-estudiadas=${n}  errores=${errores}`);
process.exit(errores ? 1 : 0);
