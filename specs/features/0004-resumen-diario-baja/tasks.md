# Tasks 0004 · Resumen Diario y Comunicación de Baja

> Spec: [`spec.md`](spec.md)

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0004-xx` · [ ] pruebas primero · [ ] contratos/matriz al día · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0004-01 | Esquemas `ResumenDiarioRequest`, `ComunicacionBajaRequest`, `LoteEnvioResponse` | — | CA-0004-05 | [x] |
| T-0004-02 | Contrato OpenAPI EP-08, EP-09 y `GET /lotes/{ticket}` | T-0004-01 | CA-0004-01 | [x] |
| T-0004-03 | **Contrastar con la guía de Resumen/Baja** las filas TR-072…078 | — | RF-0004-03, 06 | [ ] |
| T-0004-04 | *Mock* de `sendSummary`/`getStatus` con códigos 0, 98, 99 | T-0004-02 | CA-0004-02 | [x] |

## Fase 2 · Dominio y aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0004-05 | Agregados `ResumenDiario` y `ComunicacionBaja` con generador de id diario | T-0002-07 | CA-0004-01, 04 | [ ] |
| T-0004-06 | `EnviarResumenDiarioUseCase` y `EnviarBajaUseCase` | T-0004-05 | CA-0004-01, 03 | [ ] |
| T-0004-07 | `ConsultarTicketsPendientesUseCase` (job con reintentos) | T-0004-06 | CA-0004-02 | [ ] |

## Fase 3 · Infraestructura y Web
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0004-08 | Plantillas UBL `SummaryDocuments` y `VoidedDocuments` | T-0004-03 | RF-0004-03, 06 | [ ] |
| T-0004-09 | Adaptadores de `sendSummary` y `getStatus` | T-0004-04 | RF-0004-04, 05 | [ ] |
| T-0004-10 | Pantallas MVC de lotes y bajas | T-0004-06 | CA-0004-01 | [ ] |
| T-0004-11 | `IJobSchedulerPort` (Windows: tarea; Android: WorkManager) | T-0004-07 | RF-0004-08 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0004-05 | RF-0004-01…03, 06 | CA-0004-01, 04 | RN-006, RN-007 |
| T-0004-07 | RF-0004-05, 08 | CA-0004-02 | RN-050, RN-052 |
