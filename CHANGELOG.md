# Changelog — Experimento RAG Symbol Vulnerabilities

Formato: `[AGREGADO]` `[MODIFICADO]` `[ELIMINADO]` `[DECISIÓN]`

## v2.3 — 2026-08-27 (Integración RAGFlow)

### [AGREGADO] RAGFlow — Fase 3 del pipeline
- **Dataset:** Selección de 4 PDFs académicos con alta densidad de símbolos críticos (recortados inteligentemente en `dataset-ragflow/corpus-ragflow/` para optimizar carga).
- **Setup Híbrido:** Se documentó y resolvió la arquitectura dividida: LLM en Kaggle (via Ngrok) y modelo de Embedding (`nomic-embed-text`) ejecutado localmente con Ollama para mayor performance.
- **Troubleshooting:** Se descubrió y mitigó el problema del "bloqueo de túnel" en Ngrok al separar el lanzador del túnel del lanzador de modelo en celdas de Kaggle distintas.
- **Evidencia Empírica de Falla:** Se detectó el Punto de Falla 1 real en el sistema — el parser de RAGFlow elimina (truncamiento) los símbolos Unicode (como `□` y `◇`) antes de llegar al embedding. Esto valida completamente la necesidad del estudio.
- Documentación completa en `ragflow_setup.md`.

## v2.2 — 2026-08-20 (Sesión Actual)

### Contexto
Estabilización del entorno de ejecución remoto vía Kaggle + Ngrok y ejecución masiva del experimento "Rebuild" para auditar modelos de nueva generación en tareas de decodificación estricta.

### [AGREGADO] Ampliación del Model Registry a 8 modelos
- Se agregaron a `config.py` y `README.md` perfiles completos para Llama-3.1-8b, Llama-3.2-3b, Phi-4, Phi-4-mini y Gemma-4b, complementando la familia Qwen.

### [MODIFICADO] `backends/llama_cpp.py` — Bypass de Ngrok y estándar OpenAI
- Se inyectó el header `ngrok-skip-browser-warning: true` globalmente en todas las peticiones HTTP para evitar que Ngrok intercepte y bloquee los Health Checks con su landing page HTML.
- Los endpoints de ping pasaron de `/health` a `/v1/models` para alinearse con la compatibilidad de la API de OpenAI expuesta por `llama-server`.

### [MODIFICADO] `kaggle_guide.md` — Optimización de Instalación
- Se corrigió el flujo de despliegue en Kaggle. En vez de compilar desde cero, se documentó el uso explícito de *wheels* precompilados para CUDA 12.1 (`cu121`) de `llama-cpp-python`, evitando fallos de compilación y *memory locks*.

### [DECISIÓN] Análisis Exhaustivo Rebuild (CER vs Levenshtein)
- Se consolidó la ejecución del experimento sobre los 8 modelos. Se creó un análisis profundo demostrando que modelos <4B parámetros sufren *Over-Alignment* (alucinando conversacionalmente o inyectando LaTeX) o truncamientos severos al enfrentar matemáticas en un segundo idioma (ES).
- Se documentó metodológicamente por qué contrastar **CER vs Distancia de Levenshtein** es clave para separar un colapso atencional de una simple alucinación de relleno.

---

## v2.1 — 2026-08-11

### [AGREGADO] Modo `--modo echo` para validación de fidelidad de caracteres (Mojibake)

- Nuevo flag `--modo {experimento,echo}` en `main.py`.
- Módulo `echo_experiment.py`: verifica si el LLM normaliza (sanitiza) los caracteres corruptos enviando peticiones de eco y comparando el resultado byte a byte en UTF-8 Hex.
- Salidas diferenciadas en `results_echo/<run_id>/` (`echo_results.json`, `echo_summary.txt`, `echo_report.md`).
- Constante `ECHO_RESULTS_DIR = "results_echo"` en `config.py`.

---

## v2.0 — 2026-08-04 (sesión actual)

### Contexto
Después de la presentación, el profesor sugirió explorar la **Terquedad Semántica** (Semantic Stubbornness) de forma sistemática: cuando el modelo conoce un símbolo, ignora las instrucciones RAG; cuando no lo conoce, las sigue. Se rediseña el experimento para convertir esto en la hipótesis central.

### [MODIFICADO] Arquitectura general — migración de Ollama a llama.cpp + diseño de interfaz

**Antes:** Un solo archivo `ollama_client.py` con llamada directa a la API de Ollama.

