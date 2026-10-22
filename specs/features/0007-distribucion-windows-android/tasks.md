# Tasks 0007 · Distribución Windows (MSI) y Android (APK)

> Spec: [`spec.md`](spec.md)

## Definition of Done (toda tarea)
- [ ] Cumple los `CA-0007-xx` · [ ] pruebas primero (o prueba manual guiada documentada) · [ ] `npm test` en verde

## Fase 1 · Decisiones y pruebas
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0007-01 | ADR de stack y de secretos | — | RF-0007-05, 07 | [x] |
| T-0007-02 | Documento de empaquetado (matriz de entrega y de portabilidad) | — | RF-0007-01, 04 | [x] |
| T-0007-03 | Prueba de humo de Kestrel in-proc en un emulador Android (decide plan A o B) | — | CA-0007-04 | [ ] |
| T-0007-04 | Prueba cruzada de firma XMLDSig con el mismo `.pfx` en ambos hosts | T-0002-14 | CA-0007-06 | [ ] |

## Fase 2 · Windows
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0007-05 | Host `Abc.Host.Windows` (WPF + WebView2 + Kestrel loopback + token) | T-0002-17 | CA-0007-05 | [ ] |
| T-0007-06 | Proyecto WiX: instalación, accesos directos, `MajorUpgrade`, datos en `ProgramData` | T-0007-05 | CA-0007-01…03 | [ ] |
| T-0007-07 | Bootstrapper de WebView2 y firma Authenticode | T-0007-06 | RF-0007-02 | [ ] |

## Fase 3 · Android
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0007-08 | Host `Abc.Host.Android` (MAUI) con Keystore y SQLite privado | T-0007-03 | CA-0007-04 | [ ] |
| T-0007-09 | APK firmado, `minSdk 26`, permisos mínimos | T-0007-08 | RF-0007-04 | [ ] |

## Fase 4 · CI
| ID | Tarea | Depende de | Verifica | Estado |
|---|---|---|---|---|
| T-0007-10 | Pipeline: pruebas → publish → MSI/APK → firma → hashes | T-0007-07, T-0007-09 | RF-0007-08, A1 | [ ] |

## Trazabilidad tarea → requisito
| Tarea | RF | CA | ADR |
|---|---|---|---|
| T-0007-06 | RF-0007-01, 03 | CA-0007-01…03 | ADR-01 |
| T-0007-08 | RF-0007-04, 05 | CA-0007-04 | ADR-06 |
