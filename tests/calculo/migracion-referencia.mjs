// Prueba de la ESPECIFICACIÓN de la migración del legado (feature 0006, RN-070…RN-075): valida cada ficha de
// `examples/legado/<caso>.json` contra FichaLegado, la clasifica (migrada o rechazada con causa), la migra a un almacén
// en memoria y compara con `<caso>.esperado.json`; luego reprocesa el mismo archivo para probar la idempotencia (RN-074).
// ⚠ Interpretación (spec 0006 §10): «migrada» = su movimiento existe en el kardex, nuevo o de una corrida anterior; así
// leidos = migrados + rechazados (RN-075) también se cumple al reprocesar, con 0 movimientos nuevos.
// Cantidades n(12,10) como enteros de 10⁻¹⁰ con BigInt: sin float (ADR-04).
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { createHash, randomUUID } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const dir = path.join(raiz, "specs", "contracts", "examples", "legado");
const sch = path.join(raiz, "specs", "contracts", "schemas");
const leer = f => JSON.parse(readFileSync(f, "utf8"));
const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const sha256 = s => createHash("sha256").update(s).digest("hex");
const uuid = h => `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20, 32)}`;
const num = v => Number(v) / 1e10;

// RN-073: trim, mayúsculas y sin tildes (también colapsa espacios internos).
const normalizar = x => String(x ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase().replace(/\s+/g, " ").trim();
// RN-074: origenLegacyId = PK de origen o, si el legado no la trae, SHA-256 de la fila normalizada.
const CAMPOS = ["fecha", "ingreso", "salida", "producto", "nro_documento"];
const clave = f => f.idOrigen ?? sha256(JSON.stringify(CAMPOS.map(c => normalizar(f[c]))));

function fecha(s) { // dd/mm/aaaa o aaaa-mm-dd → aaaa-mm-dd; null si no es una fecha real (p. ej. 31/02)
  const t = String(s ?? "").trim();
  let d, m, a;
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(t)) [d, m, a] = t.split("/");
  else if (/^\d{4}-\d{2}-\d{2}$/.test(t)) [a, m, d] = t.split("-");
  else return null;
  const f = new Date(Date.UTC(+a, +m - 1, +d));
  return f.getUTCFullYear() === +a && f.getUTCMonth() === +m - 1 && f.getUTCDate() === +d ? `${a}-${m}-${d}` : null;
}

function cantidad(x) { // RF-0006-03: número o texto con coma decimal → unidades de 10⁻¹⁰; vacío → 0n; inválida → null
  if (x === null || x === undefined || String(x).trim() === "") return 0n;
  const m = (typeof x === "number" ? x.toFixed(10) : String(x).trim().replace(",", ".")).match(/^(\d+)(?:\.(\d{1,10}))?$/);
  return m ? BigInt(m[1] + (m[2] ?? "").padEnd(10, "0")) : null;
}

function clasificar(f) { // RN-072 (tipo) y RN-075 (causa del rechazo)
  const fe = fecha(f.fecha); if (!fe) return { causa: "FECHA_INVALIDA" };
  const ing = cantidad(f.ingreso), sal = cantidad(f.salida);
  if (ing === null || sal === null) return { causa: "CANTIDAD_INVALIDA" };
  if (ing > 0n && sal > 0n) return { causa: "INGRESO_Y_SALIDA_A_LA_VEZ" };
  if (ing === 0n && sal === 0n) return { causa: "SIN_MOVIMIENTO" };
  return { fecha: fe, tipo: ing > 0n ? "INGRESO" : "SALIDA", cantidad: ing > 0n ? ing : sal, producto: normalizar(f.producto) };
}

export function migrar(fichas, almacen) {
  const resultados = [], rechazos = [], primera = new Map();
  let nuevos = 0;
  for (const [i, f] of fichas.entries()) {
    const id = clave(f), c = clasificar(f);
    if (c.causa) { rechazos.push({ idOrigen: id, causa: c.causa, fichaOriginal: structuredClone(f) }); resultados.push({ resultado: "RECHAZADA", causa: c.causa }); continue; }
    let p = almacen.productos.get(c.producto);                                             // RN-073: se crea si no existe
    if (!p) almacen.productos.set(c.producto, p = { codigoInterno: `LEG-${String(almacen.productos.size + 1).padStart(3, "0")}`,
                                                    productoId: uuid(sha256("producto:" + c.producto)), pendienteTributario: true });
    const r = { resultado: "MIGRADA", tipo: c.tipo, cantidad: num(c.cantidad), fecha: c.fecha, producto: c.producto };
    if (almacen.movimientos.has(id)) r.duplicadaDe = primera.get(id) ?? "corrida anterior";  // RN-074: no se duplica
    else {
      almacen.movimientos.set(id, { id: uuid(sha256("movimiento:" + id)), tipo: c.tipo, fecha: c.fecha, productoId: p.productoId, cantidad: num(c.cantidad),
        docReferencia: { tipo: "INTERNO_LEGADO", numero: String(f.nro_documento) },          // RN-071: nunca comprobante SUNAT
        origenLegacyId: id, datosOriginales: structuredClone(f) });                            // RN-070: ficha íntegra
      nuevos++;
    }
    if (!primera.has(id)) primera.set(id, i + 1);
    resultados.push(r);
  }
  const migrados = resultados.filter(r => r.resultado === "MIGRADA").length;
  return { resultados, nuevos, reporte: { id: randomUUID(), estado: "COMPLETADO", leidos: fichas.length, migrados, rechazados: rechazos.length, rechazos } };
}

