# -*- coding: utf-8 -*-
"""
probe_arxiv_patched.py
======================
Corre el mismo pipeline EAR sobre los PDFs de arXiv, pero
inyectando el parche de TeX Glyph List en pdfminer antes de extraer.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# PASO CRÍTICO: el patch DEBE importarse antes que pdfplumber/pdfminer
sys.path.insert(0, str(Path(__file__).parent))
import tex_glyph_patch  # noqa: F401

# Importar las funciones de extracción y EAR ya definidas en probe_real.py
from probe_real import (
    extract_with_pdfplumber,
    extract_with_pymupdf,
    extract_with_pypdf,
    compute_ear,
    ALL_SYMBOLS,
    EXTRACTORS,
)

ROOT = Path(__file__).parent.parent
ARXIV_DIR = ROOT / "dataset-ragflow" / "corpus-ragflow" / "arxiv-harvested"
OUTPUT_JSON = ROOT / "deepdoc-research" / "arxiv_ear_patched_results.json"
OUTPUT_REPORT = ROOT / "deepdoc-research" / "arxiv_ear_patched_report.md"

# Sólo los 3 extractores principales
ACTIVE_EXTRACTORS = ["pdfplumber", "pymupdf", "pypdf"]

EXTRACTOR_FUNCS = {
    "pdfplumber": extract_with_pdfplumber,
    "pymupdf":    extract_with_pymupdf,
    "pypdf":      extract_with_pypdf,
}


def main():
    pdfs = sorted(ARXIV_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en {ARXIV_DIR}")
        return

    print(f"Corpus arXiv: {len(pdfs)} PDFs")
    print(f"Extrayendo con: {ACTIVE_EXTRACTORS} (PARCHE TEX_GLYPH APLICADO)")
    print("=" * 60)

    all_results = []
    symbol_failure_counts = {}

    for pdf_path in pdfs:
        doc_id = pdf_path.stem[:50]
        print(f"\n→ {doc_id}")

        texts = {}
        for ext_name in ACTIVE_EXTRACTORS:
            try:
                texts[ext_name] = EXTRACTOR_FUNCS[ext_name](pdf_path)
            except Exception as e:
                print(f"  [ERROR {ext_name}] {e}")
                texts[ext_name] = ""

        # Evaluar resultados contra la referencia (pypdf/pymupdf)
        per_symbol = {}
        discrepancies = []
        
        for char, name, codepoint in ALL_SYMBOLS:
            counts = {ext: texts[ext].count(char) for ext in ACTIVE_EXTRACTORS}
            pdfplumber_c = counts.get("pdfplumber", 0)
            ref_c = max(counts.get("pymupdf", 0), counts.get("pypdf", 0))
            
            if ref_c == 0 and pdfplumber_c == 0:
                status = "absent"
            elif pdfplumber_c == 0 and ref_c > 0:
                status = "still_failing"
                symbol_failure_counts[name] = symbol_failure_counts.get(name, 0) + 1
            elif pdfplumber_c >= ref_c:
                status = "resolved"
            elif pdfplumber_c > 0 and pdfplumber_c < ref_c:
                status = "partial"
            
            if pdfplumber_c > 0 and ref_c == 0:
                status = "exclusive_detection"
                
            per_symbol[name] = {
                "char": char, "codepoint": codepoint,
                "counts": counts, "status": status
            }

            if status in ("still_failing", "partial", "exclusive_detection"):
                discrepancies.append({"name": name, "char": char, "status": status, "counts": counts})

        present = [v for v in per_symbol.values() if v["status"] != "absent"]
        still_failing_count = sum(1 for v in present if v["status"] == "still_failing")
        resolved_count = sum(1 for v in present if v["status"] == "resolved")
        exclusive_count = sum(1 for v in present if v["status"] == "exclusive_detection")

        result = {
            "doc_id": doc_id,
            "per_symbol": per_symbol,
            "discrepancies": discrepancies,
            "summary": {
                "total_symbols_present": len(present),
                "resolved": resolved_count,
                "still_failing": still_failing_count,
                "exclusive": exclusive_count
            }
        }

        print(f"  Presentes: {len(present)} | Resueltos: {resolved_count} | "
              f"Aún fallando: {still_failing_count} | Exclusivos (pdfplumber): {exclusive_count}")
        all_results.append(result)

    # --- Reporte global ---
    docs_still_failing = sum(1 for r in all_results if r["summary"]["still_failing"] > 0)
    docs_with_exclusive = sum(1 for r in all_results if r["summary"]["exclusive"] > 0)
    total = len(all_results)

    # Qué tan seguido falla pdfplumber en cada símbolo
    failure_ranking = sorted(symbol_failure_counts.items(), key=lambda x: -x[1])

    report_lines = [
        "# Validación de Refactoring (Corpus arXiv)",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Total de PDFs analizados:** {total}  ",
        f"**PDFs que AÚN FALLAN:** {docs_still_failing} ({docs_still_failing/total*100:.0f}%)  ",
        f"**PDFs con EXCLUSIVAS (pdfplumber mejor que ref):** {docs_with_exclusive} ({docs_with_exclusive/total*100:.0f}%)  ",
        f"**Extractores:** `pdfplumber`, `pymupdf`, `pypdf`  ",
        "",
        "## Síntesis por documento",
        "",
        "| Documento | Símbolos | Resueltos | Siguen fallando | Exclusivos pdfplumber |",
        "|---|---|---|---|---|",
    ]

    for r in all_results:
        s = r["summary"]
        report_lines.append(
            f"| {r['doc_id'][:45]} | {s['total_symbols_present']} | {s['resolved']} | "
            f"{s['still_failing']} | {s['exclusive']} |"
        )

    report_lines += [
        "",
        "## Símbolos que SIGUEN fallando (0 en pdfplumber, >0 en ref)",
        "",
        "| Símbolo | Nombre | Docs con fallo pdfplumber | % de docs |",
        "|---|---|---|---|",
    ]

    # Obtener el char para cada nombre
    name_to_char = {name: char for char, name, _ in ALL_SYMBOLS}

    for sym_name, fail_count in failure_ranking:
        char = name_to_char.get(sym_name, "?")
        pct = fail_count / total * 100
        report_lines.append(f"| {char} | {sym_name} | {fail_count}/{total} | {pct:.0f}% |")

    report_lines += [
        "",
        "## Conclusión",
        "",
        "Con el parche ajustado (sin delimitadores), pdfplumber debería resolver los símbolos",
        "de TeX. Las 'exclusivas' indican que pdfplumber con patch es mejor que pypdf/pymupdf.",
    ]

    OUTPUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"PDFs que siguen fallando: {docs_still_failing}/{total} ({docs_still_failing/total*100:.0f}%)")
    print(f"PDFs con exclusivas: {docs_with_exclusive}/{total} ({docs_with_exclusive/total*100:.0f}%)")
    print(f"\nSímbolos más fallidos en pdfplumber:")
    for sym_name, fail_count in failure_ranking[:10]:
        char = name_to_char.get(sym_name, "?")
        print(f"  {char} {sym_name}: {fail_count}/{total} docs")
    print(f"\nReporte: {OUTPUT_REPORT.name}")


if __name__ == "__main__":
    main()
