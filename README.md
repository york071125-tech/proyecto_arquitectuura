# ABC Software Corp · Facturación electrónica SUNAT (UBL 2.1) — Especificaciones Spec-First

Examen de medio curso · Arquitectura de Software · UNAS. Fase 1: **esqueleto de especificaciones técnicas** (sin lógica de negocio).

> Para evaluación rápida, consultar [`ENTREGA.md`](ENTREGA.md), que enlaza directamente los cuatro entregables solicitados y los comandos de verificación.

## Estructura

```
proyecto_arquitectuura/
├── docs/                          Documentación de contexto y análisis
│   ├── 00-metodologia.md          Método Spec-First, convenciones e índice de ADR
│   ├── 01-contexto-normativo.md   RS 097-2012, RS 234-2006, catálogos SUNAT (catálogo 8)
│   ├── 02-casos-de-uso.md         Actores, 22 casos de uso, benchmark Nubefact
│   ├── 03-modelo-dominio.md       Entidades, estados y reglas RN-xxx
│   ├── 04-arquitectura.md         MVC monolítico → Hexagonal → microservicios (diagramas)
│   ├── 05-migracion-legado.md     Mapeo de fichas legadas y criterios de aceptación
│   ├── 06-empaquetado-distribucion.md   MSI (Windows) y APK (Android)
│   ├── 07-matriz-trazabilidad.md/.csv   SUNAT ↔ UBL ↔ dominio ↔ DTO (80 filas)
│   └── 08-prompts-agente.md       Prompts P0…P8 para el agente Claude Code
├── specs/
│   ├── adr/                       Decisiones de arquitectura ADR-01…06 (una por archivo)
│   ├── contracts/                 Contratos (fuente de verdad)
│   │   ├── abc-facturacion-api.yaml    OpenAPI: 17 endpoints (EP-xx)
│   │   ├── contratos-externos.md       SUNAT billService / OSE / consulta RUC
│   │   ├── schemas/                    JSON Schema (DTOs)
│   │   └── examples/                   Ejemplos válidos e INVALIDO-*, casos dorados (*.totales-esperados.json)
│   │       └── respuestas-sunat/ · kardex/ · legado/   Respuestas SUNAT sintéticas, kardex y fichas del legado
│   ├── features/                  Una carpeta por feature: spec.md + tasks.md (+ design.md)
│   │   ├── 0001-calculo-tributario/
│   │   ├── 0002-emision-factura-boleta/
│   │   ├── 0003-notas-credito-debito/
│   │   ├── 0004-resumen-diario-baja/
│   │   ├── 0005-almacen-kardex/
│   │   ├── 0006-migracion-legado/
│   │   └── 0007-distribucion-windows-android/
│   └── templates/                 spec-template.md · design-template.md · tasks-template.md
├── src/                           Capas del monolito (sólo README por ahora)
│   ├── Abc.Domain · Abc.Application · Abc.Infrastructure · Abc.Web
│   └── Abc.Host.Windows · Abc.Host.Android
├── tests/                         Pruebas ejecutables de la especificación
│   └── contratos/ · calculo/ · trazabilidad/ · documentacion/
├── package.json                   Scripts: validar · calculo · lotes · kardex · migracion · matriz · verificar-matriz · docs · lint · test
└── README.md
```

## Entregables del examen → dónde están

| Entregable (sección 4 del enunciado) | Ubicación |
|---|---|
| Modelo de Dominio y Contratos (DTOs / Schemas) | `docs/03-modelo-dominio.md` + `specs/contracts/schemas/` |
| Diagramas de Arquitectura MVC con visión a Hexagonal | `docs/04-arquitectura.md` |
| Especificación de Endpoints / Servicios (Contratos API) | `specs/contracts/abc-facturacion-api.yaml` + `contratos-externos.md` |
| Matriz de Trazabilidad Normativa (SUNAT ↔ UBL) | `docs/07-matriz-trazabilidad.md` y `.csv` |

## Orden de trabajo (Spec-First)

1. Leer `docs/00-metodologia.md` → `01` → `02` → `03`.
2. Revisar los contratos en `specs/contracts/` y las decisiones en `specs/adr/`.
3. Recorrer las features **en orden** `0001 → 0007`: cada `spec.md` define *qué*, `design.md` *cómo* y `tasks.md` *en qué orden*.
4. Nada de `src/` se programa hasta que la spec de esa feature esté aprobada y sus pruebas de la Fase 1 estén en verde.
5. Para una feature nueva: copiar las plantillas de `specs/templates/`.

## Verificación

```bash
npm install
npm test            # contratos + oráculos (cálculo, kardex, migración) + matriz + referencias de la documentación
npm run lint        # OpenAPI
```

## Honestidad normativa
Lo marcado **⚠ VERIFICAR** o con fuente `NO-EST` no se contrastó con la norma vigente (fórmula del ISC por precio de venta al público, umbral de boleta, plazos de envío, tarifa ICBPER, tratamiento de descuentos globales y anticipos, estructura de partes en la guía actual, operaciones exactas de `billService`, guías de NC/ND y de resumen/baja). Están señalados en la sección de riesgos de cada spec; tienen tarea de cierre T-0001-05, T-0002-06, T-0003-03 y T-0004-03, y el resto aún no.
