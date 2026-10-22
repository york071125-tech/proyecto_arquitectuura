# ADR-02 · Monolito modular con puertos desde el día 1

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | docs/04-arquitectura.md §1, §5, §6 |

## Contexto
La gerencia pide MVC monolítico hoy, pero desacoplado para migrar a Hexagonal/Clean y luego a microservicios sin reescribir.

## Decisión
Un solo despliegue, código partido en `Domain`, `Application` (casos de uso + puertos) e `Infrastructure`/`Web` (adaptadores). MVC es **un adaptador de entrada** más. Regla de dependencias verificable con tests de arquitectura.

## Alternativas consideradas
- MVC clásico con lógica en controladores/servicios acoplados a EF: rápido, pero obliga a reescribir al migrar.
- Microservicios desde el inicio: sobrecoste injustificado para una empresa mediana.

## Consecuencias
- Los contratos de entrada son los JSON Schema: sirven a MVC, REST y a futuros microservicios.
- Cada bounded context ya está en su módulo: son los cortes naturales a microservicios.
