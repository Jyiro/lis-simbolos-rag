"""Experimento de Reconstrucción — ¿Puede el LLM decodificar Mojibake con una tabla?

A diferencia del test ECHO (que prueba fidelidad ciega), este experimento pone al
LLM en el rol de 'decodificador activo': se le entrega texto con MÚLTIPLES puntos de
corrupción simultáneos y una tabla de sustitución completa, y se le pide que
reconstruya el texto limpio original.

Métricas:
  - Distancia de Levenshtein (caracteres que difieren del original limpio)
  - CER — Character Error Rate (distancia normalizada, 0.0 = perfecto)
  - Reconstrucción exacta (bool)
  - Símbolos reconstruidos correctamente (por símbolo)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backends.base import LLMBackend

from config import RESULTS_DIR
from context_tables import CORRUPT_MAP
from echo_experiment import levenshtein_distance

REBUILD_RESULTS_DIR = "results_rebuild"

# ── Corpus del experimento (Español) ─────────────────────────────────────────
# Frases que contienen MÚLTIPLES símbolos del CORRUPT_MAP al mismo tiempo.
# Cada entrada tiene:
#   clean     : el texto limpio original
#   domain    : dominio académico para contextualizar
#   symbols   : los símbolos críticos presentes (subset de CORRUPT_MAP.keys())

REBUILD_CORPUS: list[dict] = [
    {
        "id": "R1_logica_modal",
        "domain": "Lógica Modal",
        "clean": "Si □P → P y □Q → Q, entonces □(P → Q) → (□P → □Q)",
        "symbols": ["□", "→"],
        "notes": "Axioma K de lógica modal con operador de necesidad",
    },
    {
        "id": "R2_calculo_integral",
        "domain": "Cálculo",
        "clean": "∀x ∈ ℝ: si f(x) ≥ 0, entonces f × g es continua",
        "symbols": ["∀", "∈", "ℝ", "≥", "×"],
        "notes": "Enunciado con cuantificador universal, membership, reales y producto",
    },
    {
        "id": "R3_conjuntos",
        "domain": "Teoría de Conjuntos",
        "clean": "A ⊂ B si y solo si ∀x: x ∈ A → x ∈ B",
        "symbols": ["⊂", "∀", "∈", "→"],
        "notes": "Definición formal de subconjunto con cuantificador universal",
    },
    {
        "id": "R4_fisica_optica",
        "domain": "Física / Óptica",
        "clean": "La longitud de onda λ = 550 Å satisface λ ≥ λ_min donde λ_min = 400 Å",
        "symbols": ["Å", "≥"],
        "notes": "Expresión con Ångström y operador mayor-igual",
    },
    {
        "id": "R5_quimica",
        "domain": "Química",
        "clean": "La reacción A + B ⇌ C es reversible si ∃! equilibrio donde A × B = C",
        "symbols": ["⇌", "∃!", "×"],
        "notes": "Equilibrio químico con existencia única y producto de concentraciones",
    },
    {
        "id": "R6_logica_pred",
        "domain": "Lógica de Predicados",
        "clean": "∀x ∈ ℝ: ∃! y tal que x → y y y ↔ x ≥ 0",
        "symbols": ["∀", "∈", "ℝ", "∃!", "→", "↔", "≥"],
        "notes": "Enunciado máximamente denso — 7 símbolos simultáneos",
    },
    {
        "id": "R7_musica_filologia",
        "domain": "Música / Filología",
        "clean": "La escala comienza en si♭ · omnia †vincit† amor",
        "symbols": ["♭", "·", "†"],
        "notes": "Símbolos de notación musical, interpunct y obelo filológico",
    },
]

REBUILD_CORPUS_EN: list[dict] = [
    {
        "id": "R1_modal_logic",
        "domain": "Modal Logic",
        "clean": "If □P → P and □Q → Q, then □(P → Q) → (□P → □Q)",
        "symbols": ["□", "→"],
        "notes": "Modal logic axiom K with necessity operator",
    },
    {
        "id": "R2_calculus",
        "domain": "Calculus",
        "clean": "∀x ∈ ℝ: if f(x) ≥ 0, then f × g is continuous",
        "symbols": ["∀", "∈", "ℝ", "≥", "×"],
        "notes": "Statement with universal quantifier, membership, reals and product",
    },
    {
        "id": "R3_set_theory",
        "domain": "Set Theory",
        "clean": "A ⊂ B if and only if ∀x: x ∈ A → x ∈ B",
        "symbols": ["⊂", "∀", "∈", "→"],
        "notes": "Formal definition of subset with universal quantifier",
    },
    {
        "id": "R4_optics",
        "domain": "Physics / Optics",
        "clean": "The wavelength λ = 550 Å satisfies λ ≥ λ_min where λ_min = 400 Å",
        "symbols": ["Å", "≥"],
        "notes": "Expression with Angstrom unit and greater-or-equal operator",
    },
    {
        "id": "R5_chemistry",
        "domain": "Chemistry",
        "clean": "The reaction A + B ⇌ C is reversible if ∃! equilibrium where A × B = C",
        "symbols": ["⇌", "∃!", "×"],
        "notes": "Chemical equilibrium with unique existence and concentration product",
    },
    {
        "id": "R6_predicate_logic",
        "domain": "Predicate Logic",
        "clean": "∀x ∈ ℝ: ∃! y such that x → y and y ↔ x ≥ 0",
        "symbols": ["∀", "∈", "ℝ", "∃!", "→", "↔", "≥"],
        "notes": "Maximum-density statement — 7 simultaneous symbols",
    },
    {
        "id": "R7_music_philology",
        "domain": "Music / Philology",
        "clean": "The scale starts on B♭ · omnia †vincit† amor",
        "symbols": ["♭", "·", "†"],
        "notes": "Musical flat, interpunct separator, and philological obelus",
    },
]


# ── Construcción de la tabla de decodificación ────────────────────────────────

def build_decode_table(symbols: list[str]) -> str:
    """Construye la tabla de sustitución corrupto→limpio para los símbolos usados."""
    lines = ["Tabla de decodificación de caracteres corruptos (Mojibake → Original):"]
    for sym in symbols:
        corrupt = CORRUPT_MAP.get(sym)
        if corrupt:
            lines.append(f"  '{corrupt}'  →  '{sym}'")
    return "\n".join(lines)


def build_full_decode_table() -> str:
    """Construye la tabla completa con TODOS los símbolos del CORRUPT_MAP."""
    lines = ["Tabla de decodificación completa de caracteres corruptos (Mojibake → Original):"]
    for orig, corrupt in sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0])):
        lines.append(f"  '{corrupt}'  →  '{orig}'")
    return "\n".join(lines)


# ── Prompts ─────────────────────────────────────────────────────────────────────
REBUILD_PROMPT_TEMPLATE = """\
El siguiente texto contiene caracteres corruptos (Mojibake) causados por un error \
de codificación UTF-8. Utilizá EXCLUSIVAMENTE la tabla de decodificación provista \
para reemplazar cada secuencia corrupta por su símbolo correcto.

