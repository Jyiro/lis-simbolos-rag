"""
Investiga símbolos encontrados EXCLUSIVAMENTE por pdfplumber (con patch)
pero no por pymupdf ni pypdf. Los muestra en contexto para evaluación manual.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tex_glyph_patch  # noqa: F401

import pdfplumber

REPO_ROOT = Path(__file__).parent.parent
ARXIV_DIR = REPO_ROOT / "dataset-ragflow" / "corpus-ragflow" / "arxiv-harvested"

# El paper sospechoso
try:
    PDF_PATH = next(ARXIV_DIR.glob("2609.15879*.pdf"))
except StopIteration:
    print("No se encontró el PDF 2609.15879")
    sys.exit(1)

TARGET_CHAR = "\u2211"  # ∑

def get_contexts(pdf_path, char, window=80):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            pos = 0
            while True:
                idx = text.find(char, pos)
                if idx == -1:
                    break
                ctx = text[max(0, idx-window):idx+window+1]
                yield page_num, idx, ctx
                pos = idx + 1

print(f"Buscando '{TARGET_CHAR}' en {PDF_PATH.name}")
print("=" * 60)
contexts = list(get_contexts(PDF_PATH, TARGET_CHAR))
if not contexts:
    print("No se encontraron ocurrencias.")
for page, pos, ctx in contexts:
    print(f"\n[Pág {page}, pos {pos}]")
    print(repr(ctx))
    print("-" * 40)
