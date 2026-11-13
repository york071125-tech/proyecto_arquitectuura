# Spec 0006 · Migración de datos del software legado

| Campo | Valor |
|---|---|
| **ID** | 0006-migracion-legado |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-17 |
| **Depende de** | 0005 |
| **Diseño** | [`design.md`](design.md) · Detalle de mapeo: [`docs/05-migracion-legado.md`](../../../docs/05-migracion-legado.md) |

## 1. Contexto y problema
Toda la información histórica del software básico (fecha, ingreso, salida, producto, nro_documento) debe acoplarse a las nuevas entidades **sin perder trazabilidad**. El `nro_documento` legado es un número interno informal: **no** es una serie-correlativo SUNAT.

## 2. Objetivo y fuera de alcance
- **Objetivo**: importar las fichas como `MovimientoInventario` o como rechazos explicados, de forma idempotente y reversible en simulación.
- **Fuera de alcance**: reconstruir comprobantes SUNAT históricos; migración de costos (no existen en el legado).

## 3. Actores y precondiciones
Administrador. Archivo legado accesible en modo de sólo lectura (⚠ formato real por confirmar: CSV, Excel, DBF o SQLite).

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0006-01 | Leer fichas mediante `ILegacyReaderPort` sin modificar el origen | M |
| RF-0006-02 | Modo **SIMULACIÓN** que ejecuta todo el pipeline sin escribir | M |
| RF-0006-03 | Normalizar fecha (formatos tolerantes), cantidades (coma → punto) y nombre de producto | M |
| RF-0006-04 | Mapear `ingreso>0` → `INGRESO` y `salida>0` → `SALIDA` | M |
| RF-0006-05 | Resolver producto por nombre normalizado; crear si no existe (`pendienteTributario=true`); marcar ambiguos | M |
| RF-0006-06 | Guardar `nro_documento` como referencia `INTERNO_LEGADO` (nunca como comprobante SUNAT) | M |
| RF-0006-07 | Conservar la ficha original completa en `datosOriginales` | M |
| RF-0006-08 | Idempotencia por `origenLegacyId` | M |
| RF-0006-09 | Reporte del lote: `leidos = migrados + rechazados`, con causa y ficha por rechazo | M |
| RF-0006-10 | Guardar copia con hash SHA-256 del archivo origen | S |

## 5. Reglas de negocio aplicables
`RN-070`, `RN-071`, `RN-072`, `RN-073`, `RN-074`, `RN-075`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO | `almacen-migracion.schema.json#/$defs/FichaLegado`, `#/$defs/MigracionRequest`, `#/$defs/LoteMigracionResponse` |
| Endpoints | EP-15 (`POST /migracion/lotes`, `GET /migracion/lotes/{id}`) |
| Puerto | PT-03 `IMigrarLegado`, PT-16 `ILegacyReaderPort` |

## 7. Flujo principal y alternos
Ver el pipeline en [`design.md`](design.md) §4.
- **A1** Fecha inválida → rechazo `FECHA_INVALIDA`.
- **A2** Ingreso y salida a la vez → rechazo `INGRESO_Y_SALIDA_A_LA_VEZ`.
- **A3** Producto ambiguo → rechazo `PRODUCTO_AMBIGUO` hasta resolver con `mapeoProductos`.
- **A4** Falla a mitad de lote → *rollback* completo.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Prueba |
|---|---|---|---|---|
| CA-0006-01 | Un lote cualquiera | termina | `leidos = migrados + rechazados` | A1 de `docs/05-migracion-legado.md` |
| CA-0006-02 | El mismo archivo dos veces | se re-ejecuta | 0 migraciones nuevas | A2 |
| CA-0006-03 | Por producto | se compara | Σ ingresos − Σ salidas del kardex = saldo de las fichas | A3 |
| CA-0006-04 | Cualquier ficha | se migra | nunca aparece como comprobante SUNAT | A4 |
| CA-0006-05 | Cada rechazo | se consulta | trae `idOrigen`, `causa` y `fichaOriginal` | A5 |
| CA-0006-06 | Producto creado por la migración | se intenta facturar | bloqueado hasta completar afectación IGV/ISC | A6 |

CA-0006-01, 02, 04 y 05 se prueban con [`fichas-sucias.json`](../../contracts/examples/legado/fichas-sucias.json) y su `.esperado.json` (`npm run migracion`); CA-0006-03 sólo contra saldos calculados a mano (la prueba de conservación es T-0006-08) y CA-0006-06 queda para T-0006-09.

## 9. Requisitos no funcionales
Migrar 100 000 fichas en menos de 2 minutos; el origen nunca se modifica.

## 10. Riesgos y preguntas abiertas
⚠ Formato real del archivo legado; nombres inconsistentes de producto (se resuelve con `mapeoProductos`); ausencia de costos.

- ⚠ **RN-075 frente al reproceso**: el pipeline tiene un tercer destino («ya migrada → omitir») que `leidos = migrados + rechazados` no contempla. El oráculo cuenta como *migrada* toda ficha cuyo movimiento existe en el kardex (nuevo o de una corrida anterior, incluida una ficha duplicada) y verifica aparte que el reproceso cree 0 movimientos nuevos. `LoteMigracionResponse` no informa cuántos movimientos son nuevos y no existe la causa `DUPLICADO`: decidir si se agregan.
- ⚠ **Clave sin PK**: si el legado no trae clave propia, `origenLegacyId` es el SHA-256 de la fila normalizada; dos movimientos legítimos idénticos (misma fecha, producto, cantidades y `nro_documento`) se fusionarían. Confirmar con la muestra real (T-0006-03).
- `PRODUCTO_AMBIGUO` aún no se prueba: exige un maestro de productos previo o `mapeoProductos` (T-0006-06).
