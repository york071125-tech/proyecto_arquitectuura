# Tasks 0008 · Libros electrónicos (14.1 y 12.1)

> Spec: [`spec.md`](spec.md)

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0008-xx` · [ ] pruebas primero · [ ] contratos/matriz al día · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0008-01 | Esquemas `RegistroVentasFila` y `RegistroInventarioFisicoFila` (campos 1–34 y 1–19) | — | CA-0008-03, 04 | [x] |
| T-0008-02 | Contrato OpenAPI EP-17 y EP-19 (`text/plain` y JSON) | T-0008-01 | CA-0008-01 | [x] |
| T-0008-03 | Campos del 12.1 en `MovimientoInventario` y tablas 5, 6, 10, 12 | T-0008-01 | CA-0008-02 | [x] |
| T-0008-04 | Oráculo `npm run libros`: DTO → línea PLE, comparada con la escrita a mano | T-0008-01 | CA-0008-01, 02 | [x] |
| T-0008-05 | **Contrastar la ficha técnica del PLE** (cabecera, nombre del archivo, «\|» final, ICBPER, Tabla 12) | — | RF-0008-04, 07 | [ ] |
| T-0008-06 ‖ | Casos con notas de crédito y con moneda extranjera en el 14.1 | T-0008-04 | RF-0008-02, 03 | [ ] |

## Fase 2 · Dominio y aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0008-07 | `GenerarRegistroVentas` (comprobantes del periodo → filas 14.1) | T-0002-10 | RF-0008-01…03 | [ ] |
| T-0008-08 | `GenerarInventarioFisico` (movimientos → filas 12.1, entradas/salidas excluyentes) | T-0005-07 | RF-0008-05, 06 | [ ] |

## Fase 3 · Infraestructura y Web
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0008-09 | `PleTextAdapter` (PT-18): DTO → líneas PLE | T-0008-05 | RF-0008-07 | [ ] |
| T-0008-10 | Endpoints EP-17 y EP-19 y pantalla de libros | T-0008-07, T-0008-08 | CA-0008-01 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0008-04 | RF-0008-01, 05, 07, 08 | CA-0008-01, 02 | RN-084, RN-085 |
| T-0008-08 | RF-0008-05, 06 | CA-0008-02 | RN-085 |
