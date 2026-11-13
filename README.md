# ABC Software Corp · Facturación electrónica SUNAT (UBL 2.1) — Especificaciones Spec-First

Arquitectura de Software · UNAS.
- **Examen de medio curso (Fase 1):** esqueleto de especificaciones técnicas Spec-First, sin lógica de negocio.
- **Segundo Parcial (12/11/2026):** generación de **XML Invoice UBL 2.1 en Python, validado contra el XSD oficial de OASIS**, con 110 pruebas unitarias → [`docs/09-parcial2-generacion-xml.md`](docs/09-parcial2-generacion-xml.md).

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
│   ├── 07-matriz-trazabilidad.md/.csv   SUNAT ↔ UBL ↔ dominio ↔ DTO (83 filas; 74 verificadas contra el estándar vigente)
│   ├── 08-prompts-agente.md       Prompts P0…P8 para el agente Claude Code
│   └── 09-parcial2-generacion-xml.md   Segundo Parcial: caso, generador, pruebas y ejecución
├── specs/
│   ├── adr/                       Decisiones de arquitectura ADR-01…08 (una por archivo)
│   ├── contracts/                 Contratos (fuente de verdad)
│   │   ├── abc-facturacion-api.yaml    OpenAPI: 19 endpoints (EP-xx), 400/401/403 en todas las operaciones
│   │   ├── contratos-externos.md       SUNAT billService / OSE / consulta RUC
│   │   ├── schemas/                    JSON Schema (DTOs; importes como cadenas decimales)
│   │   ├── ubl-2.1/xsd/                XSD oficiales de OASIS (UBL-Invoice-2.1) con SHA-256
│   │   └── examples/                   Ejemplos válidos e INVALIDO-*, casos dorados (*.totales-esperados.json)
│   │       └── respuestas-sunat/ · kardex/ · legado/ · series/ · xml/   Respuestas SUNAT sintéticas, kardex, legado, series por dispositivo y factura XML generada
│   ├── features/                  Una carpeta por feature: spec.md + tasks.md (+ design.md)
│   │   ├── 0001-calculo-tributario/
│   │   ├── 0002-emision-factura-boleta/
│   │   ├── 0003-notas-credito-debito/
│   │   ├── 0004-resumen-diario-baja/
│   │   ├── 0005-almacen-kardex/
│   │   ├── 0006-migracion-legado/
│   │   ├── 0007-distribucion-windows-android/
│   │   ├── 0008-libros-electronicos/        Formatos PLE 14.1 y 12.1
│   │   └── 0009-generacion-xml-invoice/     Segundo Parcial
│   └── templates/                 spec-template.md · design-template.md · tasks-template.md
├── src/
│   ├── facturacion_xml/           Python: generador de factura XML UBL 2.1 + validación XSD (implementado)
│   └── Abc.* (Domain, Application, Infrastructure, Web, Host.*)   Capas .NET del diseño (solo README)
├── tests/                         Pruebas ejecutables de la especificación
│   └── generacion_xml/ (Python) · contratos/ · calculo/ · trazabilidad/ · documentacion/ (Node)
├── scripts/ · requirements.txt · .vscode/ · .editorconfig · .gitattributes
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
3. Recorrer las features **en orden** `0001 → 0009`: cada `spec.md` define *qué*, `design.md` *cómo* y `tasks.md` *en qué orden*.
4. Nada de `src/` se programa hasta que la spec de esa feature esté aprobada y sus pruebas de la Fase 1 estén en verde.
5. Para una feature nueva: copiar las plantillas de `specs/templates/`.

## Verificación

```bash
# Especificación (Node.js 20+)
npm install
npm test            # contratos + oráculos (cálculo, kardex, migración) + matriz + referencias de la documentación
npm run lint        # OpenAPI

# Segundo Parcial (Python 3.10+)
pip install -r requirements.txt
npm run xml:ejemplo # genera el XML y lo valida contra el XSD
npm run test:xml    # 110 pruebas unitarias
```

## Honestidad normativa
Lo marcado **⚠ VERIFICAR** o con fuente `NO-EST` no se contrastó con la norma vigente (fórmula del ISC por precio de venta al público, umbral de boleta, plazos de envío, tarifa ICBPER, tratamiento de descuentos globales y anticipos, estructura de partes en la guía actual, operaciones exactas de `billService`, guías de NC/ND y de resumen/baja). Están señalados en la sección de riesgos de cada spec; tienen tarea de cierre T-0001-05, T-0002-06, T-0003-03 y T-0004-03, y el resto aún no.
