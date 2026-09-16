#!/usr/bin/env python3
"""
smoke_ragflow.py — Verifica que los dos providers de RAGFlow estén accesibles.

Uso:
    python3 scripts/smoke_ragflow.py \
        --ollama http://localhost:11434 \
        --kaggle https://TU-URL.ngrok-free.app

Los valores por defecto apuntan a localhost para pruebas locales.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

# ── Colores en terminal ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}")
def info(msg):  print(f"  {YELLOW}→{RESET} {msg}")

# ── HTTP helpers ──────────────────────────────────────────────────────────────
def post_json(url: str, payload: dict, extra_headers: dict = None) -> dict:
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if extra_headers:
        for k, v in extra_headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def get_json(url: str, extra_headers: dict = None) -> dict:
    req = urllib.request.Request(url, method="GET")
    if extra_headers:
        for k, v in extra_headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


# ── Tests ─────────────────────────────────────────────────────────────────────
def test_ollama_models(base: str) -> bool:
    """Lista los modelos disponibles en Ollama."""
    url = f"{base.rstrip('/')}/api/tags"
    try:
        data   = get_json(url)
        models = [m["name"] for m in data.get("models", [])]
        if models:
            ok(f"Ollama responde. Modelos disponibles: {', '.join(models)}")
            return True
        else:
            fail("Ollama responde pero no hay modelos instalados. Corré: ollama pull nomic-embed-text")
            return False
    except urllib.error.HTTPError as e:
        fail(f"Ollama /api/tags → HTTP {e.code}: {e.reason}")
        return False
    except Exception as e:
        fail(f"No se pudo conectar a Ollama en {base}: {e}")
        return False


def test_ollama_embedding(base: str, model: str = "nomic-embed-text") -> bool:
    """Genera un embedding de prueba usando /v1/embeddings (OpenAI-compatible)."""
    url = f"{base.rstrip('/')}/v1/embeddings"
    try:
        data = post_json(url, {"model": model, "input": "símbolo de prueba □"})
        vec  = data["data"][0]["embedding"]
        ok(f"Embedding generado correctamente. Dimensiones: {len(vec)}")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        fail(f"Ollama /v1/embeddings → HTTP {e.code}: {body[:200]}")
        info("Tip: Si el error es 404, el modelo puede no estar descargado. Corré: ollama pull nomic-embed-text")
        return False
    except Exception as e:
        fail(f"Error al generar embedding: {e}")
        return False


def test_kaggle_models(base: str) -> list:
    """Lista los modelos disponibles en el servidor llama_cpp de Kaggle."""
    url = f"{base.rstrip('/')}/v1/models"
    headers = {"ngrok-skip-browser-warning": "true"}
    try:
        data   = get_json(url, extra_headers=headers)
        models = [m["id"] for m in data.get("data", [])]
        if models:
            ok(f"Servidor Kaggle responde. Modelos: {', '.join(models)}")
            return models
        else:
            fail("El servidor Kaggle responde pero no lista modelos.")
            return []
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "<html" in body.lower():
            fail(f"Kaggle /v1/models → Ngrok devolvió HTML (pantalla de advertencia). Agregá el header ngrok-skip-browser-warning.")
        else:
            fail(f"Kaggle /v1/models → HTTP {e.code}: {body[:200]}")
        return []
    except Exception as e:
        fail(f"No se pudo conectar al servidor Kaggle en {base}: {e}")
        return []


def test_kaggle_chat(base: str, model: str) -> bool:
    """Envía un mensaje de prueba al LLM de Kaggle."""
    url = f"{base.rstrip('/')}/v1/chat/completions"
    headers = {"ngrok-skip-browser-warning": "true"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Respondé solo 'OK' sin explicaciones."}],
        "max_tokens": 10,
        "temperature": 0,
    }
    try:
        data    = post_json(url, payload, extra_headers=headers)
        content = data["choices"][0]["message"]["content"].strip()
        ok(f"LLM responde correctamente. Respuesta: '{content}'")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        fail(f"Kaggle /v1/chat/completions → HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        fail(f"Error en chat completion: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Smoke test para providers de RAGFlow")
    parser.add_argument("--ollama",  default="http://localhost:11434",
                        help="URL base de Ollama (ej: http://localhost:11434 o https://xyz.serveo.net)")
    parser.add_argument("--kaggle",  default=None,
                        help="URL base del servidor Kaggle via Ngrok (ej: https://abc.ngrok-free.app)")
    parser.add_argument("--embed-model", default="nomic-embed-text",
                        help="Nombre del modelo de embedding en Ollama (default: nomic-embed-text)")
    args = parser.parse_args()

    all_ok = True

    # ── Test Ollama ──────────────────────────────────────────────────────────
    print(f"\n{BOLD}── Ollama Embedding Server ({args.ollama}) ──{RESET}")
    if not test_ollama_models(args.ollama):
        all_ok = False
    else:
        if not test_ollama_embedding(args.ollama, args.embed_model):
            all_ok = False

    # ── Test Kaggle ──────────────────────────────────────────────────────────
    if args.kaggle:
        print(f"\n{BOLD}── Kaggle LLM Server ({args.kaggle}) ──{RESET}")
        models = test_kaggle_models(args.kaggle)
        if models:
            if not test_kaggle_chat(args.kaggle, models[0]):
                all_ok = False
        else:
            all_ok = False
    else:
        print(f"\n{YELLOW}Omitiendo test de Kaggle (no se pasó --kaggle URL){RESET}")

    # ── Resultado final ───────────────────────────────────────────────────────
    print()
    if all_ok:
        print(f"{GREEN}{BOLD}✓ Todo OK — los providers están accesibles y funcionando.{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}✗ Hay problemas. Revisá los errores arriba antes de configurar RAGFlow.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
