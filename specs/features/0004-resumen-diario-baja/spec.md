# Spec 0004 · Resumen Diario de boletas y Comunicación de Baja

| Campo | Valor |
|---|---|
| **ID** | 0004-resumen-diario-baja |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-09, CU-10, CU-11, CU-13 |
| **Depende de** | 0002 |

## 1. Contexto y problema
Las boletas de venta se informan a SUNAT mediante un **Resumen Diario** (RC) y las facturas se anulan con una **Comunicación de Baja** (RA). Ambos son **asíncronos**: SUNAT devuelve un *ticket* que se consulta después hasta obtener el CDR.

## 2. Objetivo y fuera de alcance
- **Objetivo**: informar todas las boletas de un día y dar de baja documentos, con seguimiento del ticket y reintentos.
- **Fuera de alcance**: envío directo de boletas (si la norma vigente lo permite, ⚠ VERIFICAR RS 114-2019) y bajas de documentos no emitidos por el sistema.

## 3. Actores y precondiciones
Admin / proceso programado. Existen boletas `FIRMADO` del día (RC) o facturas `ACEPTADO` (RA).

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0004-01 | Generar el RC de una `fechaReferencia` con todas las boletas y notas de boleta del día | M |
| RF-0004-02 | Identificador `RC-AAAAMMDD-n` y `RA-AAAAMMDD-n`, con `n` correlativo diario por emisor | M |
| RF-0004-03 | Cada línea del RC lleva el estado del ítem (cat. 19: 1 adicionar, 2 modificar, 3 anulado) | M |
| RF-0004-04 | Enviar con `sendSummary` y guardar el *ticket* | M |
| RF-0004-05 | Consultar el ticket con `getStatus` hasta recibir el CDR (códigos 0, 98, 99) | M |
| RF-0004-06 | La Comunicación de Baja registra serie, correlativo y motivo de cada documento | M |
| RF-0004-07 | Al aceptarse la baja, el comprobante pasa a `ANULADO` | M |
| RF-0004-08 | Reintentar lotes pendientes sin duplicarlos | S |

## 5. Reglas de negocio aplicables
`RN-006`, `RN-007`, `RN-050`, `RN-052`, `RN-053`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO | `operaciones.schema.json#/$defs/ResumenDiarioRequest`, `#/$defs/ComunicacionBajaRequest`, `#/$defs/LoteEnvioResponse` |
| Endpoints | EP-08 (resumen), EP-09 (baja), consulta de ticket `GET /lotes/{ticket}` |
| Puerto | PT-02 `IEnviarLote`, PT-13 |
| Trazabilidad | `TR-072…TR-078` (⚠ fuente `NO-EST`) |

## 7. Flujo principal y alternos
1. El admin (o el *job* de fin de día) pide el RC de la fecha.
2. El sistema arma el XML `SummaryDocuments`, lo firma y lo envía → recibe *ticket*.
3. Estado `PENDIENTE`; el *job* consulta el ticket cada N minutos → `ACEPTADO` / `RECHAZADO`.
4. Las boletas del lote quedan `ACEPTADO`.
- **A1** Ticket con código 98 (en proceso) → se reintenta consulta.
- **A2** Ticket con código 99 → `RECHAZADO` y se muestran los errores.
- **A3** No hay boletas ese día → no se genera lote.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-0004-01 | 3 boletas firmadas el 2026-10-19 | se pide el RC | un lote `RC-20261019-1` con 3 líneas | prueba de aplicación |
| CA-0004-02 | Ticket en proceso (98) | pasa el intervalo | se consulta de nuevo, sin reenviar | *mock* de ticket |
| CA-0004-03 | Baja de una factura aceptada | SUNAT acepta | la factura queda `ANULADO` | integración |
| CA-0004-04 | Dos RC el mismo día | se generan | ids `…-1` y `…-2` | prueba de aplicación |
| CA-0004-05 | Request de baja sin documentos | se valida | error de esquema | `INVALIDO-comunicacion-baja-sin-documentos.json` (válidos: `comunicacion-baja-valida.json`, `resumen-diario-valido.json`) |

## 9. Requisitos no funcionales
Tolerante a cierre de la app (el *job* retoma tickets pendientes al reiniciar). En Android, usar el programador del sistema (`IJobSchedulerPort`).

## 10. Riesgos y preguntas abiertas
⚠ VERIFICAR: estructura de `SummaryDocuments` / `VoidedDocuments` (`NO-EST`), nombres de archivo `RUC-RC-AAAAMMDD-n` / `RUC-RA-AAAAMMDD-n` y plazos de baja.
