"""Estrategia TABLE_PLAIN — tabla de notación sin énfasis adicional.

Condición experimental: baseline con tabla.
La tabla aparece al inicio del user prompt con formato neutro, sin ninguna
instrucción de override. Es el punto de partida para comparar con las
estrategias I1-A a I1-D.
"""
from context_tables import build_table_content
from .base import PromptOutput, RESPUESTA_CORTA


class TablePlainStrategy:
    id    = "table_plain"
    label = "Tabla plana — sin énfasis"

    def build(
        self,
        fragment: dict,
        document_text: str,
        question: str,
    ) -> PromptOutput:
        table = build_table_content(fragment)
        user = (
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
