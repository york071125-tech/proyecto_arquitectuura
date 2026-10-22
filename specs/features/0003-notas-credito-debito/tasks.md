# Tasks 0003 · Notas de Crédito y Débito

> Spec: [`spec.md`](spec.md)

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0003-xx` · [ ] pruebas primero · [ ] contratos/matriz al día · [ ] `npm test` en verde

## Fase 1 · Contratos y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0003-01 | Esquema condicional NC/ND y ejemplos | — | CA-0003-01, 02 | [x] |
| T-0003-02 | Ejemplo inválido ND con motivo 05 y su prueba | T-0003-01 | CA-0003-03 | [x] |
| T-0003-03 | **Contrastar con la guía XML de NC/ND** las filas TR-067…071 (hoy `NO-EST`) | — | RF-0003-05 | [ ] |

## Fase 2 · Dominio y aplicación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0003-04 | Entidad `DocumentoModificado` y reglas RF-0003-01…04, 08 | T-0002-07 | CA-0003-02 | [ ] |
| T-0003-05 | Caso de uso `EmitirNota` (reutiliza `EmitirComprobante`) | T-0003-04 | CA-0003-04 | [ ] |
| T-0003-06 | Evento → ingreso de almacén por devolución | T-0003-05, T-0005-05 | CA-0003-05 | [ ] |

## Fase 3 · Infraestructura
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0003-07 | Plantillas UBL `CreditNote` y `DebitNote` | T-0003-03 | RF-0003-05 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0003-04 | RF-0003-01…04, 08 | CA-0003-02 | RN-004 |
| T-0003-06 | RF-0003-07 | CA-0003-05 | RN-061 |
