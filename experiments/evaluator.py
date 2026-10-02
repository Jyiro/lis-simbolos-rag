"""Evaluador de respuestas — retorna un EvalResult estructurado.

El evaluador tiene dos capas complementarias:
  1. Keyword matching (rápido, determinista) — clasificación principal CORRECTO/CONFUNDIDO/SIN_RESPUESTA.
  2. SemanticEvaluator (sentence-transformers) — dos métricas continuas:
       - semantic_score:    max(cos_sim(respuesta, ref) for ref in reference_answers)
                           Oracle match: tomamos la referencia correcta más cercana.
       - semantic_contrast: semantic_score - cos_sim(respuesta, wrong_reference)
                           Score contrastivo: positivo si el modelo se acercó más al polo
                           correcto que al incorrecto. Valores negativos indican confusión
                           semántica aunque el keyword eval no la detecte.

Limitaciones conocidas del keyword evaluator (falsos negativos por sinónimos) están
documentadas en investigacion.md. El SemanticEvaluator es el complemento robusto para
el análisis académico.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalResult:
    """Resultado estructurado de la evaluación de una respuesta.

    Incluye toda la información necesaria para análisis post-hoc:
    no solo el veredicto final, sino qué términos matchearon y
    las métricas semánticas continuas.
    """

    result:            str        # "✓ CORRECTO" | "✗ CONFUNDIDO" | "? SIN RESPUESTA"
    matched_expected:  list[str]  # términos esperados encontrados en la respuesta
    matched_forbidden: list[str]  # términos prohibidos encontrados en la respuesta
    expected_terms:    list[str]  # lista completa de términos esperados
    forbidden_terms:   list[str]  # lista completa de términos prohibidos

    # ── Métricas semánticas (float, -1.0 a 1.0) ──────────────────────────────
    # Rellenadas por SemanticEvaluator.enrich(); None si no se corrió el evaluador.
    semantic_score:    float | None = None
    semantic_contrast: float | None = None
    best_reference:    str | None   = None  # referencia correcta más cercana (para debug)

    @property
    def icon(self) -> str:
        """Ícono corto para tablas y logs."""
        if "CORRECTO"  in self.result: return "✓"
        if "CONFUNDIDO" in self.result: return "✗"
        return "?"

    @property
    def is_correct(self) -> bool:
        return "CORRECTO" in self.result

    @property
    def is_confused(self) -> bool:
        return "CONFUNDIDO" in self.result

    @property
    def is_no_answer(self) -> bool:
        return "SIN RESPUESTA" in self.result


def evaluate_response(
    response: str,
    expected: list[str],
    forbidden: list[str],
) -> EvalResult:
    """Evalúa una respuesta del modelo (capa 1: keyword matching).

    Lógica:
      - Si algún término prohibido aparece → CONFUNDIDO (peor caso)
      - Si ningún término esperado aparece → SIN RESPUESTA
      - Si al menos un término esperado aparece → CORRECTO

    La prioridad de CONFUNDIDO sobre CORRECTO es intencional: si el modelo
    dice algo correcto Y algo incorrecto, queremos capturar la confusión.

    Args:
        response: Texto de respuesta del modelo (se normaliza a lowercase).
        expected: Lista de términos que deben aparecer para considerar correcto.
        forbidden: Lista de términos que indican respuesta incorrecta.

    Returns:
        EvalResult con veredicto y términos matcheados.
        Los campos semantic_score/semantic_contrast son None hasta que
        se llame a SemanticEvaluator.enrich().
    """
    r = response.lower()

    matched_expected  = [t for t in expected  if t in r]
    matched_forbidden = [t for t in forbidden if t in r]

    if matched_forbidden:
        result = "✗ CONFUNDIDO"
    elif not matched_expected:
        result = "? SIN RESPUESTA"
    else:
        result = "✓ CORRECTO"

    return EvalResult(
        result=result,
        matched_expected=matched_expected,
        matched_forbidden=matched_forbidden,
        expected_terms=expected,
        forbidden_terms=forbidden,
    )


# ── Capa 2: Evaluador Semántico ───────────────────────────────────────────────

class SemanticEvaluator:
    """Evalúa respuestas usando similitud coseno sobre embeddings multilingüe.

    Usa paraphrase-multilingual-MiniLM-L12-v2 (cache en ~/.cache/huggingface/).
    Lazy-load: el modelo se carga solo cuando se llama a enrich() por primera vez.

    Métricas que produce:
      semantic_score:    max cosine similarity entre la respuesta y las reference_answers.
                         Oracle match — tomamos la referencia correcta más cercana.
                         Rango: 0.0 a 1.0.

      semantic_contrast: semantic_score - cos_sim(respuesta, wrong_reference).
                         Positivo → el modelo se acercó más al polo correcto.
                         Negativo → el modelo se acercó más al polo incorrecto
                                    (confusión semántica aunque keywords no la detecten).
                         Rango: -1.0 a 1.0.
    """

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self) -> None:
        self._model = None   # lazy-load

    def _load(self):
        """Carga el modelo la primera vez que se necesita."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.MODEL_NAME)
            except ImportError:
                raise ImportError(
                    "sentence-transformers no está instalado en este entorno. "
                    "Instalalo con: pip install sentence-transformers\n"
                    "Los modelos ya están en ~/.cache/huggingface/hub/"
                )

    def enrich(
        self,
        eval_result: EvalResult,
        response: str,
        reference_answers: list[str],
        wrong_reference: str,
    ) -> EvalResult:
        """Enriquece un EvalResult existente con las métricas semánticas.

        Args:
            eval_result:       EvalResult producido por evaluate_response().
            response:          Texto de respuesta del modelo.
            reference_answers: Lista de paráfrasis correctas del corpus.
            wrong_reference:   Respuesta incorrecta típica del corpus.

        Returns:
            El mismo EvalResult, con semantic_score, semantic_contrast y
            best_reference rellenados in-place.
        """
        self._load()

        from sentence_transformers import util

        all_texts = [response] + reference_answers + [wrong_reference]
        embeddings = self._model.encode(all_texts, convert_to_tensor=True)

        resp_emb   = embeddings[0]
        ref_embs   = embeddings[1 : 1 + len(reference_answers)]
        wrong_emb  = embeddings[-1]

        # Oracle match: max sobre todas las referencias correctas
        cos_scores    = [util.cos_sim(resp_emb, ref).item() for ref in ref_embs]
        best_idx      = int(max(range(len(cos_scores)), key=lambda i: cos_scores[i]))
        semantic_score = cos_scores[best_idx]

        # Score contrastivo
        wrong_score      = util.cos_sim(resp_emb, wrong_emb).item()
        semantic_contrast = semantic_score - wrong_score

        eval_result.semantic_score    = round(semantic_score, 4)
        eval_result.semantic_contrast = round(semantic_contrast, 4)
        eval_result.best_reference    = reference_answers[best_idx]

        return eval_result
