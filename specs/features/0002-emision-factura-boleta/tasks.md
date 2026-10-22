# Tasks 0002 · Emisión de Factura y Boleta

> Spec: [`spec.md`](spec.md) · Diseño: [`design.md`](design.md) · `[x]` hecha · `[~]` en curso · `[ ]` pendiente · `‖` en paralelo.

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0002-xx` indicados · [ ] pruebas primero, en verde · [ ] contratos/matriz actualizados · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas (Spec-First)
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0002-01 | Esquema `ComprobanteEmitirRequest` y ejemplos válidos/inválidos | — | CA-0002-01…04 | [x] |
| T-0002-02 | Contrato OpenAPI EP-05/06/07/10/11/12 | T-0002-01 | CA-0002-01 | [x] |
| T-0002-03 | Matriz de trazabilidad de la factura (TR-001…TR-066) | — | RF-0002-06 | [x] |
| T-0002-04 | *Mock* de `IEnvioComprobantePort` con CDR de ejemplo (0, 4xxx, 2xxx, caída) | T-0002-02 | CA-0002-05 | [x] |
| T-0002-05 ‖ | Obtener el XSD `UBL-Invoice-2.1` y validar un XML de ejemplo | — | CA-0002-07 | [ ] |
| T-0002-06 | Cerrar ⚠ VERIFICAR: operaciones `billService`, umbral de boleta, plazo de envío | — | RF-0002-08, 10 | [ ] |

## Fase 2 · Dominio
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0002-07 | Agregado `Comprobante` y máquina de estados | T-0001-10 | RN-050…RN-053 | [ ] |
| T-0002-08 | `SerieComprobante.siguiente()` atómico | — | RF-0002-04 | [ ] |
| T-0002-09 | Validador de RUC (módulo 11) y de adquirente | — | RN-010, RN-012 | [ ] |

## Fase 3 · Aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0002-10 | `EmitirComprobanteUseCase` con idempotencia | T-0002-07…09 | CA-0002-01, 06 | [ ] |
| T-0002-11 | `ReintentarPendientesUseCase` | T-0002-10 | CA-0002-05 | [ ] |
| T-0002-12 | Evento `ComprobanteAceptado` | T-0002-10 | RF-0002-12 | [ ] |

## Fase 4 · Infraestructura
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0002-13 | `UblXmlAdapter` (plantilla `Invoice`) | T-0002-05 | CA-0002-07 | [ ] |
| T-0002-14 | `XmlDsigAdapter` y `ISecretStorePort` | T-0002-13 | RF-0002-07 | [ ] |
| T-0002-15 | `SunatBillServiceAdapter` y `OseAdapter` | T-0002-04, T-0002-06 | RF-0002-08 | [ ] |
| T-0002-16 | `SqliteComprobanteRepository` | T-0002-07 | RF-0002-04 | [ ] |

## Fase 5 · Web (MVC)
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0002-17 | `ComprobantesController` y vistas de emisión | T-0002-10 | CA-0002-01 | [ ] |
| T-0002-18 | PDF (representación impresa) | T-0002-10 | RF-0002-13 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0002-09 | RF-0002-02, 03 | CA-0002-02 | RN-010, RN-012 |
| T-0002-10 | RF-0002-04, 05, 09, 11 | CA-0002-05, 06 | RN-050…RN-052 |
| T-0002-14 | RF-0002-07 | CA-0002-07 | RN-053 |
