"""Registry de backends — punto único de acceso para el resto del código.

Uso:
    from backends import get_backend

    backend = get_backend("llama_cpp")   # esta laptop
    backend = get_backend("ollama")      # PC de escritorio
"""
from __future__ import annotations

from .base import LLMBackend, LLMResponse
from .llama_cpp import LlamaCppBackend
from .ollama import OllamaBackend

# ── Registry ──────────────────────────────────────────────────────────────────
# Para agregar un backend nuevo: agregar la clase acá y al dict.
_REGISTRY: dict[str, type] = {
    "llama_cpp": LlamaCppBackend,
    "ollama":    OllamaBackend,
}


def get_backend(name: str, **kwargs) -> LLMBackend:
    """Factory: retorna una instancia del backend solicitado.

    Args:
        name:   Nombre del backend ("llama_cpp" | "ollama").
        **kwargs: Argumentos que se pasan al constructor del backend
                  (ej: base_url, model, temperature).

    Raises:
        ValueError: Si el nombre no está registrado.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Backend '{name}' no registrado. Disponibles: {available}"
        )
    return _REGISTRY[name](**kwargs)


def list_backends() -> list[str]:
    """Lista los nombres de backends registrados."""
    return sorted(_REGISTRY)


__all__ = [
    "LLMBackend",
    "LLMResponse",
    "get_backend",
    "list_backends",
]
