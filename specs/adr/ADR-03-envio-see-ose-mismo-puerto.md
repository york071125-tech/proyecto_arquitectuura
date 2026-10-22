# ADR-03 · Modos de emisión SEE-Del contribuyente y OSE tras el mismo puerto

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | specs/contracts/contratos-externos.md, docs/01-contexto-normativo.md |

## Contexto
RS 097-2012/SUNAT crea el SEE desarrollado desde los sistemas del contribuyente y admite enviar a un OSE. El cliente podría cambiar de modo.

## Decisión
Puerto `IEnvioComprobantePort` (PT-13) con dos adaptadores: `SunatBillServiceAdapter` (SOAP/WS-Security) y `OseAdapter`. Se elige por configuración del emisor (`modoEmision`).

## Alternativas consideradas
- Integrar sólo SUNAT: simple, pero bloquea a clientes con OSE.
- Integrar sólo un OSE: acopla el producto a un proveedor.

## Consecuencias
- El dominio no distingue SUNAT de OSE.
- Se necesita un mock del puerto para pruebas de contrato.
