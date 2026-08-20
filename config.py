"""Configuración global del experimento — condiciones, modelos, backends.

Este archivo es la única fuente de verdad para:
  - Parámetros del LLM (temperatura, tokens)
  - URLs de los servidores
  - Registry de modelos
  - Lista de condiciones experimentales
"""
from __future__ import annotations

from dataclasses import dataclass

# ── Parámetros del LLM ────────────────────────────────────────────────────────
TEMPERATURE = 0      # determinista y reproducible
MAX_TOKENS  = 1024   # suficiente para thinking + respuesta (Qwen3)
RESULTS_DIR = "results"
ECHO_RESULTS_DIR = "results_echo"

# ── URLs de servidores ────────────────────────────────────────────────────────
LLAMA_CPP_URL = "http://localhost:8080"   # llama-server (esta laptop)
OLLAMA_URL    = "http://localhost:11434"  # Ollama (PC de escritorio)
MODELS_DIR    = "/home/jonas/llama.cpp/models"  # directorio de GGUFs

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_MODEL   = "qwen3.5-2b"
DEFAULT_BACKEND = "llama_cpp"


# ── Model Registry ────────────────────────────────────────────────────────────
@dataclass
class ModelConfig:
    """Configuración de un modelo — stub si available=False."""

    id:          str   # clave CLI (--modelo qwen3.5-2b)
    gguf_name:   str   # nombre del archivo sin .gguf
    ollama_name: str   # nombre en Ollama (PC de escritorio)
    available:   bool  # False = stub (pendiente de descarga)
    notes:       str = ""


MODEL_REGISTRY: dict[str, ModelConfig] = {
    "qwen3.5-2b": ModelConfig(
        id          = "qwen3.5-2b",
        gguf_name   = "Qwen3.5-2B-Q4_K_M",
        ollama_name = "qwen3.5:2b",
        available   = True,
        notes       = "Primer modelo disponible — llama.cpp",
    ),
    "qwen3.5-4b": ModelConfig(
        id          = "qwen3.5-4b",
        gguf_name   = "qwen3.5-4b-instruct-Q4_K_M",
        ollama_name = "qwen3.5:4b",
        available   = True,
        notes       = "Qwen3.5 4B Instruct Q4 — llama.cpp",
    ),
    "qwen3.5-9b": ModelConfig(
        id          = "qwen3.5-9b",
        gguf_name   = "Qwen3.5-9B-Q4_K_M",
        ollama_name = "qwen3.5:8b",
        available   = True,
        notes       = "Qwen3.5 9B Q4 — llama.cpp",
    ),
    "gemma-4b": ModelConfig(
        id          = "gemma-4b",
        gguf_name   = "gemma-4-E4B-it-qat-UD-Q4_K_XL",
        ollama_name = "gemma3:4b",
        available   = True,
        notes       = "Gemma 4B Instruct QAT — llama.cpp",
    ),
}


# ── Condiciones Experimentales ────────────────────────────────────────────────
@dataclass(frozen=True)
class Condition:
    """Una condición experimental — inmutable y hasheable.

    Cada condición define:
      - cómo se transforma el documento (doc_version)
      - qué estrategia de prompt se usa (strategy_id → prompt_strategies/)
      - si la query también se corrompe (corrupt_query)
    """

    label:         str   # etiqueta para logs y reportes
    doc_version:   str   # "limpio" | "corrupto" | "latex"
    strategy_id:   str   # clave en prompt_strategies.REGISTRY
    corrupt_query: bool = False


CONDICIONES: list[Condition] = [
    # ── Baselines ────────────────────────────────────────────────────────────
    Condition(
        label="LIMPIO    | sin tabla",
        doc_version="limpio",
        strategy_id="plain",
    ),
    Condition(
        label="DOC CORR  | sin tabla",
        doc_version="corrupto",
        strategy_id="plain",
    ),
    Condition(
        label="LATEX     | sin tabla",
        doc_version="latex",
        strategy_id="plain",
    ),
    # ── Con tabla ─────────────────────────────────────────────────────────────
    Condition(
        label="CON TABLA | plain",
        doc_version="corrupto",
        strategy_id="table_plain",
    ),
    # ── Instruction Hierarchy (estrategias-prompt.md) ─────────────────────────
    Condition(
        label="I1-A      | énfasis simple",
        doc_version="corrupto",
        strategy_id="i1_a",
    ),
    Condition(
        label="I1-B      | override semántico",
        doc_version="corrupto",
        strategy_id="i1_b",
    ),
    Condition(
        label="I1-C      | rol simulado en user",
        doc_version="corrupto",
        strategy_id="i1_c",
    ),
    Condition(
        label="I1-D      | system message real",
        doc_version="corrupto",
        strategy_id="i1_d",
    ),
]

# Condiciones disponibles pero excluidas del run por defecto.
# Se pueden agregar con: --condiciones full_corr query_corr
# (o descomentarlas acá para includirlas siempre)
_CONDICIONES_EXTRA: list[Condition] = [
    Condition(
        label="FULL CORR | doc✗ query✗",
        doc_version="corrupto",
        strategy_id="plain",
        corrupt_query=True,
    ),
    Condition(
        label="QUERY CORR| doc✓ query✗",
        doc_version="limpio",
        strategy_id="plain",
        corrupt_query=True,
    ),
]