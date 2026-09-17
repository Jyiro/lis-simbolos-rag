import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
CORPUS_DIR = ROOT / "dataset-ragflow" / "corpus-ragflow"
OUTPUT_DIR = ROOT / "deepdoc-research" / "real_pdfs"

REAL_CORPUS = [
    ("AbstractAlgebra",            "abstract-algebra/AbstractAlgebra_cap1-3_symbols.pdf"),
    ("FirstOrderLogic",            "FirstOrderLogic_complete.pdf"),
    ("ModalLogicFundamentally",    "ModalLogicFundamentally_complete.pdf"),
    ("ModalLogicalNeuralNetworks", "ModalLogicalNeuralNetworks_complete.pdf"),
]

EXTRACTORS = ["pdfplumber", "pymupdf", "pypdf", "pymupdf4llm"]

ALL_SYMBOLS = [
    ("∀", "FOR_ALL", "U+2200"),
    ("∃", "EXISTS", "U+2203"),
    ("∄", "NOT_EXISTS", "U+2204"),
    ("¬", "NOT", "U+00AC"),
    ("∧", "AND", "U+2227"),
    ("∨", "OR", "U+2228"),
    ("→", "IMPLIES", "U+2192"),
    ("↔", "IFF", "U+2194"),
    ("⊢", "TURNSTILE", "U+22A2"),
    ("⊨", "MODELS", "U+22A8"),
    ("□", "NECESSARILY", "U+25A1"),
    ("◇", "POSSIBLY", "U+25C7"),
    ("⊤", "TOP", "U+22A4"),
    ("⊥", "BOTTOM", "U+22A5"),
    ("⊕", "XOR", "U+2295"),
    ("∈", "ELEM_OF", "U+2208"),
    ("∉", "NOT_ELEM", "U+2209"),
    ("⊂", "SUBSET", "U+2282"),
    ("⊆", "SUBSETEQ", "U+2286"),
    ("∅", "EMPTY_SET", "U+2205"),
    ("∩", "INTERSECT", "U+2229"),
    ("∪", "UNION", "U+222A"),
    ("ℝ", "REALS", "U+211D"),
    ("ℤ", "INTEGERS", "U+2124"),
    ("ℕ", "NATURALS", "U+2115"),
    ("ℚ", "RATIONALS", "U+211A"),
    ("ℂ", "COMPLEX", "U+2102"),
    ("∫", "INTEGRAL", "U+222B"),
    ("∑", "SUM", "U+2211"),
    ("∏", "PRODUCT", "U+220F"),
    ("√", "SQRT", "U+221A"),
    ("∞", "INFINITY", "U+221E"),
    ("≤", "LEQ", "U+2264"),
    ("≥", "GEQ", "U+2265"),
    ("≠", "NEQ", "U+2260"),
    ("≈", "APPROX", "U+2248"),
    ("≡", "EQUIV", "U+2261"),
    ("∂", "PARTIAL", "U+2202"),
    ("∇", "NABLA", "U+2207"),
    ("α", "ALPHA", "U+03B1"),
    ("β", "BETA", "U+03B2"),
    ("γ", "GAMMA", "U+03B3"),
    ("λ", "LAMBDA", "U+03BB"),
    ("μ", "MU", "U+03BC"),
    ("π", "PI", "U+03C0"),
    ("φ", "PHI", "U+03C6"),
    ("ψ", "PSI", "U+03C8"),
    ("ω", "OMEGA", "U+03C9"),
    ("Γ", "GAMMA_UP", "U+0393"),
    ("Δ", "DELTA_UP", "U+0394"),
    ("Σ", "SIGMA_UP", "U+03A3"),
    ("Φ", "PHI_UP", "U+03A6"),
]

def extract_with_pdfplumber(pdf_path: Path) -> str:
    import pdfplumber
    pages = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append(f"[PAGE {i+1}]\n{text}")
    except Exception as e:
        print(f"  [ERROR pdfplumber] {e}")
    return "\n\n".join(pages)

