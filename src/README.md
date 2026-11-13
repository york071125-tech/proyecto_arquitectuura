# src

| Carpeta | Contenido | Estado |
|---|---|---|
| `facturacion_xml/` | **Python** · generación de factura XML Invoice UBL 2.1 validada contra el XSD (Segundo Parcial, [feature 0009](../specs/features/0009-generacion-xml-invoice/spec.md)) | **Implementado** |
| `Abc.Domain`, `Abc.Application`, `Abc.Infrastructure`, `Abc.Web` | Capas del monolito .NET del diseño (ADR-01, ADR-02) | Solo README (diseño) |
| `Abc.Host.Windows`, `Abc.Host.Android` | Hosts MSI y APK (feature 0007) | Solo README (diseño) |

`facturacion_xml` es la **implementación de referencia** del puerto `IGeneradorUbl` (PT-11). Documentación: [`docs/09-parcial2-generacion-xml.md`](../docs/09-parcial2-generacion-xml.md).
