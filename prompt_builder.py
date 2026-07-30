"""Construcción de prompts para el experimento."""

from context_tables import build_context_table, CORRUPT_MAP, LATEX_MAP

_CORRUPT_SORTED = sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0]))
_LATEX_SORTED   = sorted(LATEX_MAP.items(),   key=lambda x: -len(x[0]))


def _corrupt_question(question: str) -> str:
    out = question
    for orig, corrupt in _CORRUPT_SORTED:
        out = out.replace(orig, corrupt)
    return out


def _latex_question(question: str) -> str:
    out = question
    for orig, latex in _LATEX_SORTED:
        out = out.replace(orig, latex)
    return out


def build_prompt(
    fragment: dict,
    version_text: str,
    pregunta: str,
    con_tabla: bool,
    corrupt_question: bool = False,
) -> str:
    pregunta_final = _corrupt_question(pregunta) if corrupt_question else pregunta

    if con_tabla:
        tabla = build_context_table(fragment)
        prompt = (
            f"{tabla}\n\n"
            f"Texto:\n{version_text}\n\n"
            f"Pregunta: {pregunta_final}\n"
            f"Respondé en una oración corta y directa. No expliques, solo respondé."
        )
    else:
        prompt = (
            f"Texto:\n{version_text}\n\n"
            f"Pregunta: {pregunta_final}\n"
            f"Respondé en una oración corta y directa. No expliques, solo respondé."
        )

    return prompt