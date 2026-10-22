# tests

Pruebas ejecutables **de la especificación** (la de código llegará con `src/`). Todo corre con `npm test`.

| Carpeta | Qué prueba | Comando |
|---|---|---|
| `contratos/` | Los JSON Schema compilan; ejemplos válidos pasan e inválidos fallan; respuestas sintéticas de SUNAT/OSE (`examples/respuestas-sunat/`); RUC módulo 11 | `npm run validar` |
| `calculo/` | Oráculo de cálculo IGV/ISC/ICBPER (decimal exacto) contra cada caso dorado `examples/*.totales-esperados.json` (feature 0001) | `npm run calculo` |
| `calculo/` | Oráculo del kardex: valida cada movimiento y el saldo acumulado de `examples/kardex/*.json` (feature 0005, RN-063) | `npm run kardex` |
| `calculo/` | Oráculo de la migración: clasifica las fichas de `examples/legado/*.json`, comprueba `leidos = migrados + rechazados` y la idempotencia al reprocesar (feature 0006, RN-070…RN-075) | `npm run migracion` |
| `trazabilidad/` | Genera y verifica la matriz SUNAT ↔ UBL (RN definidas; filas contrastadas con la guía) | `npm run matriz` · `npm run verificar-matriz -- guia.txt` |
| `documentacion/` | Enlaces relativos existentes y referencias RN, EP, PT, CU, ADR y T-NNNN-nn definidas | `npm run docs` |
| (a crear) `arquitectura/` | Reglas de dependencia entre capas (NetArchTest) | — |

API: `npm run lint` valida `specs/contracts/abc-facturacion-api.yaml`.
