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

# Experimento de reconstrucción (modo rebuild)
# El LLM recibe frases con múltiples corrupciones + tabla de decodificación
~/.venv-ml/bin/python3 main.py --modo rebuild                    # tabla mínima (solo símbolos presentes)
~/.venv-ml/bin/python3 main.py --modo rebuild --tabla-completa   # tabla completa (todo el CORRUPT_MAP)
~/.venv-ml/bin/python3 main.py --modo rebuild --modelo gemma-4b

# Smoke test (Verificar conexión rápida con el LLM, útil si estás usando ngrok)
~/.venv-ml/bin/python3 main.py --modo smoke
```

### 3. Ver resultados

```
results/<run_id>/
├── results.json   ← datos completos (keywords + cosine similarity)
├── summary.txt    ← resumen tabular rápido (incluye prom. semántico)
└── report.md      ← markdown con análisis y scores de similitud contrastiva

results_echo/<run_id>/
├── echo_results.json   ← datos completos con comparación de bytes y Levenshtein
├── echo_summary.txt    ← tabla rápida con distancias y clasificación
└── echo_report.md      ← reporte con auditoría hexadecimal byte a byte

results_rebuild/<run_id>/
├── rebuild_results.json   ← reconstrucciones completas con CER por fragmento
├── rebuild_summary.txt    ← tabla rápida: fragmento, símbolos, distancia y CER
└── rebuild_report.md      ← markdown con comparación original vs. reconstruido
```

---

## Arranque rápido — Ollama (PC de escritorio)

```bash
# Sin cambios en el código — solo cambiar el flag
~/.venv-ml/bin/python3 main.py --backend ollama --modelo qwen3.5-2b
~/.venv-ml/bin/python3 main.py --backend ollama --modelo qwen3-4b
```

---

## RAGFlow (Fase 3 — Pipeline completo)

Para correr experimentos con el pipeline RAG real (interfaz gráfica):

### 0. Instalar Ollama (si no lo tenés)

```bash
# Arch/CachyOS/Manjaro — instalar via script oficial (el paquete AUR puede estar desactualizado)
curl -fsSL https://ollama.com/install.sh | sh

# Verificar instalación
ollama --version
```

> Ollama se instala como servicio del sistema y arranca automáticamente en `http://localhost:11434`.

### 1. Levantar el servidor de embedding local

```bash
ollama pull nomic-embed-text   # solo la primera vez (~274 MB)

# Si RAGFlow corre en Docker, Ollama debe escuchar en todas las interfaces:
OLLAMA_HOST=0.0.0.0 ollama serve   # en una terminal separada (si ollama no está como servicio)
```

> Si `ollama serve` dice "address already in use", el servicio ya está corriendo — no hace falta correr ese comando.

### 2. Levantar el Chat LLM (Kaggle via Ngrok)

```bash
# Separar en dos celdas de Kaggle:
# Celda 1 (Ngrok): corre UNA vez para obtener la URL pública fija
# Celda 2 (LLM): !python -m llama_cpp.server --model {MODEL} --host 0.0.0.0 --port 8000 --n_gpu_layers -1 --n_ctx 8192 --embedding
```

### 3. Iniciar RAGFlow y configurar providers
Ver el archivo [`ragflow_setup.md`](ragflow_setup.md) para la configuración paso a paso de los providers y subida de los PDFs del corpus experimental.

---

## Arranque rápido — Nube (Kaggle + Ngrok)

Si tu computadora no tiene suficiente VRAM, podés levantar el LLM en **Kaggle** aprovechando sus 2 GPUs T4 (30GB VRAM) y conectarte remotamente desde este repositorio local usando `ngrok`. 

1. Seguí las instrucciones del archivo **`kaggle_guide.md`** incluido en este repositorio para levantar el LLM allá.
2. Ngrok te dará una URL (ej: `https://1a2b-3c4d.ngrok-free.app`).
3. En tu terminal local, configurá la variable de entorno y corré el código normalmente:

