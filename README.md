# RAG Symbol Experiment

Experimento sobre vulnerabilidades de pipelines RAG ante corrupción de caracteres especiales (mojibake Unicode) en documentos con simbología matemática.

**Fase 1:** ¿Puede un LLM interpretar texto corrupto? ¿Puede una tabla de contexto o una instrucción de sistema recuperar la comprensión?

---

## Requisitos e Instalación

El proyecto utiliza un entorno virtual (venv) **global** para aislar las dependencias pesadas de Machine Learning (`sentence-transformers`, `torch`, etc.) y evitar descargarlas múltiples veces si movés el proyecto.

```bash
# 1. Crear el entorno virtual (recomendado fuera de la carpeta del proyecto, ej. en ~/)
python3 -m venv ~/.venv-ml

# 2. Instalar dependencias
~/.venv-ml/bin/pip install -r requirements.txt
```

> **Nota:** Todos los scripts se ejecutan usando `~/.venv-ml/bin/python3`.

Necesitás un backend LLM corriendo localmente (ej: `llama-server` u Ollama) para procesar las consultas.

---

## Arranque rápido — llama.cpp (esta laptop)

### 1. Lanzar el servidor

```bash
# Modelo por defecto (qwen3.5-2b)
./serve.sh

# O especificar modelo
./serve.sh qwen3.5-2b   # 1.3 GB
./serve.sh qwen3.5-4b   # 2.7 GB
./serve.sh qwen3.5-9b   # 5.7 GB
./serve.sh gemma-4b     # 4.2 GB


```

### 2. Correr el experimento (otra terminal)

```bash
# Corrida completa — 12 fragmentos × 10 condiciones (usa el evaluador semántico)
~/.venv-ml/bin/python3 main.py

# Solo fragmentos de terquedad semántica
~/.venv-ml/bin/python3 main.py --fragmentos B3_modal B4_subconjunto

# Solo estrategias Instruction Hierarchy
~/.venv-ml/bin/python3 main.py --condiciones i1_a i1_b i1_c i1_d

# Habilitar thinking mode (solo modelos compatibles como Qwen3)
~/.venv-ml/bin/python3 main.py --thinking

# Combinado — smoke test rápido
~/.venv-ml/bin/python3 main.py --fragmentos B3_modal B4_subconjunto --condiciones i1_d --thinking

# Con gemma
~/.venv-ml/bin/python3 main.py --modelo gemma-4b

# Experimento de fidelidad de caracteres (modo echo, audita normalización silenciosa)
~/.venv-ml/bin/python3 main.py --modo echo
~/.venv-ml/bin/python3 main.py --modo echo --modelo gemma-4b
```

### 3. Ver resultados

```
results/<run_id>/
├── results.json   ← datos completos (keywords + cosine similarity)
├── summary.txt    ← resumen tabular rápido (incluye prom. semántico)
└── report.md      ← markdown con análisis y scores de similitud contrastiva

results_echo/<run_id>/
├── echo_results.json   ← datos completos con comparación de bytes
├── echo_summary.txt    ← tabla rápida de resultados
└── echo_report.md      ← reporte con análisis y hexdump auditable
```

---

## Arranque rápido — Ollama (PC de escritorio)

```bash
# Sin cambios en el código — solo cambiar el flag
~/.venv-ml/bin/python3 main.py --backend ollama --modelo qwen3.5-2b
~/.venv-ml/bin/python3 main.py --backend ollama --modelo qwen3-4b
```

---

## Hallazgos Metodológicos Clave

El proyecto implementa dos marcos de evaluación robustos para auditar LLMs:

### 1. Test ECHO (Fidelidad a nivel de Byte)
Verifica si el LLM "sanitiza" el texto corrupto (Mojibake) antes de procesarlo, lo cual invalidaría un experimento RAG. 
- Utiliza **Distancia de Levenshtein** y **Auditoría Hexadecimal**.
- **Descubrimiento (La Curva en U):** Modelos pequeños (2B) copian fielmente la basura porque carecen de inferencia. Modelos medianos (4B) detectan el error tipográfico e intentan "autocorregirlo" (Distancia > 0), desobedeciendo la instrucción de copiar literalmente. Modelos grandes (9B) detectan el error pero tienen el "alignment" necesario para obedecer al usuario y mantener fidelidad absoluta.

