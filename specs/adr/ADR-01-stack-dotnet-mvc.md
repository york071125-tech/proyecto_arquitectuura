# ADR-01 · Stack de referencia: .NET 8 con ASP.NET Core MVC

| Campo | Valor |
|---|---|
| **Estado** | Aceptada (⚠ cambiable: los contratos son agnósticos) |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | docs/04-arquitectura.md, docs/06-empaquetado-distribucion.md |

## Contexto
El enunciado exige arquitectura monolítica MVC, ejecución nativa en Windows y Android, e instalador MSI/APK. Se necesita un único lenguaje para el núcleo que compile en ambas plataformas y soporte XMLDSig y SOAP.

## Decisión
Núcleo (`Domain` + `Application`) en C# `net8.0` sin dependencias de framework web. Entrada: **ASP.NET Core MVC** (Razor). Persistencia local: **SQLite**. Hosts: **WPF + WebView2 + WiX** (MSI) y **.NET MAUI** (APK).

## Alternativas consideradas
- Flutter: no es MVC natural y obliga a reescribir el núcleo en Dart.
- Electron + Capacitor: dos runtimes y firma XMLDSig más débil.
- Java/Kotlin: válido, pero el MSI en Windows es más costoso.

## Consecuencias
- El stack es secundario: cambiarlo no invalida `specs/contracts`.
- Windows usa host propio + WiX porque MAUI en Windows produce MSIX, no MSI.
