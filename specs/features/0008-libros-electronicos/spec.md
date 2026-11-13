# Spec 0008 · Libros electrónicos: Registro de Ventas (14.1) e Inventario Permanente en Unidades Físicas (12.1)

| Campo | Valor |
|---|---|
| **ID** | 0008-libros-electronicos |
| **Estado** | Borrador (listo para revisión) |
| **Casos de uso** | CU-16 (kardex / inventario permanente), CU-18 (Registro de Ventas) |
| **Depende de** | 0002 (comprobantes), 0005 (movimientos de almacén) |
| **Origen** | Observación del ingeniero a la primera entrega: los formatos 14.1 y 12.1 estaban cubiertos solo a medias |

## 1. Contexto y problema
La RS 234-2006/SUNAT obliga a llevar libros y registros vinculados a asuntos tributarios, hoy en formato electrónico PLE. Este sistema tiene los datos de los dos libros que le competen: el **Registro de Ventas e Ingresos (Formato 14.1)**, que sale de los comprobantes, y el **Registro del Inventario Permanente en Unidades Físicas (Formato 12.1)**, que sale del kardex. La primera entrega solo devolvía una lista de comprobantes (14.1) y un saldo en unidades (12.1), sin las columnas oficiales.

## 2. Objetivo y fuera de alcance
- **Objetivo**: generar las filas de ambos libros con **las columnas y formatos oficiales** y exponerlas como `text/plain` (estructura PLE) y como JSON.
- **Fuera de alcance**: el Formato 13.1 (inventario **valorizado**; requiere el método de costo, RN-062), el envío del libro a SUNAT (SIRE/RVIE, detrás de `ILibroElectronicoPort`), la contabilidad (libro diario, mayor) y los registros de compras.

## 3. Actores y precondiciones
Contador/Administrador. Comprobantes `ACEPTADO` del periodo (14.1) y movimientos de almacén con los campos del 12.1 (feature 0005).

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0008-01 | Una fila del 14.1 por comprobante del periodo (facturas, boletas, notas), con los **campos 1 a 34** de la RS 361-2015 | M |
| RF-0008-02 | Las notas de crédito/débito informan el comprobante que modifican (campos 27–30) | M |
| RF-0008-03 | Con moneda informada, el tipo de cambio es obligatorio (campo 26; `1.000` si PEN) | M |
| RF-0008-04 | El ICBPER se informa en una columna propia del DTO y se suma al campo 23 hasta contrastar el esquema PLE vigente (⚠) | S |
| RF-0008-05 | Una fila del 12.1 por movimiento, con los **campos 1 a 19** de la RS 042-2018: establecimiento, tipo de existencia (Tabla 5), documento de soporte (Tabla 10), tipo de operación (Tabla 12), unidad (Tabla 6) | M |
| RF-0008-06 | Entradas y salidas son excluyentes en una fila: entradas ≥ 0, salidas ≤ 0 | M |
| RF-0008-07 | Salida de texto: campos separados por «\|» y terminados con «\|»; fechas `DD/MM/AAAA`; importes con punto decimal y sin separador de miles; campos sin dato, vacíos | M |
| RF-0008-08 | Periodo con formato `AAAAMM00` (campo 1) | M |
| RF-0008-09 | El 12.1 no calcula costos; el 13.1 queda fuera (RN-062) | M |
| RF-0008-10 | Puerto `ILibroElectronicoPort` para que un adaptador posterior (SIRE/RVIE) reemplace la salida de texto | S |

## 5. Reglas de negocio aplicables
`RN-062`, `RN-084`, `RN-085`, `RN-086`, `RN-089`.

## 6. Contratos
| Tipo | Referencia |
|---|---|
| DTO 14.1 | `libros.schema.json#/$defs/RegistroVentasFila` |
| DTO 12.1 | `libros.schema.json#/$defs/RegistroInventarioFisicoFila` |
| Movimiento | `almacen-migracion.schema.json#/$defs/MovimientoInventario` (campos del 12.1) |
| Endpoints | EP-17 `GET /libros/registro-ventas/{periodo}` · EP-19 `GET /libros/inventario-permanente-fisico/{periodo}` |
| Puerto | PT-18 `ILibroElectronicoPort` |
| Mapeo | `docs/03-modelo-dominio.md` §4.9 |

## 7. Flujo principal y alternos
1. El contador pide el libro de un periodo (`AAAAMM00`).
2. El sistema reúne los comprobantes (14.1) o movimientos (12.1) del periodo y los convierte en filas del DTO.
3. Devuelve `text/plain` (líneas PLE) o `application/json` (filas).
- **A1** Periodo con formato inválido → 422.
- **A2** Una nota sin comprobante modificado → la fila se rechaza (`LIBRO_INCOMPLETO`).
- **A3** Periodo sin operaciones → lista vacía (no es un error).

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Prueba |
|---|---|---|---|---|
| CA-0008-01 | La fila de ejemplo de la factura F001-1 | se convierte a PLE | la línea tiene 34 campos y coincide con la escrita a mano | `npm run libros` |
| CA-0008-02 | La fila de ejemplo del movimiento de salida | se convierte a PLE | la línea tiene 19 campos y coincide con la escrita a mano | `npm run libros` |
| CA-0008-03 | Una nota de crédito sin comprobante modificado | se valida | error de esquema | `INVALIDO-registro-ventas-nota-sin-comprobante-modificado.json` |
| CA-0008-04 | Un tipo de existencia `77` | se valida | error (Tabla 5) | `INVALIDO-inventario-fisico-tipo-existencia-77.json` |
| CA-0008-05 | Una fila con importes como número JSON | se valida | error (cadena decimal, ADR-04) | `validar-contratos` |

## 9. Requisitos no funcionales
Un libro mensual de 100 000 filas se genera en menos de 10 s; la salida es determinista (mismo periodo → mismo texto).

## 10. Riesgos y preguntas abiertas
- ⚠ **Tabla 12** (tipo de operación): el PDF oficial consultado no tiene capa de texto en esa tabla; solo se confirma el formato de 2 dígitos.
- ⚠ **ICBPER** en el 14.1: la estructura de 2015 no tiene columna propia; verificar el esquema vigente.
- ⚠ **Nombre y cabecera del archivo PLE** (`LE` + RUC + periodo + código de libro…) y si cada línea termina con «\|»: confirmar con la ficha técnica del PLE antes de implementar.
- ⚠ Códigos de catálogo (Tabla 13) para el 12.1: el sistema hoy usa el código propio y el UNSPSC de `Producto.codigoSunat`.
