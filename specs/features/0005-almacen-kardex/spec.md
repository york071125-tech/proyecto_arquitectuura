# Spec 0005 · Almacén: movimientos y kardex

| Campo | Valor |
|---|---|
| **ID** | 0005-almacen-kardex |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-14, CU-15, CU-16 |
| **Depende de** | — (la migración 0006 y las notas 0003 lo consumen) |

## 1. Contexto y problema
El software actual registra fichas sencillas (fecha, ingreso, salida, producto, número de documento interno). Con la facturación electrónica, cada venta debe descontar stock y cada devolución reponerlo, con **trazabilidad** hacia el comprobante. La RS 234-2006/SUNAT (libros y registros) respalda el **Registro de Inventario Permanente**.

## 2. Objetivo y fuera de alcance
- **Objetivo**: registrar ingresos, salidas y ajustes, y consultar el kardex por producto con saldo.
- **Fuera de alcance**: multialmacén, lotes/series, costeo avanzado (método por definir con contabilidad, RN-062).

## 3. Actores y precondiciones
Almacenero (manual); evento `ComprobanteAceptado` (automático); producto existente en el maestro.

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0005-01 | Registrar movimiento con fecha, producto, cantidad > 0, tipo y documento de referencia | M |
| RF-0005-02 | Tipos: `INGRESO`, `SALIDA`, `AJUSTE` | M |
| RF-0005-03 | Al aceptarse un comprobante con ítems inventariables, generar `SALIDA` por ítem | M |
| RF-0005-04 | Al aceptarse una NC por devolución, generar `INGRESO` por ítem | S |
| RF-0005-05 | Consultar kardex por producto y rango de fechas con saldo acumulado | M |
| RF-0005-06 | No permitir saldo negativo salvo parámetro explícito | S |
| RF-0005-07 | Movimiento inmutable: se corrige con un `AJUSTE`, no se edita | M |
| RF-0005-08 | Referencia al documento: `COMPROBANTE_SUNAT`, `INTERNO_LEGADO` o `AJUSTE_MANUAL` | M |
| RF-0005-09 | Un `AJUSTE` declara `sentido` (`AUMENTO` o `DISMINUCION`); `INGRESO` y `SALIDA` no lo llevan. La cantidad sigue siendo > 0 (RN-063) | M |

## 5. Reglas de negocio aplicables
`RN-060`, `RN-061`, `RN-062`, `RN-063`, `RN-070`, `RN-072`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO | `almacen-migracion.schema.json#/$defs/MovimientoInventario` |
| Endpoints | EP-14 (`POST /almacen/movimientos`, `GET /almacen/kardex`) |
| Puerto | PT-04 `IRegistrarMovimiento` |

## 7. Flujo principal y alternos
1. Llega un movimiento manual o un evento `ComprobanteAceptado`.
2. Se valida producto, cantidad y saldo.
3. Se persiste el movimiento inmutable.
4. El kardex recalcula el saldo acumulado por producto.
- **A1** Saldo insuficiente → `ESTADO_NO_PERMITIDO` (según RF-0005-06).
- **A2** Producto `pendienteTributario` → permitido en almacén, bloqueado para facturar.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-0005-01 | Ingreso 100 y salida 30 del mismo producto | se consulta el kardex | saldo final 70 | `examples/kardex/kardex-arroz.json` (pasos 1–2) · `npm run kardex` |
| CA-0005-02 | Factura aceptada con 10 sacos de arroz | llega el evento | una `SALIDA` de 10 con referencia al comprobante | integración con 0002 |
| CA-0005-03 | Movimiento con cantidad 0 o negativa | se valida | error | prueba de esquema/aplicación |
| CA-0005-04 | Se intenta editar un movimiento | se solicita | rechazado; sólo `AJUSTE` | prueba de aplicación |
| CA-0005-05 | Ingreso 100, salida 30, `AJUSTE` `DISMINUCION` 5 y salida 20 del mismo producto | se consulta el kardex | saldos 100, 70, 65 y 45 | `examples/kardex/kardex-arroz.json` · `npm run kardex` |
| CA-0005-06 | `AJUSTE` sin `sentido` | se valida | error de esquema | `INVALIDO-movimiento-ajuste-sin-sentido.json` |

## 9. Requisitos no funcionales
Consulta de kardex < 1 s para 100 000 movimientos (índice por producto y fecha).

## 10. Riesgos y preguntas abiertas
- ⚠ Definir con contabilidad el método de valorización (costo promedio u otro) — RN-062.
- ⚠ ¿El legado trae costos? No figuran en el enunciado.
