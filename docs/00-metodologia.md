# 00 · Metodología Spec-First y convenciones

> Proyecto: **Facturación electrónica y almacén para ABC Software Corp** (Perú · SUNAT · UBL 2.1).
> Fase 1 del examen: *esqueleto de especificaciones técnicas*. **No hay lógica de negocio implementada**; sólo reglas, contratos y validaciones.

## 1. Qué significa Spec-First aquí

1. La **especificación es la fuente de verdad**; el código se deriva de ella.
2. Cada feature recorre el mismo ciclo, con una plantilla por etapa (`specs/templates/`):

| Etapa | Artefacto | Responde |
|---|---|---|
| Qué | `spec.md` (plantilla `spec-template.md`) | ¿Qué debe hacer y cómo se acepta? |
| Cómo | `design.md` (plantilla `design-template.md`) | ¿Qué componentes, puertos y secuencia? |
| Orden | `tasks.md` (plantilla `tasks-template.md`) | ¿En qué orden y con qué verificación? |
| Decisiones | `specs/adr/ADR-xx-*.md` | ¿Por qué se eligió así? |
| Contratos | `specs/contracts/` | ¿Qué forma exacta tienen los datos y servicios? |
| Verificación | `tests/` + `specs/contracts/examples/` (`npm test`) | ¿Cómo se demuestra que la spec se cumple? |

3. **Definition of Done de una spec**: identificador estable, criterios de aceptación verificables (con ejemplo válido e inválido) y enlace a su fuente normativa.
4. **Uso de IA**: la IA redacta y cruza; las reglas normativas se verifican contra fuentes oficiales (SUNAT/OASIS). Lo no confirmado queda marcado `⚠ VERIFICAR`.

## 2. Orden de lectura

| Paso | Archivo | Pregunta que responde |
|---|---|---|
| 1 | [`01-contexto-normativo.md`](01-contexto-normativo.md) | ¿Qué exige la ley y de dónde sale cada exigencia? |
| 2 | [`02-casos-de-uso.md`](02-casos-de-uso.md) | ¿Qué debe poder hacer el sistema? |
| 3 | [`03-modelo-dominio.md`](03-modelo-dominio.md) | ¿Qué entidades, invariantes y reglas existen? |
| 4 | [`../specs/contracts/`](../specs/contracts/) | ¿Qué forma exacta tienen los datos y servicios? |
| 5 | [`04-arquitectura.md`](04-arquitectura.md) | ¿Cómo se organiza para migrar a Hexagonal sin reescribir? |
| 6 | [`07-matriz-trazabilidad.md`](07-matriz-trazabilidad.md) | ¿Cada dato SUNAT dónde vive en UBL, dominio y DTO? |
| 7 | [`05-migracion-legado.md`](05-migracion-legado.md) | ¿Cómo se conserva la trazabilidad histórica? |
| 8 | [`06-empaquetado-distribucion.md`](06-empaquetado-distribucion.md) | ¿Cómo se entrega en Windows (MSI) y Android (APK)? |
| 9 | [`../specs/features/`](../specs/features/) | ¿Cómo se construye, feature por feature? |

## 3. Convención de identificadores

| Prefijo | Significado | Dónde se define |
|---|---|---|
| `CU-nn` | Caso de uso | `docs/02-casos-de-uso.md` |
| `RN-nnn` | Regla de negocio / validación | `docs/01-…` (RN-001…007) y `docs/03-…` |
| `EP-nn` | Endpoint o servicio | `specs/contracts/abc-facturacion-api.yaml` |
| `PT-nn` | Puerto hexagonal | `docs/04-arquitectura.md` §4.1 |
| `TR-nnn` | Fila de la matriz de trazabilidad | `docs/07-matriz-trazabilidad.md` |
| `ADR-nn` | Decisión arquitectónica | `specs/adr/` |
| `RF-NNNN-nn` · `CA-NNNN-nn` · `T-NNNN-nn` | Requisito, criterio de aceptación y tarea de la feature NNNN | `specs/features/NNNN-*/` |

## 4. Decisiones de arquitectura (índice)

| ADR | Decisión | Estado |
|---|---|---|
| [ADR-01](../specs/adr/ADR-01-stack-dotnet-mvc.md) | Stack de referencia: .NET 8 + ASP.NET Core MVC (⚠ cambiable) | Aceptada |
| [ADR-02](../specs/adr/ADR-02-monolito-modular-puertos.md) | Monolito modular con puertos desde el día 1 | Aceptada |
| [ADR-03](../specs/adr/ADR-03-envio-see-ose-mismo-puerto.md) | SEE-Del contribuyente y OSE tras el mismo puerto | Aceptada |
| [ADR-04](../specs/adr/ADR-04-dinero-decimal-exacto.md) | Dinero con decimales exactos y redondeo por línea | Aceptada |
| [ADR-05](../specs/adr/ADR-05-parametros-tributarios-versionados.md) | Parámetros tributarios en configuración versionada | Aceptada |
| [ADR-06](../specs/adr/ADR-06-secretos-almacen-seguro.md) | Secretos fuera de la base de datos plana | Aceptada |

## 5. Supuestos y límites

- Se estudió el **Anexo de catálogos (RS 245-2017)** y la **Guía de elaboración XML Factura UBL 2.1** de SUNAT. Antes de producción hay que contrastar con la versión vigente en <https://cpe.sunat.gob.pe>.
- **No se creó** cuenta DEMO en Nubefact (lo debe hacer el alumno); ver `docs/02-casos-de-uso.md` §4.
- El XSD `UBL-Invoice-2.1.xsd` (OASIS) define la estructura; SUNAT la restringe con su guía. La matriz usa la guía de SUNAT para la obligatoriedad y el XSD para la cardinalidad estructural.
