"""Pruebas unitarias de la generación de XML Invoice UBL 2.1 (Segundo Parcial).

Ejecutar desde la raíz del proyecto:  python -m unittest discover -s tests/generacion_xml -t . -v
"""
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROYECTO / "src"))   # para importar facturacion_xml sin instalarlo
