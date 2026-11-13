# Tasks 0006 · Migración del legado

> Spec: [`spec.md`](spec.md) · Diseño: [`design.md`](design.md) · `[x]` hecha · `[~]` en curso · `[ ]` pendiente

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0006-xx` · [ ] pruebas primero · [ ] contratos/matriz al día · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0006-01 | Esquemas `FichaLegado`, `MigracionRequest`, `LoteMigracionResponse` | — | CA-0006-05 | [x] |
| T-0006-02 | Contrato OpenAPI EP-15 | T-0006-01 | CA-0006-01 | [x] |
| T-0006-03 | **Obtener una muestra real del legado** y confirmar formato | — | RF-0006-01 | [ ] |
| T-0006-04 | Archivo de prueba con casos sucios (fechas, ingreso+salida, ambiguos, duplicados) | T-0006-03 | CA-0006-01…05 | [x] |

## Fase 2 · Dominio y aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0006-05 | `NormalizadorFicha` (fecha, cantidad, producto) | T-0006-04 | RF-0006-03 | [ ] |
| T-0006-06 | `ResolutorProducto` y `mapeoProductos` | T-0006-05 | RF-0006-05 | [ ] |
| T-0006-07 | `MigrarLegadoUseCase` con simulación e idempotencia | T-0006-05, T-0006-06, T-0005-07 | CA-0006-01, 02 | [ ] |
| T-0006-08 | Prueba de conservación de saldos por producto | T-0006-07 | CA-0006-03 | [ ] |
| T-0006-09 | Bloqueo de facturación de productos `pendienteTributario` | T-0002-10 | CA-0006-06 | [ ] |

## Fase 3 · Infraestructura y Web
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0006-10 | Adaptador `ILegacyReaderPort` según el formato real | T-0006-03 | RF-0006-01 | [ ] |
| T-0006-11 | Pantalla MVC: simulación, ejecución y reporte de rechazos | T-0006-07 | CA-0006-05 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0006-05 | RF-0006-03, 04, 06 | CA-0006-04 | RN-071, RN-072 |
| T-0006-07 | RF-0006-02, 07…09 | CA-0006-01, 02 | RN-070, RN-074, RN-075 |
