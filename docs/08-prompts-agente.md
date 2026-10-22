# 08 · Prompts para el agente Claude Code (en orden)

Cada prompt es **un paso**. Se envían uno por uno y se espera el reporte antes del siguiente. Regla común: *Spec-First, sin lógica de negocio en `src/`*; todo cambio termina con `npm test` en verde y el reporte lista lo que quedó `⚠ VERIFICAR`.

| # | Objetivo | Tareas que cierra |
|---|---|---|
| P0 | Orientación y lectura de la estructura (sin modificar) | — |
| P1 | Cálculo tributario: más casos dorados | T-0001-04 |
| P2 | Emisión: ejemplos sintéticos de respuestas SUNAT | T-0002-04 |
| P3 | Notas: caso inválido de ND con motivo 05 | T-0003-02 |
| P4 | Resumen y baja: ejemplos de request y su prueba | (CA-0004-05) |
| P5 | Almacén: casos dorados de kardex y su oráculo | T-0005-03 |
| P6 | Migración: archivo legado de prueba y oráculo de normalización | T-0006-04 |
| P7 | Distribución: revisión de la spec (sin código) | — |
| P8 | Cierre: consistencia global y estado de tareas | — |

---

## P0 · Orientación
```
Lee README.md, docs/00-metodologia.md y la carpeta specs/ de este proyecto. Es la especificación Spec-First (SUNAT/UBL 2.1) del examen de Arquitectura de Software, organizada en docs/, specs/{adr,contracts,features,templates}, src/ y tests/. Resúmeme en 10 líneas: la estructura, el orden de trabajo por features (0001 a 0007) y qué tareas Fase 1 están pendientes en cada tasks.md. No modifiques ningún archivo.
```

## P1 · Feature 0001 — casos dorados de cálculo
```
Trabaja en specs/features/0001-calculo-tributario (tarea T-0001-04). Agrega casos dorados en specs/contracts/examples/ con su archivo *.totales-esperados.json: (a) venta exonerada, (b) inafecta, (c) exportación, (d) ISC con sistemaIsc 02 (monto fijo, catálogo 8), (e) descuento global, (f) anticipo. Calcula los totales a mano siguiendo RN-020 a RN-045 de docs/03-modelo-dominio.md y regístralos en el caso esperado; extiende tests/calculo/calculo-referencia.mjs para recorrer todos los casos. NO implementes el sistema ISC 03: debe seguir lanzando el error de fórmula pendiente. Marca [x] T-0001-04 en tasks.md solo si npm test pasa. Termina con npm test y dime qué quedó pendiente.
```

## P2 · Feature 0002 — respuestas SUNAT sintéticas
```
Trabaja en specs/features/0002-emision-factura-boleta (tarea T-0002-04). Crea specs/contracts/examples/respuestas-sunat/ con 4 JSON sintéticos del resultado de envío (aceptado código 0, aceptado con observación 4xxx, rechazado 2xxx/3xxx, servicio no disponible). Deben validar contra comprobante.schema.json#/$defs/ResultadoSunat o operaciones.schema.json#/$defs/Problema según corresponda, y llevar un campo "_nota": "ejemplo sintético, no oficial". Añade su validación a tests/contratos/validar-contratos.mjs. No inventes códigos de error reales: usa los rangos de docs/01-contexto-normativo.md §4. Termina con npm test.
```

## P3 · Feature 0003 — ND con motivo inválido
```
Trabaja en specs/features/0003-notas-credito-debito (tarea T-0003-02). Crea specs/contracts/examples/INVALIDO-nota-debito-motivo-05.json: una nota de débito (tipoDocumento 08) con motivoCodigo "05", que debe FALLAR el esquema porque el catálogo 10 solo admite 01-03. Confirma que el validador la reporta como inválida y marca [x] T-0003-02. Termina con npm test.
```

## P4 · Feature 0004 — ejemplos de resumen y baja
```
Trabaja en specs/features/0004-resumen-diario-baja. Crea ejemplos en specs/contracts/examples/: resumen-diario-valido.json, comunicacion-baja-valida.json e INVALIDO-comunicacion-baja-sin-documentos.json (criterio CA-0004-05). Extiende tests/contratos/validar-contratos.mjs para validarlos contra operaciones.schema.json (#/$defs/ResumenDiarioRequest y #/$defs/ComunicacionBajaRequest). Termina con npm test.
```

## P5 · Feature 0005 — kardex dorado
```
Trabaja en specs/features/0005-almacen-kardex (tarea T-0005-03). Crea specs/contracts/examples/kardex/ con un caso dorado: movimientos de un producto (ingreso 100, salida 30, ajuste -5, salida 20) y el saldo esperado tras cada uno. Crea tests/calculo/kardex-referencia.mjs que calcule el saldo acumulado y compare, e inclúyelo como script "kardex" en package.json y dentro de "npm test". Valida cada movimiento contra almacen-migracion.schema.json#/$defs/MovimientoInventario. Termina con npm test.
```

## P6 · Feature 0006 — legado sucio
```
Trabaja en specs/features/0006-migracion-legado (tarea T-0006-04). Crea specs/contracts/examples/legado/fichas-sucias.json con ~12 fichas del software antiguo (campos fecha, ingreso, salida, producto, nro_documento) que incluyan: fechas en dd/mm/aaaa y aaaa-mm-dd, cantidades con coma decimal, una ficha con ingreso y salida a la vez, una sin movimiento, nombres de producto con distinta escritura del mismo producto, y una ficha duplicada. Crea tests/calculo/migracion-referencia.mjs con las reglas RN-070 a RN-075 que clasifique cada ficha (migrada o rechazada con causa) y compruebe leidos = migrados + rechazados y la idempotencia al reprocesar. Valida las fichas contra almacen-migracion.schema.json#/$defs/FichaLegado. Agrégalo a "npm test". Termina con npm test.
```

## P7 · Feature 0007 — revisión de distribución
```
Revisa specs/features/0007-distribucion-windows-android y docs/06-empaquetado-distribucion.md frente a los ADR-01, ADR-02 y ADR-06. No escribas código. Dime: contradicciones, requisitos sin criterio de aceptación verificable, y riesgos que falten. Propón cambios concretos (archivo y texto) pero no los apliques todavía.
```

## P8 · Cierre
```
Cierre de fase: (1) ejecuta npm test y npm run lint; (2) revisa que cada tasks.md tenga el estado correcto de sus tareas según lo hecho; (3) enlista todo lo marcado ⚠ VERIFICAR o NO-EST que siga abierto, agrupado por feature; (4) confirma que README.md y docs/00-metodologia.md describen la estructura real. Corrige solo inconsistencias documentales y reporta el resultado final.
```
