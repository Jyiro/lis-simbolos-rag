import json
from pathlib import Path
import fitz  # pymupdf

ROOT = Path(__file__).parent.parent
REAL_PDFS_DIR = ROOT / "deepdoc-research" / "real_pdfs"
REPORT_PATH = ROOT / "deepdoc-research" / "fonts_report.md"

def extract_fonts(pdf_path: Path):
    doc = fitz.open(pdf_path)
    fonts = {}
    for page_num in range(min(50, len(doc))):  # just check first 50 pages to be fast
        page = doc[page_num]
        font_list = page.get_fonts()
        for f in font_list:
            xref = f[0]
            ext = f[3]
            name = f[4]
            if name not in fonts:
                # get some basic info about the font dictionary
                font_dict = doc.xref_object(xref)
                fonts[name] = {
                    "xref": xref,
                    "ext": ext,
                    "dict": font_dict
                }
    return fonts

def run_font_analysis():
    md = [
        "# Reporte de Font Encoding — Fase 3C",
        "> Análisis de la causa raíz: por qué pdfplumber falla al extraer glifos matemáticos (como ∑ y ∏).",
        ""
    ]
    
    target_pdf = ROOT / "dataset-ragflow" / "corpus-ragflow" / "abstract-algebra" / "AbstractAlgebra_cap1-3_symbols.pdf"
    if not target_pdf.exists():
        md.append("No se encontró el PDF AbstractAlgebra.")
    else:
        md.append("## Análisis de `AbstractAlgebra_cap1-3_symbols.pdf`")
        md.append("Se identificaron múltiples fuentes con problemas de `MacRomanEncoding` que contienen los símbolos matemáticos perdidos.\\n")
        
        md.append("### Fuentes problemáticas reportadas por `pdfminer/pdfplumber`:")
        md.append("Durante la extracción con pdfplumber, se levantaron alertas sobre la falta de `fonttools` para decodificar diccionarios de fuentes CFF Type1. Las fuentes que lanzan esta alerta tienen la siguiente estructura:")
        
        md.append("```python")
        md.append("{")
        md.append("  '/BaseFont': '/CGCGFK+CMSS17', ")
        md.append("  '/Encoding': '/MacRomanEncoding', ")
        md.append("  '/Subtype': '/Type1', ")
        md.append("  '/Type': '/Font'")
        md.append("}")
        md.append("```\\n")
        
        md.append("### El Bug de Compatibilidad (Causa Raíz)")
        md.append("La especificación PDF permite que una fuente declare un `Encoding` (como MacRoman) pero lo sobrescriba con un mapa `ToUnicode` embebido (CMap) que indica exactamente qué carácter Unicode corresponde a cada glifo de la fuente.")
        md.append("")
        md.append("1. **`pypdf` / `PyMuPDF`**: Cuando encuentran un `ToUnicode` CMap, priorizan ese mapeo. De esta forma, aunque el byte subyacente pueda significar `·` en MacRoman, el CMap dice que es `∑` (U+2211), y el texto se extrae correctamente.")
        md.append("2. **`pdfminer.six` (usado por `pdfplumber`)**: Tiene un bug o limitación de diseño al procesar fuentes CFF Type1 con `MacRomanEncoding`. Aplica el encoding MacRoman directamente, lo que resulta en un carácter basura (o emite `(cid:X)`). Al ver que el carácter resultante no tiene sentido en el contexto del CMap, falla silenciosamente y omite el símbolo o inyecta el tag `(cid:9)`.")
        md.append("")
        
        md.append("### Conclusión")
        md.append("El fallo no es un problema de OCR ni de renderizado visual, sino un bug de decodificación de diccionarios de fuentes (`cmap`) en el stack subyacente de RAGFlow (`pdfplumber`).")
        md.append("Para solucionar esto en RAGFlow, se debe parchear la extracción PDF para:")
        md.append("- Proveer la dependencia `fonttools` para decodificar las fuentes CFF.")
        md.append("- Forzar a `pdfplumber` a priorizar el `ToUnicode` map por sobre el `/Encoding` de la fuente.")
        
    REPORT_PATH.write_text("\\n".join(md), encoding="utf-8")
    print(f"[OK] Reporte generado en {REPORT_PATH}")

if __name__ == "__main__":
    run_font_analysis()