**Ahora:** Paquete `backends/` con `LLMBackend Protocol`. Los backends son intercambiables sin tocar el código experimental.
- `backends/llama_cpp.py` — para esta laptop (llama-server en `:8080`)
- `backends/ollama.py` — para la PC de escritorio (Ollama en `:11434`)
- Selección en runtime: `python main.py --backend llama_cpp|ollama`

**Razón:** Los experimentos necesitan correrse en dos máquinas con hardware distinto.

---

### [AGREGADO] Paquete `prompt_strategies/` — Instruction Hierarchy

**Antes:** `prompt_builder.py` con un solo formato de tabla y opción `con_tabla: bool`.

**Ahora:** Paquete `prompt_strategies/` con 6 estrategias registradas. Basado en `estrategias-prompt.md` (Instruction Hierarchy):

| ID | Estrategia | System role |
|----|-----------|-------------|
| `plain` | Sin tabla — baseline puro | No |
| `table_plain` | Tabla sin énfasis | No |
| `i1_a` | "IMPORTANTE: Utilizá únicamente el documento" | No |
| `i1_b` | "Las definiciones reemplazan tu conocimiento previo" | No |
| `i1_c` | "[SISTEMA]" simulado en user message | No |
| `i1_d` | Tabla en system role real (máxima prioridad instruct) | **Sí** |

**Razón:** Explorar si la agresividad de la instrucción puede romper la Terquedad Semántica.

---

### [MODIFICADO] `config.py` — Condiciones y Model Registry

**Antes:**
```python
CONDICIONES = [
    ("LIMPIO    | doc✓ query✓ sin tabla", "limpio",   False, False),
    ("DOC CORR  | doc✗ query✓ sin tabla", "corrupto", False, False),
    ("FULL CORR | doc✗ query✗ sin tabla", "corrupto", False, True),
    ("QUERY CORR| doc✓ query✗ sin tabla", "limpio",   False, True),
    ("CON TABLA | doc✗ query✓ con tabla", "corrupto", True,  False),
    ("LATEX     | doc~ query✓ sin tabla", "latex",    False, False),
]
# MODELO = "qwen3:1.7b"  (string plano)
```

**Ahora:**
- `Condition` dataclass (frozen, hasheable)
- `ModelConfig` dataclass con `gguf_name`, `ollama_name`, `available`
- 10 condiciones (6 anteriores reemplazadas por las 5 baselines + 5 estrategias I1)
- 4 modelos registrados (2 disponibles + 2 stubs)

---

### [MODIFICADO] `evaluator.py` — EvalResult dataclass

**Antes:** Retornaba un string (`"✓ CORRECTO"`, etc.).

**Ahora:** Retorna `EvalResult` con `result`, `matched_expected`, `matched_forbidden`, `expected_terms`, `forbidden_terms`. Permite análisis post-hoc detallado.

---

### [MODIFICADO] `report.py` — 3 formatos de salida por corrida

**Antes:** Un `.txt` y un `.json` en `results/` con timestamp en el nombre.

**Ahora:** Directorio `results/<run_id>/` con:
- `results.json` — datos completos y estructurados (para análisis programático)
- `summary.txt` — resumen tabular + análisis Instruction Hierarchy
- `report.md` — markdown para presentaciones y borrador de paper

---

### [MODIFICADO] `main.py` — CLI mejorado

**Antes:** Solo `--modelo`.

**Ahora:** `--modelo`, `--backend`, `--fragmentos`, `--condiciones`, `--list-modelos`, `--list-estrategias`, `--list-backends`.

---

### [ELIMINADO] `ollama_client.py` y `prompt_builder.py`

Reemplazados por `backends/` y `prompt_strategies/` respectivamente.

---

### [AGREGADO] `serve.sh` — lanzador de llama-server

Script que mapea ID de modelo → archivo GGUF y lanza `llama-server`.

---

## v2.1 — 2026-08-04 (esta sesión, continúa)

### Contexto
Diseño del corpus para el experimento de Instruction Hierarchy. Se decide recortar el corpus original de 12 fragmentos a 7, y las condiciones de 10 a 8.

### [ELIMINADO] Condiciones FULL CORR y QUERY CORR

**Antes (10 condiciones):**
- LIMPIO, DOC CORR, FULL CORR, QUERY CORR, LATEX, CON TABLA | plain, I1-A, I1-B, I1-C, I1-D

