# ADR-08 · Series exclusivas por dispositivo

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-11-06 |
| **Relacionada con** | RN-002, RN-051, RN-082, RN-083, [ADR-01](ADR-01-stack-dotnet-mvc.md), [feature 0007](../features/0007-distribucion-windows-android/spec.md) |

## Contexto
La distribución es un **MSI** (Windows) y un **APK** (Android). Cada instalación tiene su propia base SQLite y emite **sin conexión**. Si dos cajas usan la misma serie `F001`, ambas generan `F001-00000001` y SUNAT rechaza el segundo comprobante o se pierde la numeración consecutiva. La primera entrega no resolvía este caso (−2 puntos).

## Decisión
- Una serie `(tipoDocumento, serie)` pertenece a **un solo dispositivo**: `F001` en la caja 1, `F002` en la caja 2 (RN-082).
- Solo el **administrador** registra dispositivos y asigna series (EP-18). El registro rechaza una serie ya asignada con 409 `SERIE_DUPLICADA` (RN-083).
- El correlativo es independiente por `(dispositivo, serie)` y se reserva en la BD local del dispositivo; RN-002 (consecutivo) y RN-051 (un correlativo consumido no se reutiliza) no cambian.
- La emisión envía la cabecera `X-Dispositivo-Id`; una serie que no es del dispositivo responde 403 `SERIE_NO_ASIGNADA`.

## Alternativas consideradas
| Alternativa | Pros | Contras | Decisión |
|---|---|---|---|
| Servidor central de numeración | Una sola secuencia | Exige conexión: contradice emitir sin red (RN-050) | Descartada |
| Misma serie con **rangos** de correlativos por dispositivo | Una serie para todos | SUNAT exige correlativo consecutivo **sin saltos** por serie | Descartada |
| **Series exclusivas por dispositivo** | Funciona sin conexión; sin choques; sencillo de auditar | Más series que administrar | **Elegida** |

## Consecuencias
- Un dispositivo nuevo no puede emitir hasta que el administrador le asigne serie.
- ⚠ **Pendiente de decisión:** el Resumen Diario (`RC-AAAAMMDD-n`) y la baja (`RA-…`) usan un correlativo diario por emisor. Con varios dispositivos hay que decidir si los envía solo un dispositivo concentrador o si se reparte el `n`. Queda como pregunta abierta en la feature 0004 y 0007.
- Prueba ejecutable: `npm run series` (`specs/contracts/examples/series/`).
