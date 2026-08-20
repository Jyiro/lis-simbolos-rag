#!/usr/bin/env bash
# download_all.sh — Descarga global completa de herramientas ML/NLP/OCR
# Ejecutar como usuario normal (no root), desde cualquier directorio.
# Tiempo estimado: 30-90 min dependiendo de la velocidad de internet.

set -e
LOGFILE="$HOME/download_all.log"
echo "▶ Iniciando descarga completa — $(date)" | tee "$LOGFILE"

# ── 1. Paquetes del sistema (pacman) ─────────────────────────────────────────
echo -e "\n[1/4] Instalando paquetes del sistema (pacman)..." | tee -a "$LOGFILE"
sudo pacman -S --noconfirm --needed \
    tesseract \
    tesseract-data-spa \
    tesseract-data-eng \
    poppler \
    libmagic \
    2>&1 | tee -a "$LOGFILE"

# ── 2. Crear entorno virtual global en ~/.venv-ml ────────────────────────────
echo -e "\n[2/4] Creando entorno virtual global en ~/.venv-ml..." | tee -a "$LOGFILE"
python3 -m venv ~/.venv-ml
~/.venv-ml/bin/pip install --upgrade pip wheel 2>&1 | tee -a "$LOGFILE"

# ── 2a. Paquetes pip — Métricas semánticas ────────────────────────────────────
echo -e "\n[2a] sentence-transformers, scikit-learn, scipy..." | tee -a "$LOGFILE"
~/.venv-ml/bin/pip install \
    sentence-transformers scikit-learn scipy numpy \
    2>&1 | tee -a "$LOGFILE"

# ── 2b. Paquetes pip — Evaluación NLP ────────────────────────────────────────
echo -e "\n[2b] evaluate, bert-score, rouge-score..." | tee -a "$LOGFILE"
~/.venv-ml/bin/pip install \
    evaluate bert-score rouge-score sacrebleu \
    2>&1 | tee -a "$LOGFILE"

# ── 2c. Paquetes pip — OCR y extracción de documentos ────────────────────────
echo -e "\n[2c] OCR y parsers de documentos..." | tee -a "$LOGFILE"
~/.venv-ml/bin/pip install \
    markitdown pymupdf pdfplumber pytesseract docling easyocr marker-pdf \
    2>&1 | tee -a "$LOGFILE"

# ── 2d. Paquetes pip — Utilidades generales ML ───────────────────────────────
echo -e "\n[2d] Utilidades generales ML..." | tee -a "$LOGFILE"
~/.venv-ml/bin/pip install \
    transformers datasets accelerate huggingface-hub tokenizers \
    pandas matplotlib seaborn tqdm \
    2>&1 | tee -a "$LOGFILE"

# ── 3. Modelos HuggingFace ─────────────────────────────────────────────────────
echo -e "\n[3/4] Descargando modelos HuggingFace al cache global..." | tee -a "$LOGFILE"
~/.venv-ml/bin/python3 << 'PYEOF'
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

print(">> paraphrase-multilingual-MiniLM-L12-v2 (~470MB)")
SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("✅ MiniLM OK")

print(">> paraphrase-multilingual-mpnet-base-v2 (~1.1GB)")
SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print("✅ MPNet OK")

print(">> all-MiniLM-L6-v2 (~90MB)")
SentenceTransformer('all-MiniLM-L6-v2')
print("✅ MiniLM-L6 OK")

print(">> bert-base-multilingual-cased (~711MB)")
AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
AutoModel.from_pretrained('bert-base-multilingual-cased')
print("✅ BERT Multilingual OK")

print(">> xlm-roberta-base (~1.1GB)")
AutoTokenizer.from_pretrained('xlm-roberta-base')
AutoModel.from_pretrained('xlm-roberta-base')
print("✅ XLM-RoBERTa OK")

print("\n✅ TODOS LOS MODELOS HUGGINGFACE DESCARGADOS")
print("   Cache: ~/.cache/huggingface/hub/")
PYEOF

# ── 4. Modelos EasyOCR ────────────────────────────────────────────────────────
echo -e "\n[4/4] Pre-descargando modelos EasyOCR (es + en, ~500MB)..." | tee -a "$LOGFILE"
~/.venv-ml/bin/python3 -c "
import easyocr
reader = easyocr.Reader(['es', 'en'], gpu=False)
print('✅ EasyOCR modelos es+en descargados')
" 2>&1 | tee -a "$LOGFILE"

# ── Resumen final ─────────────────────────────────────────────────────────────
echo -e "\n=======================================" | tee -a "$LOGFILE"
echo "✅ DESCARGA COMPLETA — $(date)" | tee -a "$LOGFILE"
echo "   Entorno global: ~/.venv-ml/bin/python3" | tee -a "$LOGFILE"
echo "   Models cache:   ~/.cache/huggingface/hub/" | tee -a "$LOGFILE"
echo "   Log completo:   $LOGFILE" | tee -a "$LOGFILE"
echo "=======================================" | tee -a "$LOGFILE"
echo ""
echo "Tip: En nuevos proyectos, los modelos HuggingFace NO se re-descargan."
echo "Solo instalá los paquetes pip en el .venv del proyecto y ya los usa."
