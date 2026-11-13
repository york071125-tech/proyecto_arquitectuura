# Tasks 0001 · Cálculo tributario

> Spec: [`spec.md`](spec.md) · `[ ]` pendiente · `[x]` hecha · `‖` en paralelo.

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0001-xx` indicados · [ ] pruebas primero, en verde · [ ] contratos/matriz actualizados · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas (Spec-First)
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0001-01 | Caso dorado de la factura de ejemplo con totales esperados | — | CA-0001-01 | [x] |
| T-0001-02 | Oráculo de cálculo `tests/calculo/calculo-referencia.mjs` | T-0001-01 | CA-0001-01/02 | [x] |
| T-0001-03 | Esquemas con reglas condicionales ISC/gratuitas | — | CA-0001-03/04 | [x] |
| T-0001-04 ‖ | Más casos dorados: exonerada, inafecta, exportación, monto fijo (cat. 08 = 02), descuento global, anticipo | T-0001-02 | CA-0001-05 | [x] |
| T-0001-05 | **Cerrar ⚠ VERIFICAR del ISC por PVP** con norma y fijar caso dorado | — | RF-0001-02 | [ ] |

## Fase 2 · Dominio (cuando se pase a código)
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0001-06 | Prueba de propiedades: totales = suma de líneas (10 000 casos) | T-0001-04 | CA-0001-05 | [ ] |
| T-0001-07 | `Dinero` (value object `decimal`) y redondeo half-up | — | RN-021, RN-024 | [ ] |
| T-0001-08 | Estrategias `IscAlValor`, `IscMontoFijo`, `IscPrecioVentaPublico` | T-0001-05, T-0001-07 | RF-0001-02 | [ ] |
| T-0001-09 | `CalculadoraIgv`, `CalculadoraIcbper`, `ClasificadorAfectacion` | T-0001-07 | RF-0001-03…06 | [ ] |
| T-0001-10 | `CalculadoraTotales` + leyenda 1000 (monto en letras) | T-0001-09 | RF-0001-07/08 | [ ] |

## Fase 3 · Aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0001-11 | Puerto `IParametrosPort` con vigencias (ADR-05) y siembra inicial | — | RF-0001-01 | [ ] |
| T-0001-12 | Caso de uso `CalcularComprobante` (función pura) | T-0001-10, T-0001-11 | CA-0001-01 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0001-02 | RF-0001-01…07 | CA-0001-01, 02 | RN-020…RN-042 |
| T-0001-08 | RF-0001-02 | CA-0001-02 | RN-040, RN-041 |
| T-0001-09 | RF-0001-03…06 | CA-0001-01 | RN-020, RN-030…RN-032, RN-042 |
