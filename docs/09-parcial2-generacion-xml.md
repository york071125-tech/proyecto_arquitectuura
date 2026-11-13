# 09 · Segundo Parcial: generación de XML Invoice UBL 2.1 con validación XSD

> Entrega: 12/11/2026, hasta la medianoche · Especificación: [`specs/features/0009-generacion-xml-invoice/`](../specs/features/0009-generacion-xml-invoice/spec.md)

## 1. Descripción del caso

**Problema.** ABC Software Corp vende abarrotes y mercadería al por mayor. Su software emite comprobantes sin cumplir la normativa: no calcula bien los impuestos y no genera el documento que exige SUNAT.

**Contexto en el Perú.** La factura electrónica se emite como un archivo **XML** en el estándar internacional **UBL 2.1** (Universal Business Language, OASIS). SUNAT, o un Operador de Servicios Electrónicos (OSE), recibe el XML, lo valida y devuelve una constancia (CDR). Si el XML tiene una etiqueta mal escrita, un elemento fuera de orden, un importe mal redondeado o una tilde mal codificada, **se rechaza** y el comprobante no tiene validez.

**Qué resuelve este parcial.** Dado un modelo de dominio de la factura (emisor, receptor, detalle de productos y servicios, tipo de afectación, impuestos y totales), el programa:

1. calcula los importes con decimales exactos;
2. construye el XML `Invoice` UBL 2.1 como un **árbol de elementos** (no con texto ni plantillas);
3. lo serializa en UTF-8, con los caracteres especiales del español bien escapados;
4. lo **valida contra el XSD oficial `UBL-Invoice-2.1.xsd`** de OASIS antes de entregarlo.

**Por qué validar con el XSD.** El XSD es la definición oficial de qué elementos existen, en qué orden van y de qué tipo son. Validar contra él detecta errores de estructura *antes* de enviar el documento. No reemplaza las reglas tributarias de SUNAT (cálculos, catálogos): esas se prueban aparte.

**Alcance.** Solo la **factura** (`Invoice`) sin firma digital. Fuera de este parcial: firma `ds:Signature`, envío a SUNAT/OSE, notas de crédito/débito, boletas, ISC, ICBPER. Tampoco se levantó Odoo, ni Docker, ni se integró ningún addon: eso corresponde a los Parciales 3 y 4.

## 2. Tecnologías

| Tecnología | Uso | Versión probada |
|---|---|---|
| Python | Lenguaje de la solución | 3.12 (compatible con 3.10 o superior) |
| `lxml` | Construir el XML y validarlo contra el XSD | 6.1.3 (`requirements.txt`: `>=5.0,<7`) |
| `unittest` | Pruebas unitarias (biblioteca estándar) | incluida en Python |
| XSD UBL 2.1 OS (OASIS) | Esquema oficial de validación | 14 archivos, ver `specs/contracts/ubl-2.1/` |

Una sola dependencia externa. No hay `pytest`, ni generadores de código.

## 3. Estructura del proyecto

```
src/facturacion_xml/            Paquete Python (sin pruebas dentro)
  dominio.py                    Factura, Emisor, Receptor, DetalleFactura, TipoAfectacion, FormaPago
  calculo.py                    Importes y totales con Decimal
  monto_en_letras.py            Leyenda 1000 («SON: ... CON 50/100 SOLES»)
  generador_invoice.py          GeneradorFacturaXml: dominio → árbol UBL → XML UTF-8
  validador_xsd.py              ValidadorXsd: valida contra el XSD oficial
  catalogos.py · errores.py     Catálogos SUNAT y errores propios
  ejemplo.py · __main__.py      Factura de ejemplo y línea de comandos
tests/generacion_xml/           Pruebas unitarias, una por aspecto pedido
specs/contracts/ubl-2.1/xsd/    XSD oficiales de OASIS (sin modificar) + SHA256SUMS.txt
specs/contracts/examples/xml/   factura-ejemplo.xml (salida real del generador)
```

## 4. El generador de XML

`GeneradorFacturaXml.generar(factura)` hace cinco pasos:

1. **Calcula** los importes de cada línea y los totales (`calculo.py`). Redondeo half-up a 2 decimales **por línea**; los totales son la suma de las líneas. Se usa `Decimal`; un `float` se rechaza.
2. **Construye el árbol** con `lxml`, agregando los elementos en el orden que exige el XSD de `Invoice`: versión, ID, fechas, tipo de documento, leyendas, moneda, firmante, emisor, receptor, forma de pago, impuestos, totales y líneas. `lxml` escapa `&`, `<`, `>` y respeta los espacios de nombres.
3. **Serializa** en UTF-8 con declaración XML.
4. **Valida** contra el XSD. Si falla, lanza `XmlInvalidoError` con las líneas del error.
5. **Devuelve** los bytes del XML.

### Los cuatro tipos de afectación

Los códigos 1001–1004 son los del enunciado (catálogo 14 de SUNAT). En el XML se expresan con el tributo del catálogo 05 y la afectación del catálogo 07:

| Código | Operación | Tributo | Nombre / tipo | Categoría | Afectación | IGV |
|---|---|---|---|---|---|---|
| **1001** | Gravado | 1000 | IGV / VAT | S | 10 | sí, 18 % por defecto |
| **1002** | Inafecto | 9998 | INA / FRE | O | 30 | no |
| **1003** | Exonerado | 9997 | EXO / VAT | E | 20 | no |
| **1004** | Gratuito | 9996 | GRA / FRE | Z | 21 | no se cobra |

