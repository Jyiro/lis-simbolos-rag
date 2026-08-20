#!/usr/bin/env python3
"""
download_hf_models.py — Descarga los modelos HuggingFace al cache global.

Ejecutar UNA SOLA VEZ. Los modelos quedan en ~/.cache/huggingface/hub/
y cualquier proyecto Python los reutiliza automáticamente sin re-descargar.

Uso:
    ~/.venv-ml/bin/python3 scripts/download_hf_models.py
"""

import sys

MODELS = [
    # (nombre_en_hub, descripcion, tamaño, tipo)
    ("paraphrase-multilingual-MiniLM-L12-v2", "SentenceTransformer", "~470 MB", "🔴 ESENCIAL — similitud coseno en español"),
    ("paraphrase-multilingual-mpnet-base-v2", "SentenceTransformer", "~1.1 GB", "🟡 RECOMENDADO — mejor calidad que MiniLM"),
    ("all-MiniLM-L6-v2",                      "SentenceTransformer", "~90 MB",  "🟡 RECOMENDADO — rápido, inglés"),
    ("bert-base-multilingual-cased",           "AutoModel",           "~711 MB", "🟡 RECOMENDADO — base para BERTScore en español"),
    ("xlm-roberta-base",                       "AutoModel",           "~1.1 GB", "🟢 OPCIONAL    — mejor que BERT para español"),
]

TOTAL_GB = 3.5

def sep():
    print("─" * 65)

def main():
    print()
    print("=" * 65)
    print("  Descarga de Modelos HuggingFace al Cache Global")
    print(f"  Total aprox: {TOTAL_GB} GB → ~/.cache/huggingface/hub/")
    print("=" * 65)

    try:
        from sentence_transformers import SentenceTransformer
        from transformers import AutoTokenizer, AutoModel
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("   Asegurate de correr con ~/.venv-ml/bin/python3")
        sys.exit(1)

    results = []

    for model_id, model_type, size, desc in MODELS:
        sep()
        print(f"  {desc}")
        print(f"  Modelo: {model_id}  ({size})")
        sep()
        try:
            if model_type == "SentenceTransformer":
                SentenceTransformer(model_id)
            else:
                AutoTokenizer.from_pretrained(model_id)
                AutoModel.from_pretrained(model_id)
            print(f"  ✅ OK — {model_id}")
            results.append((model_id, True))
        except Exception as e:
            print(f"  ❌ ERROR — {model_id}: {e}")
            results.append((model_id, False))
        print()

    sep()
    print("\n  RESUMEN FINAL")
    sep()
    ok = sum(1 for _, s in results if s)
    for model_id, success in results:
        icon = "✅" if success else "❌"
        print(f"  {icon} {model_id}")
    print()
    print(f"  {ok}/{len(results)} modelos descargados correctamente.")
    print(f"  Cache: ~/.cache/huggingface/hub/")
    sep()
    print()

if __name__ == "__main__":
    main()
