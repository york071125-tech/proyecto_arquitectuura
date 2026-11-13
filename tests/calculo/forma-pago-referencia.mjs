// Oráculo de RN-080/RN-081 (forma de pago): una factura a CRÉDITO lleva monto pendiente y cuotas que cuadran.
// Cuotas: Σ cuotas = montoPendiente; fechas no anteriores a la emisión ni decrecientes; montoPendiente = importe total − anticipos.
// Aritmética en centavos con BigInt (ADR-04). Reutiliza el oráculo de totales de la spec 0001.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { calcular } from "./calculo-referencia.mjs";

const raiz = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ej = f => JSON.parse(readFileSync(path.join(raiz, "specs", "contracts", "examples", f), "utf8"));
const cent = s => BigInt(String(s).replace(".", ""));   // "141.60" → 14160n (Monto2 siempre trae 2 decimales)

export function validarFormaPago(factura) {
  const fp = factura.formaPago, e = [];
  if (!fp) return ["FORMA_PAGO_FALTANTE"];                                                    // RN-080
  if (fp.tipo === "CONTADO") return fp.cuotas || fp.montoPendiente ? ["CUOTAS_INCONSISTENTES: contado no lleva cuotas"] : [];
  const t = calcular(factura), esperado = cent(t.importeTotal.toFixed(2)) - cent(t.anticipos.toFixed(2));
  if (cent(fp.montoPendiente) !== esperado) e.push("CUOTAS_INCONSISTENTES: montoPendiente ≠ importe total − anticipos");
  if ((fp.cuotas ?? []).reduce((a, c) => a + cent(c.monto), 0n) !== cent(fp.montoPendiente)) e.push("CUOTAS_INCONSISTENTES: Σ cuotas ≠ montoPendiente");
  let previa = factura.fechaEmision;
  for (const c of fp.cuotas ?? []) { if (c.fechaVencimiento < previa) e.push(`CUOTAS_INCONSISTENTES: ${c.fechaVencimiento} anterior a ${previa}`); previa = c.fechaVencimiento; }
  return e;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const ok = ej("factura-credito-valida.json");
  const con = cambios => ({ ...ok, formaPago: { ...ok.formaPago, ...cambios } });
  const casos = [
    ["crédito válido (2 cuotas = 283.20)", ok, []],
    ["contado válido", { ...ok, formaPago: { tipo: "CONTADO" } }, []],
    ["sin forma de pago", { ...ok, formaPago: undefined }, ["FORMA_PAGO_FALTANTE"]],
    ["cuotas no suman el pendiente", con({ cuotas: [{ monto: "100.00", fechaVencimiento: "2026-11-19" }] }), ["Σ cuotas"]],
    ["pendiente distinto del total", con({ montoPendiente: "300.00" }), ["montoPendiente"]],
    ["cuota vence antes de la emisión", con({ cuotas: [{ monto: "141.60", fechaVencimiento: "2026-10-01" }, { monto: "141.60", fechaVencimiento: "2026-12-19" }] }), ["anterior a"]],
    ["fechas decrecientes", con({ cuotas: [{ monto: "141.60", fechaVencimiento: "2026-12-19" }, { monto: "141.60", fechaVencimiento: "2026-11-19" }] }), ["anterior a"]],
  ];
  let fallos = 0;
  for (const [nombre, f, esperados] of casos) {
    const e = validarFormaPago(f), bien = esperados.length ? esperados.every(x => e.some(y => y.includes(x))) : e.length === 0;
    if (!bien) fallos++;
    console.log(`${bien ? "OK  " : "FAIL"} ${nombre}${e.length ? " → " + e[0] : ""}`);
  }
  console.log(`casos=${casos.length}  fallos=${fallos}`);
  process.exit(fallos ? 1 : 0);
}
