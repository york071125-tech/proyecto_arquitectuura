# Tasks 0005 · Almacén y kardex

> Spec: [`spec.md`](spec.md)

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0005-xx` · [ ] pruebas primero · [ ] contratos/matriz al día · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0005-01 | Esquema `MovimientoInventario` | — | CA-0005-03 | [x] |
| T-0005-02 | Contrato OpenAPI EP-14 | T-0005-01 | CA-0005-01 | [x] |
| T-0005-03 | Casos dorados de kardex (ingreso, salida, ajuste, saldo) | — | CA-0005-01, 05, 06 | [x] |
| T-0005-04 | Decidir con contabilidad el método de valorización (RN-062) | — | RF-0005-05 | [ ] |

## Fase 2 · Dominio y aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0005-05 | Consumidor del evento `ComprobanteAceptado` → `SALIDA`, y de NC por devolución → `INGRESO` | T-0002-12 | CA-0005-02 | [ ] |
| T-0005-06 | Agregado `MovimientoInventario` inmutable y regla de saldo | T-0005-03 | CA-0005-01, 04 | [ ] |
| T-0005-07 | `RegistrarMovimientoUseCase` y `ConsultarKardexUseCase` | T-0005-06 | CA-0005-01 | [ ] |

## Fase 3 · Infraestructura y Web
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0005-08 | Repositorio SQLite con índice (producto, fecha) | T-0005-06 | RNF 9 | [ ] |
| T-0005-09 | Pantallas MVC de ingreso/salida y kardex | T-0005-07 | CA-0005-01 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0005-05 | RF-0005-03, 04 | CA-0005-02 | RN-061 |
| T-0005-06 | RF-0005-01, 02, 06, 07, 09 | CA-0005-03, 04, 06 | RN-060, RN-063 |
