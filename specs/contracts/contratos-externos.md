# Contratos de servicios externos (puertos de salida)

Estos contratos los define un tercero; aquí se fija **cómo los consume el sistema** para poder simularlos (*mock/contract tests*) antes de escribir el adaptador.

## 1. PT-13 `IEnvioComprobantePort`

| Operación del puerto | SUNAT `billService` (SOAP, WS-Security UsernameToken: `RUC+usuarioSOL` / clave SOL) | Uso |
|---|---|---|
| `enviarComprobante(nombreZip, contenidoZip)` | `sendBill(fileName, contentFile)` → `applicationResponse` (CDR zip en base64) | Facturas y notas, respuesta **síncrona** |
| `enviarLote(nombreZip, contenidoZip)` | `sendSummary(fileName, contentFile)` → `ticket` | Resumen diario (RC) y baja (RA), **asíncrono** |
| `consultarTicket(ticket)` | `getStatus(ticket)` → `statusCode` + `content` (CDR) | Sondeo de lotes |
| `consultarCdr(ruc, tipo, serie, correlativo)` | `getStatusCdr(...)` | Recuperar CDR de un comprobante |

> ⚠ VERIFICAR contra la versión vigente de la guía de servicios web de SUNAT: nombres de operaciones, URLs beta/producción y el uso de `sendPack`.

**Mapeo de resultado → estado interno**

| Respuesta | Estado del comprobante |
|---|---|
| `ResponseCode 0` sin notas | `ACEPTADO` |
| `ResponseCode 0` con observaciones 4xxx | `ACEPTADO_CON_OBS` |
| Error 2xxx/3xxx | `RECHAZADO` |
| `statusCode 98` (en proceso) | permanece `ENVIADO`; se reintenta consulta |
| `statusCode 99` (con errores) | `RECHAZADO` |
| Falla SOAP 0100–0999 / sin red | `PENDIENTE_ENVIO` (RN-050) |

**Archivos**: `RUC-TT-SERIE-CORRELATIVO.xml` dentro de `RUC-TT-SERIE-CORRELATIVO.zip` (RN-003). Lotes: `RUC-RC-AAAAMMDD-n.xml` y `RUC-RA-AAAAMMDD-n.xml`.

## 2. Adaptador OSE (alternativo, ADR-03)
Mismo puerto. El OSE valida y reenvía a SUNAT; devuelve CDR firmado por el OSE. Config por emisor: `oseUrl` + credenciales. Un OSE concreto define su propio contrato; el adaptador sólo traduce al mapeo de la tabla anterior.

## 3. PT-14 `IConsultaRucPort`
Entrada: `ruc` (ya validado por RN-010). Salida: `{ razonSocial, estado, condicion, direccion?, ubigeo? }`. Fuente: padrón reducido de SUNAT o proveedor externo. Falla ⇒ **degradar**: se acepta RUC con formato válido y se marca `verificacionPendiente=true` (no bloquea la venta offline).

## 4. Pruebas de contrato
- Cada operación tiene un par `request.xml` / `response.xml` de ejemplo en `tests/contratos-externos/` (fase de implementación).
- El adaptador debe pasar contra el *mock* antes de apuntar a `beta`.
