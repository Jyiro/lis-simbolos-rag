# Changelog — Experimento RAG Symbol Vulnerabilities

Formato: `[AGREGADO]` `[MODIFICADO]` `[ELIMINADO]` `[DECISIÓN]`

## v2.4 — 2026-09-09 (DeepDoc Research — Extracción Simbólica Empírica)

### Contexto
Se abandona el stack completo de RAGFlow por limitaciones de RAM. En su lugar, se construye un entorno de investigación propio (`deepdoc-research/`) que replica empíricamente el comportamiento del parser subyacente de DeepDoc (pdfplumber + pymupdf + pypdf), sin necesitar levantar el servidor completo.

### [AGREGADO] `deepdoc-research/` — Carpeta de investigación autónoma
- **`probe.py` (Fase 1):** Baseline con PDFs sintéticos (generados con `reportlab`). Extrae todos los símbolos con los tres extractores y calcula un CPR (Char Preservation Rate). Resultado: 100% para todos los símbolos en PDFs ideales.
- **`probe_real.py` (Fase 2):** Análisis sobre el corpus real (`corpus-ragflow/`). Introduce la métrica **EAR (Extractor Agreement Rate)**: si los tres extractores no coinciden en el conteo de un símbolo, se marca discrepancia — sin necesidad de ground truth. Resultado: fallos críticos en los PDFs académicos reales.
- **`phase3a_forensic.py` (Fase 3A):** Análisis forense del texto corrupto. Alinea manualmente el texto de `pypdf` (referencia) con `pdfplumber` (motor RAGFlow) para determinar **qué pone el extractor en lugar del símbolo perdido**.
- **`phase3b_chunking.py` (Fase 3B):** Simula el chunking de tamaño fijo de RAGFlow (≈2000 chars, overlap 200). Mide cuántos símbolos que sí sobrevivieron la extracción quedan partidos entre chunks o pierden su contexto semántico.
- **`phase3c_fonts.py` (Fase 3C):** Análisis de causa raíz via `fonttools`. Documenta por qué `pdfminer.six` (el motor de pdfplumber) falla en fuentes **CFF Type1 con MacRomanEncoding**.

### [AGREGADO] Corpus de PDFs reales extendido a 4 documentos
- `FirstOrderLogic_complete.pdf`
- `ModalLogicFundamentally_complete.pdf`
- `ModalLogicalNeuralNetworks_complete.pdf`
- `abstract-algebra/AbstractAlgebra_cap1-3_symbols.pdf`

### [AGREGADO] Dependencia: `fonttools==4.64.0`
- Instalada en el virtualenv `.venv-ml` para la Fase 3C.

### [DECISIÓN] Metodología EAR en lugar de CPR con ground truth
- Se descartó generar ground truth a mano para los PDFs reales. En su lugar, el consenso entre tres extractores independientes actúa como proxy de "verdad". Si dos de tres concuerdan contra uno, se detecta la discrepancia sin necesidad de etiquetado manual.

### Hallazgos Clave (Fase 2 + Fase 3A)

| Símbolo | Doc | pdfplumber | pypdf | Tipo de Corrupción |
|---|---|---|---|---|
| `∑` (SUM) | AbstractAlgebra | 0 | 65 | Inyecta `(cid:9)` en línea anterior; operador desaparece de la ecuación |
| `∏` (PRODUCT) | AbstractAlgebra | 0 | 19 | Inyecta `(cid:10)` en línea anterior; operador desaparece |
| `⊨` (MODELS) | ModalLogicFundamentally | 0 | 2 | Sustituido por `(cid:15)` (código interno de glifo, no Unicode) |
| `⊢` (TURNSTILE) | FirstOrderLogic | 640 | 640 | PyMuPDF solo ve 216 (instabilidad entre extractores, EAR 33.8%) |

### Hallazgos Clave (Fase 3B — Chunking)

- `⊢` (TURNSTILE) en FirstOrderLogic: **28 de 691 ocurrencias** (4.1%) caen en el borde de un chunk; **165 ocurrencias** (23.9%) quedan en chunks sin palabras clave de contexto semántico.
- La doble pérdida (Fase 2: corrupción en extracción + Fase 3B: pérdida de contexto semántico en chunking) opera en capas independientes y acumulativas.

