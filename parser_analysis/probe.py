import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Rutas
ROOT = Path(__file__).parent.parent
DATASET_DIR = ROOT / "dataset-ragflow" / "simbolos-temas"
OUTPUT_DIR = ROOT / "deepdoc-research"

CORPUS = [
    ("01_matematica", "01-matematica.pdf", "01_matematica_content.txt"),
    ("02_logica", "02-logica.pdf", "02_logica_content.txt"),
    ("03_fisica", "03-fisica.pdf", "03_fisica_content.txt"),
    ("04_quimica", "04-quimica.pdf", "04_quimica_content.txt"),
    ("05_musica", "05-musica.pdf", "05_musica_content.txt"),
    ("06_literatura", "06-literatura.pdf", "06_literatura_content.txt"),
]

EXTRACTORS = ["pdfplumber", "pymupdf", "pypdf"]

CORE_SYMBOLS = [
    ("→", "ARROW_RIGHT", "U+2192"),
    ("∈", "ELEM_OF", "U+2208"),
    ("⊂", "SUBSET", "U+2282"),
    ("∞", "INFINITY", "U+221E"),
    ("±", "PLUS_MINUS", "U+00B1"),
    ("≤", "LEQ", "U+2264"),
    ("≥", "GEQ", "U+2265"),
    ("≠", "NEQ", "U+2260"),
    ("≈", "APPROX", "U+2248"),
    ("∂", "PARTIAL", "U+2202"),
    ("∇", "NABLA", "U+2207"),
    ("×", "CROSS", "U+00D7"),
]

DOMAIN_SYMBOLS = {
    "01_matematica": [
        ("∫", "INTEGRAL", "U+222B"), ("∑", "SUM", "U+2211"), ("∏", "PRODUCT", "U+220F"),
        ("√", "SQRT", "U+221A"), ("ℝ", "REALS", "U+211D"), ("ℤ", "INTEGERS", "U+2124"),
        ("ℕ", "NATURALS", "U+2115"), ("ℚ", "RATIONALS", "U+211A"), ("ℂ", "COMPLEX", "U+2102"),
        ("≡", "EQUIV", "U+2261"), ("∝", "PROPTO", "U+221D"), ("∬", "INTEGRAL2", "U+222C"),
        ("∮", "CONTOUR_INT", "U+222E"), ("∛", "CBRT", "U+221B"),
    ],
    "02_logica": [
        ("∀", "FOR_ALL", "U+2200"), ("∃", "EXISTS", "U+2203"), ("∄", "NOT_EXISTS", "U+2204"),
        ("¬", "NOT", "U+00AC"), ("∧", "AND", "U+2227"), ("∨", "OR", "U+2228"),
        ("↔", "IFF", "U+2194"), ("⊕", "XOR", "U+2295"), ("⊢", "TURNSTILE", "U+22A2"),
        ("⊨", "MODELS", "U+22A8"), ("⊆", "SUBSETEQ", "U+2286"), ("□", "NECESSARILY", "U+25A1"),
        ("◇", "POSSIBLY", "U+25C7"), ("⊤", "TOP", "U+22A4"), ("⊥", "BOTTOM", "U+22A5"),
    ],
    "03_fisica": [
        ("α", "ALPHA", "U+03B1"), ("β", "BETA", "U+03B2"), ("γ", "GAMMA", "U+03B3"),
        ("δ", "DELTA_LOWER", "U+03B4"), ("λ", "LAMBDA", "U+03BB"), ("μ", "MU", "U+03BC"),
        ("π", "PI", "U+03C0"), ("σ", "SIGMA_LOWER", "U+03C3"), ("φ", "PHI_LOWER", "U+03C6"),
        ("ω", "OMEGA_LOWER", "U+03C9"), ("Δ", "DELTA_UPPER", "U+0394"), ("Ω", "OHM", "U+03A9"),
        ("ħ", "HBAR", "U+0127"), ("∓", "MINUS_PLUS", "U+2213"),
    ],
    "04_quimica": [
        ("⇌", "EQUIL", "U+21CC"), ("⇒", "DOUBLE_ARROW", "U+21D2"), ("←", "ARROW_LEFT", "U+2190"),
        ("⟶", "LONG_ARROW", "U+27F6"), ("₀", "SUB0", "U+2080"), ("₁", "SUB1", "U+2081"),
        ("₂", "SUB2", "U+2082"), ("₃", "SUB3", "U+2083"), ("₄", "SUB4", "U+2084"),
        ("⁺", "SUP_PLUS", "U+207A"), ("⁻", "SUP_MINUS", "U+207B"), ("²", "SUP2", "U+00B2"),
        ("³", "SUP3", "U+00B3"), ("°", "DEGREE", "U+00B0"), ("Δ", "DELTA_UPPER", "U+0394"),
    ],
    "05_musica": [
        ("♯", "SHARP", "U+266F"), ("♭", "FLAT", "U+266D"), ("♮", "NATURAL", "U+266E"),
        ("♩", "QUARTER_NOTE", "U+2669"), ("♪", "EIGHTH_NOTE", "U+266A"),
        ("♫", "BEAMED_NOTES", "U+266B"), ("♬", "BEAMED_NOTES2", "U+266C"),
        ("𝄞", "TREBLE_CLEF", "U+1D11E"), ("𝄢", "BASS_CLEF", "U+1D122"),
        ("𝄪", "DOUBLE_SHARP", "U+1D12A"), ("𝄫", "DOUBLE_FLAT", "U+1D12B"),
    ],
    "06_literatura": [],
}

