"""Construcción de la tabla de contexto por fragmento."""

# Ordenados por longitud descendente en corrupt_text/latex_text para evitar
# reemplazos parciales (ej: "∃!" debe procesarse antes que "∃").
CORRUPT_MAP = {
    # — Alta frecuencia —
    "≥":  "â¥",
    "⟺":  "âŸº",
    "∀":  "â",
    "×":  "Ã",
    # — Media frecuencia —
    "⇌":  "â‡Œ",
    "Å":  "Ã…",
    "□":  "â–¡",
    "∃!": "â!",
    "⊂":  "âŠ‚",
    # — Baja frecuencia —
    "æ":  "Ã¦",
    "·":  "Â·",
    "♭":  "â™­",
    "†":  "â\u00a0",
    # — Auxiliares (aparecen en documentos del corpus) —
    "∃":  "â",
    "∈":  "â",
    "ℝ":  "â",
    "↔":  "âÃ",
    "→":  "â",
}

LATEX_MAP = {
    # — Alta frecuencia —
    "≥":  r"\geq",
    "⟺":  r"\Longleftrightarrow",
    "∀":  r"\forall",
    "×":  r"\times",
    # — Media frecuencia —
    "⇌":  r"\rightleftharpoons",
    "Å":  r"\text{\AA}",
    "□":  r"\Box",
    "∃!": r"\exists!",
    "⊂":  r"\subset",
    # — Baja frecuencia —
    "æ":  r"\ae",
    "·":  r"\cdot",
    "♭":  r"\flat",
    "†":  r"\dagger",
    # — Auxiliares —
    "∃":  r"\exists",
    "∈":  r"\in",
    "ℝ":  r"\mathbb{R}",
    "↔":  r"\leftrightarrow",
    "→":  r"\to",
}


def build_context_table(fragmento: dict) -> str:
    """Construye la tabla de contexto para un fragmento específico."""
    sym      = fragmento["critical_symbol"]
    defn     = fragmento["context_definition"]
    corrupto = CORRUPT_MAP.get(sym, "?")
    latex    = LATEX_MAP.get(sym, r"\symbol{?}")

    return (
        f"Tabla de notación para este documento:\n"
        f"- '{sym}' (también puede aparecer como '{corrupto}' o '{latex}')\n"
        f"  {defn}"
    )


def corrupt_text(text: str) -> str:
    """Reemplaza todos los símbolos conocidos por su versión corrupta."""
    out = text
    for orig, corrupt in sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(orig, corrupt)
    return out


def latex_text(text: str) -> str:
    """Reemplaza todos los símbolos conocidos por su representación LaTeX."""
    out = text
    for orig, latex in sorted(LATEX_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(orig, latex)
    return out