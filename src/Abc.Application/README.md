# Abc.Application

**Casos de uso y puertos.** Sólo referencia `Abc.Domain`.

- Casos de uso: `EmitirComprobante`, `EmitirNota`, `EnviarResumenDiario`, `EnviarBaja`, `RegistrarMovimiento`, `MigrarLegado`.
- Puertos de entrada: PT-01…PT-04. Puertos de salida: PT-10…PT-17 (ver `docs/04-arquitectura.md` §4.1).
- DTOs = los JSON Schema de `specs/contracts/schemas`.

Estado: **sin implementar**.
