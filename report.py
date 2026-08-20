"""Generación de reportes en tres formatos: JSON, TXT y Markdown.

Cada corrida produce un directorio en results/<run_id>/ con:
  - results.json   → datos completos y estructurados (para análisis programático)
  - summary.txt    → resumen tabular legible (para revisión rápida en terminal)
  - report.md      → markdown con análisis (para presentaciones y borrador de paper)
"""
from __future__ import annotations

import json
import os
import math
from collections import defaultdict
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from experiment import ExperimentResult

from config import RESULTS_DIR


# ── Directorio de corrida ─────────────────────────────────────────────────────

def make_run_dir(run_id: str) -> str:
    """Crea y retorna el directorio para esta corrida."""
    path = os.path.join(RESULTS_DIR, run_id)
    os.makedirs(path, exist_ok=True)
    return path


# ── Formato 1: JSON completo ──────────────────────────────────────────────────

def save_json(
    results: list["ExperimentResult"],
    run_dir: str,
    modelo_id: str,
    backend_name: str,
) -> str:
    """Guarda el JSON completo con todos los resultados."""
    # Metadata del run (del primer resultado)
    first = results[0] if results else None
    run_meta = {
        "run_id":       first.run_id       if first else "?",
        "model_id":     modelo_id,
        "backend":      backend_name,
        "timestamp":    first.timestamp     if first else "?",
        "total_results": len(results),
    }

    payload = {
        "run": run_meta,
        "results": [r.to_dict() for r in results],
    }

    path = os.path.join(run_dir, "results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


# ── Formato 2: Resumen TXT ────────────────────────────────────────────────────

def _tabla_por_condicion(results: list["ExperimentResult"]) -> str:
    """Tabla de correctos/confundidos/sin_resp y promedios semánticos por condición."""
    por_condicion: dict[str, list["ExperimentResult"]] = defaultdict(list)
    for r in results:
        por_condicion[r.condition_label].append(r)

    lineas = [
        f"\n{'Condición':<30} {'✓ Cor':>7} {'✗ Con':>7} {'? Sin':>7} {'Total':>6} │ {'SemScore':>8} {'Contrast':>9}",
        "─" * 84,
    ]
    for label, evals in por_condicion.items():
        c = sum(1 for r in evals if "CORRECTO" in r.eval_result)
        x = sum(1 for r in evals if "CONFUNDIDO" in r.eval_result)
        s = sum(1 for r in evals if "SIN RESPUESTA" in r.eval_result)
        t = len(evals)
        
        sem = [r.semantic_score for r in evals if r.semantic_score is not None]
        avg_sem = sum(sem)/len(sem) if sem else float('nan')
        cont = [r.semantic_contrast for r in evals if r.semantic_contrast is not None]
        avg_cont = sum(cont)/len(cont) if cont else float('nan')
        
        sem_str = f"{avg_sem:.2f}" if not math.isnan(avg_sem) else "---"
        cont_str = f"{avg_cont:+.2f}" if not math.isnan(avg_cont) else "---"

        lineas.append(f"{label:<30} {c:>4}/{t:<2} {x:>4}/{t:<2} {s:>4}/{t:<2} {t:>6} │ {sem_str:>8} {cont_str:>9}")
    return "\n".join(lineas)


def _tabla_por_nivel(results: list["ExperimentResult"]) -> str:
    """Tabla de resultados en condición LIMPIO agrupada por nivel de frecuencia."""
    por_nivel: dict[str, list] = defaultdict(list)
    for r in results:
        if "LIMPIO" in r.condition_label:
            por_nivel[r.fragment_level].append(r.eval_result)

    lineas = ["\nPor nivel de frecuencia (condición LIMPIO):"]
    for nivel, evals in sorted(por_nivel.items()):
        c = evals.count("✓ CORRECTO")
        x = evals.count("✗ CONFUNDIDO")
        s = evals.count("? SIN RESPUESTA")
        t = len(evals)
        lineas.append(f"  {nivel:<6} → ✓{c}/{t}  ✗{x}/{t}  ?{s}/{t}")
    return "\n".join(lineas)


def _tabla_instruction_hierarchy(results: list["ExperimentResult"]) -> str:
    """Tabla comparativa de las condiciones Instruction Hierarchy."""
    ih_ids = {"table_plain", "i1_a", "i1_b", "i1_c", "i1_d"}
    ih_results = [r for r in results if r.strategy_id in ih_ids]
    if not ih_results:
        return ""

    por_estrategia: dict[str, list["ExperimentResult"]] = defaultdict(list)
    for r in ih_results:
        por_estrategia[r.strategy_id].append(r)

    lineas = ["\nInstruction Hierarchy — Resumen:"]
    for sid, evals in por_estrategia.items():
        c = sum(1 for r in evals if "CORRECTO" in r.eval_result)
        x = sum(1 for r in evals if "CONFUNDIDO" in r.eval_result)
        s = sum(1 for r in evals if "SIN RESPUESTA" in r.eval_result)
        t = len(evals)
        
        sem = [r.semantic_score for r in evals if r.semantic_score is not None]
        avg_sem = sum(sem)/len(sem) if sem else float('nan')
        sem_str = f"{avg_sem:.2f}" if not math.isnan(avg_sem) else "---"

        label = next((r.strategy_label for r in ih_results if r.strategy_id == sid), sid)
        lineas.append(f"  {label:<45} ✓{c}/{t}  ✗{x}/{t}  ?{s}/{t}  │ sem={sem_str}")
    return "\n".join(lineas)


def save_txt(
    results: list["ExperimentResult"],
    run_dir: str,
    modelo_id: str,
    backend_name: str,
) -> str:
    """Guarda el resumen TXT legible."""
    first = results[0] if results else None
    lines = [
        f"{'='*72}",
        f"EXPERIMENTO FASE 1 — COMPRENSIÓN + INSTRUCTION HIERARCHY",
        f"Modelo:    {modelo_id}",
        f"Backend:   {backend_name}",
        f"Run ID:    {first.run_id if first else '?'}",
        f"Timestamp: {first.timestamp if first else '?'}",
        f"{'='*72}",
    ]

    lines.append("\n" + "─"*72)
    lines.append("RESUMEN POR CONDICIÓN")
    lines.append(_tabla_por_condicion(results))
    lines.append(_tabla_por_nivel(results))
    lines.append(_tabla_instruction_hierarchy(results))

    lines.append("""
Categorías:
  ✓ CORRECTO      → respondió con al menos un término clave correcto
  ✗ CONFUNDIDO    → respondió con un término específicamente incorrecto
  ? SIN RESPUESTA → no dijo nada correcto ni incorrecto

Condiciones:
  LIMPIO    | sin tabla  → techo: modelo con símbolos perfectos
  DOC CORR  | sin tabla  → escenario RAG más común
  FULL CORR | doc✗ query✗ → peor caso total
  QUERY CORR| doc✓ query✗ → usuario con clipboard corrupto
  LATEX     | sin tabla  → notación LaTeX alternativa
  CON TABLA | plain      → tabla sin énfasis (baseline con tabla)
  I1-A      | énfasis simple    → "IMPORTANTE: usá el documento"
  I1-B      | override semántico → "las definiciones reemplazan tu conocimiento"
  I1-C      | rol simulado      → "[SISTEMA]" en user message
  I1-D      | system message    → system role real (máxima prioridad)
""")

    lines.append("\n" + "─"*72)
    lines.append("DETALLE POR FRAGMENTO")
    for frag_id in dict.fromkeys(r.fragment_id for r in results):
        frag_results = [r for r in results if r.fragment_id == frag_id]
        first_frag   = frag_results[0]
        lines.append(f"\n{'─'*40}")
        lines.append(f"📄 {frag_id}  [{first_frag.fragment_level}]  {first_frag.fragment_domain}")
        lines.append(f"   Símbolo: {first_frag.critical_symbol}")
        lines.append(f"   Doc limpio:   {first_frag.doc_limpio}")
        lines.append(f"   Doc corrupto: {first_frag.doc_corrupto}")
        for r in frag_results:
            sem_str = f" [sem={r.semantic_score:.2f}]" if r.semantic_score is not None else ""
            lines.append(
                f"  [{r.eval_result[0]}]{sem_str} {r.condition_label:<35} "
                f"→ \"{r.response[:80]}\""
            )

    path = os.path.join(run_dir, "summary.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── Formato 3: Markdown para presentaciones ───────────────────────────────────

def _icon(eval_result: str) -> str:
    if "CORRECTO"   in eval_result: return "✓"
    if "CONFUNDIDO" in eval_result: return "✗"
    return "?"


def save_markdown(
    results: list["ExperimentResult"],
    run_dir: str,
    modelo_id: str,
    backend_name: str,
) -> str:
    """Guarda el reporte Markdown para presentaciones y borrador de paper."""
    first = results[0] if results else None
    lines: list[str] = []
    A = lines.append

    A(f"# Reporte Experimento — Fase 1 + Instruction Hierarchy")
    A(f"")
    A(f"| Campo | Valor |")
    A(f"|-------|-------|")
    A(f"| Modelo | `{modelo_id}` |")
    A(f"| Backend | `{backend_name}` |")
    A(f"| Run ID | `{first.run_id if first else '?'}` |")
    A(f"| Timestamp | {first.timestamp if first else '?'} |")
    A(f"| Fragmentos | {len({r.fragment_id for r in results})} |")
    A(f"| Condiciones | {len({r.condition_label for r in results})} |")
    A(f"")
    A(f"---")

    # ── Tabla resumen por condición ───────────────────────────────────────────
    A(f"## Resumen por Condición")
    A(f"")
    A(f"| Condición | ✓ Correct | ✗ Confund | ? Sin resp | Total | SemScore | Contrast |")
    A(f"|-----------|----------:|----------:|-----------:|------:|---------:|---------:|")
    por_condicion: dict[str, list["ExperimentResult"]] = defaultdict(list)
    for r in results:
        por_condicion[r.condition_label].append(r)
    for label, evals in por_condicion.items():
        c = sum(1 for r in evals if "CORRECTO" in r.eval_result)
        x = sum(1 for r in evals if "CONFUNDIDO" in r.eval_result)
        s = sum(1 for r in evals if "SIN RESPUESTA" in r.eval_result)
        t = len(evals)
        
        sem = [r.semantic_score for r in evals if r.semantic_score is not None]
        avg_sem = sum(sem)/len(sem) if sem else float('nan')
        cont = [r.semantic_contrast for r in evals if r.semantic_contrast is not None]
        avg_cont = sum(cont)/len(cont) if cont else float('nan')
        
        sem_str = f"{avg_sem:.2f}" if not math.isnan(avg_sem) else "---"
        cont_str = f"{avg_cont:+.2f}" if not math.isnan(avg_cont) else "---"
        
        A(f"| `{label}` | {c}/{t} | {x}/{t} | {s}/{t} | {t} | {sem_str} | {cont_str} |")
    A(f"")

    # ── Instruction Hierarchy — análisis ──────────────────────────────────────
    ih_ids = {"table_plain", "i1_a", "i1_b", "i1_c", "i1_d"}
    ih_results = [r for r in results if r.strategy_id in ih_ids]
    if ih_results:
        A(f"---")
        A(f"## Instruction Hierarchy — Efecto por Estrategia")
        A(f"")
        A(f"> **Hipótesis:** estrategias de mayor jerarquía deberían aumentar la ")
        A(f"> fidelidad al contexto y disminuir el uso de conocimiento paramétrico.")
        A(f"")

        # Tabla: estrategia × fragmento
        frag_ids   = list(dict.fromkeys(r.fragment_id for r in ih_results))
        strat_ids  = list(dict.fromkeys(r.strategy_id for r in ih_results))
        strat_labels = {r.strategy_id: r.strategy_label for r in ih_results}

        header = "| Estrategia | " + " | ".join(frag_ids) + " | % Correcto |"
        sep    = "|" + "---|" * (len(frag_ids) + 2)
        A(header)
        A(sep)

        for sid in strat_ids:
            sr = [r for r in ih_results if r.strategy_id == sid]
            by_frag = {r.fragment_id: _icon(r.eval_result) for r in sr}
            cells = " | ".join(by_frag.get(fid, "—") for fid in frag_ids)
            correct_pct = int(
                sum(1 for r in sr if r.eval_result == "✓ CORRECTO") / len(sr) * 100
            ) if sr else 0
            A(f"| {strat_labels[sid]} | {cells} | {correct_pct}% |")
        A(f"")

    # ── Terquedad Semántica — análisis detallado ──────────────────────────────
    terquedad_ids = ["B3_modal", "B4_subconjunto"]
    terquedad_results = [r for r in results if r.fragment_id in terquedad_ids]
    if terquedad_results:
        A(f"---")
        A(f"## ⚡ Terquedad Semántica — Análisis de Casos")
        A(f"")
        A(f"> Fragmentos donde el modelo ignora la instrucción RAG y alucina")
        A(f"> basándose en sus pesos paramétricos.")
        A(f"")

        for frag_id in terquedad_ids:
            fr = [r for r in terquedad_results if r.fragment_id == frag_id]
            if not fr:
                continue
            first_fr = fr[0]
            A(f"### {frag_id}")
            A(f"")
            A(f"**Símbolo crítico:** `{first_fr.critical_symbol}`")
            A(f"**Dominio:** {first_fr.fragment_domain}")
            A(f"")
            A(f"| Doc limpio | Doc corrupto |")
            A(f"|------------|--------------|")
            A(f"| `{first_fr.doc_limpio}` | `{first_fr.doc_corrupto}` |")
            A(f"")
            A(f"| Condición | Resultado | Respuesta |")
            A(f"|-----------|-----------|-----------|")
            for r in fr:
                resp_short = r.response.replace("\n", " ")[:100]
                A(f"| {r.condition_label} | {r.eval_result} | {resp_short} |")
            A(f"")

    # ── Detalle por fragmento ─────────────────────────────────────────────────
    A(f"---")
    A(f"## Detalle por Fragmento")
    A(f"")

    condiciones_ord = list(dict.fromkeys(r.condition_label for r in results))
    for frag_id in dict.fromkeys(r.fragment_id for r in results):
        fr = [r for r in results if r.fragment_id == frag_id]
        fi = fr[0]
        A(f"### {frag_id}  *(nivel: {fi.fragment_level})*")
        A(f"")
        A(f"> **Dominio:** {fi.fragment_domain}  ")
        A(f"> **Símbolo:** `{fi.critical_symbol}`  ")
        A(f"> **Doc limpio:** `{fi.doc_limpio}`  ")
        A(f"> **Pregunta:** {fi.question_used}")
        A(f"")
        A(f"| Condición | Resultado | SemScore | Respuesta |")
        A(f"|-----------|:---------:|:--------:|-----------|")
        for cond_label in condiciones_ord:
            r = next((x for x in fr if x.condition_label == cond_label), None)
            if r is None:
                continue
            resp_short = r.response.replace("\n", " ")[:90]
            sem_str = f"{r.semantic_score:.2f}" if r.semantic_score is not None else "---"
            A(f"| `{cond_label}` | {r.eval_result} | {sem_str} | {resp_short} |")
        A(f"")

    path = os.path.join(run_dir, "report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── Entry point unificado ─────────────────────────────────────────────────────

def save_all(
    results: list["ExperimentResult"],
    run_id:  str,
    modelo_id:    str,
    backend_name: str,
) -> tuple[str, str, str]:
    """Guarda los tres formatos y retorna las rutas (json, txt, md)."""
    run_dir = make_run_dir(run_id)
    json_path = save_json(results, run_dir, modelo_id, backend_name)
    txt_path  = save_txt(results,  run_dir, modelo_id, backend_name)
    md_path   = save_markdown(results, run_dir, modelo_id, backend_name)
    return json_path, txt_path, md_path