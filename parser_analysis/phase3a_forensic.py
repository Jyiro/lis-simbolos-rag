import json
import re
from pathlib import Path
import difflib

ROOT = Path(__file__).parent.parent
REAL_PDFS_DIR = ROOT / "deepdoc-research" / "real_pdfs"
REPORT_PATH = ROOT / "deepdoc-research" / "forensic_report.md"

# Targets based on Phase 2
TARGETS = [
    {
        "doc": "AbstractAlgebra",
        "symbol": "∑",
        "name": "SUM"
    },
    {
        "doc": "AbstractAlgebra",
        "symbol": "∏",
        "name": "PRODUCT"
    },
    {
        "doc": "ModalLogicFundamentally",
        "symbol": "⊨",
        "name": "MODELS"
    }
]

def clean_for_anchor(text: str) -> str:
    """Keep only alphanumeric chars to find anchors robustly."""
    return re.sub(r'[^a-zA-Z0-9]+', '', text)

def find_context_windows(text: str, char: str, window: int = 120) -> list:
    results = []
    pos = 0
    while True:
        idx = text.find(char, pos)
        if idx == -1:
            break
            
        start = max(0, idx - window)
        end = min(len(text), idx + window + 1)
        
        left_context = text[start:idx]
        right_context = text[idx+1:end]
        
        results.append({
            "idx": idx,
            "left_context": left_context,
            "char": char,
            "right_context": right_context
        })
        pos = idx + 1
    return results

def find_anchor(target_text: str, left_context: str, right_context: str, window: int = 150) -> dict:
    """
    Search for a similar neighborhood in target_text using difflib
    or regex matching of alphanumeric anchors.
    """
    # Create an anchor from the immediate surroundings (e.g., 20 chars left and 20 right)
    left_anchor = left_context[-40:] if len(left_context) >= 40 else left_context
    right_anchor = right_context[:40]
    
    # We use a simple sliding window difflib approach on the target_text 
    # to find the best match for left_anchor + right_anchor
    search_str = left_anchor + right_anchor
    search_str_clean = clean_for_anchor(search_str)
    
    if not search_str_clean or len(search_str_clean) < 10:
        return None
        
    # A faster heuristic: find the clean left anchor in clean target_text
    clean_target = clean_for_anchor(target_text)
    clean_left = clean_for_anchor(left_anchor[-20:])
    clean_right = clean_for_anchor(right_anchor[:20])
    
    # Find approx position
    # To keep it simple, we will just search the raw left anchor using string find
    # with some fuzziness. But let's try regex first with spaces made optional
    left_regex = r'\s*'.join(re.escape(c) for c in clean_left if c.strip())
    right_regex = r'\s*'.join(re.escape(c) for c in clean_right if c.strip())
    
    pattern = f"({left_regex})" + r"(.{0,10}?)" + f"({right_regex})"
    try:
        match = re.search(pattern, target_text, re.IGNORECASE | re.DOTALL)
        if match:
            return {
                "match": True,
                "left_found": match.group(1),
                "middle_found": match.group(2), # This is where the symbol should be
                "right_found": match.group(3),
                "full_context": target_text[max(0, match.start() - 30): min(len(target_text), match.end() + 30)]
            }
    except:
        pass
    return None

def classify_corruption(middle: str) -> str:
    if not middle:
        return "DELETION (Silenciosa)"
    if middle.isspace():
        return "WHITESPACE (Espacios en blanco)"
    return f"SUBSTITUTION (Reemplazado por: {repr(middle)})"

def run_forensic():
    md = [
        "# Reporte Forense — Fase 3A",
        "> Análisis de cómo pdfplumber corrompe los símbolos ausentes.",
        ""
    ]
    
    for t in TARGETS:
        doc = t["doc"]
        sym = t["symbol"]
        name = t["name"]
        
        md.append(f"## {doc} — Símbolo `{sym}` ({name})")
        
        pypdf_path = REAL_PDFS_DIR / doc / "pypdf_extracted.txt"
        plumber_path = REAL_PDFS_DIR / doc / "pdfplumber_extracted.txt"
        
        if not pypdf_path.exists() or not plumber_path.exists():
            md.append("Archivos de texto no encontrados.\\n")
            continue
            
        pypdf_text = pypdf_path.read_text(encoding="utf-8")
        plumber_text = plumber_path.read_text(encoding="utf-8")
        
        windows = find_context_windows(pypdf_text, sym, window=60)
        if not windows:
            md.append("No se encontraron ocurrencias en pypdf (Reference).\\n")
            continue
            
        md.append("| # | Contexto pypdf (Reference) | Contexto pdfplumber (Damaged) | Tipo de Corrupción |")
        md.append("|---|---|---|---|")
        
        # Analizamos máximo 10 ejemplos para no llenar el reporte
        analyzed = 0
        for i, w in enumerate(windows):
            if analyzed >= 10:
                break
                
            anchor_res = find_anchor(plumber_text, w["left_context"], w["right_context"])
            if anchor_res:
                ref_context = w["left_context"][-30:] + "**" + sym + "**" + w["right_context"][:30]
                ref_context = ref_context.replace("\\n", " ")
                
                mid = anchor_res["middle_found"]
                dam_context = anchor_res["left_found"][-30:] + "**" + mid + "**" + anchor_res["right_found"][:30]
                dam_context = dam_context.replace("\\n", " ")
                
                corr_type = classify_corruption(mid)
                
                md.append(f"| {i+1} | `{ref_context}` | `{dam_context}` | {corr_type} |")
                analyzed += 1
                
        if analyzed == 0:
            md.append("\\n*No se pudo alinear el texto para encontrar el contexto dañado.*")
            
        md.append("")
        
    REPORT_PATH.write_text("\\n".join(md), encoding="utf-8")
    print(f"[OK] Reporte generado en {REPORT_PATH}")

if __name__ == "__main__":
    run_forensic()
