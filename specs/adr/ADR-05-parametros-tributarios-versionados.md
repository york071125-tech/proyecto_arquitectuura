# ADR-05 · Parámetros tributarios en configuración versionada

| Campo | Valor |
|---|---|
| **Estado** | Aceptada |
| **Fecha** | 2026-10-22 |
| **Relacionada con** | docs/01-contexto-normativo.md §5, docs/03-modelo-dominio.md |

## Contexto
IGV (18 %), tarifa ICBPER, umbral de boleta, plazos de envío y listas de catálogos cambian por norma.

## Decisión
Tabla `ParametroTributario` con vigencia (`desde`/`hasta`) y catálogos cargables (EP-16). Nada tributario va en constantes de código.

## Alternativas consideradas
- Constantes en código: obliga a recompilar y redistribuir MSI/APK ante cada cambio.

## Consecuencias
- Cada comprobante guarda los parámetros con que se calculó (auditoría).
- Hay que sembrar los valores iniciales y marcar los `⚠ VERIFICAR`.
