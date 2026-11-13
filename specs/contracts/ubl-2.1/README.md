# Esquemas XSD oficiales de UBL 2.1 (OASIS)

Esta carpeta contiene, **sin modificar**, el esquema `Invoice` de UBL 2.1 y los módulos que importa. Es el archivo exacto contra el que se valida el XML del Segundo Parcial.

## Identificación

| Dato | Valor |
|---|---|
| Estándar | OASIS Universal Business Language (UBL) **2.1 OS** (ISO/IEC 19845:2015) |
| Esquema principal | `xsd/maindoc/UBL-Invoice-2.1.xsd` |
| Namespace del documento | `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2` |
| Release | 04-11-2013 (según el encabezado del propio archivo) |
| Origen | <https://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/> (sitio oficial de OASIS) |
| Descargado | 06-11-2026 |
| Archivos | 14 (`maindoc/` ×1 y `common/` ×13), 2,8 MB |
| Integridad | SHA-256 de cada archivo en [`xsd/SHA256SUMS.txt`](xsd/SHA256SUMS.txt) |

Solo se descargaron el esquema `Invoice` y sus dependencias directas e indirectas (`xsd:import`), no el paquete completo de UBL (58 MB).

## Verificar la integridad

```bash
cd specs/contracts/ubl-2.1/xsd
sha256sum -c SHA256SUMS.txt        # Windows (Git Bash) o Linux
```

## Alcance y límites
- El XSD define **estructura**: nombres de elementos, orden, cardinalidad y tipos. **No** contiene las reglas tributarias de SUNAT (cálculos, catálogos, obligatoriedades condicionales); esas están en `docs/03-modelo-dominio.md` y `docs/07-matriz-trazabilidad.md`.
- SUNAT usa este mismo esquema con `ext:UBLExtensions` (donde va la firma digital). La firma no forma parte del Segundo Parcial.
- `CreditNote`, `DebitNote` (también de OASIS) y `SummaryDocuments`/`VoidedDocuments` (esquemas propios de SUNAT) **no** se incluyen: pertenecen a otras features.

## Aviso de copyright
Copyright © OASIS Open 2013. All Rights Reserved. Los archivos conservan el encabezado original de OASIS. Su uso y copia se rige por la política de propiedad intelectual de OASIS (<https://www.oasis-open.org/policies-guidelines/ipr/>).
