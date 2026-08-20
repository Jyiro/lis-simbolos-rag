"""Funciones para generar variantes corruptas/LaTeX de un documento."""
from __future__ import annotations

from context_tables import CORRUPT_MAP, LATEX_MAP

# Pre-ordenados por longitud descendente para evitar reemplazos parciales
# ("∃!" debe procesarse antes que "∃")
_CORRUPT_SORTED = sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0]))
_LATEX_SORTED   = sorted(LATEX_MAP.items(),   key=lambda x: -len(x[0]))


def unicode_corruption(text: str) -> str:
    """Reemplaza símbolos originales por su versión corrupta (mojibake)."""
    out = text
    for orig, corrupt in _CORRUPT_SORTED:
        out = out.replace(orig, corrupt)
    return out


def latex_version(text: str) -> str:
    """Reemplaza símbolos por su equivalente LaTeX inline."""
    out = text
    for orig, latex in _LATEX_SORTED:
        out = out.replace(orig, latex)
    return out


def corrupt_question(question: str) -> str:
    """Corrompe los símbolos en una pregunta (para condición QUERY CORR / FULL CORR)."""
    out = question
    for orig, corrupt in _CORRUPT_SORTED:
        out = out.replace(orig, corrupt)
    return out


def build_condition(document: str, condition_key: str) -> str:
    """Construye la variante del documento según la condición.

    Args:
        document:      Texto del documento original (limpio).
        condition_key: "limpio" | "corrupto" | "latex"

    Returns:
        Texto transformado según la condición.
    """
    if condition_key == "limpio":
        return document
    if condition_key == "corrupto":
        return unicode_corruption(document)
    if condition_key == "latex":
        return latex_version(document)
    return document