#!/usr/bin/env bash
# serve.sh — Lanzador de llama-server para el experimento RAG
#
# Uso:
#   ./serve.sh                    → modelo default (qwen3.5-2b)
#   ./serve.sh qwen3.5-2b
#   ./serve.sh gemma-4b
#   ./serve.sh qwen3-4b           → ERROR si el GGUF no existe aún
#
# Para correr el experimento después:
#   python main.py --modelo qwen3.5-2b --backend llama_cpp
#   python main.py --modelo qwen3.5-2b --fragmentos B3_modal B4_subconjunto

set -euo pipefail

MODEL_DIR="/home/jonas/llama.cpp/models"
PORT=8080
CTX_SIZE=4096    # contexto amplio para los prompts con tabla de notación

# ── Registry de modelos (sincronizado con config.py MODEL_REGISTRY) ───────────
declare -A MODELS=(
    ["qwen3.5-2b"]="Qwen3.5-2B-Q4_K_M"
    ["qwen3.5-4b"]="qwen3.5-4b-instruct-Q4_K_M"
    ["qwen3.5-9b"]="Qwen3.5-9B-Q4_K_M"
    ["gemma-4b"]="gemma-4-E4B-it-qat-UD-Q4_K_XL"
)

# ── Argumento: modelo ID ──────────────────────────────────────────────────────
MODELO_ID="${1:-qwen3.5-2b}"

if [[ ! -v MODELS[$MODELO_ID] ]]; then
    echo "❌ Modelo '$MODELO_ID' no registrado en serve.sh."
    echo "   Modelos disponibles:"
    for key in "${!MODELS[@]}"; do
        echo "     $key → ${MODELS[$key]}.gguf"
    done
    exit 1
fi

GGUF_NAME="${MODELS[$MODELO_ID]}"
GGUF_PATH="$MODEL_DIR/$GGUF_NAME.gguf"

if [[ ! -f "$GGUF_PATH" ]]; then
    echo "❌ Archivo GGUF no encontrado: $GGUF_PATH"
    echo "   Verificá que el modelo esté descargado o actualizá serve.sh."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Lanzando llama-server"
echo "   Modelo:  $MODELO_ID"
echo "   GGUF:    $GGUF_PATH"
echo "   Puerto:  $PORT"
echo "   Contexto: $CTX_SIZE tokens"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Presioná Ctrl+C para detener el servidor."
echo ""

exec llama-server \
    --model "$GGUF_PATH" \
    --port "$PORT" \
    --ctx-size "$CTX_SIZE" \
    --reasoning off
