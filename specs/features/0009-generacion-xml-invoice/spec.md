# Spec 0009 · Generación de XML Invoice UBL 2.1 con validación XSD (Segundo Parcial)

| Campo | Valor |
|---|---|
| **ID** | 0009-generacion-xml-invoice |
| **Estado** | En implementación (referencia en Python) |
| **Casos de uso** | CU-21 (generar XML UBL), parte de CU-05 y CU-20 |
| **Depende de** | 0001 (reglas de cálculo), [ADR-07](../../adr/ADR-07-xml-sin-plantillas-validado-xsd.md) |
| **Diseño** | [`design.md`](design.md) · Documentación del parcial: [`docs/09-parcial2-generacion-xml.md`](../../../docs/09-parcial2-generacion-xml.md) |
| **Entrega** | Segundo Parcial · 12/11/2026 hasta la medianoche |

## 1. Contexto y problema
En el Perú la factura electrónica se emite en **XML UBL 2.1** y SUNAT (o un OSE) la recibe, valida y responde con una constancia (CDR). Un XML con una etiqueta mal escrita, un elemento fuera de orden o una tilde mal codificada se rechaza. La primera entrega generaba el XML con plantillas de texto, una práctica frágil que el ingeniero observó. Este parcial entrega una **implementación de referencia** que construye el XML desde un modelo de dominio y lo **valida contra el XSD oficial `UBL-Invoice-2.1.xsd` de OASIS** antes de entregarlo.

## 2. Objetivo y fuera de alcance
- **Objetivo**: a partir de una `Factura` del dominio (emisor, receptor, detalle, afectaciones), producir un XML `Invoice` UBL 2.1 correcto, en UTF-8, que pase la validación XSD, con pruebas unitarias reproducibles.
- **Fuera de alcance** (pertenece a otras fases): firma digital (`ds:Signature`), envío a SUNAT/OSE, notas de crédito/débito, resumen diario y baja, ISC, ICBPER, descuentos globales, anticipos, boletas. Tampoco se despliega Odoo ni se integra ningún addon (Parciales 3 y 4).

## 3. Actores y precondiciones
| Actor | Rol | Precondición |
|---|---|---|
| Código de la aplicación | Invoca `GeneradorFacturaXml` | Tiene una `Factura` válida |
| Estudiante / ingeniero | Ejecuta las pruebas y el ejemplo | Python 3.10+ y `lxml` instalado |

## 4. Requisitos funcionales
| ID | Requisito | Prioridad |
|---|---|---|
| RF-0009-01 | Modelo de dominio con nombres del negocio: `Factura`, `Emisor`, `Receptor`, `DetalleFactura`, `TipoAfectacion`, `TotalesFactura` | M |
| RF-0009-02 | Validar al construir: RUC del emisor con módulo 11 (RN-010), serie `^F[A-Z0-9]{3}$` y correlativo 1–99 999 999 (RN-001, RN-002), cantidad > 0, unidad del catálogo 03 (RN-086), receptor con RUC en toda factura (RN-012) | M |
| RF-0009-03 | Calcular importes con `Decimal` (nunca `float`), redondeo half-up por línea y totales como suma de líneas (RN-021, RN-022, ADR-04) | M |
| RF-0009-04 | Soportar los cuatro tipos de afectación del enunciado: **1001 gravado, 1002 inafecto, 1003 exonerado, 1004 gratuito** (tabla §6) | M |
| RF-0009-05 | La tasa del IGV es un **parámetro explícito** (18 % por defecto); otras tasas (p. ej. 10 % de restaurantes y hoteles) se aceptan solo si se pasan expresamente, sin generalizarlas (⚠ vigencia por verificar) | M |
| RF-0009-06 | Construir el XML como **árbol de elementos** con espacios de nombres UBL, nunca con texto ni plantillas (RN-088) | M |
| RF-0009-07 | Respetar el orden de elementos y los atributos del XSD de `Invoice` | M |
| RF-0009-08 | Codificación UTF-8 con declaración XML; los caracteres especiales (`ñ`, tildes, `&`, `<`, `>`, comillas) se escapan y se conservan al leer el XML | M |
| RF-0009-09 | Forma de pago `Contado` o `Credito` con cuotas (`PaymentTerms`, RN-080, RN-081) | M |
| RF-0009-10 | Leyenda `1000` (monto en letras) siempre; leyenda `1002` si hay operaciones gratuitas (RN-045, RN-031) | M |
| RF-0009-11 | **Validar contra el XSD oficial** antes de devolver el XML; si falla, lanzar `XmlInvalidoError` con la lista de errores (RN-088) | M |
| RF-0009-12 | Línea de comandos que genera un XML de ejemplo y reporta el resultado de la validación | S |
| RF-0009-13 | Separar el generador de las pruebas: el paquete no importa `unittest`; las pruebas viven en `tests/generacion_xml/` | M |

## 5. Reglas de negocio aplicables
`RN-001`, `RN-002`, `RN-010`, `RN-012`, `RN-020`, `RN-021`, `RN-022`, `RN-024`, `RN-030`, `RN-031`, `RN-045`, `RN-080`, `RN-081`, `RN-086`, `RN-088`, `RN-089`.

