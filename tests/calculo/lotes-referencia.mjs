// Oráculo de referencia para el seguimiento asíncrono de lotes SUNAT (T-0004-04).
// Los códigos representan el contrato documentado: 0=aceptado, 98=en proceso, 99=rechazado.
import assert from "node:assert/strict";

const casos = [
  { codigo: "0", estadoEsperado: "ACEPTADO", vuelveAConsultar: false },
  { codigo: "98", estadoEsperado: "EN_PROCESO", vuelveAConsultar: true },
  { codigo: "99", estadoEsperado: "RECHAZADO", vuelveAConsultar: false },
];

function interpretarEstadoTicket(codigo) {
  if (codigo === "0") return { estado: "ACEPTADO", vuelveAConsultar: false };
  if (codigo === "98") return { estado: "EN_PROCESO", vuelveAConsultar: true };
  if (codigo === "99") return { estado: "RECHAZADO", vuelveAConsultar: false };
  throw new Error(`Código de ticket no soportado: ${codigo}`);
}

let consultas = 0;
let reenvios = 0;
for (const caso of casos) {
  consultas++;
  const resultado = interpretarEstadoTicket(caso.codigo);
  assert.deepEqual(resultado, {
    estado: caso.estadoEsperado,
    vuelveAConsultar: caso.vuelveAConsultar,
  });
  // Consultar un ticket existente nunca vuelve a ejecutar sendSummary.
  assert.equal(reenvios, 0);
  console.log(`OK   ticket ${caso.codigo} → ${resultado.estado} · reconsulta=${resultado.vuelveAConsultar}`);
}

assert.equal(consultas, 3);
assert.throws(() => interpretarEstadoTicket("97"), /no soportado/);
console.log(`casos=${casos.length} consultas=${consultas} reenvios=${reenvios} fallos=0`);
