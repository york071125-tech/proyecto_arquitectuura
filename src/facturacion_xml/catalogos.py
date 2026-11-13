"""Catálogos SUNAT usados por el generador.

La lista de unidades de medida debe ser la misma que la del contrato JSON
(`specs/contracts/schemas/common.schema.json`, `UnidadMedida`); una prueba lo comprueba.
"""

# Catálogo 03 (UN/ECE Rec. 20): subconjunto operativo de ABC. Para ampliarlo se añade el código desde el catálogo vigente.
UNIDADES_MEDIDA = frozenset({"NIU", "ZZ", "KGM", "GRM", "LTR", "MLT", "MTR", "BX", "BG", "BO", "CA", "CT", "DZN", "TNE", "GLL"})

MONEDAS = {"PEN": "SOLES", "USD": "DÓLARES AMERICANOS"}      # catálogo 02 (ISO 4217)

# Catálogo 07: afectaciones que corresponden a una transferencia gratuita.
MOTIVOS_GRATUITO = frozenset({"11", "12", "13", "14", "15", "16", "21", "31", "32", "33", "34", "35", "36"})

TIPO_DOCUMENTO_FACTURA = "01"          # catálogo 01
TIPO_OPERACION_VENTA_INTERNA = "0101"  # catálogo 51
TIPO_DOC_IDENTIDAD_RUC = "6"           # catálogo 06

# Identificadores de catálogos SUNAT que se escriben como atributos del XML.
URI_CATALOGO = "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo{:02d}"