## 6. Afectaciones soportadas
Los códigos **1001–1004** son los del enunciado; coinciden con el catálogo 14 de SUNAT («total valor de venta de operaciones gravadas / inafectas / exoneradas / gratuitas»). En el XML cada afectación se expresa con el tributo del catálogo 05 y el código de afectación del catálogo 07:

| Código | Operación | Tributo (cat. 05) | Nombre | Tipo internacional | Categoría UN/ECE 5305 | Afectación (cat. 07) | IGV |
|---|---|---|---|---|---|---|---|
| **1001** | Gravado | 1000 | IGV | VAT | S | 10 | Sí, con la tasa vigente |
| **1002** | Inafecto | 9998 | INA | FRE | O | 30 | No |
| **1003** | Exonerado | 9997 | EXO | VAT | E | 20 | No |
| **1004** | Gratuito | 9996 | GRA | FRE | Z | 21 por defecto (acepta 11–16, 21, 31–36) | No se cobra |

- **Inafecto ≠ exonerado:** son tributos y categorías distintos (`9998/O` frente a `9997/E`); nunca se mezclan.
- **Gratuito:** el valor de venta de la línea es `0.00`; el valor referencial va en `PricingReference` con tipo de precio `02`; no suma al importe total (RN-031).
- ⚠ **Por confirmar:** los nombres abreviados `INA`, `EXO`, `GRA` (catálogo 05) y que el código por defecto de la afectación gratuita sea `21`.

## 7. Flujo principal y alternos
1. El código crea una `Factura` con `Emisor`, `Receptor` y `DetalleFactura` (valida en el constructor).
2. `calcular_totales(factura)` obtiene los importes por línea y los totales.
3. `GeneradorFacturaXml.generar(factura)` construye el árbol UBL, lo serializa en UTF-8 y lo valida contra el XSD.
4. Devuelve los bytes del XML (o lanza `XmlInvalidoError`).

- **A1** Dato de dominio inválido (RUC, serie, cantidad, unidad) → `FacturaInvalidaError` con el motivo, sin generar XML.
- **A2** El XSD rechaza el XML → `XmlInvalidoError` con las líneas del error.
- **A3** El archivo XSD no existe → `XsdNoEncontradoError` indicando la ruta esperada (no se afirma validación).

## 8. Criterios de aceptación
| ID | Dado | Cuando | Entonces | Prueba |
|---|---|---|---|---|
| CA-0009-01 | Una factura válida | se genera | bytes de un XML bien formado con raíz `Invoice` y declaración UTF-8 | `test_generacion` |
| CA-0009-02 | El XML generado | se inspecciona | existen los elementos obligatorios (versión, ID, fechas, tipo, moneda, emisor, receptor, impuestos, totales, líneas) | `test_estructura` |
| CA-0009-03 | Emisor y receptor | se generan | RUC, `schemeID`, razón social y dirección correctos | `test_partes` |
| CA-0009-04 | Productos y servicios | se generan | descripción, cantidad, `unitCode`, valor y precio unitario correctos (`NIU` y `ZZ`) | `test_detalle` |
| CA-0009-05 | Una factura con importes conocidos | se calcula | totales exactos al centavo e IGV = 18 % de la base gravada | `test_importes` |
| CA-0009-06 | Líneas 1001, 1002, 1003 y 1004 | se generan | cada una con su tributo, categoría y código de afectación de la tabla §6 | `test_afectaciones` |
| CA-0009-07 | Textos con `ñ`, tildes, `&`, `<`, comillas | se generan y se leen | se conservan idénticos; el archivo está en UTF-8 | `test_caracteres_especiales` |
| CA-0009-08 | El XML de una factura válida | se valida contra `UBL-Invoice-2.1.xsd` | 0 errores | `test_validacion_xsd` |
| CA-0009-09 | Un XML al que se le quita un elemento obligatorio o se le cambia el orden | se valida | el validador lo **rechaza** (la validación no es decorativa) | `test_validacion_xsd` |
| CA-0009-10 | Datos de dominio inválidos | se construye la factura | `FacturaInvalidaError` | `test_dominio` |
| CA-0009-11 | Tasa 10 % pasada expresamente | se calcula | IGV al 10 %; sin parámetro, 18 % | `test_importes` |
| CA-0009-12 | Forma de pago a crédito con cuotas | se genera | `PaymentTerms` con `FormaPago`, `Credito` y `Cuota001…` | `test_forma_pago` |

## 9. Requisitos no funcionales
- Reproducible: `pip install -r requirements.txt` y `python -m unittest discover -s tests/generacion_xml -t . -v`.
- Una sola dependencia externa (`lxml`); pruebas con `unittest` de la biblioteca estándar.
- Código legible por un estudiante: sin metaprogramación ni clases generadas.

## 10. Riesgos y preguntas abiertas
- El XSD valida **estructura**, no las reglas tributarias de SUNAT (por eso hay pruebas de importes y afectaciones).
- ⚠ La firma digital (`ext:UBLExtensions` con `ds:Signature`) queda para una fase posterior: sin ella SUNAT no aceptaría el comprobante.
- ⚠ Tasa reducida del 10 %: vigencia y condiciones por verificar con la norma antes de usarla en producción.
- Los XSD oficiales se descargaron de OASIS el 06-11-2026; sus SHA-256 están en `specs/contracts/ubl-2.1/xsd/SHA256SUMS.txt`.
