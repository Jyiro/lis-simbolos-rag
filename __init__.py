"""Paquete del experimento RAG — Vulnerabilidades de Pipelines RAG
ante Corrupción de Caracteres Especiales.

Módulos principales:
  backends/         → LLMBackend Protocol + implementaciones (llama_cpp, ollama)
  prompt_strategies/ → PromptStrategy Protocol + implementaciones (plain, table_plain, i1_a..i1_d)
  corpus.py         → 12 fragmentos experimentales (3 niveles × 4 dominios)
  config.py         → Condition dataclass, MODEL_REGISTRY, CONDICIONES
  context_tables.py → CORRUPT_MAP, LATEX_MAP, build_table_content()
  corruption.py     → build_condition(), corrupt_question()
  evaluator.py      → EvalResult dataclass, evaluate_response()
  experiment.py     → ExperimentResult dataclass, correr_experimento()
  report.py         → save_all() → results/<run_id>/{results.json, summary.txt, report.md}
  main.py           → CLI con --modelo, --backend, --fragmentos, --condiciones
"""

__all__ = [
    "backends",
    "prompt_strategies",
    "config",
    "corpus",
    "context_tables",
    "corruption",
    "evaluator",
    "experiment",
    "report",
]