const saldos = almacen => Object.fromEntries([...almacen.productos].map(([nombre, p]) => [nombre, num([...almacen.movimientos.values()]
  .filter(m => m.productoId === p.productoId).reduce((a, m) => a + (m.tipo === "INGRESO" ? 1n : -1n) * cantidad(m.cantidad), 0n))]));
const describir = r => r.causa ? `RECHAZADA ${r.causa}` : r.duplicadaDe ? `MIGRADA, duplicada de la ficha ${r.duplicadaDe} (sin movimiento nuevo)`
  : `MIGRADA ${r.tipo} ${r.cantidad} ${r.producto} (${r.fecha})`;

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ajv = new Ajv2020({ strict: false, allErrors: true }); addFormats(ajv);
  for (const f of readdirSync(sch).filter(f => f.endsWith(".schema.json"))) ajv.addSchema(leer(path.join(sch, f)));
  const [vFicha, vMov, vLote] = ["FichaLegado", "MovimientoInventario", "LoteMigracionResponse"]
    .map(d => ajv.getSchema(`https://abc-software.example/schemas/almacen-migracion.schema.json#/$defs/${d}`));
  let fallos = 0;
  const chequeo = (ok, texto) => { if (!ok) fallos++; console.log(`${ok ? "OK  " : "FAIL"} ${texto}`); };

  for (const f of readdirSync(dir).filter(f => f.endsWith(".json") && !f.endsWith(".esperado.json"))) {
    const { fichas } = leer(path.join(dir, f)), esp = leer(path.join(dir, f.replace(/\.json$/, ".esperado.json")));
    const invalidas = fichas.map((x, i) => vFicha(x) ? null : `ficha ${i + 1}: ${ajv.errorsText(vFicha.errors)}`).filter(Boolean);
    chequeo(!invalidas.length && esp.fichas.length === fichas.length, `${f} · ${fichas.length} fichas válidas contra FichaLegado ${invalidas.join(" · ")}`);

    const almacen = { productos: new Map(), movimientos: new Map() };
    const r1 = migrar(fichas, almacen), rep = r1.reporte, movs = [...almacen.movimientos.values()];
    for (const [i, r] of r1.resultados.entries()) {
      const e = esp.fichas[i] ?? {}, difs = Object.keys(e).filter(k => r[k] !== e[k]);
      chequeo(Object.keys(e).length && !difs.length, `${f} · ficha ${i + 1} → ${describir(r)}${difs.length ? `  (esperado ${JSON.stringify(e)})` : ""}`);
    }
    chequeo(rep.leidos === rep.migrados + rep.rechazados && ["leidos", "migrados", "rechazados"].every(k => rep[k] === esp.reporte[k]) && r1.nuevos === esp.movimientosNuevos,
      `${f} · RN-075 leidos=${rep.leidos} = migrados=${rep.migrados} + rechazados=${rep.rechazados} · movimientos nuevos=${r1.nuevos}`);
    chequeo(vLote(rep) && rep.rechazos.every(x => x.causa && fichas.some(o => clave(o) === x.idOrigen && igual(o, x.fichaOriginal))),
      `${f} · reporte válido contra LoteMigracionResponse; cada rechazo trae idOrigen, causa y fichaOriginal (CA-0006-05)`);
    chequeo(movs.every(m => vMov(m) && m.docReferencia.tipo === "INTERNO_LEGADO" && fichas.some(o => clave(o) === m.origenLegacyId && igual(o, m.datosOriginales))),
      `${f} · ${movs.length} movimientos válidos contra MovimientoInventario, referencia INTERNO_LEGADO (RN-071) y ficha íntegra (RN-070)`);
    chequeo(almacen.productos.size === esp.productosCreados && [...almacen.productos.values()].every(p => p.pendienteTributario),
      `${f} · ${almacen.productos.size} productos creados con pendienteTributario=true (RN-073)`);
    const s1 = saldos(almacen);
    chequeo(igual(Object.keys(s1).sort(), Object.keys(esp.saldos).sort()) && Object.entries(esp.saldos).every(([k, v]) => s1[k] === v),
      `${f} · saldos del kardex por producto ${JSON.stringify(s1)}`);

    const antes = JSON.stringify([...almacen.movimientos.values()]), r2 = migrar(fichas, almacen), rep2 = r2.reporte;
    chequeo(rep2.leidos === rep2.migrados + rep2.rechazados && ["leidos", "migrados", "rechazados"].every(k => rep2[k] === esp.reproceso[k])
      && r2.nuevos === esp.reproceso.movimientosNuevos && JSON.stringify([...almacen.movimientos.values()]) === antes && igual(saldos(almacen), s1),
      `${f} · reproceso idempotente (RN-074): leidos=${rep2.leidos} = migrados=${rep2.migrados} + rechazados=${rep2.rechazados} · movimientos nuevos=${r2.nuevos} · kardex sin cambios`);
  }
  console.log(`fallos=${fallos}`);
  process.exit(fallos ? 1 : 0);
}
