"""Estrategia I1-B — Override semántico explícito.

Corresponde a la Variante C del experimento de Instruction Hierarchy
(estrategias-prompt.md, sección "Posible experimento"):

    C) Las definiciones del documento reemplazan cualquier conocimiento previo.

Framing más fuerte que I1-A: no solo dice "usá el documento" sino que
establece explícitamente una relación de reemplazo entre el documento
y los pesos paramétricos del modelo.
"""
from context_tables import build_table_content
from .base import PromptOutput, RESPUESTA_CORTA

_PREFIX = (
    "Las definiciones presentes en el documento reemplazan cualquier conocimiento "
    "matemático, lógico o científico que hayas aprendido previamente.\n"
    "Si el documento define un símbolo de una manera que contradice tu entrenamiento, "
    "la definición del documento es la correcta."
)


class I1BStrategy:
    id    = "i1_b"
    label = "I1-B — Override semántico explícito"

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