DANGEROUS_PAIRS = {
    "01_matematica": [
        ("ℝ", "R", "reals/letter-R"), ("ℤ", "Z", "integers/letter-Z"),
        ("ℕ", "N", "naturals/letter-N"), ("ℚ", "Q", "rationals/letter-Q"),
        ("ℂ", "C", "complex/letter-C"), ("≤", "<=", "leq/ascii"),
        ("≥", ">=", "geq/ascii"), ("≠", "!=", "neq/ascii"),
        ("≈", "~=", "approx/ascii"), ("√", "sqrt", "sqrt/text"),
    ],
    "02_logica": [
        ("→", "->", "implication/ascii"), ("↔", "<->", "biconditional/ascii"),
        ("∧", "^", "conjunction/caret"), ("∨", "v", "disjunction/letter-v"),
        ("¬", "~", "negation/tilde"), ("∈", "ε", "elem-of/epsilon"),
        ("⊢", "|-", "turnstile/ascii"), ("⊨", "|=", "models/ascii"),
        ("⊤", "T", "top/letter-T"), ("⊥", "F", "bottom/letter-F"),
    ],
    "03_fisica": [
        ("Ω", "ohm", "ohm/text"), ("μ", "u", "mu/letter-u"),
        ("λ", "l", "lambda/letter-l"), ("π", "pi", "pi/text"),
        ("Δ", "D", "delta/letter-D"), ("α", "a", "alpha/letter-a"),
        ("β", "b", "beta/letter-b"),
    ],
    "04_quimica": [
        ("⇌", "=", "equilibrium/equals"), ("⇌", "<=>", "equilibrium/ascii"),
        ("→", "->", "reaction/ascii"), ("₂", "2", "subscript2/digit"),
        ("₃", "3", "subscript3/digit"), ("⁺", "+", "superscript-plus/ascii"),
        ("⁻", "-", "superscript-minus/ascii"), ("°", "o", "degree/letter-o"),
    ],
    "05_musica": [
        ("♯", "#", "sharp/hash"), ("♭", "b", "flat/letter-b"),
        ("♮", "n", "natural/letter-n"),
    ],
    "06_literatura": [],
}

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
        import fitz
    except ImportError:
        print("  [SKIP pymupdf] fitz no instalado")
        return ""
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

EXTRACTOR_FUNCS = {
    "pdfplumber": extract_with_pdfplumber,
    "pymupdf": extract_with_pymupdf,
    "pypdf": extract_with_pypdf,
}

def analyze_extraction(doc_id: str, extractor: str, extracted: str, gt: str) -> dict:
    symbols_to_check = CORE_SYMBOLS + DOMAIN_SYMBOLS.get(doc_id, [])
    
    result = {
        "doc_id": doc_id,
        "extractor": extractor,
        "per_symbol": {},
        "dangerous_pairs": {},
        "domain_cpr": 0.0,
        "symbols_lost": [],
        "symbols_degraded": [],
        "symbols_perfect": [],
        "total_gt_symbols": 0,
        "total_ex_symbols": 0,
    }
    
    cprs = []
    
    for char, name, codepoint in symbols_to_check:
        gt_count = gt.count(char)
        if gt_count == 0:
            continue
            
        ex_count = extracted.count(char)
        cpr = round((ex_count / gt_count) * 100, 1)
        
        note = "SMP character — limited parser support expected" if len(char.encode("utf-32-be")) > 4 else ""
        
        result["per_symbol"][name] = {
            "char": char,
            "codepoint": codepoint,
            "gt_count": gt_count,
            "ex_count": ex_count,
            "cpr": cpr,
            "note": note
        }
        
        result["total_gt_symbols"] += gt_count
        result["total_ex_symbols"] += ex_count
        cprs.append(cpr)
        
        if cpr == 0:
            result["symbols_lost"].append(name)
        elif cpr < 100:
            result["symbols_degraded"].append(name)
        else:
            result["symbols_perfect"].append(name)
            
    if cprs:
        result["domain_cpr"] = round(sum(cprs) / len(cprs), 1)
        
    for char, sub, desc in DANGEROUS_PAIRS.get(doc_id, []):
        contexts = []
        for lineno, line in enumerate(extracted.split("\n"), 1):
            if sub in line:
                contexts.append({"line": lineno, "text": line.strip()[:120]})
            if len(contexts) >= 5:
                break
        if contexts:
            result["dangerous_pairs"][desc] = {
                "original": char,
                "substitution": sub,
                "occurrences": len(contexts),
                "contexts": contexts
            }
            
    return result

