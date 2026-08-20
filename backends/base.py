"""Backend protocol y value objects compartidos por todos los backends.

Programado contra interfaz — ningún módulo externo importa directamente
los backends concretos; siempre usan get_backend() de backends/__init__.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, runtime_checkable


@dataclass
class LLMResponse:
    """Respuesta estructurada de cualquier backend LLM."""

    text:         str    # respuesta visible (sin el bloque <think>)
    timing_ms:    float
    model:        str    # identificador del modelo (gguf_name u ollama_name)
    backend:      str    # "llama_cpp" | "ollama"
    thinking_text: str = ""  # razonamiento interno (vacío si thinking_mode=False)
    extra: dict = field(default_factory=dict)  # metadata específica del backend


@runtime_checkable
class LLMBackend(Protocol):
    """Protocolo que deben implementar todos los backends LLM.

    Cualquier clase que tenga estos tres métodos cumple el protocolo
    sin necesidad de heredar explícitamente.
    """

    def query(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        on_token: Callable[[str], None] | None = None,
        on_thinking_token: Callable[[str], None] | None = None,
    ) -> LLMResponse:
        """Envía un prompt y retorna una respuesta estructurada.

        Args:
            user_prompt:        Contenido del mensaje de usuario.
            system_prompt:      Contenido del mensaje de sistema (None → no se envía).
            on_token:           Callback invocado con cada token de respuesta visible.
                                Si es None, no se hace streaming de la respuesta.
            on_thinking_token:  Callback invocado con cada token de razonamiento.
                                Solo tiene efecto si thinking_mode=True.
                                Si es None, el razonamiento se captura pero no se muestra.

        Returns:
            LLMResponse con texto visible completo, texto de razonamiento, timing y metadata.
        """
        ...

    def health_check(self) -> bool:
        """Retorna True si el backend es alcanzable."""
        ...

    def info(self) -> dict:
        """Retorna metadata del backend: nombre, versión, modelo cargado."""
        ...
