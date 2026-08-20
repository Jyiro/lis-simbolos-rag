# Entorno Global de ML/NLP — `~/.venv-ml`

Entorno virtual Python instalado el **2026-08-13** con todas las herramientas de ML, NLP
y OCR necesarias para investigación. **Global al sistema**: disponible para cualquier proyecto.

---

## Ubicación

| Recurso | Ruta |
|---|---|
| Entorno virtual (Python) | `~/.venv-ml/` |
| Ejecutable Python | `~/.venv-ml/bin/python3` |
| Pip del entorno | `~/.venv-ml/bin/pip` |
| Modelos HuggingFace (cache) | `~/.cache/huggingface/hub/` |
| Modelos EasyOCR | `~/.EasyOCR/model/` |
| Script de instalación | `scripts/download_all.sh` |
| Tamaño total del venv | **~5.8 GB** |

---

## Cómo activarlo en cualquier proyecto

```bash
# Opción 1: Activar en Fish shell
source ~/.venv-ml/bin/activate.fish

# Opción 2: Activar en bash/zsh
source ~/.venv-ml/bin/activate

# Opción 3: Ejecutar directamente sin activar
~/.venv-ml/bin/python3 mi_script.py
~/.venv-ml/bin/jupyter notebook
```

---

## Paquetes Instalados por Categoría

### Métricas Semánticas y Evaluación NLP

| Paquete | Versión | Para qué sirve |
|---|---|---|
| `sentence-transformers` | 5.7.0 | Embeddings semánticos + similitud coseno |
| `scikit-learn` | 1.9.0 | F1, Accuracy, Confusion Matrix, McNemar test |
| `scipy` | 1.18.0 | Tests estadísticos (Wilcoxon, etc.) |
| `numpy` | (última) | Operaciones numéricas base |
| `evaluate` | 0.4.6 | Framework de métricas HuggingFace |
| `bert-score` | 0.3.13 | BERTScore (Precision/Recall/F1 semántico) |
| `rouge-score` | 0.1.2 | ROUGE (N-gram overlap — textos de resumen) |
| `sacrebleu` | 2.6.0 | BLEU score (estándar en traducción/generación) |

### Modelos de Transformers y LLM

| Paquete | Versión | Para qué sirve |
|---|---|---|
| `transformers` | 5.15.0 | Acceso a todos los modelos HuggingFace |
| `tokenizers` | 0.22.2 | Tokenización rápida (base de transformers) |
| `datasets` | 5.0.1 | Carga y procesamiento de datasets HuggingFace |
| `accelerate` | 1.14.0 | Inferencia multi-GPU / CPU optimizada |
| `huggingface-hub` | 1.27.0 | Descarga y gestión de modelos del Hub |
| `safetensors` | 0.8.0 | Formato seguro de modelos (reemplaza .bin) |
| `torch` | 2.13.0 | PyTorch — backend de todos los modelos |
| `torchvision` | 0.28.0 | Modelos de visión (para OCR visual) |
| `onnxruntime` | 1.28.0 | Inferencia rápida de modelos ONNX |

### OCR y Extracción de Documentos

| Paquete | Versión | Para qué sirve |
|---|---|---|
| `markitdown` | 0.1.7 | PDF/DOCX/PPT → Markdown (Microsoft) |
| `pymupdf` | 1.28.2 | Extracción directa de texto/imágenes de PDF |
| `pdfplumber` | 0.11.10 | Extracción de texto + tablas de PDF |
| `pdfminer.six` | 20260107 | Parser de bajo nivel para PDFs |
| `pypdfium2` | 5.12.1 | Binding de PDFium (motor de Chrome) |
| `pytesseract` | 0.3.13 | Wrapper Python para Tesseract OCR |
| `easyocr` | 1.7.2 | OCR por deep learning (50+ idiomas) |
| `marker-pdf` | 2.0.0 | PDF académico → Markdown + LaTeX (fórmulas) |
| `docling` | 2.119.0 | Pipeline OCR académico completo (IBM Research) |
| `docling-ibm-models` | 3.14.0 | Modelos internos de Docling |
| `rapidocr` | 3.9.2 | OCR rápido basado en ONNX |
| `opencv_python` | 5.0.0 | Visión por computador (preprocesado de imágenes) |
| `magika` | 0.6.3 | Detección de tipo de archivo (Google) |

### Análisis de Datos y Visualización

| Paquete | Versión | Para qué sirve |
|---|---|---|
| `pandas` | 3.0.5 | DataFrames — análisis de resultados |
| `matplotlib` | (última) | Gráficos estáticos |
| `seaborn` | 0.13.2 | Gráficos estadísticos sobre matplotlib |
| `pyarrow` | 25.0.1 | Formato columnar rápido (backend de pandas) |

