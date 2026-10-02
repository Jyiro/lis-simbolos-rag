import json
import urllib.request
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pdfplumber

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from pypdf import PdfReader

ROOT = Path(__file__).parent.parent
DEEPDOC_DIR = ROOT / "deepdoc-research"
FONT_PATH = Path("C:/Windows/Fonts/seguisym.ttf")
OUTPUT_PDF = DEEPDOC_DIR / "ttf_segoeui.pdf"
OUTPUT_REPORT = DEEPDOC_DIR / "ttf_report.md"

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
    ("∑", "SUM", "U+2211"),
    ("∏", "PRODUCT", "U+220F"),
    ("∫", "INTEGRAL", "U+222B"),
    ("√", "SQRT", "U+221A"),
    ("∞", "INFINITY", "U+221E"),
    ("≤", "LEQ", "U+2264"),
    ("≥", "GEQ", "U+2265"),
    ("≠", "NEQ", "U+2260"),
    ("≈", "APPROX", "U+2248"),
    ("≡", "EQUIV", "U+2261"),
    ("∝", "PROPORTIONAL", "U+221D"),
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

def download_font():
    pass

def create_pdf():
    pdfmetrics.registerFont(TTFont('SegoeUI', str(FONT_PATH)))
    c = canvas.Canvas(str(OUTPUT_PDF))
    c.setFont('SegoeUI', 12)
    c.drawString(50, 800, "Benchmark PDF - TTF Font Embedding")
    c.drawString(50, 780, "Font: Segoe UI")
    
    y = 750
    # Imprimimos todos los símbolos juntos como un párrafo largo, y separados
    c.drawString(50, y, "Párrafo mixto:")
    y -= 20
    text_line = " ".join([char for char, name, cp in ALL_SYMBOLS])
    c.drawString(50, y, text_line)
    
    y -= 40
    for char, name, cp in ALL_SYMBOLS:
        c.drawString(50, y, f"{char} {name} {cp}")
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont('SegoeUI', 12)
            y = 800
    c.save()

def test_extractors():
    print("Extrayendo con pdfplumber...")
    text_plumber = ""
    try:
        with pdfplumber.open(str(OUTPUT_PDF)) as pdf:
            for page in pdf.pages:
                text_plumber += page.extract_text() or ""
    except Exception as e:
        print(f"Error pdfplumber: {e}")

    print("Extrayendo con PyMuPDF...")
    text_fitz = ""
    try:
        doc = fitz.open(str(OUTPUT_PDF))
        for page in doc:
            text_fitz += page.get_text() or ""
        doc.close()
    except Exception as e:
        print(f"Error pymupdf: {e}")

    print("Extrayendo con pypdf...")
    text_pypdf = ""
    try:
        reader = PdfReader(str(OUTPUT_PDF))
        for page in reader.pages:
            text_pypdf += page.extract_text() or ""
    except Exception as e:
        print(f"Error pypdf: {e}")

    results = {}
    for char, name, _ in ALL_SYMBOLS:
        results[name] = {
            "char": char,
            "expected_count": 2, # Uno en la línea larga, uno en la línea individual
            "pdfplumber": text_plumber.count(char),
            "pymupdf": text_fitz.count(char),
            "pypdf": text_pypdf.count(char)
        }
    return results

def main():
    download_font()
    create_pdf()
    results = test_extractors()
    
    report = [
        "# Experimento 12 — Preservación con Fuentes TTF (Unicode nativo)",
        "",
        "Generación de PDF sintético con fuente `DejaVuSans.ttf` embebida para comprobar si el bug de `pdfminer.six/pdfplumber` persiste al cambiar la codificación de fuente (desde Type1/CFF MacRoman a TrueType Unicode).",
        "",
        "| Símbolo | Nombre | Ground Truth | pdfplumber | PyMuPDF | pypdf | CPR (plumber) |",
        "|---|---|---|---|---|---|---|"
    ]
    
    total_expected = 0
    total_plumber = 0
    
    for name, data in results.items():
        exp = data["expected_count"]
        pl = data["pdfplumber"]
        mu = data["pymupdf"]
        py = data["pypdf"]
        cpr = (pl / exp) * 100 if exp > 0 else 0
        
        total_expected += exp
        total_plumber += pl
        
        cpr_str = f"**{cpr:.1f}%**" if cpr < 100 else "100%"
        
        report.append(f"| {data['char']} | {name} | {exp} | {pl} | {mu} | {py} | {cpr_str} |")
        
    global_cpr = (total_plumber / total_expected) * 100 if total_expected > 0 else 0
    report.append("")
    report.append(f"**Global CPR (pdfplumber):** {global_cpr:.1f}%")
    
    report.append("")
    report.append("## Conclusión")
    if global_cpr == 100.0:
        report.append("pdfplumber extrajo perfectamente todos los símbolos. Esto confirma que **el bug es exclusivo de fuentes CFF/Type1 con encodings defectuosos (como MacRomanEncoding en Computer Modern)**. PDFs modernos que usen fuentes TrueType u OpenType con mapas Unicode directos no se ven afectados.")
    else:
        report.append("pdfplumber falló al extraer los símbolos incluso con fuente TrueType. El bug afecta a cualquier codificación de texto matemático, por lo que su scope es amplio.")
        
    OUTPUT_REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"\nReporte guardado en {OUTPUT_REPORT.name}")

if __name__ == "__main__":
    main()