```bash
export LLAMA_CPP_URL="https://1a2b-3c4d.ngrok-free.app"
~/.venv-ml/bin/python3 main.py --modo smoke
~/.venv-ml/bin/python3 main.py --modo experimento
```
*(El archivo `backends/llama_cpp.py` tomará la variable automáticamente en lugar de buscar en localhost).*

---

## Hallazgos Metodológicos Clave

El proyecto implementa dos marcos de evaluación robustos para auditar LLMs:

### 1. Test ECHO (Fidelidad a nivel de Byte)
Verifica si el LLM "sanitiza" el texto corrupto (Mojibake) antes de procesarlo, lo cual invalidaría un experimento RAG. 
- Utiliza **Distancia de Levenshtein** y **Auditoría Hexadecimal**.
- **Descubrimiento (La Curva en U):** Modelos pequeños (2B) copian fielmente la basura porque carecen de inferencia. Modelos medianos (4B) detectan el error tipográfico e intentan "autocorregirlo" (Distancia > 0), desobedeciendo la instrucción de copiar literalmente. Modelos grandes (9B) detectan el error pero tienen el "alignment" necesario para obedecer al usuario y mantener fidelidad absoluta.

### 2. Test de Reconstrucción (Decodificación Activa)
A diferencia del ECHO que prueba obediencia pasiva, el Rebuild evalúa comprensión activa: el LLM recibe frases con **múltiples puntos de corrupción simultáneos** (hasta 7 símbolos diferentes en una sola frase) y una tabla de decodificación, y debe reconstruir el texto original.
- Métricas: **CER (Character Error Rate)** y **Levenshtein** respecto al texto limpio original.
- Flag `--tabla-completa` para comparar si más contexto ayuda o satura al modelo.
- Evalúa si el modelo puede operar como un "decodificador activo" cuando se le proveen las reglas de traducción.

### 3. Evaluación Semántica Continua
Las palabras clave (`✓` / `✗`) son binarias y frágiles. Se implementó un pipeline con `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`):
- **Max Cosine Similarity:** Se compara la respuesta del LLM contra múltiples referencias válidas, tomando la mayor similitud para absorber parafraseos.
- **Score Contrastivo:** Se resta la similitud de una respuesta "terca" o alucinada. Un score negativo cuantifica empíricamente la **Terquedad Semántica** (cuando el LLM desobedece el RAG y prioriza sus pesos paramétricos erróneos).

---

## Modelos disponibles

| ID | GGUF | Ollama | Estado |
|----|------|--------|--------|
| `qwen3.5-2b` | `Qwen3.5-2B-Q4_K_M.gguf` | `qwen3.5:2b` | ✅ |
| `qwen3.5-4b` | `qwen3.5-4b-instruct-Q4_K_M.gguf` | `qwen3.5:4b` | ✅ |
| `qwen3.5-9b` | `Qwen3.5-9B-Q4_K_M.gguf` | `qwen3.5:8b` | ✅ |
| `gemma-4b` | `gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf` | `gemma3:4b` | ✅ |
| `phi-4-mini` | `microsoft_Phi-4-mini-instruct-Q4_K_M.gguf`| `phi4:mini` | ✅ |
| `phi-4` | `phi-4-Q4_K_M.gguf` | `phi4` | ✅ |
| `llama-3.2-3b`| `llama-3.2-3b-instruct-q4_k_m.gguf` | `llama3.2` | ✅ |
| `llama-3.1-8b`| `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` | `llama3.1` | ✅ |

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

## Siguientes pasos

- Explicar brevemente el área / tópico para ver si varían los resultados.
- Explicaciones técnicas de diferencias entre las familias de modelos, benchmarks de qué tanto siguen instrucciones.
- Mantener un ojo para la regresión de los modelos: detección de problemas en los chunks.