def extract_with_pymupdf(pdf_path: Path) -> str:
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            pages.append(f"[PAGE {i+1}]\n{text}")
        doc.close()
    except Exception as e:
        print(f"  [ERROR pymupdf] {e}")
    return "\n\n".join(pages)

def extract_with_pypdf(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  [SKIP pypdf] pypdf no instalado")
        return ""
    pages = []
    try:
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(f"[PAGE {i+1}]\n{text}")
    except Exception as e:
        print(f"  [ERROR pypdf] {e}")
    return "\n\n".join(pages)

def extract_with_pymupdf4llm(pdf_path: Path) -> str:
    try:
        import pymupdf4llm
    except ImportError:
        print("  [SKIP pymupdf4llm] pymupdf4llm no instalado")
        return ""
    try:
        text = pymupdf4llm.to_markdown(str(pdf_path))
    except Exception as e:
        print(f"  [ERROR pymupdf4llm] {e}")
        text = ""
    return text

EXTRACTOR_FUNCS = {
    "pdfplumber":  extract_with_pdfplumber,
    "pymupdf":     extract_with_pymupdf,
    "pypdf":       extract_with_pypdf,
    "pymupdf4llm": extract_with_pymupdf4llm,
}

def compute_ear(doc_id: str, texts: dict) -> dict:
    result = {
        "doc_id": doc_id,
        "per_symbol": {},
        "discrepancies": [],
        "summary": {}
    }

    for char, name, codepoint in ALL_SYMBOLS:
        counts = {ext: texts[ext].count(char) for ext in EXTRACTORS}
        min_c = min(counts.values())
        max_c = max(counts.values())

        if max_c == 0:
            ear, status = None, "absent"
        elif min_c == max_c:
            ear, status = 100.0, "perfect"
        else:
            ear = round((min_c / max_c) * 100, 1)
            status = "discrepancy"
            result["discrepancies"].append({
                "name": name, "char": char,
                "codepoint": codepoint,
                "ear": ear, "counts": counts
            })

        result["per_symbol"][name] = {
            "char": char, "codepoint": codepoint,
            "counts": counts, "min_count": min_c, "max_count": max_c,
            "ear": ear, "status": status
        }

    result["discrepancies"].sort(key=lambda x: x["ear"])

    present = [v for v in result["per_symbol"].values() if v["max_count"] > 0]
    disc    = [v for v in present if v["status"] == "discrepancy"]
    perfect = [v for v in present if v["status"] == "perfect"]

    result["summary"] = {
        "total_symbols_present": len(present),
        "perfect_agreements":    len(perfect),
        "discrepancies_count":   len(disc),
        "absent_count":          len(ALL_SYMBOLS) - len(present),
        "mean_ear_of_discrepancies": round(sum(v["ear"] for v in disc) / len(disc), 1) if disc else 100.0,
        "worst_symbol": result["discrepancies"][0]["name"] if result["discrepancies"] else None,
        "worst_ear":    result["discrepancies"][0]["ear"]  if result["discrepancies"] else 100.0,
    }

    return result

def find_lines_with_char(text: str, char: str, context: int = 1, max_hits: int = 3) -> list:
    lines = text.split("\n")
    results = []
    for i, line in enumerate(lines):
        if char in line:
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            snippet = "\n".join(lines[start:end]).strip()
            results.append({"line_no": i + 1, "snippet": snippet})
        if len(results) >= max_hits:
            break
    return results

def generate_real_report(all_results: dict) -> str:
    md = [
        "# Benchmark de Preservación Simbólica — EAR (Extractor Agreement Rate)",
        "",
        "**Fase:** 2 (PDFs Reales)",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "> **Extractor Agreement Rate (EAR)**: Mide el consenso entre extractores. EAR < 100% indica discrepancia,",
        "> evidenciando que la extracción base no es confiable para ese símbolo en ese documento. DeepDoc (RAGFlow)",
        "> hereda estas vulnerabilidades.",
        "",
        "## 1. Resumen Ejecutivo por PDF",
        "",
        "| Documento | Símbolos Presentes | Discrepancias | Peor Símbolo | Peor EAR |",
        "|---|---|---|---|---|"
    ]
    
    for doc_id, res in all_results.items():
        s = res["summary"]
        md.append(f"| {doc_id} | {s['total_symbols_present']} | {s['discrepancies_count']} | {s['worst_symbol'] or '-'} | {s['worst_ear']}% |")
        
    md.extend(["", "## 2. Tabla de EAR Cruzada", ""])
    
    # Encontrar qué símbolos están presentes en al menos un PDF
    present_symbols = []
    for name, data in all_results[list(all_results.keys())[0]]["per_symbol"].items():
        if any(all_results[d]["per_symbol"][name]["max_count"] > 0 for d in all_results):
            present_symbols.append((name, data["char"]))
            
    header = "| Símbolo | Nombre | " + " | ".join(all_results.keys()) + " |"
    sep = "|---|---| " + " | ".join(["---"] * len(all_results)) + " |"
    md.extend([header, sep])
    
    for name, char in present_symbols:
        row = f"| {char} | {name} |"
        for doc_id in all_results:
            ear = all_results[doc_id]["per_symbol"][name]["ear"]
            if ear is None:
                row += " — |"
            elif ear < 100:
                row += f" **{ear}%** |"
            else:
                row += f" 100% |"
        md.append(row)
        
    md.extend(["", "## 3. Detalles de Discrepancias", ""])
    for doc_id, res in all_results.items():
        if res["discrepancies"]:
            md.extend([f"### {doc_id}", ""])
            md.extend(["| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | pymupdf4llm | EAR |", "|---|---|---|---|---|---|---|"])
            for disc in res["discrepancies"]:
                c = disc["counts"]
                md.append(f"| {disc['char']} | {disc['name']} | {c['pdfplumber']} | {c['pymupdf']} | {c['pypdf']} | {c.get('pymupdf4llm', 0)} | **{disc['ear']}%** |")
            md.append("")
            
    return "\n".join(md)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {}

    for doc_id, pdf_file in REAL_CORPUS:
        print(f"\n{'='*60}\nProcesando: {doc_id}")
        pdf_path = CORPUS_DIR / pdf_file

        if not pdf_path.exists():
            print(f"  [SKIP] No encontrado: {pdf_path}")
            continue

        doc_out = OUTPUT_DIR / doc_id
        doc_out.mkdir(parents=True, exist_ok=True)

        texts = {}
        for ext in EXTRACTORS:
            print(f"  [{ext}]", end=" ", flush=True)
            texts[ext] = EXTRACTOR_FUNCS[ext](pdf_path)
            (doc_out / f"{ext}_extracted.txt").write_text(texts[ext], encoding="utf-8")
            print(f"{len(texts[ext])} chars")

        ear_result = compute_ear(doc_id, texts)
        all_results[doc_id] = ear_result
        (doc_out / "ear_analysis.json").write_text(
            json.dumps(ear_result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        diff_data = {}
        for disc in ear_result["discrepancies"][:3]:
            name, char = disc["name"], disc["char"]
            diff_data[name] = {
                ext: find_lines_with_char(texts[ext], char)
                for ext in EXTRACTORS
            }
        (doc_out / "disagreements.json").write_text(
            json.dumps(diff_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        s = ear_result["summary"]
        print(f"  -> Presentes: {s['total_symbols_present']} | "
              f"Perfectos: {s['perfect_agreements']} | "
              f"Discrepancias: {s['discrepancies_count']} | "
              f"Peor: {s['worst_symbol']} (EAR {s['worst_ear']}%)")

    report_dir = OUTPUT_DIR.parent
    (report_dir / "real_results.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (report_dir / "real_report.md").write_text(
        generate_real_report(all_results), encoding="utf-8"
    )
    print(f"\n[OK] real_report.md generado en {report_dir}")

if __name__ == "__main__":
    main()