{decode_table}

Texto corrupto a reconstruir:
{corrupt_text}

Respondé ÚNICAMENTE con el texto reconstruido, sin explicaciones, sin comillas, \
sin texto adicional."""

REBUILD_PROMPT_TEMPLATE_EN = """\
The following text contains corrupt characters (Mojibake) caused by a UTF-8 encoding error. \
Use EXCLUSIVELY the decoding table provided below to replace each corrupt sequence \
with its correct symbol.

{decode_table}

Corrupt text to reconstruct:
{corrupt_text}

Respond with ONLY the reconstructed text, no explanations, no quotes, \
no additional text."""

PROMPTS = {"es": REBUILD_PROMPT_TEMPLATE, "en": REBUILD_PROMPT_TEMPLATE_EN}
CORPORA = {"es": REBUILD_CORPUS, "en": REBUILD_CORPUS_EN}


# ── Dataclass de resultado ────────────────────────────────────────────────────

@dataclass
class RebuildResult:
    """Resultado de una prueba de reconstrucción."""
    run_id:           str
    model_id:         str
    backend_name:     str
    timestamp:        str

    lang:             str         # "es" | "en"
    fragment_id:      str
    domain:           str
    symbols_tested:   list[str]   # símbolos presentes en la frase

    clean_text:       str         # texto limpio original (ground truth)
    corrupt_text:     str         # texto enviado con mojibake
    prompt_sent:      str         # prompt completo

    response_raw:     str
    response_clean:   str

    levenshtein_dist:  int        # distancia absoluta al texto limpio
    cer:               float      # Character Error Rate (0.0 = perfecto)
    exact_match:       bool       # coincidencia exacta con el original
    eval_result:       str        # "PERFECTO" | "CASI" | "PARCIAL" | "FALLIDO"
    eval_detail:       str


# ── Evaluación ────────────────────────────────────────────────────────────────

def evaluate_rebuild(clean: str, response: str) -> tuple[int, float, bool, str, str]:
    """Evalúa la calidad de la reconstrucción."""
    dist = levenshtein_distance(clean.strip(), response.strip())
    max_len = max(len(clean.strip()), len(response.strip()))
    cer = dist / max_len if max_len > 0 else 1.0
    exact = dist == 0

    if exact:
        return dist, cer, exact, "PERFECTO", "Reconstrucción exacta del texto original."
    elif cer <= 0.05:
        return dist, cer, exact, "CASI", f"Reconstrucción casi perfecta (CER: {cer:.2f}, dist: {dist})."
    elif cer <= 0.30:
        return dist, cer, exact, "PARCIAL", f"Reconstrucción parcial — algunos símbolos fallaron (CER: {cer:.2f}, dist: {dist})."
    else:
        return dist, cer, exact, "FALLIDO", f"Reconstrucción fallida (CER: {cer:.2f}, dist: {dist})."


# ── Lógica del experimento ────────────────────────────────────────────────────

def corrupt_text(clean: str) -> str:
    """Aplica la corrupción Mojibake a todos los símbolos conocidos del texto."""
    out = clean
    for orig, corrupt in sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0])):
        out = out.replace(orig, corrupt)
    return out


def correr_rebuild(
    backend: "LLMBackend",
    modelo_id: str,
    run_id: str,
    tabla_completa: bool = False,
) -> list[RebuildResult]:
    """Ejecuta el experimento de reconstrucción en español e inglés.

    Itera ambos corpora (ES + EN) en un mismo run, produciendo 14 resultados.
    Cada resultado lleva el campo `lang` para identificar el idioma.
    """
    from datetime import datetime

    results: list[RebuildResult] = []
    tabla_label = "completa" if tabla_completa else "mínima (solo símbolos presentes)"

    all_runs = [
        ("es", REBUILD_CORPUS,    REBUILD_PROMPT_TEMPLATE,    "Español 🇪🇸"),
        ("en", REBUILD_CORPUS_EN, REBUILD_PROMPT_TEMPLATE_EN, "English 🇬🇧"),
    ]

    for lang, corpus, prompt_tmpl, lang_label in all_runs:
        total = len(corpus)
        print(f"\n{'='*60}")
        print(f"  {lang_label} — {total} fragmentos | Tabla: {tabla_label}")
        print(f"{'='*60}\n")

        for item in corpus:
            frag_id   = item["id"]
            clean     = item["clean"]
            symbols   = item["symbols"]
            corrupted = corrupt_text(clean)

            decode_table = (
                build_full_decode_table() if tabla_completa
                else build_decode_table(symbols)
            )
            prompt = prompt_tmpl.format(
                decode_table=decode_table,
                corrupt_text=corrupted,
            )

            print(f"  [{frag_id}] {item['domain']}")
            print(f"    Original: {clean}")
            print(f"    Corrupto: {corrupted}")

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
                    print(f"{sep}    → ", end="", flush=True)
                    _as[0] = True
                print(t, end="", flush=True)

            timestamp = datetime.now().isoformat()
            try:
                resp = backend.query(
                    user_prompt=prompt,
                    system_prompt=None,
                    on_token=_on_answer,
                    on_thinking_token=_on_thinking,
                )
                response_raw = resp.text
                print()
            except Exception as e:
                response_raw = f"[ERROR] {e}"
                print(f"\n    ❌ Error: {e}")

            response_clean = response_raw.strip()
            dist, cer, exact, eval_res, eval_det = evaluate_rebuild(clean, response_clean)

            icon = "✅" if exact else ("🟡" if cer <= 0.05 else ("🟠" if cer <= 0.30 else "❌"))
            print(f"    {icon} {eval_res} | dist={dist} | CER={cer:.2f}")
            print()

            results.append(RebuildResult(
                run_id=run_id,
                model_id=modelo_id,
                backend_name=backend.NAME,
                timestamp=timestamp,
                lang=lang,
                fragment_id=frag_id,
                domain=item["domain"],
                symbols_tested=symbols,
                clean_text=clean,
                corrupt_text=corrupted,
                prompt_sent=prompt,
                response_raw=response_raw,
                response_clean=response_clean,
                levenshtein_dist=dist,
                cer=cer,
                exact_match=exact,
                eval_result=eval_res,
                eval_detail=eval_det,
            ))

    return results


# ── Guardado de resultados ────────────────────────────────────────────────────

def save_rebuild_results(
    results: list[RebuildResult],
    run_id: str,
    modelo_id: str,
    backend_name: str,
) -> tuple[str, str, str]:
    """Guarda los resultados del experimento de reconstrucción en tres formatos."""
    run_dir = os.path.join(REBUILD_RESULTS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    json_path = os.path.join(run_dir, "rebuild_results.json")
    txt_path  = os.path.join(run_dir, "rebuild_summary.txt")
    md_path   = os.path.join(run_dir, "rebuild_report.md")

    # ── JSON ──────────────────────────────────────────────────────────────────
    es_results = [r for r in results if r.lang == "es"]
    en_results = [r for r in results if r.lang == "en"]
    payload = {
        "metadata": {
            "run_id":         run_id,
            "model_id":       modelo_id,
            "backend":        backend_name,
            "total_frags":    len(results),
            "exact_total":    sum(1 for r in results if r.exact_match),
            "avg_cer":        round(sum(r.cer for r in results) / len(results), 4) if results else 0,
            "avg_cer_es":     round(sum(r.cer for r in es_results) / len(es_results), 4) if es_results else 0,
            "avg_cer_en":     round(sum(r.cer for r in en_results) / len(en_results), 4) if en_results else 0,
            "exact_es":       sum(1 for r in es_results if r.exact_match),
            "exact_en":       sum(1 for r in en_results if r.exact_match),
        },
        "results": [asdict(r) for r in results],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ── TXT ───────────────────────────────────────────────────────────────────
    es_results = [r for r in results if r.lang == "es"]
    en_results = [r for r in results if r.lang == "en"]
    exact_count = sum(1 for r in results if r.exact_match)
    avg_cer     = sum(r.cer for r in results) / len(results) if results else 0
    avg_cer_es  = sum(r.cer for r in es_results) / len(es_results) if es_results else 0
    avg_cer_en  = sum(r.cer for r in en_results) / len(en_results) if en_results else 0

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"REPORTE RECONSTRUCCIÓN — {run_id}\n")
        f.write(f"{'='*90}\n")
        f.write(f"Modelo:  {modelo_id}   |   Backend: {backend_name}\n")
        f.write(f"Total exactos: {exact_count}/{len(results)}   |   CER global: {avg_cer:.3f}   |   CER es: {avg_cer_es:.3f}   |   CER en: {avg_cer_en:.3f}\n")
        f.write(f"{'='*90}\n")
        f.write(f"{'LANG':<5} {'ID':<22} {'SÍMBOLOS':<28} {'EVAL':<10} {'DIST':>5} {'CER':>6}\n")
        f.write(f"{'-'*90}\n")
        for r in results:
            syms = " ".join(r.symbols_tested)
            f.write(f"{r.lang.upper():<5} {r.fragment_id:<22} {syms:<28} {r.eval_result:<10} {r.levenshtein_dist:>5} {r.cer:>6.3f}\n")

        for lang_tag, lang_results, lang_name in [("es", es_results, "ESPAÑOL"), ("en", en_results, "ENGLISH")]:
            f.write(f"\n{'─'*90}\nDETALLE — {lang_name}\n{'─'*90}\n\n")
            for r in lang_results:
                f.write(f"[{r.fragment_id}] {r.domain}\n")
                f.write(f"  Símbolos: {' '.join(r.symbols_tested)}\n")
                f.write(f"  Original: {r.clean_text}\n")
                f.write(f"  Corrupto: {r.corrupt_text}\n")
                f.write(f"  LLM dijo: {r.response_clean}\n")
                f.write(f"  Resultado: {r.eval_result} — {r.eval_detail}\n\n")

    # ── Markdown ──────────────────────────────────────────────────────────────
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Reporte de Experimento — Reconstrucción de Mojibake (ES + EN)\n\n")
        f.write(f"| Campo | Valor |\n|---|---|\n")
        f.write(f"| Modelo | `{modelo_id}` |\n")
        f.write(f"| Backend | `{backend_name}` |\n")
        f.write(f"| Run ID | `{run_id}` |\n")
        f.write(f"| Total exactos | {exact_count}/{len(results)} |\n")
        f.write(f"| CER promedio global | {avg_cer:.3f} |\n")
        f.write(f"| CER promedio ES | {avg_cer_es:.3f} |\n")
        f.write(f"| CER promedio EN | {avg_cer_en:.3f} |\n\n")
        f.write(f"---\n\n## Resumen (todos los fragmentos)\n\n")
        f.write(f"| Lang | Fragmento | Dominio | Símbolos | Resultado | Dist | CER |\n")
        f.write(f"|:---:|---|---|---|:---:|---:|---:|\n")
        for r in results:
            syms = " ".join(f"`{s}`" for s in r.symbols_tested)
            icon = "✅" if r.exact_match else ("🟡" if r.cer <= 0.05 else ("🟠" if r.cer <= 0.30 else "❌"))
            lang_flag = "🇪🇸" if r.lang == "es" else "🇬🇧"
            f.write(f"| {lang_flag} | `{r.fragment_id}` | {r.domain} | {syms} | {icon} **{r.eval_result}** | {r.levenshtein_dist} | {r.cer:.3f} |\n")

        for lang_tag, lang_results, lang_name in [("es", es_results, "Español 🇪🇸"), ("en", en_results, "English 🇬🇧")]:
            f.write(f"\n---\n\n## Detalle — {lang_name}\n\n")
            for r in lang_results:
                icon = "✅" if r.exact_match else ("🟡" if r.cer <= 0.05 else ("🟠" if r.cer <= 0.30 else "❌"))
                f.write(f"### {icon} `{r.fragment_id}` — {r.domain}\n\n")
                f.write(f"**Símbolos probados:** {' '.join(f'`{s}`' for s in r.symbols_tested)}\n\n")
                f.write(f"| | Texto |\n|---|---|\n")
                f.write(f"| **Original** | `{r.clean_text}` |\n")
                f.write(f"| **Corrupto** | `{r.corrupt_text}` |\n")
                f.write(f"| **LLM reconstruyó** | `{r.response_clean}` |\n\n")
                f.write(f"> **{r.eval_result}** — {r.eval_detail}\n\n")

    return json_path, txt_path, md_path