### Causa Raíz Identificada (Fase 3C) — Hipótesis Inicial (2026-09-09)

`pdfminer.six` (motor subyacente de `pdfplumber` y `DeepDoc`) aplica directamente el encoding `/MacRomanEncoding` declarado en el diccionario de fuente CFF Type1, en lugar de priorizar el mapa `ToUnicode CMap` embebido en la fuente. `pypdf` y `PyMuPDF` priorizan correctamente el CMap, resultando en extracción Unicode correcta. El tag `(cid:X)` es el síntoma visible de este bug de resolución de encoding.

### [REVISIÓN] Causa Raíz — Diagnóstico más preciso (2026-09-17)

> La hipótesis anterior era parcialmente correcta pero incompleta. Tras inspeccionar el código fuente de pdfminer.six, se identificó el mecanismo de fallo principal:

`to_unichr()` en pdfminer **ya intenta primero el ToUnicode CMap** — la prioridad en sí no es el bug principal. El problema real es que los **nombres de glifo TeX** (`summationdisplay`, `productdisplay`, `square`, etc.) **no están en el Adobe Glyph List (AGL)** que usa pdfminer en su `glyphname2unicode`. Cuando una fuente Computer Modern declara `/Differences: [9 /summationdisplay ...]`, pdfminer llama a `name2unicode("summationdisplay")`, no lo encuentra, lanza `PDFKeyError`, y el slot cid=9 queda vacío → `(cid:9)`.

Ambos mecanismos de fallo coexisten según el PDF:
1. **Nombres TeX ausentes del AGL** (principal) — aplica a CMEX, LASY, CMSY
2. **Prioridad de encoding incorrecta** (secundario) — aplica a fuentes sin ToUnicode CMap explícito

**Fix identificado:** Monkey-patch que inyecta la TeX Glyph List en `pdfminer.glyphlist.glyphname2unicode`. Especificación completa en `deepdoc-research/plan_patch.md`.

### Próximos Pasos Planificados

| Prioridad | Acción | Complejidad | Impacto |
|---|---|---|---|
| Alta | **Post-procesador `(cid:X)`:** componente que carga el PDF con `fonttools`, construye el mapa `glifo_id → unicode` por fuente, y reemplaza los `(cid:X)` en el texto ya extraído. | Baja | Alto (fix inmediato para RAGFlow) |
| Media | **Parche a `pdfminer.six`:** forzar prioridad del ToUnicode CMap sobre el `/Encoding` declarado cuando `fonttools` está disponible. Podría resultar en un PR al repo open source. | Media | Alto |
| Alta | **PR a RAGFlow / DeepDoc:** agregar `fonttools` como dependencia + integrar el post-procesador en `deepdoc/parser/`. El benchmark EAR construido funciona como el bug report técnico que justifica el cambio. | Alta | Muy Alto |
| Media | **Hybrid extractor fallback:** detectar tasa de `(cid:X)` por página; si supera umbral, re-extraer esa página con `pypdf` y hacer merge. Sin tocar `pdfminer`. | Media | Medio |

## v2.3 — 2026-08-27 (Integración RAGFlow)

### [AGREGADO] RAGFlow — Fase 3 del pipeline
- **Dataset:** Selección de 4 PDFs académicos con alta densidad de símbolos críticos (recortados inteligentemente en `dataset-ragflow/corpus-ragflow/` para optimizar carga).
- **Setup Híbrido:** Se documentó y resolvió la arquitectura dividida: LLM en Kaggle (via Ngrok) y modelo de Embedding (`nomic-embed-text`) ejecutado localmente con Ollama para mayor performance.
- **Troubleshooting:** Se descubrió y mitigó el problema del "bloqueo de túnel" en Ngrok al separar el lanzador del túnel del lanzador de modelo en celdas de Kaggle distintas.
- **Evidencia Empírica de Falla:** Se detectó el Punto de Falla 1 real en el sistema — el parser de RAGFlow elimina (truncamiento) los símbolos Unicode (como `□` y `◇`) antes de llegar al embedding. Esto valida completamente la necesidad del estudio.
- Documentación completa en `ragflow_setup.md`.

