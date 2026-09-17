# -*- coding: utf-8 -*-
"""
probe_arxiv.py
==============
Corre el mismo pipeline EAR de probe_real.py sobre los 30 PDFs
descargados de arXiv por arxiv_harvest.py.

Genera:
  deepdoc-research/arxiv_ear_report.md   — resumen Markdown
  deepdoc-research/arxiv_ear_results.json — datos crudos

Uso:
    python deepdoc-research/probe_arxiv.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Importar las funciones de extracción y EAR ya definidas en probe_real.py
sys.path.insert(0, str(Path(__file__).parent))
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
OUTPUT_JSON = ROOT / "deepdoc-research" / "arxiv_ear_results.json"
OUTPUT_REPORT = ROOT / "deepdoc-research" / "arxiv_ear_report.md"

# Sólo los 3 extractores principales (pymupdf4llm ya descartado en Exp 10)
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
    print(f"Extrayendo con: {ACTIVE_EXTRACTORS}")
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

        # Calcular EAR directamente sobre los 3 extractores activos
        per_symbol = {}
        discrepancies = []

        for char, name, codepoint in ALL_SYMBOLS:
            counts = {ext: texts[ext].count(char) for ext in ACTIVE_EXTRACTORS}
            min_c = min(counts.values())
            max_c = max(counts.values())

            if max_c == 0:
                ear, status = None, "absent"
            elif min_c == max_c:
                ear, status = 100.0, "perfect"
            else:
                ear = round((min_c / max_c) * 100, 1)
                status = "discrepancy"
                discrepancies.append({"name": name, "char": char, "ear": ear, "counts": counts})

            per_symbol[name] = {
                "char": char, "codepoint": codepoint,
                "counts": counts, "ear": ear, "status": status
            }

            # Contar fallos explícitos de pdfplumber (0 donde los otros sí encuentran)
            if status == "discrepancy":
                ref = max(counts.get("pymupdf", 0), counts.get("pypdf", 0))
                if counts.get("pdfplumber", 0) == 0 and ref > 0:
                    symbol_failure_counts[name] = symbol_failure_counts.get(name, 0) + 1

        discrepancies.sort(key=lambda x: x["ear"])
        present = [v for v in per_symbol.values() if v["status"] != "absent"]
        disc = [v for v in present if v["status"] == "discrepancy"]

        mean_ear = round(sum(v["ear"] for v in disc) / len(disc), 1) if disc else 100.0
        worst = discrepancies[0] if discrepancies else None

        result = {
            "doc_id": doc_id,
            "per_symbol": per_symbol,
            "discrepancies": discrepancies,
            "summary": {
                "total_symbols_present": len(present),
                "discrepancies_count": len(disc),
                "mean_ear_of_discrepancies": mean_ear,
                "worst_symbol": worst["name"] if worst else None,
                "worst_ear": worst["ear"] if worst else 100.0,
            }
        }

        print(f"  Símbolos: {len(present)} | Discrepancias: {len(disc)} | "
              f"EAR medio: {mean_ear:.1f}% | "
              f"Peor: {worst['name'] if worst else '—'} ({worst['ear'] if worst else 100}%)")
        all_results.append(result)

    # --- Reporte global ---
    docs_with_discrepancies = sum(1 for r in all_results if r["summary"]["discrepancies_count"] > 0)
    total = len(all_results)

    # Qué tan seguido falla pdfplumber en cada símbolo (EAR=0 en ese doc)
    failure_ranking = sorted(symbol_failure_counts.items(), key=lambda x: -x[1])

    report_lines = [
        "# EAR sobre Corpus arXiv Expandido",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Total de PDFs analizados:** {total}  ",
        f"**PDFs con al menos una discrepancia:** {docs_with_discrepancies} ({docs_with_discrepancies/total*100:.0f}%)  ",
        f"**Extractores:** `pdfplumber`, `pymupdf`, `pypdf`  ",
        "",
        "## Síntesis por documento",
        "",
        "| Documento | Símbolos | Discrepancias | EAR medio | Peor símbolo | Peor EAR |",
        "|---|---|---|---|---|---|",
    ]

    for r in all_results:
        s = r["summary"]
        report_lines.append(
            f"| {r['doc_id'][:45]} | {s['total_symbols_present']} | {s['discrepancies_count']} | "
            f"{s['mean_ear_of_discrepancies']:.0f}% | {s['worst_symbol'] or '—'} | {s['worst_ear']}% |"
        )

    report_lines += [
        "",
        "## Síntesis por símbolo (frecuencia de fallo total en pdfplumber)",
        "",
        "Un 'fallo' se cuenta cuando pdfplumber extrae 0 ocurrencias de un símbolo",
        "que sí es detectado por pymupdf o pypdf en ese documento.",
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
        "Esta tabla permite confirmar si el patrón de fallo de `pdfplumber` observado en el corpus",
        "original (4 PDFs LaTeX) se generaliza estadísticamente al corpus ampliado de arXiv (30 PDFs).",
    ]

    OUTPUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"PDFs con discrepancias: {docs_with_discrepancies}/{total} ({docs_with_discrepancies/total*100:.0f}%)")
    print(f"\nSímbolos más fallidos en pdfplumber:")
    for sym_name, fail_count in failure_ranking[:10]:
        char = name_to_char.get(sym_name, "?")
        print(f"  {char} {sym_name}: {fail_count}/{total} docs")
    print(f"\nReporte: {OUTPUT_REPORT.name}")


if __name__ == "__main__":
    main()
