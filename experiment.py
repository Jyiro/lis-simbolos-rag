"""Coordinador del experimento — orquesta corpus × condiciones × backend.

Este módulo es puro de dominio: no sabe nada de HTTP ni de formatos de salida.
Recibe un backend y retorna una lista de ExperimentResult.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime

from corpus import FRAGMENTOS
from config import CONDICIONES, Condition
from corruption import build_condition, corrupt_question
from prompt_strategies import get_strategy
from backends.base import LLMBackend
from evaluator import evaluate_response, EvalResult, SemanticEvaluator


# ── Value Object de resultado ─────────────────────────────────────────────────

@dataclass
class ExperimentResult:
    """Un resultado experimental completo y auto-contenido.

    Diseñado para ser serializable a JSON directamente con asdict().
    Contiene toda la información necesaria para análisis post-hoc,
    reproducibilidad y escritura del paper.
    """

    # ── Identificación ────────────────────────────────────────────────────────
    run_id:          str
    model_id:        str
    backend_name:    str
    timestamp:       str

    # ── Fragmento ─────────────────────────────────────────────────────────────
    fragment_id:     str
    fragment_level:  str   # "alta" | "media" | "baja"
    fragment_domain: str
    critical_symbol: str

    # ── Condición ─────────────────────────────────────────────────────────────
    condition_label:  str
    doc_version:      str   # "limpio" | "corrupto" | "latex"
    strategy_id:      str
    strategy_label:   str
    corrupt_query:    bool

    # ── Documentos (todas las versiones, para referencia cruzada) ─────────────
    doc_limpio:   str
    doc_corrupto: str
    doc_latex:    str

    # ── Prompt (para reproducibilidad total) ──────────────────────────────────
    prompt_user:   str
    prompt_system: str | None
    question_used: str   # pregunta tal como se envió (posiblemente corrupta)

    # ── Respuesta ─────────────────────────────────────────────────────────────
    response:      str
    thinking_text: str    # razonamiento del modelo (vacío si thinking_mode=False)
    timing_ms:     float

    # ── Evaluación ─────────────────────────────────────────────────────────────────────
    eval_result:            str        # "✓ CORRECTO" | "✗ CONFUNDIDO" | "? SIN RESPUESTA"
    eval_matched_expected:  list[str]
    eval_matched_forbidden: list[str]
    eval_expected_terms:    list[str]
    eval_forbidden_terms:   list[str]

    # ── Métricas semánticas (None si el evaluador no está disponible) ─────────
    semantic_score:    float | None = None   # max cos_sim vs reference_answers (0–1)
    semantic_contrast: float | None = None   # semantic_score − cos_sim(wrong_ref) (−1–1)
    best_reference:    str   | None = None   # referencia correcta más cercana (debug)

    def to_dict(self) -> dict:
        return asdict(self)


# ── Runner principal ──────────────────────────────────────────────────────────

def correr_experimento(
    backend:            LLMBackend,
    modelo_id:          str,
    run_id:             str,
    thinking_mode:      bool = False,
    fragmentos_filter:  list[str] | None = None,
    condiciones_filter: list[str] | None = None,
) -> list[ExperimentResult]:
    """Corre el experimento completo y retorna los resultados estructurados.

    Args:
        backend:            Instancia de LLMBackend (llama_cpp u ollama).
        modelo_id:          ID del modelo en MODEL_REGISTRY (para logs).
        run_id:             Identificador único del run (timestamp).
        thinking_mode:      Si True, el modelo piensa antes de responder (Qwen3).
        fragmentos_filter:  Si se especifica, solo corre estos fragment IDs.
        condiciones_filter: Si se especifica, solo corre estas strategy IDs.

    Returns:
        Lista de ExperimentResult — una por cada combinación fragmento × condición.
    """
    timestamp = datetime.now().isoformat()
    backend_info = backend.info()

    # ── Instanciar el evaluador semántico (lazy-load, carga el modelo al primer uso) ──
    sem_evaluator = SemanticEvaluator()

    fragmentos = FRAGMENTOS
    if fragmentos_filter:
        fragmentos = [f for f in FRAGMENTOS if f["id"] in fragmentos_filter]
        if not fragmentos:
            raise ValueError(
                f"Ningún fragmento encontrado para el filtro: {fragmentos_filter}. "
                f"IDs disponibles: {[f['id'] for f in FRAGMENTOS]}"
            )

    condiciones = CONDICIONES
    if condiciones_filter:
        condiciones = [c for c in CONDICIONES if c.strategy_id in condiciones_filter]
        if not condiciones:
            raise ValueError(
                f"Ninguna condición encontrada para el filtro: {condiciones_filter}"
            )

    resultados: list[ExperimentResult] = []

    header = (
        f"\n{'='*72}\n"
        f"EXPERIMENTO FASE 1 — COMPRENSIÓN + INSTRUCTION HIERARCHY\n"
        f"Modelo:       {modelo_id}\n"
        f"Backend:      {backend_info.get('backend', '?')}\n"
        f"Thinking:     {'habilitado 🧠' if thinking_mode else 'deshabilitado ⚡'}\n"
        f"Run ID:       {run_id}\n"
        f"Fragmentos:   {len(fragmentos)} | Condiciones: {len(condiciones)}\n"
        f"{'='*72}\n"
    )
    print(header)

    for frag in fragmentos:
        print(f"\n{'─'*72}")
        print(f"📄 {frag['id']}  [{frag.get('level','?')}]  {frag.get('domain','')}")
        print(f"   Símbolo: {frag['critical_symbol']}")
        print(f"   Doc:     {frag['document']}")
        print(f"   Pregunta: {frag['question']}")

        # Pre-computar las tres versiones del documento
        doc_limpio   = frag["document"]
        doc_corrupto = build_condition(doc_limpio, "corrupto")
        doc_latex    = build_condition(doc_limpio, "latex")

        for cond in condiciones:
            # ── Construir texto del documento según la condición ───────────────────
            doc_text = build_condition(doc_limpio, cond.doc_version)

            # ── Corromper la pregunta si corresponde ───────────────────────────
            question = frag["question"]
            if cond.corrupt_query:
                question = corrupt_question(question)

            # ── Construir el prompt con la estrategia correspondiente ─────────────
            strategy = get_strategy(cond.strategy_id)
            prompt   = strategy.build(frag, doc_text, question)

            # ── Header de la condición ─────────────────────────────────────────
            sys_mark = " 🟣" if prompt.system_prompt else ""
            print(f"\n  [{cond.label}]{sys_mark}")

            # ── Callbacks de streaming dinámicos ─────────────────────────────────
            # Muestra 💭 si el modelo envía razonamiento (Qwen3) y → para la respuesta.
            thinking_started = [False]
            answer_started   = [False]

            def _on_thinking(t: str, _ts=thinking_started) -> None:
                if not _ts[0]:
                    print("   💭 ", end="", flush=True)
                    _ts[0] = True
                print(t, end="", flush=True)

            def _on_answer(t: str, _ts=thinking_started, _as=answer_started) -> None:
                if not _as[0]:
                    sep = "\n" if _ts[0] else ""
                    print(f"{sep}   → ", end="", flush=True)
                    _as[0] = True
                print(t, end="", flush=True)

            on_thinking_cb = _on_thinking
            on_token_cb    = _on_answer

            # ── Llamar al backend ─────────────────────────────────────────────────
            try:
                response = backend.query(
                    user_prompt=prompt.user_prompt,
                    system_prompt=prompt.system_prompt,
                    on_token=on_token_cb,
                    on_thinking_token=on_thinking_cb,
                )
                response_text = response.text
                response_thinking = response.thinking_text
                timing_ms     = response.timing_ms
            except Exception as exc:
                print(f"[ERROR: {exc}]", end="")
                response_text     = f"[ERROR: {exc}]"
                response_thinking = ""
                timing_ms         = 0.0

            # ── Evaluar y mostrar resultado ───────────────────────────────────
            eval_result = evaluate_response(
                response_text,
                frag["expected"],
                frag["forbidden"],
            )

            # ── Enriquecer con métricas semánticas (si el fragmento las tiene) ──────
            if frag.get("reference_answers") and frag.get("wrong_reference"):
                try:
                    sem_evaluator.enrich(
                        eval_result=eval_result,
                        response=response_text,
                        reference_answers=frag["reference_answers"],
                        wrong_reference=frag["wrong_reference"],
                    )
                except Exception as exc:
                    print(f"   [sem eval error: {exc}]", end="")

            print(f"\n   {eval_result.result}", end="")
            if eval_result.semantic_score is not None:
                contrast_icon = "🟢" if (eval_result.semantic_contrast or 0) >= 0 else "🔴"
                print(
                    f"  │ sem={eval_result.semantic_score:.2f} "
                    f"contrast={eval_result.semantic_contrast:+.2f}{contrast_icon}",
                    end="",
                )
            print()
            if eval_result.matched_forbidden:
                print(f"   ⚠️  forbidden: {eval_result.matched_forbidden}")

            # ── Registrar resultado ───────────────────────────────────────────
            resultados.append(ExperimentResult(
                run_id=run_id,
                model_id=modelo_id,
                backend_name=backend_info.get("backend", "?"),
                timestamp=timestamp,
                fragment_id=frag["id"],
                fragment_level=frag.get("level", "?"),
                fragment_domain=frag.get("domain", "?"),
                critical_symbol=frag["critical_symbol"],
                condition_label=cond.label,
                doc_version=cond.doc_version,
                strategy_id=cond.strategy_id,
                strategy_label=strategy.label,
                corrupt_query=cond.corrupt_query,
                doc_limpio=doc_limpio,
                doc_corrupto=doc_corrupto,
                doc_latex=doc_latex,
                prompt_user=prompt.user_prompt,
                prompt_system=prompt.system_prompt,
                question_used=question,
                response=response_text,
                thinking_text=response_thinking,
                timing_ms=timing_ms,
                eval_result=eval_result.result,
                eval_matched_expected=eval_result.matched_expected,
                eval_matched_forbidden=eval_result.matched_forbidden,
                eval_expected_terms=eval_result.expected_terms,
                eval_forbidden_terms=eval_result.forbidden_terms,
                semantic_score=eval_result.semantic_score,
                semantic_contrast=eval_result.semantic_contrast,
                best_reference=eval_result.best_reference,
            ))

    return resultados