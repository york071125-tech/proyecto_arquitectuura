# ADR-07 · El XML UBL se construye como objetos o árbol, nunca con plantillas, y se valida contra el XSD

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-11-06 |
| **Relacionada con** | RN-088, [feature 0009](../features/0009-generacion-xml-invoice/spec.md), [ADR-01](ADR-01-stack-dotnet-mvc.md), `specs/contracts/ubl-2.1/` |

## Contexto
El sistema debe emitir cinco documentos UBL distintos: `Invoice`, `CreditNote`, `DebitNote` (esquemas OASIS UBL 2.1) y `SummaryDocuments`, `VoidedDocuments` (esquemas propios de SUNAT). La primera entrega los describía con **plantillas de texto** («Plantillas Invoice», T-0002-13, T-0003-07, T-0004-08). Las plantillas duplican la estructura en cada documento y fallan en silencio: orden de elementos, espacios de nombres, escape de `&` y de tildes, atributos obligatorios. El ingeniero lo calificó como el error más grave de la entrega (−8 puntos).

## Decisión
1. **Prohibido generar XML concatenando o interpolando texto.** El documento se construye como un modelo de objetos o un árbol de elementos y lo serializa una biblioteca XML, que escapa y ordena.
2. **Antes de firmar** (y antes de enviar) el XML se valida contra el **XSD oficial** (RN-088). Un XML inválido nunca se firma.
3. **.NET (sistema de producción):** clases generadas desde los XSD oficiales con `XmlSchemaClassGenerator` (o `xsd.exe`) y serializadas con `XmlSerializer`. Un único `UblXmlAdapter` sirve a `Invoice`, `CreditNote` y `DebitNote`; las clases de resumen y baja se generan desde los XSD de SUNAT.
4. **Implementación de referencia del Segundo Parcial (Python):** árbol de elementos con `lxml` y validación contra `UBL-Invoice-2.1.xsd`. Los XSD oficiales se versionan en `specs/contracts/ubl-2.1/xsd/` con su SHA-256.
5. El XSD valida **estructura**, no las reglas tributarias de SUNAT (cálculos, catálogos, obligatoriedades condicionales): esas siguen en el dominio y en la matriz de trazabilidad.

## Alternativas consideradas
| Alternativa | Pros | Contras | Decisión |
|---|---|---|---|
| Plantillas de texto | Rápidas de escribir | Errores silenciosos; una plantilla por documento; sin validación | **Descartada** |
| Clases generadas desde el XSD (.NET) | Imposible emitir una etiqueta inexistente; un adaptador para tres documentos | Requiere el generador en el *build* | **Elegida para .NET** |
| `xsdata` en Python (clases generadas) | Mismo principio en Python | Medido en esta entrega: genera **16 archivos, ~69 000 líneas y 3 MB** solo para `Invoice`, y su cadena de herramientas fue frágil (versión de `ruff` incompatible) | Descartada por costo y por no ser explicable |
| Árbol `lxml` + validación XSD (Python) | Pequeño, explicable, escapa y respeta namespaces | Los nombres de etiqueta los escribe una persona | **Elegida para la referencia**; el XSD atrapa cualquier error de nombre u orden |

## Consecuencias
- Cambian las tareas T-0002-13, T-0003-07 y T-0004-08: «adaptador por clases generadas», no «plantilla».
- El *build* valida un XML de ejemplo contra el XSD en cada ejecución de pruebas (`CA-0002-07`).
- Los XSD oficiales son datos de entrada versionados; actualizarlos exige volver a ejecutar las pruebas.
