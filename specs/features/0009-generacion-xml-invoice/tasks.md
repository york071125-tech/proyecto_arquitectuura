# Tasks 0009 · Generación de XML Invoice UBL 2.1 (Segundo Parcial)

> Spec: [`spec.md`](spec.md) · Diseño: [`design.md`](design.md) · `[x]` hecha · `[ ]` pendiente

## Definition of Done (toda tarea)
- [x] Cumple los `CA-0009-xx` indicados · [x] pruebas ejecutadas de verdad y en verde · [x] documentación al día

## Fase 1 · Insumos oficiales
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0009-01 | Identificar el XSD exacto: `UBL-Invoice-2.1.xsd` de OASIS (UBL 2.1 OS, release 04-11-2013) | — | RF-0009-11 | [x] |
| T-0009-02 | Descargar solo ese XSD y sus 13 dependencias desde `docs.oasis-open.org`; versionar con SHA-256 y README | T-0009-01 | CA-0009-08 | [x] |
| T-0009-03 | Contrastar la estructura de `Invoice` con el estándar vigente de SUNAT (matriz, 74 filas verificadas) | — | RF-0009-07 | [x] |

## Fase 2 · Dominio
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0009-04 | Modelo: `Factura`, `Emisor`, `Receptor`, `DetalleFactura`, `TipoAfectacion` (1001–1004), `FormaPago` | — | CA-0009-10 | [x] |
| T-0009-05 | Validaciones: RUC módulo 11, serie, correlativo, cantidad, unidad catálogo 03, receptor con RUC | T-0009-04 | CA-0009-10 | [x] |
| T-0009-06 | Cálculo con `Decimal`, half-up por línea, totales, forma de pago | T-0009-04 | CA-0009-05, 11 | [x] |
| T-0009-07 | Monto en letras (leyenda 1000) | — | CA-0009-02 | [x] |

## Fase 3 · Generador y validador
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0009-08 | `GeneradorFacturaXml`: árbol `lxml` en el orden del XSD, UTF-8 | T-0009-06 | CA-0009-01…07 | [x] |
| T-0009-09 | `ValidadorXsd`: errores con número de línea, `XmlInvalidoError`, `XsdNoEncontradoError` | T-0009-02 | CA-0009-08, 09 | [x] |
| T-0009-10 | CLI `python -m facturacion_xml` y XML de ejemplo versionado | T-0009-08 | RF-0009-12 | [x] |

## Fase 4 · Pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0009-11 | Pruebas unitarias de los 9 aspectos del ingeniero (110 pruebas) | T-0009-08 | CA-0009-01…12 | [x] |
| T-0009-12 | Prueba de que el validador **rechaza** XML incorrecto | T-0009-09 | CA-0009-09 | [x] |
| T-0009-13 | Verificar la utilidad de las pruebas con mutaciones del código (10 de 10 detectadas) | T-0009-11 | RF-0009-13 | [x] |
| T-0009-14 | Reproducibilidad en un entorno virtual limpio (`pip install -r requirements.txt`) | T-0009-11 | §9 | [x] |

## Fase 5 · Documentación
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0009-15 | `docs/09-parcial2-generacion-xml.md`: caso, tecnologías, estructura, generador, pruebas, ejecución | T-0009-11 | — | [x] |

## Pendiente fuera de este parcial
| ID | Tarea | Fase |
|---|---|---|
| T-0009-16 | Firma digital `ds:Signature` en `ext:UBLExtensions` | siguiente fase |
| T-0009-17 | `CreditNote`, `DebitNote` y esquemas SUNAT de resumen/baja | features 0003 y 0004 |
| T-0009-18 | Confirmar los nombres `INA`, `EXO`, `GRA` del catálogo 05 y el motivo gratuito por defecto | verificación normativa |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | RN |
|---|---|---|---|
| T-0009-05 | RF-0009-02 | CA-0009-10 | RN-001, RN-002, RN-010, RN-012, RN-086 |
| T-0009-06 | RF-0009-03, 04, 05 | CA-0009-05, 06, 11 | RN-020…RN-022, RN-024, RN-030, RN-031 |
| T-0009-08 | RF-0009-06…10 | CA-0009-01…07, 12 | RN-045, RN-080, RN-081, RN-088 |
| T-0009-09 | RF-0009-11 | CA-0009-08, 09 | RN-088 |
