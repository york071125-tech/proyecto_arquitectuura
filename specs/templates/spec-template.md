# Spec NNNN · <Nombre de la feature>

| Campo | Valor |
|---|---|
| **ID** | NNNN-nombre-corto |
| **Estado** | Borrador · En revisión · Aprobada · Implementada |
| **Casos de uso** | CU-xx, CU-yy (ver `docs/02-casos-de-uso.md`) |
| **Depende de** | Specs previas (NNNN) |
| **Autor / Fecha** | |

## 1. Contexto y problema
¿Qué dolor del negocio resuelve? ¿Qué norma lo exige? (cita RS/catálogo).

## 2. Objetivo y fuera de alcance
- **Objetivo** (una frase medible).
- **Fuera de alcance** (lista explícita).

## 3. Actores y precondiciones
| Actor | Rol | Precondición |
|---|---|---|

## 4. Requisitos funcionales
| ID | Requisito (verificable, uno por fila) | Prioridad (M/S/C) |
|---|---|---|
| RF-NNNN-01 | | M |

## 5. Reglas de negocio aplicables
Enlazar `RN-xxx` de `docs/03-modelo-dominio.md`. No redefinir reglas aquí: **referenciarlas**.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO de entrada | `specs/contracts/schemas/…#/$defs/…` |
| DTO de salida | |
| Endpoint(s) | `EP-xx` en `specs/contracts/abc-facturacion-api.yaml` |
| Puertos hexagonales | `PT-xx` (ver `docs/04-arquitectura.md`) |
| Filas de trazabilidad | `TR-xxx` (ver `docs/07-matriz-trazabilidad.md`) |

## 7. Flujo principal y alternos
1. …
- **A1** …

## 8. Criterios de aceptación (Dado / Cuando / Entonces)
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-NNNN-01 | | | | `specs/contracts/examples/…` |

## 9. Requisitos no funcionales
Rendimiento, seguridad, offline, auditoría (con criterio medible).

## 10. Riesgos, supuestos y preguntas abiertas
Marcar `⚠ VERIFICAR` lo que no esté confirmado contra fuente oficial.
