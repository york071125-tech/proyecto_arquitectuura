"""Demostración: genera una factura XML de ejemplo y la valida contra el XSD.

Uso:  python -m facturacion_xml [--salida RUTA]
"""
import argparse
import sys
from pathlib import Path

from .calculo import calcular_totales
from .ejemplo import factura_ejemplo
from .generador_invoice import GeneradorFacturaXml
from .validador_xsd import RAIZ_PROYECTO, RUTA_XSD_INVOICE, ValidadorXsd

SALIDA_POR_DEFECTO = RAIZ_PROYECTO / "specs" / "contracts" / "examples" / "xml" / "factura-ejemplo.xml"


def main() -> int:
    # La consola de Windows usa cp1252 y no imprime todo el español: se fuerza UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Genera una factura XML de ejemplo y la valida contra el XSD.")
    parser.add_argument("--salida", type=Path, default=SALIDA_POR_DEFECTO, help="archivo XML a escribir")
    args = parser.parse_args()

    factura = factura_ejemplo()
    totales = calcular_totales(factura)
    xml = GeneradorFacturaXml().generar(factura)   # lanza XmlInvalidoError si el XSD lo rechaza
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_bytes(xml)

    errores = ValidadorXsd().errores(args.salida.read_bytes())   # segunda validación, sobre el archivo escrito
    print(f"Factura {factura.numero} · {len(factura.detalles)} líneas · importe total {totales.importe_total} {factura.moneda}")
    print(f"XML escrito en: {args.salida}  ({len(xml)} bytes, UTF-8)")
    print(f"XSD usado:      {RUTA_XSD_INVOICE.relative_to(RAIZ_PROYECTO)}")
    print("Validación XSD: " + ("CORRECTA (0 errores)" if not errores else f"FALLÓ con {len(errores)} errores"))
    for error in errores:
        print("  -", error)
    return 0 if not errores else 1


if __name__ == "__main__":
    raise SystemExit(main())