## v2.9 — 2026-09-17

### Contexto
Fin de la fase diagnóstica. Aislamiento absoluto del bug de extracción y paso a fase de implementación de solución técnica.

### [NUEVO] Plan de Implementación: Monkey-patch dinámico
- El rastreo exhaustivo en arXiv determinó que `MacRomanEncoding` no es el factor primario: la ausencia de nombres de glifo TeX en el AGL de `pdfminer.six` causa la falla silenciosa en todas las fuentes `CMEX`/`LASY` independientemente del vector de encoding.
- Se resolvió atacar la causa raíz mediante **Monkey-patching**. En lugar de requerir que RAGFlow implemente lógica multi-librería (hybrid fallback) o espere meses por un PR en `pdfminer.six`, se inyectará la TeX Glyph List directamente en el entorno de ejecución de Python.
- Actualización de `TODO.md` y `evidencias.md` para reflejar este enfoque como la solución óptima.

## v2.8 — 2026-09-16

### Contexto
Validación estadística sobre corpus arXiv + análisis de causa raíz (Exp 13).

### [NUEVO] Corpus arXiv Expandido
- Se crearon `arxiv_harvest.py` y `probe_arxiv.py` para descargar y analizar 30 papers de arXiv en categorías de matemática y lógica.
- **Resultado:** 7/30 papers (23%) con discrepancias. Símbolos fallidos: ∑ CMEX (4 docs), □ LASY (3 docs), ∏ CMEX (1 doc).

### [NUEVO] Causa Raíz Identificada con Precisión
- El bug reside en la **capa de mapeo Glyph → Unicode** de `pdfminer.six`.
- Los glyph names de CMEX (`summationtext`, `producttext`) no están en el Adobe Glyph List (AGL). Sin tabla `ToUnicode` CMap en el PDF, `pdfminer.six` no puede resolverlos.
- La solución canónica (ISO 32000 / PDFlib `forceencoding`): aplicar la **TeX glyph list** para fuentes `CM*`/`CMEX*`/`LASY*`.

## v2.7 — 2026-09-16

### Contexto
Evaluación de fuentes TrueType (TTF) (Exp 12).

### [NUEVO] Descubrimiento de Fallo Estructural (Corregido)
- Se creó `probe_ttf.py` generando PDFs sintéticos con fuentes modernas TTF (`Segoe UI Symbol`).
- **Hallazgo Crítico:** Todos los extractores de Python (`pdfplumber`, `PyMuPDF`, `pypdf`) lograron un **100% de CPR** al extraer los símbolos matemáticos (`∀`, `∃`, `⊢`, `⊨`, etc.).
- Esto **confirma definitivamente la hipótesis original**: el bug está estrictamente limitado a encodings legacy (CFF/Type1 MacRomanEncoding) provenientes de LaTeX (Computer Modern). Los PDFs modernos y las fuentes TTF Unicode nativas no sufren corrupción. El scope del problema es acotado pero crucial para papers académicos.

## v2.6 — 2026-09-16

### Contexto
Métrica de Diferencia de Embeddings (Exp 11).

### [NUEVO] Análisis de Impacto en Retrieval
- Se creó `embedding_diff.py` para comparar vectores de `pypdf` vs `pdfplumber` usando `paraphrase-multilingual-MiniLM-L12-v2`.
- Se demostró cuantitativamente que la corrupción hace caer el cosine similarity a ~0.55, confirmando que RAGFlow no puede recuperar estos fragmentos durante una consulta.

## v2.5 — 2026-09-16

### Contexto
Evaluación de `pymupdf4llm` como alternativa de extracción a Markdown.

### [NUEVO] Extractor pymupdf4llm
- Se agregó a `probe_real.py` el cuarto extractor `pymupdf4llm`.
- Se concluyó que tiene un rendimiento peor que `pdfplumber` omitiendo y corrompiendo símbolos, por lo que se descartó como solución.

---

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