def generate_report(all_results: dict) -> str:
    md = [
        "# Benchmark de Preservación Simbólica — Extracción Base\n",
        "**Corpus:** 6 documentos (matemática, lógica, física, química, música, literatura)\n",
        "**Fase:** Baseline — Extracción de texto Unicode nativo\n",
        "**Extractores:** pdfplumber, PyMuPDF, pypdf\n",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "\n> **Nota metodológica:** pdfplumber es el motor interno de RAGFlow/DeepDoc para PDFs\n",
        "> con texto Unicode nativo. Sus resultados representan el **techo teórico de preservación**\n",
        "> de la capa de extracción. Si pdfplumber pierde un símbolo, DeepDoc tampoco puede recuperarlo.\n\n",
        "## 1. Tabla Resumen — Domain CPR por Documento\n\n",
        "| Documento | pdfplumber | PyMuPDF | pypdf |\n",
        "|---|---|---|---|"
    ]
    
    for doc_id in sorted(all_results.keys()):
        row = f"| {doc_id} "
        for ext in EXTRACTORS:
            cpr = all_results[doc_id].get(ext, {}).get("domain_cpr", "N/A")
            row += f"| {cpr}% "
        row += "|"
        md.append(row)
        
    md.extend(["\n## 2. Detalles (02_logica)\n", "| Símbolo | Nombre | GT Count | pdfplumber | PyMuPDF | pypdf |\n", "|---|---|---|---|---|---|"])
    
    logica_results = all_results.get("02_logica", {})
    if logica_results:
        plumber_syms = logica_results.get("pdfplumber", {}).get("per_symbol", {})
        for name, data in plumber_syms.items():
            char = data["char"]
            gt = data["gt_count"]
            row = f"| {char} | {name} | {gt} |"
            for ext in EXTRACTORS:
                ext_cpr = logica_results.get(ext, {}).get("per_symbol", {}).get(name, {}).get("cpr", "N/A")
                ext_count = logica_results.get(ext, {}).get("per_symbol", {}).get(name, {}).get("ex_count", "N/A")
                row += f" {ext_count} ({ext_cpr}%) |"
            md.append(row)
            
    return "\n".join(md)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {}
    
    for doc_id, pdf_file, gt_file in CORPUS:
        print(f"\n{'='*60}\nProcesando: {doc_id}")
        pdf_path = DATASET_DIR / pdf_file
        gt_path = DATASET_DIR / gt_file
        
        if not pdf_path.exists() or not gt_path.exists():
            print(f"  [SKIP] Archivos no encontrados")
            continue
            
        gt_text = gt_path.read_text(encoding="utf-8")
        doc_out = OUTPUT_DIR / "per_document" / doc_id
        doc_out.mkdir(parents=True, exist_ok=True)
        all_results[doc_id] = {}
        
        for ext in EXTRACTORS:
            print(f"  [{ext}]", end=" ", flush=True)
            extracted = EXTRACTOR_FUNCS[ext](pdf_path)
            
            (doc_out / f"{ext}_extracted.txt").write_text(extracted, encoding="utf-8")
            
            res = analyze_extraction(doc_id, ext, extracted, gt_text)
            all_results[doc_id][ext] = res
            
            print(f"Domain CPR: {res['domain_cpr']}%")
            
            (doc_out / f"{ext}_analysis.json").write_text(
                json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            
        (doc_out / "comparison.json").write_text(
            json.dumps(all_results[doc_id], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        
    (OUTPUT_DIR / "full_results.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    
    (OUTPUT_DIR / "summary_report.md").write_text(generate_report(all_results), encoding="utf-8")
    print(f"\n[OK] Reporte guardado en {OUTPUT_DIR}/summary_report.md")

if __name__ == "__main__":
    main()
