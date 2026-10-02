"""Estrategia I1-A — Énfasis simple con IMPORTANTE.

Corresponde a la Variante B del experimento de Instruction Hierarchy
(estrategias-prompt.md, sección "Posible experimento"):

    B) IMPORTANTE:
       Utilizá únicamente el documento.

La tabla sigue en el user prompt pero precedida de una instrucción
explícita de prioridad. Es el nivel más suave de override.
"""
from context_tables import build_table_content
from .base import PromptOutput, RESPUESTA_CORTA

_PREFIX = (
    "IMPORTANTE: Utilizá únicamente las definiciones del documento para responder.\n"
    "No uses conocimiento matemático, lógico o científico aprendido previamente."
)


class I1AStrategy:
    id    = "i1_a"
    label = "I1-A — Énfasis simple (IMPORTANTE)"

    def build(
        self,
        fragment: dict,
        document_text: str,
        question: str,
    ) -> PromptOutput:
        table = build_table_content(fragment)
        user = (
            f"{_PREFIX}\n\n"
            f"{table}\n\n"
            f"Texto:\n{document_text}\n\n"
            f"Pregunta: {question}\n"
            f"{RESPUESTA_CORTA}"
        )
        return PromptOutput(
            user_prompt=user,
            system_prompt=None,
            strategy_id=self.id,
            strategy_label=self.label,
        )
