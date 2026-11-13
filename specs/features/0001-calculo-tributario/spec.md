# Spec 0001 · Cálculo tributario (IGV, ISC, ICBPER) y totales

| Campo | Valor |
|---|---|
| **ID** | 0001-calculo-tributario |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-20 (y soporte de CU-05, CU-06, CU-07, CU-08) |
| **Depende de** | — (es la base de 0002 y 0003) |

## 1. Contexto y problema
El software actual **no calcula correctamente los impuestos** (IGV, ISC, ICBPER). Un solo centavo de diferencia entre líneas y totales provoca rechazo de SUNAT. La norma exige además que el ISC se calcule según el **Catálogo 08** (campo `cbc:TierRange`) y que forme parte de la base del IGV.

## 2. Objetivo y fuera de alcance
- **Objetivo**: dado un comprobante (ítems, descuentos, anticipos), producir **totales exactos y reproducibles** que cuadren línea por línea, con trazabilidad al XML UBL.
- **Fuera de alcance**: percepciones, retenciones, detracciones, IVAP, tipo de cambio oficial (sólo se recibe `tipoCambio` informativo, RN-036). Sistema ISC **03** (PVP) queda *especificado como estrategia* pero su fórmula está **⚠ VERIFICAR**.

## 3. Actores y precondiciones
| Actor | Rol | Precondición |
|---|---|---|
| Caso de uso `EmitirComprobante` | invoca el cálculo | `ParametroTributario` vigente cargado (ADR-05) |
| Contador/Admin | mantiene parámetros | — |

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0001-01 | Calcular el valor de venta de cada línea: `round2(cantidad × valorUnitario − descuento)` | M |
| RF-0001-02 | Calcular **ISC por línea** según `sistemaIsc` (cat. 08): `01` al valor, `02` monto fijo, `03` precio de venta al público | M |
| RF-0001-03 | Calcular IGV con base `valorVenta + ISC` (el ISC integra la base del IGV) | M |
| RF-0001-04 | Calcular ICBPER = nº de bolsas × tarifa vigente; **no** integra la base del IGV; tributo 7152 | M |
| RF-0001-05 | Clasificar cada línea por afectación (cat. 07) en gravada / exonerada / inafecta / exportación / gratuita | M |
| RF-0001-06 | Las operaciones gratuitas **no suman** al importe total, usan `tipoPrecio=02` y agregan leyenda 1002 | M |
| RF-0001-07 | Totales = suma de líneas por tipo; importe total según RN-022 | M |
| RF-0001-08 | Generar la leyenda 1000 (monto en letras) | M |
| RF-0001-09 | Derivar `precioUnitario` (cat. 16 = 01) con tolerancia configurable (RN-023) | S |
| RF-0001-10 | Rechazar producto con `sistemaIsc` sin tasa/monto (`ISC_SIN_PARAMETRO`) | M |

## 5. Reglas de negocio aplicables
`RN-020`, `RN-021`, `RN-022`, `RN-023`, `RN-024`, `RN-030`, `RN-031`, `RN-032`, `RN-034`, `RN-035`, `RN-040`, `RN-041`, `RN-042`, `RN-043`, `RN-044`, `RN-045` (ver [`docs/03-modelo-dominio.md`](../../../docs/03-modelo-dominio.md)).

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO entrada | `comprobante.schema.json#/$defs/ItemRequest` |
| DTO salida | `comprobante.schema.json#/$defs/Totales`, `#/$defs/TributoLinea` |
| Catálogos | `common.schema.json#/$defs/SistemaIsc` (cat. 08), `AfectacionIgv` (cat. 07), `CodigoTributo` (cat. 05) |
| Trazabilidad | `TR-032…TR-043` (totales), `TR-052…TR-059` (tributos por ítem; **TR-056 = `cbc:TierRange`**) |
| Puerto | `IParametrosPort` (PT-17) |

## 7. Flujo principal
1. Obtener parámetros vigentes (IGV, tarifa ICBPER) a la fecha de emisión.
2. Por cada ítem: valor de venta → ISC → base IGV → IGV → ICBPER; acumular por afectación.
3. Aplicar descuentos globales y anticipos; calcular importe total.
4. Construir leyendas (1000, y 1002 si hay gratuitas).
- **A1** Producto con ISC sin parámetro → error `ISC_SIN_PARAMETRO` (no se calcula nada).
- **A2** `sistemaIsc = 03` → `NotImplemented` explícito hasta cerrar el ⚠ VERIFICAR.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-0001-01 | La factura de ejemplo (arroz, cerveza con ISC 17 % al valor, bolsas, muestra gratuita) | se calcula | `gravadas=1308.00`, `isc=18.36`, `igv=238.74`, `icbper=1.50`, `gratuitas=3.50`, `importeTotal=1566.60` | `examples/factura-valida.totales-esperados.json` · `npm run calculo` |
| CA-0001-02 | Cerveza 24 × 4.50 con ISC 17 % | se calcula la línea | `valor=108.00`, `ISC=18.36`, `baseIGV=126.36`, `IGV=22.74` | idem |
| CA-0001-03 | Producto con `sistemaIsc=01` sin `tasaIsc` | se valida el DTO | error de esquema | `INVALIDO-isc-sin-tasa.json` |
| CA-0001-04 | Ítem con afectación 13 y `tipoPrecio=01` | se valida el DTO | error de esquema (debe ser 02) | `INVALIDO-gratuita-precio-01.json` |
| CA-0001-05 | Cualquier comprobante | se suman las líneas | totales = suma de líneas, 0 diferencias de centavos en 10 000 casos generados | prueba de propiedades (T-0001-06) |

## 9. Requisitos no funcionales
Decimal exacto, nunca `float` (ADR-04). El cálculo es una **función pura** sin E/S (testeable sin BD ni red).

## 10. Riesgos y preguntas abiertas
- ⚠ VERIFICAR fórmula del ISC por PVP (Apéndice IV, lit. C del TUO IGV/ISC).
- ⚠ VERIFICAR tarifa ICBPER vigente (el ejemplo usa S/ 0.50) y tasa IGV 18 %.
- La tasa 17 % del ISC en el ejemplo es **ilustrativa**, no una tasa legal.
- ⚠ VERIFICAR **descuento global**: RN-022 lo resta después del IGV, lo que sólo es coherente con un descuento que *no* afecta la base del IGV (cat. 53 = 03, el usado en `factura-descuento-global-valida`). El descuento global que *sí* afecta la base (cat. 53 = 02) no está modelado.
- ⚠ VERIFICAR **anticipos** (RN-022, RN-033): el monto del anticipo (con IGV) se resta sólo del importe total y el IGV de la factura final se calcula sobre toda la venta (`factura-anticipo-valida`: `igv=302.40`). Si la guía SUNAT exige deducir antes la base del anticipo (cat. 53 = 04), quedaría `gravadas=1180.00`, `igv=212.40`, con el mismo `importeTotal=1392.40`.
