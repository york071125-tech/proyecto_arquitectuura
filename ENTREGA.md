# Guía de entrega · Examen de Arquitectura de Software

**Caso:** ABC Software Corp · Facturación electrónica SUNAT / UBL 2.1  
**Alcance:** primera fase Spec-First — esqueleto de especificaciones técnicas  
**Fecha del enunciado:** 19 de octubre de 2026

## Entregables solicitados

| Entregable | Evidencia principal |
|---|---|
| Modelo de Dominio y Contratos (DTOs / Schemas) | [`docs/03-modelo-dominio.md`](docs/03-modelo-dominio.md) y [`specs/contracts/schemas/`](specs/contracts/schemas/) |
| Diagramas de Arquitectura MVC con visión Hexagonal | [`docs/04-arquitectura.md`](docs/04-arquitectura.md) y [`specs/adr/`](specs/adr/) |
| Especificación de Endpoints / Servicios | [`specs/contracts/abc-facturacion-api.yaml`](specs/contracts/abc-facturacion-api.yaml) |
| Matriz de Trazabilidad Normativa SUNAT–UBL | [`docs/07-matriz-trazabilidad.md`](docs/07-matriz-trazabilidad.md) y [`docs/07-matriz-trazabilidad.csv`](docs/07-matriz-trazabilidad.csv) |

## Lectura recomendada

1. [`README.md`](README.md): alcance y estructura completa.
2. [`docs/00-metodologia.md`](docs/00-metodologia.md): método, convenciones y orden de lectura.
3. Los cuatro entregables de la tabla anterior.
4. [`specs/features/`](specs/features/): requisitos, criterios de aceptación, diseños y tareas por funcionalidad.

## Verificación reproducible

Requiere Node.js 20 o posterior.

```bash
npm ci
npm test
npm run lint
```

Resultado esperado: contratos y ejemplos válidos/inválidos verificados; oráculos de cálculo, tickets SUNAT, kardex y migración aprobados; matriz de 83 filas (74 verificadas contra el estándar vigente de SUNAT) y referencias documentales consistentes; OpenAPI válido sin advertencias.

## Segundo Parcial: generación de XML Invoice UBL 2.1

| Requisito | Evidencia |
|---|---|
| Descripción del caso | [`docs/09-parcial2-generacion-xml.md`](docs/09-parcial2-generacion-xml.md) §1 |
| Generación de XML desde Invoice XSD 2.1 (Python) | [`src/facturacion_xml/`](src/facturacion_xml/) |
| XSD oficial usado | [`specs/contracts/ubl-2.1/`](specs/contracts/ubl-2.1/README.md) |
| Pruebas unitarias de generación | [`tests/generacion_xml/`](tests/generacion_xml/) |
| XML generado | [`specs/contracts/examples/xml/factura-ejemplo.xml`](specs/contracts/examples/xml/factura-ejemplo.xml) |

```bash
pip install -r requirements.txt           # una sola dependencia: lxml
python scripts/generar_factura_ejemplo.py  # genera el XML y lo valida contra el XSD
python -m unittest discover -s tests/generacion_xml -t . -v
```

## Nota de alcance

Esta entrega comprende la primera fase (especificaciones técnicas Spec-First, corregida según las observaciones del ingeniero) y el Segundo Parcial (XML Invoice UBL 2.1). No incluye los Parciales 3 y 4 (Odoo monolítico, Docker, addon) ni el examen final. Las marcas `⚠ VERIFICAR` y `NO-EST` identifican conscientemente datos que requieren contraste adicional con fuentes oficiales o insumos reales antes de implementar o usar en producción. No representan afirmaciones normativas no verificadas.
