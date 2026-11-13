# Abc.Domain

**Núcleo del negocio. No referencia nada externo.** (ADR-02)

- Entidades y agregados: `Comprobante`, `ItemComprobante`, `SerieComprobante`, `Producto`, `Cliente`, `MovimientoInventario`.
- Value objects: `Dinero` (decimal, ADR-04), `Ruc`, `Ubigeo`.
- Calculadoras y reglas RN-xxx: IGV, ISC (estrategias cat. 08), ICBPER, totales.
- Especificado en: `specs/features/0001-calculo-tributario` y `docs/03-modelo-dominio.md`.

Estado: **sin implementar** (fase Spec-First).
