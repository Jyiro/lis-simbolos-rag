"""Registry de estrategias de prompt — punto único de acceso.

Para agregar una nueva estrategia:
  1. Crear un archivo en prompt_strategies/ con la clase.
  2. Importarla y registrarla en REGISTRY.
  No hace falta tocar ningún otro archivo.

Uso:
    from prompt_strategies import get_strategy

    strategy = get_strategy("i1_d")
    output   = strategy.build(fragment, doc_text, question)
"""
from __future__ import annotations

from .base import PromptOutput, PromptStrategy
from .plain import PlainStrategy
from .table_plain import TablePlainStrategy
from .i1_a import I1AStrategy
from .i1_b import I1BStrategy
from .i1_c import I1CStrategy
from .i1_d import I1DStrategy

# ── Registry ──────────────────────────────────────────────────────────────────
REGISTRY: dict[str, PromptStrategy] = {
    s.id: s
    for s in [
        PlainStrategy(),
        TablePlainStrategy(),
        I1AStrategy(),
        I1BStrategy(),
        I1CStrategy(),
        I1DStrategy(),
    ]
}


def get_strategy(name: str) -> PromptStrategy:
    """Retorna la estrategia de prompt por nombre.

    Raises:
        ValueError: Si el nombre no está registrado.
    """
    if name not in REGISTRY:
        available = ", ".join(sorted(REGISTRY))
        raise ValueError(
            f"Estrategia '{name}' no registrada. Disponibles: {available}"
        )
    return REGISTRY[name]


def list_strategies() -> list[dict]:
    """Lista todas las estrategias con id y label."""
    return [{"id": s.id, "label": s.label} for s in REGISTRY.values()]


__all__ = [
    "PromptOutput",
    "PromptStrategy",
    "REGISTRY",
    "get_strategy",
    "list_strategies",
]
