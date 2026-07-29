"""Funciones para generar variantes corruptas/LaTeX de un documento."""

from context_tables import CORRUPT_MAP, LATEX_MAP


def unicode_corruption(text: str) -> str:
    """Reemplaza símbolos originales por su versión corrupta (mojibake)."""
    out = text
    for orig, corrupt in CORRUPT_MAP.items():
        out = out.replace(orig, corrupt)
    return out


def latex_version(text: str) -> str:
    """Reemplaza símbolos por su equivalente LaTeX inline."""
    out = text
    for orig, latex in LATEX_MAP.items():
        out = out.replace(orig, latex)
    return out


def build_condition(document: str, condition_key: str, critical_symbol: str) -> str:
    """Construye la variante del documento según la condición.

    condition_key: "limpio", "corrupto", "latex"
    """
    if condition_key == "limpio":
        return document
    if condition_key == "corrupto":
        return unicode_corruption(document)
    if condition_key == "latex":
        return latex_version(document)
    return document