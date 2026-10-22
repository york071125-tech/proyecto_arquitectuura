# Spec 0002 · Emisión de Factura y Boleta electrónicas

| Campo | Valor |
|---|---|
| **ID** | 0002-emision-factura-boleta |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-05, CU-06, CU-08, CU-12, CU-19, CU-21, CU-22 |
| **Depende de** | 0001 (cálculo). Integra 0005 (salida de almacén) por evento |
| **Diseño** | [`design.md`](design.md) |

## 1. Contexto y problema
El sistema actual no valida RUC, no genera XML firmado ni se comunica con SUNAT/OSE. La RS 097-2012/SUNAT exige emitir comprobantes en UBL 2.1, firmados digitalmente, y obtener la constancia de recepción (CDR).

## 2. Objetivo y fuera de alcance
- **Objetivo**: emitir una factura (01) o boleta (03) válida, firmada y enviada, con CDR y representación impresa, sin perder el correlativo ante fallos de red.
- **Fuera de alcance**: guía de remisión, retenciones/percepciones/detracciones, venta itinerante.

## 3. Actores y precondiciones
| Actor | Rol | Precondición |
|---|---|---|
| Vendedor/Cajero | emite | Emisor, serie y certificado configurados (CU-01…03) |
| SUNAT / OSE | recibe y responde | Credenciales SOL o cuenta OSE válidas |
| Servicio de RUC | valida adquirente | Opcional; degrada si falla |

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0002-01 | Validar la forma del request contra `ComprobanteEmitirRequest` | M |
| RF-0002-02 | Validar RUC del adquirente (formato + dígito verificador) y, si hay red, estado SUNAT | M |
| RF-0002-03 | Factura exige adquirente con RUC (salvo exportación); boleta sólo exige identificación sobre el umbral | M |
| RF-0002-04 | Reservar el siguiente correlativo de la serie de forma **atómica** | M |
| RF-0002-05 | Calcular totales (feature 0001) | M |
| RF-0002-06 | Generar XML UBL 2.1 (`Invoice`) y validarlo contra el XSD | M |
| RF-0002-07 | Firmar con XMLDSig (certificado del emisor) y guardar SHA-256 inmutable | M |
| RF-0002-08 | Enviar por `IEnvioComprobantePort` (SEE u OSE según el emisor) y registrar el CDR | M |
| RF-0002-09 | Si no hay conexión: estado `PENDIENTE_ENVIO` y reintento posterior | M |
| RF-0002-10 | Boletas no se envían una a una: pasan a la cola del Resumen Diario (feature 0004) | M |
| RF-0002-11 | Idempotencia por `idempotencyKey` (reintento no duplica correlativo) | M |
| RF-0002-12 | Publicar evento `ComprobanteAceptado` para generar la salida de almacén | S |
| RF-0002-13 | Descargar XML, CDR y PDF (EP-07) | S |

## 5. Reglas de negocio aplicables
`RN-001…RN-006`, `RN-010…RN-013`, `RN-030…RN-036`, `RN-045`, `RN-050…RN-053`, `RN-061`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO entrada | `comprobante.schema.json#/$defs/ComprobanteEmitirRequest` |
| DTO salida | `#/$defs/ComprobanteResponse`, `#/$defs/ResultadoSunat` |
| Errores | `operaciones.schema.json#/$defs/Problema` |
| Endpoints | EP-05 (emitir), EP-06 (consultar), EP-07 (xml/cdr/pdf), EP-10 (validar RUC), EP-11 (reenviar), EP-12 (consultar estado) |
| Puertos | PT-01, PT-10, PT-11, PT-12, PT-13, PT-14, PT-15 |
| Trazabilidad | `TR-001…TR-031` (cabecera, emisor, adquirente, globales), `TR-044…TR-066` (ítems), `TR-079…TR-080` (CDR) |

## 7. Flujo principal y alternos
1. El controller recibe el DTO y valida la forma.
2. El caso de uso valida el adquirente (CU-19) y la regla RN-012.
3. Reserva el correlativo (transacción) → calcula (0001) → arma el `Comprobante`.
4. `IGeneradorUbl` produce el XML → `IFirmaDigital` lo firma → se persiste con su hash.
5. Factura: `IEnvioComprobantePort.enviarComprobante` → CDR → estado.
6. Boleta: queda `FIRMADO` y se informa por Resumen Diario.
7. Se publica `ComprobanteAceptado`.

- **A1** RUC inválido → `RUC_INVALIDO`, **no** consume correlativo.
- **A2** Sin red → `PENDIENTE_ENVIO`, HTTP 202.
- **A3** Rechazo 2xxx/3xxx → `RECHAZADO`; el correlativo no se reutiliza (RN-051).
- **A4** Observación 4xxx → `ACEPTADO_CON_OBS`.
- **A5** Mismo `idempotencyKey` → devuelve el comprobante existente.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Ejemplo / prueba |
|---|---|---|---|---|
| CA-0002-01 | Request de factura válido | POST `/comprobantes` | 201, estado `ACEPTADO` (con *mock* SUNAT), `numero = F001-1` | `factura-valida.json` |
| CA-0002-02 | Factura con adquirente DNI | se valida | error (RN-012) | `INVALIDO-factura-sin-ruc.json` |
| CA-0002-03 | Boleta con serie `F001` | se valida | error de esquema | `INVALIDO-serie-boleta-con-F.json` |
| CA-0002-04 | Factura de exportación con documento distinto de RUC | se valida | válida | `factura-exportacion-valida.json` |
| CA-0002-05 | SUNAT no disponible | se emite | 202, `PENDIENTE_ENVIO`, correlativo consumido una sola vez | prueba con *mock* caído |
| CA-0002-06 | Mismo `idempotencyKey` dos veces | se emite | un solo comprobante | prueba de integración |
| CA-0002-07 | Comprobante `ACEPTADO` | se pide el XML | XML válido contra XSD y con `ds:Signature` | validación XSD |

## 9. Requisitos no funcionales
Emisión local < 2 s sin red; firma con RSA-SHA256 (⚠ confirmar contra la guía vigente); secretos sólo en `ISecretStorePort`; XML y CDR inmutables.

## 10. Riesgos y preguntas abiertas
- ⚠ VERIFICAR: operaciones exactas de `billService`, URLs beta/producción, umbral de boleta (S/ 700), plazo máximo de envío (RS 003-2023).
- ⚠ VERIFICAR la estructura de partes (`PartyTaxScheme` vs `PartyLegalEntity`) en la guía vigente.
