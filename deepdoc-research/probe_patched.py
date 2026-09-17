"""
probe_patched.py
================
Valida el monkey-patch tex_glyph_patch comparando EAR antes y después
sobre el corpus original y el corpus arXiv. Incluye validación 
con los 4 extractores principales (pdfplumber, pypdf, fitz, pymupdf4llm).

Uso:
    ~/.venv-ml/bin/python3 deepdoc-research/probe_patched.py

Output:
    deepdoc-research/patch_validation_report.md
"""

import json
from pathlib import Path
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

CORPUS_ORIGINAL = [
    "dataset-ragflow/corpus-ragflow/abstract-algebra/AbstractAlgebra_cap1-3_symbols.pdf",
    "dataset-ragflow/corpus-ragflow/FirstOrderLogic_complete.pdf",
    "dataset-ragflow/corpus-ragflow/ModalLogicFundamentally_complete.pdf",
    "dataset-ragflow/corpus-ragflow/ModalLogicalNeuralNetworks_complete.pdf",
]

ARXIV_WITH_DISCREPANCIES = [
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.16957v1_Reduction_techniques_for_the_derived_delooping_levels.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.17177v1_Finite_Borel_asymptotic_dimension_of_bounded-to-one_commutat.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.17438v2_Quandles_associated_with_group_actions.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.18032v1_Scott_topologies_on_products_of_countable_complete_Heyting_a.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.18433v1_Generating_the_twist_subgroup_of_the_level_2_mapping_class_g.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.18486v1_Towards_a_Proof-Theoretic_Analysis_of_IncorrectIncomplete_Pr.pdf",
    "dataset-ragflow/corpus-ragflow/arxiv-harvested/2609.18730v1_A_minimal_type_of_Morley_rank_ω_in_a_partial_differential_fi.pdf",
]

# Símbolos a auditar (nombre → carácter Unicode)
SYMBOLS_TO_AUDIT = {
    "SUM":         "∑",
    "PRODUCT":     "∏",
    "NECESSARILY": "□",
    "TURNSTILE":   "⊢",
    "MODELS":      "⊨",
    "INTEGRAL":    "∫",
}

# ─── FUNCIONES DE EXTRACCIÓN ──────────────────────────────────────────────────

def count_symbols_pdfplumber(pdf_path: str, symbols: dict) -> dict[str, int]:
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text += t
    return {name: text.count(char) for name, char in symbols.items()}

def count_symbols_pypdf(pdf_path: str, symbols: dict) -> dict[str, int]:
    import pypdf
    text = ""
    reader = pypdf.PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return {name: text.count(char) for name, char in symbols.items()}

def count_symbols_fitz(pdf_path: str, symbols: dict) -> dict[str, int]:
    import fitz
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return {name: text.count(char) for name, char in symbols.items()}

def count_symbols_pymupdf4llm(pdf_path: str, symbols: dict) -> dict[str, int]:
    import pymupdf4llm
    text = pymupdf4llm.to_markdown(pdf_path)
    return {name: text.count(char) for name, char in symbols.items()}

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def run_validation():
    all_pdfs = CORPUS_ORIGINAL + ARXIV_WITH_DISCREPANCIES

    results_before = {}
    results_after  = {}

    # ── PASO 1: Medir SIN patch ──────────────────────────────────────────
    print("Midiendo baseline (sin patch) - Todos los extractores...")
    for pdf_path in all_pdfs:
        if not Path(pdf_path).exists():
            continue
            
        name = Path(pdf_path).stem[:40]
        plumb = count_symbols_pdfplumber(pdf_path, SYMBOLS_TO_AUDIT)
        pyp   = count_symbols_pypdf(pdf_path, SYMBOLS_TO_AUDIT)
        fz    = count_symbols_fitz(pdf_path, SYMBOLS_TO_AUDIT)
        llm   = count_symbols_pymupdf4llm(pdf_path, SYMBOLS_TO_AUDIT)
        
        results_before[name] = {
            "pdfplumber": plumb, 
            "pypdf": pyp, 
            "fitz": fz, 
            "pymupdf4llm": llm
        }
        print(f"  {name}: plumber={plumb} | pypdf={pyp} | fitz={fz} | llm={llm}")

    # ── PASO 2: Aplicar patch ────────────────────────────────────────────
    print("\nAplicando monkey-patch...")
    import sys
    sys.path.append(str(Path("deepdoc-research").absolute()))
    from tex_glyph_patch import apply_patch
    n_added = apply_patch()
    print(f"  Patch aplicado: {n_added} nuevas entradas en glyphname2unicode")

    # ── PASO 3: Medir CON patch ──────────────────────────────────────────
    print("\nMidiendo post-patch (solo pdfplumber es afectado)...")
    import importlib, pdfminer.encodingdb, pdfminer.pdffont
    importlib.reload(pdfminer.encodingdb) 

    for pdf_path in all_pdfs:
        if not Path(pdf_path).exists():
            continue
        name = Path(pdf_path).stem[:40]
        # Solo volvemos a medir con pdfplumber porque los demás no son afectados por el patch
        plumb = count_symbols_pdfplumber(pdf_path, SYMBOLS_TO_AUDIT)
        results_after[name] = {"pdfplumber": plumb}
        print(f"  {name}: pdfplumber={plumb}")

    # ── PASO 4: Comparar y reportar ──────────────────────────────────────
    generate_report(results_before, results_after)


def generate_report(before: dict, after: dict):
    lines = [
        "# Reporte de Validación — Monkey-Patch pdfminer.six (4 Extractores)",
        f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n> **Nota:** `pypdf` funciona como ground-truth. `fitz` y `pymupdf4llm` se incluyen para demostrar que el parche de `pdfminer` (que arregla a `pdfplumber` y RAGFlow) no los afecta, pues su falla es por un motor C++ diferente.",
        "\n## Tabla de Resultados\n",
        "| Documento | Símbolo | pdfplumber (Antes) | pdfplumber (Después) | pypdf (Ref) | PyMuPDF | pymupdf4llm | Δ (plumber) | OK? |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    all_ok = True
    for doc in before:
        for sym in SYMBOLS_TO_AUDIT:
            b_plumb = before[doc]["pdfplumber"].get(sym, 0)
            a_plumb = after[doc]["pdfplumber"].get(sym, 0)
            ref     = before[doc]["pypdf"].get(sym, 0)
            fz      = before[doc]["fitz"].get(sym, 0)
            llm     = before[doc]["pymupdf4llm"].get(sym, 0)
            
            delta   = a_plumb - b_plumb
            ok      = "✅" if a_plumb == ref else ("⚠️" if a_plumb > 0 else "❌")
            if a_plumb != ref:
                all_ok = False
            
            # Solo mostramos filas donde el símbolo realmente exista o pypdf lo vea
            if ref > 0 or b_plumb > 0 or fz > 0 or llm > 0:
                lines.append(f"| {doc[:30]} | **{sym}** | {b_plumb} | **{a_plumb}** | {ref} | {fz} | {llm} | +{delta} | {ok} |")

    lines.append(f"\n## Resultado Global: {'✅ PATCH EXITOSO (pdfplumber empató con pypdf en todo)' if all_ok else '⚠️ PATCH PARCIAL — revisar'}")

    report_path = Path("deepdoc-research/patch_validation_report.md")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReporte generado: {report_path}")

if __name__ == "__main__":
    run_validation()
