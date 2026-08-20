"""Protocolo y value objects para las estrategias de prompt.

Cada estrategia encapsula cómo se construye el prompt para una condición
experimental. Son stateless — no guardan estado entre llamadas.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class PromptOutput:
    """Salida de una estrategia de prompt.

    Contiene todo lo necesario para llamar a backend.query() y para
    loggear el prompt completo en los resultados.
    """

    user_prompt:    str
    system_prompt:  str | None  # None → no se usa el system role
    strategy_id:    str
    strategy_label: str


@runtime_checkable
class PromptStrategy(Protocol):
    """Protocolo que deben implementar todas las estrategias de prompt."""

    id:    str
    label: str

    def build(
        self,
        fragment: dict,
        document_text: str,
        question: str,
    ) -> PromptOutput:
        """Construye el prompt para un fragmento y versión de documento dados.

        Args:
            fragment:      Diccionario completo del fragmento (corpus.py).
            document_text: Texto del documento ya transformado (limpio/corrupto/latex).
            question:      Pregunta (ya posiblemente corrupta si la condición lo indica).

        Returns:
            PromptOutput con user_prompt, system_prompt y metadata de la estrategia.
        """
        ...


# Instrucción final compartida por todas las estrategias
RESPUESTA_CORTA = (
    "Respondé en una oración corta y directa. No expliques, solo respondé."
)