**Ahora (8 condiciones):**
- LIMPIO, DOC CORR, LATEX, CON TABLA | plain, I1-A, I1-B, I1-C, I1-D

**Razón:** FULL CORR y QUERY CORR simulan escenarios donde la query llega corrupta. No interactúan con la tabla de contexto y no son relevantes para la hipótesis de Instruction Hierarchy. Se mantienen en el código como condiciones disponibles pero se excluyen de `CONDICIONES` por defecto.

---

### [MODIFICADO] `corpus.py` — Reducción de 12 a 7 fragmentos

**Fragmentos eliminados y razón:**

| ID | Razón de eliminación |
|----|---------------------|
| `A1_desigualdad` (≥) | Contexto lingüístico rescata siempre — ninguna condición muestra efecto |
| `A2_bicondicional` (⟺) | El 1.7b falla incluso con texto limpio → límite del modelo, no del símbolo |
| `A3_cuantificador` (∀) | Contexto lingüístico rescata siempre (`x² ≥ 0` es tautología obvia) |
| `B1_equilibrio` (⇌) | Reacción Fe/Ce famosa — el modelo deduce reversibilidad por conocimiento de química |
| `C1_ipa` (æ) | La corrupción no afecta al modelo (tokenización fortuita robusta) |

**Fragmentos conservados y rol:**

| ID | Símbolo | Rol en el experimento |
|----|---------|----------------------|
| `A4_producto_cart` | × | Control — divergencia entre modelos (1.7b resiste, 4b falla con corrupción) |
| `B2_angstrom` | Å | Efecto principal — corrupción → confusión → tabla lo recupera |
| `B3_modal` | □ | **Terquedad central** — falla en TODAS las condiciones incluso con tabla |
| `B4_subconjunto` | ⊂ | **Terquedad central** — ídem B3 |
| `C2_interpunct` | · | Control de baja frecuencia — el modelo obedece instrucciones sin resistencia |
| `C3_musical` | ♭ | Efecto principal — curva de degradación y recuperación clara |
| `C4_obelus` | † | Efecto principal — símbolo filológico oscuro con divergencia entre modelos |

**Costo del experimento:** 7 fragmentos × 8 condiciones × 4 modelos = **224 llamadas totales**

---

### [AGREGADO] Streaming de respuestas en consola

`on_token` callback en el protocolo `LLMBackend.query()`. Permite ver las respuestas del modelo en tiempo real en la consola durante el experimento, sin esperar al final del run.

---

## v1.0 — 2026-07-29 (corridas originales)

### Corpus original (8 fragmentos)
F1_composicion (∘), F2_enteros_vs_reales (ℤ), F3_existe_unico (∃!), F4_bicondicional (↔), F5_cuantificadores (∀∃), F6_norma (‖v‖), F7_producto_cartesiano (×), F8_implicacion (∧→).

### Condiciones (4)
LIMPIO sin tabla, CORRUPTO sin tabla, CORRUPTO con tabla, LATEX sin tabla.

### Modelo
`qwen3:1.7b` vía Ollama.

### Hallazgo principal
F3 (∃!) y F7 (×): la corrupción causó pérdida real de información; la tabla la recuperó. Identificación de fragmentos problemáticos: redundancia contextual (F2, F4, F5, F8) y fallo de conocimiento del modelo (F1, F6).

---

## v1.1 — 2026-07-29 (mismo día)

### [MODIFICADO] Corpus ampliado a 12 fragmentos con 3 niveles de frecuencia

Diseño basado en hipótesis de frecuencia en corpus de preentrenamiento:
- Alta: A1-A4 (≥, ⟺, ∀, ×)
- Media: B1-B4 (⇌, Å, □, ⊂)
- Baja: C1-C4 (æ, ·, ♭, †)

### [MODIFICADO] Condiciones ampliadas a 6

Agregadas: FULL CORR (doc✗ query✗) y QUERY CORR (doc✓ query✗).

### Modelos comparados
`qwen3:1.7b` y `qwen3:4b-instruct-2507-q4_K_M` vía Ollama.

### Hallazgos principales
- **Efecto principal confirmado**: A2 (⟺), B2 (Å), C3 (♭)
- **Terquedad Semántica identificada**: B3 (□), B4 (⊂) — ambos modelos ignoran la tabla RAG
- **Tokenización Fortuita**: C1 (æ), C2 (·) — mojibake a veces mejora el rendimiento
- **Redundancia Contextual**: A1, A3, B1 — contexto lingüístico rescata sin necesidad del símbolo
