"""Genera la factura XML de ejemplo y la valida contra el XSD. Funciona sin configurar PYTHONPATH.

Uso:  python scripts/generar_factura_ejemplo.py [--salida RUTA]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from facturacion_xml.__main__ import main  # noqa: E402  (el import va después de ajustar sys.path)

if __name__ == "__main__":
    raise SystemExit(main())