### Utilidades

| Paquete | Versión | Para qué sirve |
|---|---|---|
| `tqdm` | 4.70.0 | Barras de progreso |
| `nltk` | 3.10.3 | NLP clásico (tokenización, stopwords) |
| `sympy` | 1.14.0 | Matemática simbólica |
| `tabulate` | 0.10.0 | Impresión de tablas en consola |

---

## Paquetes del Sistema (pacman)

| Paquete | Notas |
|---|---|
| `tesseract` | Motor OCR base (ya estaba instalado) |
| `tesseract-data-spa` | Datos de idioma Español para Tesseract |
| `tesseract-data-eng` | Datos de idioma Inglés para Tesseract |
| `poppler` | Utilidades de línea de comandos para PDF |
| `python-pillow` | PIL/Pillow 12.3.0 (sistema, Python 3.14 compatible) |

---

## Modelos HuggingFace en Cache

> **Estado:** ✅ Instalados y listos para usarse.
> **Ubicación exacta de los pesos:** `~/.cache/huggingface/hub/`
> 
> Al instanciar uno de estos modelos desde cualquier entorno virtual de tu computadora (por ej. `.venv` de este proyecto), la librería buscará en esta carpeta y los cargará instantáneamente desde el disco sin descargar nada de internet.

### Modelos a descargar

| Modelo | Tamaño | Uso en investigación | Prioridad |
|---|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | ~470 MB | **Principal:** similitud coseno en español, evaluador semántico de respuestas del LLM | 🔴 Esencial |
| `paraphrase-multilingual-mpnet-base-v2` | ~1.1 GB | Alternativa de mayor calidad al MiniLM para resultados finales de paper | 🟡 Recomendado |
| `all-MiniLM-L6-v2` | ~90 MB | Modelo rápido en inglés, útil para fragmentos mixtos | 🟡 Recomendado |
| `bert-base-multilingual-cased` | ~711 MB | Base para BERTScore en español (Precision/Recall/F1 semántico) | 🟡 Recomendado |
| `xlm-roberta-base` | ~1.1 GB | Mejor que BERT para español; reemplaza a BERT multilingual en tareas de evaluación | 🟢 Opcional |

**Total descarga:** ~3.5 GB

### Descripción de cada modelo

#### `paraphrase-multilingual-MiniLM-L12-v2` ⭐
- **Arquitectura:** MiniLM (12 capas), fine-tuned en 50+ idiomas
- **Salida:** Vector de 384 dimensiones por oración
- **Velocidad:** Rápido en CPU (apropiado para este proyecto sin GPU)
- **Uso típico:**
  ```python
  from sentence_transformers import SentenceTransformer, util
  model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
  emb_ref = model.encode("No, el dominio son pares ordenados de reales")
  emb_resp = model.encode(respuesta_del_modelo)
  score = util.cos_sim(emb_ref, emb_resp).item()  # 0.0 a 1.0
  ```

#### `paraphrase-multilingual-mpnet-base-v2`
- **Arquitectura:** MPNet, más grande que MiniLM
- **Salida:** Vector de 768 dimensiones
- **Velocidad:** Más lento pero mejor calidad en textos cortos y técnicos
- **Cuándo usarlo:** Para las corridas finales del paper donde la precisión importa más que la velocidad

#### `bert-base-multilingual-cased`
- **Arquitectura:** BERT original de Google, entrenado en 104 idiomas
- **Uso típico:** Como modelo base para `bert-score`
  ```python
  from bert_score import score
  P, R, F1 = score(candidatos, referencias, lang='es', model_type='bert-base-multilingual-cased')
  ```

#### `xlm-roberta-base`
- **Arquitectura:** RoBERTa entrenado en 100 idiomas (CC-100 corpus)
- **Calidad:** Superior a BERT multilingual en casi todos los benchmarks de español
- **Uso típico:** Reemplazar `bert-base-multilingual-cased` como modelo de BERTScore

---

## Uso en el Proyecto RAG Symbols

Para usar estas librerías en el proyecto actual, instalar solo los paquetes pip en el `.venv` local.
Los modelos HuggingFace ya están en el cache global y no se re-descargan:

```bash
# Dentro del proyecto:
.venv/bin/pip install sentence-transformers scikit-learn scipy evaluate bert-score
# Los modelos en ~/.cache/huggingface/ se reutilizan automáticamente.
```

---

## Nota sobre Python 3.14

El entorno usa Python 3.14 (CachyOS rolling release). Algunos paquetes (`easyocr`, `marker-pdf`)
fueron instalados con `--no-deps` para evitar que sobreescriban `pillow>=12.3.0` del sistema
con versiones antiguas incompatibles con Python 3.14.

