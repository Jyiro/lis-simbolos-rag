"""Estrategia PLAIN — sin tabla de notación.

Condición experimental: baseline puro.
Corresponde a la variante A del experimento de Instruction Hierarchy:
  "Pregunta normal, sin contexto adicional."

El modelo solo tiene el documento (limpio, corrupto o LaTeX) y la pregunta.
"""
from .base import PromptOutput, RESPUESTA_CORTA


class PlainStrategy:
    id    = "plain"
    label = "Sin tabla — baseline puro"

    def build(
        self,
        fragment: dict,
        document_text: str,
        question: str,
    ) -> PromptOutput:
        user = (
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