- **Inafecto no es exonerado**: tienen tributo y categoría distintos y nunca se mezclan.
- La tasa del IGV es un **parámetro**: 18 % por defecto. El 10 % (restaurantes y hoteles) solo se aplica si se pasa expresamente; no se toma como tasa general porque su vigencia y condiciones deben verificarse.
- ⚠ Por confirmar: los nombres abreviados `INA`, `EXO`, `GRA` y el motivo gratuito por defecto (`21`).

### Caracteres especiales y codificación
- Todo el proyecto está en **UTF-8**; hay un `.editorconfig` y un `.gitattributes` que lo fijan.
- Se revisaron los 158 archivos de texto: ninguno con UTF-8 inválido ni caracteres corruptos. El único BOM es el del CSV de la matriz, a propósito, para que Excel muestre las tildes.
- En Windows la consola usa cp1252 y no imprime todo el español: la línea de comandos fuerza UTF-8 en la salida, y `.vscode/settings.json` define `PYTHONUTF8=1`.
- No se tocó la configuración de ninguna base de datos: este parcial no usa una.

## 5. Las pruebas unitarias

Se ejecutan con `unittest`. Cada archivo cubre uno de los aspectos pedidos:

| # | Aspecto | Archivo |
|---|---|---|
| 1, 2 | Se genera un XML con la estructura esperada | `test_generacion.py` |
| 3 | Elementos obligatorios | `test_elementos_obligatorios.py` |
| 4 | Emisor y receptor | `test_emisor_receptor.py` |
| 5 | Productos y servicios | `test_detalle_productos.py` |
| 6 | Importes y totales | `test_importes_totales.py` |
| 7 | Afectaciones 1001, 1002, 1003 y 1004 | `test_afectaciones.py` |
| 8 | Caracteres especiales del español | `test_caracteres_especiales.py` |
| 9 | Validación contra Invoice XSD 2.1 | `test_validacion_xsd.py` |
| — | Reglas del dominio, forma de pago, monto en letras, coherencia con el contrato | `test_dominio.py`, `test_forma_pago.py`, `test_monto_en_letras.py`, `test_catalogos_y_ejemplo.py` |

**Resultado real:** `Ran 110 tests … OK`.

Cómo se comprobó que las pruebas sirven y no son decorativas:
- Los valores esperados de importes están escritos **a mano** en las pruebas, no calculados con el código que se prueba.
- La validación XSD se prueba también en negativo: el validador **rechaza** un XML sin un elemento obligatorio, con elementos fuera de orden, con un elemento inventado, con otro espacio de nombres, mal formado y con un valor de tipo incorrecto.
- Se hizo una **prueba de mutación**: se rompió el código de 10 maneras (redondeo, tributo del inafecto, tasa por defecto, codificación ISO-8859-1, validador que siempre acepta, validación omitida, gratuito que suma, pérdida de la ñ, RUC sin dígito verificador, orden de elementos). Las pruebas detectaron **10 de 10**.
- Se ejecutaron en un entorno virtual limpio con solo `lxml`: 110 pruebas en verde.

## 6. Cómo ejecutar y demostrar

Requisitos: Python 3.10 o superior.

```bash
python -m venv .venv
.venv\Scripts\activate                      # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

python scripts/generar_factura_ejemplo.py   # genera el XML y lo valida contra el XSD
python -m unittest discover -s tests/generacion_xml -t . -v    # 110 pruebas
```

También con npm: `npm run xml:ejemplo` y `npm run test:xml`.

**Desde Visual Studio Code:** abrir la carpeta; el panel de *Testing* descubre las pruebas (`.vscode/settings.json`) y *Run and Debug* tiene la configuración «Generar factura XML de ejemplo y validar contra el XSD».

**Para demostrar al ingeniero:**
1. Ejecutar `python scripts/generar_factura_ejemplo.py` → muestra `Validación XSD: CORRECTA (0 errores)`.
2. Abrir `specs/contracts/examples/xml/factura-ejemplo.xml` y señalar emisor, receptor, las cinco líneas con sus afectaciones y los totales.
3. Ejecutar las pruebas → `OK`.
4. Mostrar `test_validacion_xsd.py`: el validador rechaza XML incorrecto.
5. Mostrar `specs/contracts/ubl-2.1/README.md`: el XSD es el oficial de OASIS y sus SHA-256 verifican que no se modificó.

## 7. Evidencia de validación contra Invoice XSD 2.1

- **Esquema usado:** `specs/contracts/ubl-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd`, OASIS UBL 2.1 OS (release 04-11-2013), descargado de <https://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/> el 06-11-2026.
- **Integridad:** `sha256sum -c SHA256SUMS.txt` → 14 de 14 archivos correctos; una prueba unitaria repite la comprobación.
- **Resultado:** `Validación XSD: CORRECTA (0 errores)` para la factura de ejemplo, con crédito y cuotas, en dólares y para cada tipo de afectación por separado.

## 8. Límites

- El XSD valida **estructura**. Las reglas tributarias de SUNAT no están en el XSD; se cubren con pruebas de importes y afectaciones y con la matriz de trazabilidad (`docs/07`).
- Sin firma digital, SUNAT no aceptaría este comprobante: queda para una fase posterior.
- La tasa del 10 % y los nombres `INA`/`EXO`/`GRA` están por verificar contra la norma.
