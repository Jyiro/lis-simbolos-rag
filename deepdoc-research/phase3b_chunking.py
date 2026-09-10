import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
REAL_PDFS_DIR = ROOT / "deepdoc-research" / "real_pdfs"
REPORT_PATH = ROOT / "deepdoc-research" / "chunking_report.md"

# Targets to check
TARGETS = [
    {"doc": "FirstOrderLogic", "symbol": "⊢", "name": "TURNSTILE", "context": ["demuestra", "prueba", "derivación", "regla", "axioma", "concluye", "implica", "premisas", "φ", "ψ", "Γ"]},
    {"doc": "ModalLogicFundamentally", "symbol": "¬", "name": "NOT", "context": ["negation", "logical", "false", "true", "proposition", "lattice", "complement"]},
    {"doc": "AbstractAlgebra", "symbol": "∈", "name": "ELEM_OF", "context": ["element", "set", "group", "ring", "field", "belongs", "g", "G", "x", "y"]}
]

def chunk_fixed_size(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """
    Chunking by fixed size (characters for simplicity, representing tokens approx).
    Normally 512 tokens ~ 2000 chars. Let's use 2000 chars and 200 overlap.
    """
    chunk_chars = 2000
    overlap_chars = 200
    chunks = []
    
    if not text:
        return chunks
        
    pos = 0
    chunk_id = 0
    while pos < len(text):
        end_pos = min(pos + chunk_chars, len(text))
        chunk_text = text[pos:end_pos]
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "start": pos,
            "end": end_pos
        })
        chunk_id += 1
        pos += (chunk_chars - overlap_chars)
        if pos >= len(text) or end_pos == len(text):
            break
            
    return chunks

def analyze_symbol_in_chunks(chunks: list, symbol: str, keywords: list, border_window: int = 50) -> dict:
    total_occurrences = 0
    in_border = 0
    context_lost = 0
    
    # Track which chunks have the symbol in a border
    border_examples = []
    
    for c in chunks:
        text = c["text"]
        pos = 0
        while True:
            idx = text.find(symbol, pos)
            if idx == -1:
                break
                
            total_occurrences += 1
            
            # Check if it's in border
            is_border = (idx < border_window) or (idx > len(text) - border_window)
            if is_border:
                in_border += 1
                
            # Check if it lost semantic context (none of the keywords exist in this chunk)
            has_context = False
            lower_text = text.lower()
            for kw in keywords:
                if kw.lower() in lower_text:
                    has_context = True
                    break
                    
            if not has_context:
                context_lost += 1
                
            if is_border and not has_context and len(border_examples) < 2:
                # Save an example
                context_snippet = text[max(0, idx - 60):min(len(text), idx + 60)].replace("\\n", " ")
                border_examples.append({
                    "chunk_id": c["id"],
                    "snippet": context_snippet,
                    "is_start": idx < border_window
                })
                
            pos = idx + 1
            
    return {
        "total": total_occurrences,
        "in_border": in_border,
        "context_lost": context_lost,
        "examples": border_examples
    }

def run_chunking():
    md = [
        "# Reporte de Chunking — Fase 3B",
        "> Análisis de pérdida de contexto al fragmentar documentos que contienen símbolos matemáticos.",
        "",
        "## Modo: Fixed-size (Aprox 512 tokens / 2000 chars, overlap 200 chars)",
        ""
    ]
    
    for t in TARGETS:
        doc = t["doc"]
        sym = t["symbol"]
        name = t["name"]
        keywords = t["context"]
        
        # We use pypdf text for this, because we want to see what happens to symbols that *do* survive extraction
        pypdf_path = REAL_PDFS_DIR / doc / "pypdf_extracted.txt"
        
        if not pypdf_path.exists():
            continue
            
        text = pypdf_path.read_text(encoding="utf-8")
        chunks = chunk_fixed_size(text)
        
        res = analyze_symbol_in_chunks(chunks, sym, keywords)
        
        md.append(f"### {doc} — Símbolo `{sym}` ({name})")
        md.append("| Símbolo | Total Extraído | En borde de chunk (<50 chars) | Sin contexto semántico |")
        md.append("|---|---|---|---|")
        
        pct_border = round(res["in_border"] / res["total"] * 100, 1) if res["total"] > 0 else 0
        pct_lost = round(res["context_lost"] / res["total"] * 100, 1) if res["total"] > 0 else 0
        
        md.append(f"| `{sym}` | {res['total']} | {res['in_border']} ({pct_border}%) | {res['context_lost']} ({pct_lost}%) |")
        md.append("")
        
        if res["examples"]:
            md.append("**Ejemplos de símbolo en borde sin contexto:**")
            for ex in res["examples"]:
                border_type = "Inicio del chunk" if ex["is_start"] else "Fin del chunk"
                md.append(f"- **Chunk {ex['chunk_id']} ({border_type}):** `...{ex['snippet']}...`")
            md.append("")
            
    REPORT_PATH.write_text("\\n".join(md), encoding="utf-8")
    print(f"[OK] Reporte generado en {REPORT_PATH}")

if __name__ == "__main__":
    run_chunking()
