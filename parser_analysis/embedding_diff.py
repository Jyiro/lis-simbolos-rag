import json
from pathlib import Path
import numpy as np
from difflib import SequenceMatcher

try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
except ImportError:
    print("Error: sentence-transformers no está instalado. Instalalo en tu venv local.")
    exit(1)

ROOT = Path(__file__).parent.parent
REAL_PDFS_DIR = ROOT / "deepdoc-research" / "real_pdfs"
OUTPUT_REPORT = ROOT / "deepdoc-research" / "embedding_diff_report.md"

CRITICAL_SYMBOLS = {
    "∑": "SUM",
    "∏": "PRODUCT",
    "⊨": "MODELS",
    "⊢": "TURNSTILE"
}

def cosine(text_a: str, text_b: str) -> float:
    emb_a = model.encode(text_a, convert_to_tensor=True)
    emb_b = model.encode(text_b, convert_to_tensor=True)
    return util.cos_sim(emb_a, emb_b).item()

def find_best_match(ref_chunk: str, target_chunks: list[str]) -> str:
    best_score = -1
    best_chunk = ""
    for t_chunk in target_chunks:
        score = SequenceMatcher(None, ref_chunk, t_chunk).real_quick_ratio()
        if score > best_score:
            best_score = score
            best_chunk = t_chunk
    if best_score < 0.5:
        for t_chunk in target_chunks:
            score = SequenceMatcher(None, ref_chunk, t_chunk).ratio()
            if score > best_score:
                best_score = score
                best_chunk = t_chunk
    return best_chunk

def get_chunks(text: str) -> list[str]:
    return [c.strip() for c in text.split("\n\n") if len(c.strip()) > 20]

def main():
    if not REAL_PDFS_DIR.exists():
        print("No se encontraron los textos extraídos en real_pdfs/")
        return

    report = [
        "# Métrica de Diferencia de Embeddings (Fase 5)",
        "",
        "Evalúa cuánto desplaza la corrupción de `pdfplumber` los vectores de embedding en comparación con la extracción correcta de `pypdf` usando `paraphrase-multilingual-MiniLM-L12-v2`.",
        "",
        "| Símbolo | Documento | Muestras | Coseno Medio | < 0.70 |",
        "|---|---|---|---|---|"
    ]

    for doc_dir in REAL_PDFS_DIR.iterdir():
        if not doc_dir.is_dir():
            continue
            
        doc_id = doc_dir.name
        pypdf_file = doc_dir / "pypdf_extracted.txt"
        pdfplumber_file = doc_dir / "pdfplumber_extracted.txt"
        
        if not pypdf_file.exists() or not pdfplumber_file.exists():
            continue
            
        print(f"Procesando {doc_id}...")
        ref_text = pypdf_file.read_text(encoding="utf-8")
        tgt_text = pdfplumber_file.read_text(encoding="utf-8")
        
        ref_chunks = get_chunks(ref_text)
        tgt_chunks = get_chunks(tgt_text)
        
        for symbol, name in CRITICAL_SYMBOLS.items():
            hits = [c for c in ref_chunks if symbol in c]
            if not hits:
                continue
                
            print(f"  - {name} ({symbol}): {len(hits)} hits")
            
            import random
            random.seed(42)
            sample_hits = random.sample(hits, min(30, len(hits)))
            
            cosines = []
            below_threshold = 0
            
            for ref_chunk in sample_hits:
                tgt_chunk = find_best_match(ref_chunk, tgt_chunks)
                
                score = cosine(ref_chunk, tgt_chunk)
                cosines.append(score)
                if score < 0.70:
                    below_threshold += 1
                    
            mean_cos = sum(cosines) / len(cosines)
            report.append(f"| {symbol} ({name}) | {doc_id} | {len(sample_hits)} | {mean_cos:.3f} | {below_threshold} |")

    report.append("")
    report.append("## Conclusión")
    report.append("Un coseno medio alto (>0.90) indica que la ausencia del símbolo *no desplaza* significativamente el vector (el retrieval seguiría funcionando). Un coseno < 0.70 indica que la corrupción destruye la representación semántica al punto de fallar un retrieval estándar.")
    
    OUTPUT_REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"\nReporte generado: {OUTPUT_REPORT.name}")

if __name__ == "__main__":
    main()
