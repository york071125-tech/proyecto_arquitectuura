# Spec 0003 · Notas de Crédito y Débito electrónicas

| Campo | Valor |
|---|---|
| **ID** | 0003-notas-credito-debito |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-07 |
| **Depende de** | 0001, 0002 |

## 1. Contexto y problema
Un comprobante emitido no se edita: se corrige o anula con una nota (07 crédito, 08 débito), que debe **referenciar** el documento modificado y declarar un motivo normado (cat. 09/10). Las notas usan otras raíces XML (`CreditNote` / `DebitNote`) y líneas distintas.

## 2. Objetivo y fuera de alcance
- **Objetivo**: emitir NC/ND vinculadas, con motivo válido y efecto correcto sobre almacén (devolución → ingreso).
- **Fuera de alcance**: notas sobre documentos físicos o anteriores al sistema.

## 3. Actores y precondiciones
Vendedor/Admin. El documento modificado existe, está `ACEPTADO` y pertenece al mismo emisor.

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0003-01 | `documentoModificado` obligatorio en 07/08 y prohibido en 01/03 | M |
| RF-0003-02 | Motivo: NC cat. 09 (01–10); ND cat. 10 (01–03) | M |
| RF-0003-03 | Verificar que el documento modificado existe y está aceptado | M |
| RF-0003-04 | La letra de la serie (F/B) hereda la del documento modificado | M |
| RF-0003-05 | Generar `CreditNote` / `DebitNote` con `BillingReference` y `DiscrepancyResponse` | M |
| RF-0003-06 | NC por anulación total (01) marca el documento origen como `ANULADO` | M |
| RF-0003-07 | NC por devolución (06/07) genera `INGRESO` de almacén (RN-061) | S |
| RF-0003-08 | El importe de la NC no puede exceder el del documento origen | M |

## 5. Reglas de negocio aplicables
`RN-004`, `RN-020…RN-024`, `RN-051`, `RN-061`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO | `ComprobanteEmitirRequest` con `tipoDocumento` ∈ {07, 08} y `documentoModificado` |
| Endpoint | EP-05 (mismo recurso) |
| Trazabilidad | `TR-067…TR-071` |

## 7. Flujo principal y alternos
Igual que 0002, más: cargar el documento origen → validar RF-0003-03/04/08 → generar la plantilla `CreditNote` / `DebitNote`.
- **A1** Origen inexistente o `RECHAZADO` → `ESTADO_NO_PERMITIDO`.
- **A2** Monto mayor al del origen → `TOTALES_INCONSISTENTES`.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-0003-01 | NC con `documentoModificado` válido (motivo 07) | se valida | válida | `nota-credito-valida.json` |
| CA-0003-02 | NC sin `documentoModificado` | se valida | error | `INVALIDO-nota-sin-documento-modificado.json` |
| CA-0003-03 | ND con motivo `05` | se valida | error (sólo 01–03) | `INVALIDO-nota-debito-motivo-05.json` (T-0003-02) |
| CA-0003-04 | NC total sobre factura aceptada | se acepta | la factura pasa a `ANULADO` | integración |
| CA-0003-05 | NC por devolución | se acepta | movimiento `INGRESO` por ítem | integración con 0005 |

## 9. Requisitos no funcionales
Los mismos de 0002.

## 10. Riesgos y preguntas abiertas
⚠ VERIFICAR (fuente `NO-EST` en la matriz): estructura exacta de `BillingReference` / `DiscrepancyResponse` y de las líneas `CreditNoteLine` / `DebitNoteLine` en la guía de NC/ND.
