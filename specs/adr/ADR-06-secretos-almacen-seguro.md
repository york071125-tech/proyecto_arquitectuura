# ADR-06 · Secretos fuera de la base de datos plana

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | specs/contracts/abc-facturacion-api.yaml (EP-03), docs/06-empaquetado-distribucion.md §5 |

## Contexto
La clave SOL y el certificado .pfx permiten emitir a nombre de la empresa; su filtración es crítica.

## Decisión
Puerto `ISecretStorePort` (PT-15): **DPAPI** en Windows y **Android Keystore** en Android. Los secretos nunca viajan en DTO de lectura ni en logs (EP-03 es sólo de escritura).

## Alternativas consideradas
- Guardarlos en SQLite cifrado con clave en archivo: la clave queda expuesta.
- Pedirlos en cada emisión: inviable para el vendedor.

## Consecuencias
- Cada plataforma implementa su adaptador; el núcleo no cambia.
- Rotación de certificado = nueva carga por EP-03.
