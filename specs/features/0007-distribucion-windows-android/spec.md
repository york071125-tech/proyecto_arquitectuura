# Spec 0007 · Distribución multiplataforma: MSI (Windows) y APK (Android)

| Campo | Valor |
|---|---|
| **ID** | 0007-distribucion-windows-android |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | Transversal (requisito de empaquetado del enunciado) |
| **Depende de** | Specs 0002 y 0005 como mínimo funcional |
| **Detalle** | [`docs/06-empaquetado-distribucion.md`](../../../docs/06-empaquetado-distribucion.md), [ADR-01](../../adr/ADR-01-stack-dotnet-mvc.md), [ADR-06](../../adr/ADR-06-secretos-almacen-seguro.md) |

## 1. Contexto y problema
La aplicación debe correr de forma **nativa** en Windows y Android y **empaquetarse obligatoriamente** en un formato de instalación amigable: **MSI** para escritorio o **APK** para Android.

## 2. Objetivo y fuera de alcance
- **Objetivo**: un instalador MSI firmado y un APK firmado que instalen y ejecuten el mismo núcleo.
- **Fuera de alcance**: publicación en Microsoft Store o Google Play, iOS y macOS.

## 3. Actores y precondiciones
Administrador/instalador. Windows 10/11 x64 o Android 8.0+ (API 26+).

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0007-01 | Generar `AbcFacturacion-x.y.z.msi` con WiX; instalación silenciosa `msiexec /i … /qn` | M |
| RF-0007-02 | El MSI incluye el prerrequisito WebView2 Runtime | M |
| RF-0007-03 | Los datos viven en `%ProgramData%\ABC\Facturacion\data` y **no se borran** al actualizar | M |
| RF-0007-04 | Generar `AbcFacturacion-x.y.z.apk` firmado, `minSdk 26`, permisos mínimos | M |
| RF-0007-05 | Secretos en DPAPI (Windows) y Android Keystore (`ISecretStorePort`) | M |
| RF-0007-06 | Kestrel escucha sólo en loopback con token de sesión por arranque | M |
| RF-0007-07 | Núcleo sin `#if` de plataforma: todo lo específico detrás de puertos | M |
| RF-0007-08 | Publicar hashes SHA-256 de cada instalador | S |

## 5. Reglas de negocio aplicables
`ADR-01`, `ADR-02`, `ADR-06`; RNF de `docs/04-arquitectura.md` §8.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| Puertos de plataforma | `ISecretStorePort`, `IRutasPort`, `IPdfPort`, `IJobSchedulerPort` |
| Calidad | Puerta de build: `npm test` y tests de arquitectura en verde |

## 7. Flujo principal y alternos
1. CI ejecuta las pruebas → publica Windows y Android → empaqueta MSI/APK → firma → publica hashes.
- **A1** Si falla cualquier prueba de contrato, **no** se generan instaladores.
- **A2** Si el emulador de Android no soporta Kestrel in-proc, se usa el **plan B**: invocar los casos de uso directamente desde MAUI sin HTTP local.

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Prueba |
|---|---|---|---|---|
| CA-0007-01 | Un Windows limpio | se instala el MSI | la app abre y emite un comprobante en beta | manual guiada |
| CA-0007-02 | App instalada con datos | se instala una versión mayor | los datos se conservan | prueba de actualización |
| CA-0007-03 | Desinstalación | se completa | sin procesos residuales | manual |
| CA-0007-04 | Un Android 8+ | se instala el APK | la app abre y emite un comprobante en beta | manual en emulador |
| CA-0007-05 | Segundo proceso local | llama al servidor sin token | 401 | prueba de seguridad |
| CA-0007-06 | El mismo `.pfx` de prueba en ambos hosts | se firma un XML | la firma verifica en ambos | prueba cruzada |

## 9. Requisitos no funcionales
Arranque en frío < 5 s en Windows y < 8 s en Android de gama media.

## 10. Riesgos y preguntas abiertas
- Kestrel embebido en Android requiere pruebas de ciclo de vida (la app pasa a segundo plano).
- MAUI en Windows genera MSIX; por eso el MSI usa un host propio con WiX.
- ⚠ Certificado de firma de código (Authenticode) y keystore de release: ¿quién los custodia?