### 2. Evaluación Semántica Continua
Las palabras clave (`✓` / `✗`) son binarias y frágiles. Se implementó un pipeline con `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`):
- **Max Cosine Similarity:** Se compara la respuesta del LLM contra múltiples referencias válidas, tomando la mayor similitud para absorber parafraseos.
- **Score Contrastivo:** Se resta la similitud de una respuesta "terca" o alucinada. Un score negativo cuantifica empíricamente la **Terquedad Semántica** (cuando el LLM desobedece el RAG y prioriza sus pesos paramétricos erróneos).

---

## Modelos disponibles

| ID | GGUF | Ollama | Estado |
|----|------|--------|--------|
| `qwen3.5-2b` | `Qwen3.5-2B-Q4_K_M.gguf` | `qwen3.5:2b` | ✅ |
| `gemma-4b` | `gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf` | `gemma3:4b` | ✅ |
| `qwen3-4b` | `Qwen3-4B-Q4_K_M.gguf` | `qwen3:4b` | 🔲 stub |
| `qwen3-7b` | `Qwen3-7B-Q4_K_M.gguf` | `qwen3:7b` | 🔲 stub |

> Cuando descargues un stub: actualizá `gguf_name` y `available=True` en `config.py`, y el nombre en `serve.sh`.

```bash
# Ver todos los modelos y su estado
python main.py --list-modelos
```

---

## Estrategias de prompt

| ID | Descripción | System role |
|----|-------------|-------------|
| `plain` | Sin tabla — baseline puro | No |
| `table_plain` | Tabla de notación sin énfasis | No |
| `i1_a` | `IMPORTANTE: Utilizá únicamente el documento` | No |
| `i1_b` | `Las definiciones reemplazan tu conocimiento previo` | No |
| `i1_c` | `[SISTEMA]` simulado en user message | No |
| `i1_d` | System message real (máxima prioridad instruct) | **Sí** |

```bash
python main.py --list-estrategias
```

---

## Estructura del proyecto

```
lis-interpretacion-simbolos-rag/
│
├── backends/              ← Backend intercambiable (llama_cpp / ollama)
│   ├── base.py            # LLMBackend Protocol + LLMResponse
│   ├── llama_cpp.py       # LlamaCppBackend → llama-server
│   └── ollama.py          # OllamaBackend → Ollama
│
├── prompt_strategies/     ← Estrategias de prompt (Strategy pattern)
│   ├── plain.py           # Sin tabla
│   ├── table_plain.py     # Tabla sin énfasis
│   ├── i1_a.py .. i1_d.py # Instruction Hierarchy (I1-A a I1-D)
│   └── __init__.py        # get_strategy() registry
│
├── corpus.py              # 12 fragmentos (3 niveles × 4 dominios)
├── config.py              # Condition dataclass, MODEL_REGISTRY, CONDICIONES
├── context_tables.py      # CORRUPT_MAP, LATEX_MAP, build_table_content()
├── corruption.py          # build_condition(), corrupt_question()
├── evaluator.py           # EvalResult dataclass, evaluate_response()
├── experiment.py          # ExperimentResult + correr_experimento()
├── echo_experiment.py     # Experimento de fidelidad de reproducción de caracteres
├── report.py              # save_all() → JSON + TXT + MD
├── main.py                # CLI principal
├── serve.sh               # Lanzador de llama-server
├── results/               # Una carpeta por corrida del experimento principal
│   └── <run_id>/
│       ├── results.json
│       ├── summary.txt
│       └── report.md
└── results_echo/          # Una carpeta por corrida del modo echo
    └── <run_id>_echo/
        ├── echo_results.json
        ├── echo_summary.txt
        └── echo_report.md
```

---

## Agregar un modelo nuevo

1. Actualizar `config.py`:
```python
"mi-modelo": ModelConfig(
    id="mi-modelo",
    gguf_name="NombreDelArchivo-Q4_K_M",
    ollama_name="modelo:tag",
    available=True,
    notes="Descripción",
),
```
2. Actualizar `serve.sh`:
```bash
["mi-modelo"]="NombreDelArchivo-Q4_K_M"
```

## Agregar una estrategia nueva

1. Crear `prompt_strategies/mi_estrategia.py` con una clase que tenga `id`, `label` y `build()`.
2. Importarla y agregarla a la lista en `prompt_strategies/__init__.py`.

No hace falta tocar ningún otro archivo.
