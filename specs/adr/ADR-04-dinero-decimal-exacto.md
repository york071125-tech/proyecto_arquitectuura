# ADR-04 · Dinero con decimales exactos y redondeo por línea

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | docs/03-modelo-dominio.md §4.2 |

## Contexto
SUNAT valida montos a 2 decimales y precios/cantidades a hasta 10 decimales; diferencias de centavos provocan rechazo.

## Decisión
Tipo `decimal` (nunca `float/double`). Montos n(12,2); cantidades y precios unitarios n(12,10). Redondeo half-up **por línea**; totales = suma de líneas (RN-021, RN-022, RN-024).

## Alternativas consideradas
- Enteros en céntimos: evita decimales pero complica precios con 10 decimales.
- Redondear sólo en el total: contradice la guía XML (los totales deben cuadrar con las líneas).

## Consecuencias
- JSON Schema no expresa decimales exactos con fiabilidad: la regla se valida en la aplicación.
- Criterio: 0 diferencias de centavos en 10 000 comprobantes de prueba.
