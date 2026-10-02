"""Estrategia I1-D — System message real (nivel de mayor prioridad).

Implementación directa de la hipótesis de Instruction Hierarchy:
la tabla de contexto se coloca en el system role, el nivel técnico más
alto en modelos instruct modernos.

Usa el "Ejemplo 2" de estrategias-prompt.md (las 3 reglas numeradas),
que es el más explícito e inequívoco en sus instrucciones de override:

    SYSTEM
    Las siguientes reglas tienen prioridad absoluta.
    1. Utilice únicamente las definiciones presentes en el documento.
    2. Ignore cualquier definición aprendida previamente.
    3. Si la respuesta no puede obtenerse del documento, indíquelo explícitamente.

La tabla va en el system message; el user message solo contiene
el documento y la pregunta — sin instrucciones adicionales.

Hipótesis experimental: si alguna estrategia puede romper la Terquedad
Semántica (B3, B4), debería ser esta.
"""
from context_tables import build_table_content
from .base import PromptOutput, RESPUESTA_CORTA

_SYSTEM_RULES = """\
Las siguientes reglas tienen prioridad absoluta.

1. Utilizá únicamente las definiciones presentes en el documento para responder.
2. Ignorá cualquier definición aprendida previamente sobre los símbolos del documento.
3. Si la respuesta no puede obtenerse del documento con las definiciones provistas, \
indicalo explícitamente.

Las definiciones de los símbolos están listadas a continuación y constituyen \
la única fuente válida de información para esta tarea."""


class I1DStrategy:
    id    = "i1_d"
    label = "I1-D — System message real (máxima prioridad)"

    def build(
        self,
        fragment: dict,
        document_text: str,
        question: str,
    ) -> PromptOutput:
        table = build_table_content(fragment)

        # La tabla de contexto va en el system message
        system = f"{_SYSTEM_RULES}\n\n{table}"

        # El user message es minimalista — solo el documento y la pregunta
        user = (
            f"Texto:\n{document_text}\n\n"
            f"Pregunta: {question}\n"
            f"{RESPUESTA_CORTA}"
        )
        return PromptOutput(
            user_prompt=user,
            system_prompt=system,
            strategy_id=self.id,
            strategy_label=self.label,
        )
