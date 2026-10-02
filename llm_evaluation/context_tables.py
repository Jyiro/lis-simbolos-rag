"""Tablas de corrupción y LaTeX, y constructor de contenido de tabla.

Este módulo tiene dos responsabilidades:
  1. Datos: CORRUPT_MAP y LATEX_MAP (mapeos símbolo ↔ versión alternativa).
  2. Contenido de tabla: build_table_content() retorna el texto de la tabla
     de notación para un fragmento — sin formato de énfasis (eso lo maneja
     cada estrategia en prompt_strategies/).

Ordenados por longitud descendente en los maps para evitar reemplazos
parciales (ej: "∃!" debe procesarse antes que "∃").
"""
from __future__ import annotations

CORRUPT_MAP: dict[str, str] = {
    # ── Alta frecuencia ───────────────────────────────────────────────────────
    "≥":   "â¥",
    "⟺":  "âŸº",
    "∀":   "â",
    "×":   "Ã",
    # ── Media frecuencia ──────────────────────────────────────────────────────
    "⇌":  "â‡Œ",
    "Å":   "Ã…",
    "□":   "â–¡",
    "∃!":  "â!",
    "⊂":   "âŠ‚",
    # ── Baja frecuencia ───────────────────────────────────────────────────────
    "æ":   "Ã¦",
    "·":   "Â·",
    "♭":   "â™­",
    "†":   "â\u00a0",
    # ── Auxiliares (aparecen en documentos del corpus) ────────────────────────
    "∃":   "â",
    "∈":   "â",
    "ℝ":   "â",
    "↔":   "âÃ",
    "→":   "â",
}

LATEX_MAP: dict[str, str] = {
    # ── Alta frecuencia ───────────────────────────────────────────────────────
    "≥":   r"\geq",
    "⟺":  r"\Longleftrightarrow",
    "∀":   r"\forall",
    "×":   r"\times",
    # ── Media frecuencia ──────────────────────────────────────────────────────
    "⇌":  r"\rightleftharpoons",
    "Å":   r"\text{\AA}",
    "□":   r"\Box",
    "∃!":  r"\exists!",
    "⊂":   r"\subset",
    # ── Baja frecuencia ───────────────────────────────────────────────────────
    "æ":   r"\ae",
    "·":   r"\cdot",
    "♭":   r"\flat",
    "†":   r"\dagger",
    # ── Auxiliares ────────────────────────────────────────────────────────────
    "∃":   r"\exists",
    "∈":   r"\in",
    "ℝ":   r"\mathbb{R}",
    "↔":   r"\leftrightarrow",
    "→":   r"\to",
}


def build_table_content(fragment: dict) -> str:
    """Construye el texto de la tabla de notación para un fragmento.

    Retorna solo el contenido (símbolo, variantes, definición) sin ningún
    prefijo de énfasis — el énfasis lo agrega cada estrategia de prompt.

    Args:
        fragment: Diccionario de un fragmento del corpus.

    Returns:
        String con la tabla de notación lista para insertar en un prompt.
    """
    sym      = fragment["critical_symbol"]
    defn     = fragment["context_definition"]
    corrupto = CORRUPT_MAP.get(sym, "?")
    latex    = LATEX_MAP.get(sym, r"\symbol{?}")

    return (
        f"Tabla de notación para este documento:\n"
        f"- '{sym}' (también puede aparecer como '{corrupto}' o '{latex}')\n"
        f"  {defn}"
    )


# ── Funciones de utilidad (usadas por corruption.py y prompt_strategies) ──────

def corrupt_symbol(text: str) -> str:
    """Reemplaza todos los símbolos conocidos por su versión corrupta (mojibake)."""
    out = text
    for orig, corrupt in sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(orig, corrupt)
    return out


def latex_symbol(text: str) -> str:
    """Reemplaza todos los símbolos conocidos por su representación LaTeX."""
    out = text
    for orig, latex in sorted(LATEX_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(orig, latex)
    return out