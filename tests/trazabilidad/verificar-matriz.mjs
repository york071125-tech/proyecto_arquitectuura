// Verifica la matriz de trazabilidad:
//  (1) toda RN-nnn citada está definida en docs/01-contexto-normativo.md (RN-001…007) o docs/03-modelo-dominio.md;
//  (2) opcional: contrasta las filas con fuente G-VIG contra el texto de los anexos oficiales de SUNAT.
//      Se compara la RUTA COMPLETA del XPath (no solo el elemento hoja) y las filas «Retirado» deben NO aparecer.
//
// Uso: node verificar-matriz.mjs [anexo1.txt anexo2.txt …]
//   Los .txt salen de:  pdftotext -raw anexo.pdf anexo.txt   (Anexo 9-A de la RS 114-2019 y Anexo X para el resumen diario).
//   Los PDF oficiales NO se guardan en el repo; las URLs están en docs/07-matriz-trazabilidad.md.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { filas } from "./generar-matriz.mjs";

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "docs");
const dominio = ["01-contexto-normativo.md", "03-modelo-dominio.md"].map(f => readFileSync(path.join(dir, f), "utf8")).join("\n");
const definidas = new Set([...dominio.matchAll(/\|\s*(RN-\d{3})\s*\|/g)].map(m => m[1]));
const idFila = i => `TR-${String(i + 1).padStart(3, "0")}`;
let errores = 0;
const fallo = msg => { console.log("✗", msg); errores++; };

for (const [i, f] of filas.entries()) {
  for (const rn of String(f[9]).match(/RN-\d{3}/g) ?? []) {
    if (!definidas.has(rn)) fallo(`${idFila(i)}: ${rn} no está definida en 01/03`);
  }
}

// El PDF parte las rutas en varias líneas y columnas: se compara sin espacios y sin distinguir mayúsculas.
const compacto = s => s.replace(/\s+/g, "").toLowerCase();
// «/CreditNote|DebitNote/x» equivale a dos rutas; «a · b» son dos rutas distintas de la misma fila.
function rutasDe(xpath) {
  return xpath.split(" · ").flatMap(r => {
    const m = r.match(/^\/([A-Za-z]+(?:\|[A-Za-z]+)+)(\/.*)$/);
    return m ? m[1].split("|").map(raiz => `/${raiz}${m[2]}`) : [r];
  });
}

const guias = process.argv.slice(2);
let contrastadas = 0, retiradas = 0;
if (guias.length) {
  const texto = compacto(guias.map(g => readFileSync(g, "utf8")).join("\n"));
  for (const [i, f] of filas.entries()) {
    if (f[11] !== "G-VIG") continue;
    const retirada = String(f[10]).startsWith("Retirado");
    for (const ruta of rutasDe(f[2])) {
      const esta = texto.includes(compacto(ruta));
      if (retirada && esta) fallo(`${idFila(i)}: marcada «Retirado» pero SÍ figura en el estándar → ${ruta}`);
      if (!retirada && !esta) fallo(`${idFila(i)}: no figura en el estándar vigente → ${ruta}`);
    }
    retirada ? retiradas++ : contrastadas++;
  }
}

const cuenta = fuente => filas.filter(f => f[11] === fuente).length;
console.log(`filas=${filas.length}  G-VIG=${cuenta("G-VIG")}  ANEXO=${cuenta("ANEXO")}  NO-EST=${cuenta("NO-EST")}  errores=${errores}`);
if (guias.length) console.log(`contrastadas con el estándar: ${contrastadas} · retiradas (ausencia comprobada): ${retiradas}`);
else console.log("(sin anexos: solo se validaron las RN; pase los .txt de los anexos SUNAT para contrastar las rutas)");
process.exit(errores ? 1 : 0);
