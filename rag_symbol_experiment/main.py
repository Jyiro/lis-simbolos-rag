"""Punto de entrada del experimento.

Uso:
    python main.py                          # modelo por defecto (config.py)
    python main.py --modelo qwen3:4b-instruct-2507-q4_K_M
    python main.py --modelo qwen3:1.7b
"""

import argparse
import requests

from config import OLLAMA_URL, MODELO as MODELO_DEFAULT
from experiment import correr_experimento


def main():
    parser = argparse.ArgumentParser(
        description="Experimento Fase 1 — Comprensión RAG con símbolos especiales"
    )
    parser.add_argument(
        "--modelo",
        default=None,
        help=f"Modelo Ollama a usar (default: {MODELO_DEFAULT})",
    )
    args = parser.parse_args()
    modelo = args.modelo or MODELO_DEFAULT

    print(f"Conectando con Ollama en {OLLAMA_URL}...")
    try:
        requests.get("http://localhost:11434", timeout=5)
        print(f"✅ Ollama responde  |  modelo: {modelo}\n")
    except Exception:
        print("❌ Ollama no responde. Corré: ollama serve")
        return

    correr_experimento(modelo=modelo)


if __name__ == "__main__":
    main()
