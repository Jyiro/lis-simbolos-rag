# Timeline de Investigación — RAG Symbol Experiment

> **Propósito de este documento:** Narrar la evolución de la investigación por experimentos, no por versiones de código (para eso existe [`CHANGELOG.md`](../CHANGELOG.md)). Cada entrada responde: *¿qué preguntamos, cómo lo probamos, qué encontramos, y a qué nos llevó?*
>
> **Unidad de organización:** experimento individual, no sesión de trabajo.

---

## Resumen visual

```
Jul 2026                    Ago 2026                          Sep 2026
    │                           │                                 │
[1] Corpus          [3] Instruction   [4] ECHO      [6] RAGFlow  [7-9] DeepDoc
    original    [2] Hierarchy    [5] Rebuild         real          Research
    (8 frags)  ampliado                                            (Fases 1-3C)
               (12 frags)
```

---

## Exp 1 — Fase 1: Corpus Original (8 fragmentos)

**Julio 2026** · `main.py` (versión inicial) · Resultados en [`results/resultados-viejos-v1/`](../results/resultados-viejos-v1/)

### Objetivo
Verificar si un LLM local puede interpretar texto con símbolos matemáticos corruptos (mojibake UTF-8), y si una tabla de contexto inyectada en el prompt puede recuperar la comprensión perdida.

### Diseño
- **Corpus:** 8 fragmentos matemáticos (composición de funciones, enteros, cuantificadores, producto cartesiano, norma vectorial, bicondicional, implicación, existe-único)
- **Condiciones:** 4 por fragmento — LIMPIO, DOC CORR, CON TABLA, LATEX
- **Modelo:** `qwen3:1.7b` vía Ollama
- **Evaluación:** keyword matching binario (✓ CORRECTO / ✗ CONFUNDIDO / ? SIN RESPUESTA)

### Hallazgos
Los 8 fragmentos se separaron espontáneamente en tres categorías:

| Categoría | Fragmentos | Patrón |
|---|---|---|
| **Corrupción importa** | ∃! (F3), × (F7) | Limpio→✓, Corrupto→✗/?, Con Tabla→✓ — validan la hipótesis |
| **Contexto rescata** | ∀, ↔, ∧→, ℤ | El modelo responde igual con o sin símbolo — fragmentos mal diseñados |
| **Fallo de conocimiento** | ∘ (F1), ‖v‖ (F6) | Falla incluso con texto limpio — límite del 1.7B, no del símbolo |

**Resultado neto:** 2 de 8 fragmentos son "casos de oro" (F3 y F7). Los otros 6 revelan problemas de diseño del corpus o limitaciones del modelo.

### ¿Qué motivó el siguiente paso?
El corpus necesitaba rediseño: cerrar los "escapes contextuales" y agregar fragmentos de distintos dominios y frecuencias de símbolo. También surgió la pregunta de si el fallo de F1/F6 desaparecería con un modelo más grande.

### Documentos relacionados
- [`docs/investigacion.md`](investigacion.md) — marco teórico completo
- [`docs/archivo/contexto-experimento.md`](archivo/contexto-experimento.md) — diario de diseño de esta fase

---

## Exp 2 — Fase 1: Corpus Ampliado (12 fragmentos, 3 niveles)

**Julio 2026** · `main.py` (v1.1) · Resultados en [`results/resultados-viejos-v1/`](../results/resultados-viejos-v1/)

### Objetivo
Probar la **hipótesis de frecuencia en preentrenamiento**: la capacidad del modelo de compensar la corrupción de un símbolo depende de cuán frecuente es ese símbolo en el corpus de preentrenamiento.

### Diseño
- **Corpus:** 12 fragmentos reorganizados en 3 niveles de frecuencia estimada
  - **Alta** (A1–A4): ≥, ⟺, ∀, × — deberían ser compensados por el modelo
  - **Media** (B1–B4): ⇌, Å, □, ⊂ — degradación parcial esperada
  - **Baja** (C1–C4): æ, ·, ♭, † — fallo sin compensación esperado
- **Condiciones:** 6 (se agregan FULL CORR y QUERY CORR)
- **Modelos:** `qwen3:1.7b` y `qwen3:4b-instruct-2507` vía Ollama para comparativa

### Hallazgos

| Fenómeno | Fragmentos | Descripción |
|---|---|---|
| **✦ Efecto principal** | A2 (⟺), B2 (Å), C3 (♭) | Curva limpia: Limpio→✓, Corrupto→✗, Con Tabla→✓ |
| **⚡ Terquedad Semántica** | B3 (□), B4 (⊂) | El modelo ignora la tabla RAG en todas las condiciones — alucinación paramétrica que supera al contexto inyectado |
| **🔤 Tokenización Fortuita** | C1 (æ), C2 (·) | La corrupción *mejora* el rendimiento — el mojibake actúa como separador más efectivo que el símbolo limpio |
| **⚠ Redundancia Contextual** | A1, A3, B1 | El contexto circundante rescata la respuesta sin importar el símbolo |

**Patrón 1.7B vs 4B:** el 4B compensa la redundancia contextual por volumen paramétrico (enmascara el efecto), mientras que el 1.7B muestra la *paradoja de la obediencia*: obedece la tabla RAG exactamente cuando *no conoce* el símbolo, y la ignora cuando sí lo conoce.

### ¿Qué motivó el siguiente paso?
La Terquedad Semántica emergió como hallazgo central. La pregunta: ¿puede una instrucción más agresiva (colocada en el canal de mayor prioridad del modelo) romper ese sesgo paramétrico?

### Documentos relacionados
- [`docs/fase1_analisis.md`](fase1_analisis.md) — análisis metodológico completo
- [`docs/fase1_resultados.md`](fase1_resultados.md) — tabla detallada de respuestas por modelo y condición

---

## Exp 3 — Fase 1: Instruction Hierarchy (I1-A a I1-D)

**Agosto 2026** · `main.py` (v2.0–v2.1) · Resultados en [`results/`](../results/)

### Objetivo
Probar si colocar las instrucciones RAG en el canal de **máxima prioridad** del modelo (`system message`) puede superar la Terquedad Semántica, frente a variantes de colocación en el canal `user`.

### Diseño
- **Corpus reducido:** 7 fragmentos (eliminados los 5 con redundancia o fallos de conocimiento probados)
- **8 condiciones:** 3 baselines (LIMPIO, DOC CORR, LATEX) + 5 estrategias de prompt

| Estrategia | Canal | Descripción |
|---|---|---|
| `plain` | user | Sin tabla — baseline puro |
| `table_plain` | user | Tabla sin énfasis |
| `i1_a` | user | "IMPORTANTE: Utilizá únicamente el documento" |
| `i1_b` | user | "Las definiciones reemplazan tu conocimiento previo" |
| `i1_c` | user | `[SISTEMA]` simulado en user message |
| `i1_d` | **system** | System message real — máxima prioridad instruct |

- **Modelos:** Qwen3.5-2B y Gemma-4B (primer modelo no-Qwen del proyecto)
- **Migración técnica:** abandono de Ollama, adopción de `llama-server` (llama.cpp). Arquitectura `backends/` intercambiable.

### Hallazgos

| Fenómeno | Detalle |
|---|---|
| **`I1-D` rompe la Terquedad de Gemma** | En B3 (□), Gemma ignoró todas las estrategias de usuario. Solo el System Message forzó compliance. |
| **`I1-C` es óptima para Qwen 2B** | El "rol simulado" con `[SYSTEM]` en el canal user funciona mejor para modelos pequeños con inestabilidad atencional. |
| **Over-refusal de Gemma con `I1-D`** | Al recibir reglas estrictas en el canal system, Gemma se abstiene en lugar de responder, incluso en casos donde antes acertaba. Trade-off: anti-alucinación vs capacidad de inferencia. |

### ¿Qué motivó el siguiente paso?
Antes de concluir que la Instruction Hierarchy funciona, había que auditar una premisa: ¿los modelos estaban procesando el texto corrupto tal cual, o lo "autocorregían" silenciosamente antes?

### Documentos relacionados
- [`docs/instruccion_hierarchy.md`](instruccion_hierarchy.md) — análisis cualitativo exhaustivo Qwen vs Gemma
- [`docs/estrategias_prompt.md`](estrategias_prompt.md) — ideación original de las estrategias I1

---

## Exp 4 — Test ECHO: Fidelidad de Caracteres

**Agosto 2026** · `echo_experiment.py` · Resultados en [`results_echo/`](../results_echo/)

### Objetivo
Auditar si el LLM "sanitiza" silenciosamente el texto corrupto (mojibake) antes de procesarlo. Si lo hace, los experimentos de Fase 1 estarían midiendo la corrección del modelo, no su comprensión del texto corrupto tal como llega.

### Diseño
- Se le pide al modelo que copie literalmente una cadena corrupta
- Se compara el output byte a byte con el input usando **Distancia de Levenshtein**
- Se audita carácter a carácter en hexadecimal para detectar sustituciones silenciosas
- **Modelos:** Qwen3.5-2B, 4B, 9B

### Hallazgo principal — La Curva en U

| Modelo | Comportamiento | Levenshtein |
|---|---|---|
| **Qwen3.5-2B** | Copia fielmente — carece de inferencia para detectar el "error" | 0 |
| **Qwen3.5-4B** | Detecta el "error tipográfico" e intenta autocorregirlo — **desobedece la instrucción** | > 0 |
| **Qwen3.5-9B** | Detecta el error pero tiene alignment suficiente para obedecer al usuario | 0 |

**Consecuencia metodológica:** el 4B puede estar procesando una versión parcialmente corregida del texto, no el mojibake exacto. Los resultados de Fase 1 con este modelo tienen esa advertencia.

---

## Exp 5 — Test Rebuild: Decodificación Activa

**Agosto 2026** · `rebuild_experiment.py` · Resultados en [`results_rebuild/`](../results_rebuild/)

### Objetivo
Evaluar si el LLM puede operar como "decodificador activo": dada una frase con **múltiples puntos de corrupción simultáneos** (hasta 7 símbolos distintos) más una tabla de decodificación, ¿puede reconstruir el texto original?

### Diseño
- Fragmentos con corrupción múltiple (todo el `CORRUPT_MAP` aplicado)
- Dos modos: `--tabla-completa` vs tabla mínima (solo símbolos presentes)
- **Métricas:** CER (Character Error Rate) y Levenshtein respecto al texto limpio original
- **Modelos:** 8 (familia Qwen, Llama 3.1/3.2, Phi-4/mini, Gemma-4B)

### Hallazgos

| Hallazgo | Detalle |
|---|---|
| **Over-Alignment en modelos < 4B** | Los modelos pequeños alucinan conversacionalmente o inyectan LaTeX en lugar de reconstruir literalmente |
| **Colapso atencional en español** | Modelos entrenados principalmente en inglés sufren degradación severa ante matemáticas en ES |
| **CER vs Levenshtein como par diagnóstico** | CER alto + Levenshtein bajo → truncamiento severo. Ambos altos → alucinación de relleno. |
| **Más contexto no siempre ayuda** | La `--tabla-completa` en ocasiones saturó al modelo y empeoró el CER |

---

## Exp 6 — Fase 3: RAGFlow Real (Pipeline Completo)

**Agosto 2026** · Setup en [`docs/ragflow_setup.md`](ragflow_setup.md)

### Objetivo
Validar end-to-end los hallazgos de Fase 1 sobre el pipeline RAG real: documentos reales ingestados, embeddings generados, retrieval real, respuesta del LLM con contexto recuperado.

### Diseño — Arquitectura híbrida
```
LLM (Chat)  →  Kaggle T4 GPU  →  llama_cpp.server  →  Ngrok tunnel
Embedding   →  Local Ollama   →  nomic-embed-text
RAGFlow     →  Docker local   →  Interfaz web
```
- **Corpus:** 4 PDFs académicos (Álgebra Abstracta, Lógica Modal, Lógica Primer Orden, Redes Neuronales Modales)
- **Queries de prueba:** símbolos □ y ⊂ — los mismos de la Terquedad Semántica

### Hallazgo central
**Punto de Falla 1 confirmado empíricamente:** el parser de DeepDoc/pdfplumber **elimina los símbolos Unicode** antes de llegar al embedding. Al revisar los chunks en la UI de RAGFlow, los símbolos (□, ◇) no estaban en el texto — el LLM respondía en base a contexto sin el símbolo crítico.

### Limitaciones
- RAGFlow completo requiere ~16GB RAM
- Setup Kaggle+Ngrok frágil (URL de tunnel cambia al reiniciar)
- **Decisión:** replicar el parser de forma autónoma → Experimentos 7–9

---

## Exp 7 — DeepDoc Research Fase 1: PDFs Sintéticos (Baseline CPR)

**Septiembre 2026** · `parser_analysis/probe.py` · [`parser_analysis/summary_report.md`](../parser_analysis/summary_report.md)

### Objetivo
Establecer un baseline: ¿funcionan perfectamente los extractores en condiciones ideales? Si sí, el bug que encontramos es específico a cómo LaTeX codifica las fuentes en PDFs académicos.

### Resultado
CPR 100% en todos los extractores (`pdfplumber`, `PyMuPDF`, `pypdf`) sobre 6 PDFs sintéticos. **El bug no existe en PDFs con encoding Unicode correcto** — es específico a fuentes CFF Type1.

---

## Exp 8 — DeepDoc Research Fase 2: PDFs Reales (Métrica EAR)

**Septiembre 2026** · `parser_analysis/probe_real.py` · [`parser_analysis/real_report.md`](../parser_analysis/real_report.md) · [`parser_analysis/evidencias.md`](../parser_analysis/evidencias.md)

### Objetivo
Cuantificar el fallo sobre corpus real sin necesitar ground truth manual, usando el **consenso entre extractores** como proxy de verdad.

### Métrica: EAR (Extractor Agreement Rate)
Si los 3 extractores coinciden en el conteo de un símbolo → EAR 100%. Si no → hay una discrepancia.

### Hallazgos

| Símbolo | Documento | pdfplumber | pypdf | EAR |
|---|---|---|---|---|
| `∑` | AbstractAlgebra | **0** | 65 | **0%** |
| `∏` | AbstractAlgebra | **0** | 19 | **0%** |
| `⊨` | ModalLogicFundamentally | **0** | 2 | **0%** |
| `⊢` | FirstOrderLogic | 640 | 640 | **33.8%** |

Adicionalmente: ~2.785 artefactos `(cid:X)` en el PDF de Álgebra Abstracta — la corrupción es sistémica, no solo en los símbolos del catálogo.

---

## Exp 9 — DeepDoc Research Fases 3A/3B/3C: Forense y Causa Raíz

**Septiembre 2026** · `phase3a_forensic.py`, `phase3b_chunking.py`, `phase3c_fonts.py`

### Fase 3A — Taxonomía de corrupción (¿qué pone el parser?)

| Tipo | Descripción |
|---|---|
| **Sustitución** | `⊨` → `(cid:15)` — código interno del glifo |
| **Omisión** | `∑` → *(vacío)* — el operador desaparece de la fórmula |
| **Artefacto disociado** | `∑` en línea N, `(cid:9)` aparece en línea N-1 |

El tag `(cid:X)` es una **huella detectable**: con el diccionario de fuentes del PDF original puede mapearse determinísticamente al símbolo correcto.

### Fase 3B — Chunking

Sobre `⊢` (turnstile) en FirstOrderLogic.pdf, que *sí* sobrevive la extracción:
- **4.1%** de ocurrencias caen en el borde exacto de un chunk
- **23.9%** quedan en chunks sin contexto semántico relevante

La corrupción opera en **capas acumulativas e independientes**.

### Fase 3C — Causa raíz

> **`pdfminer.six`** (motor de `pdfplumber` y DeepDoc) aplica `/MacRomanEncoding` directamente sobre fuentes CFF Type1, ignorando el **ToUnicode CMap** embebido en la fuente.
>
> `pypdf` y `PyMuPDF` priorizan el CMap correctamente → extracción Unicode válida.
>
> El `(cid:X)` es el síntoma visible de este bug de priorización.

### Soluciones propuestas

| Solución | Complejidad | Impacto |
|---|---|---|
| **Hybrid fallback** (re-extraer páginas con alta tasa de `cid:X` usando pypdf) | Baja | Alto |
| **Post-procesador fonttools** (mapear `cid → unicode` con el CMap del PDF) | Media | Alto |
| **PR a RAGFlow / DeepDoc** | Alta | Muy alto |
| **PR a pdfminer.six** (fix upstream) | Media | Máximo |

### Documentos relacionados
- [`parser_analysis/evidencias.md`](../parser_analysis/evidencias.md) — consolidación completa

## Exp 10 — DeepDoc Research Fase 4: Evaluación de pymupdf4llm

**Septiembre 2026** · `parser_analysis/probe_real.py` · [`parser_analysis/real_report.md`](../parser_analysis/real_report.md)

### Objetivo
Evaluar si la conversión directa de PDF a Markdown estructurado mediante `pymupdf4llm` lograba eludir el fallo de preservación simbólica, constituyéndose en una posible alternativa de bajo coste de implementación.

### Diseño
Se integró `pymupdf4llm` como cuarto extractor en el benchmark EAR sobre el corpus real. Se regeneró el reporte cruzando las discrepancias.

### Hallazgos
`pymupdf4llm` resultó ser **peor** que `pdfplumber`. A las omisiones heredadas (por ej. `SUM`, `PRODUCT` con 0% de EAR) le sumó alucinación de formato y truncamiento de glifos. Por ejemplo, en `TURNSTILE (⊢)` solo extrajo 180 frente a 640 del reference (pypdf).

### ¿Qué motivó el siguiente paso?
Descartar la alternativa Markdown. Queda ratificado que se requiere un fix de bajo nivel, ya sea parcheando `pdfminer.six` o inyectando un paso intermedio con `pypdf`.

---

## Exp 11 — DeepDoc Research Fase 5: Métrica de Embeddings

**Septiembre 2026** · `parser_analysis/embedding_diff.py` · [`parser_analysis/embedding_diff_report.md`](../parser_analysis/embedding_diff_report.md)

### Objetivo
Evaluar cuantitativamente si la corrupción sintáctica producida por `pdfplumber` desplaza el significado semántico lo suficiente como para hacer fallar la fase de retrieval (distancia coseno < 0.70) usando un modelo estándar (`paraphrase-multilingual-MiniLM-L12-v2`).

### Diseño
Se extrajeron los chunks donde pypdf identificó un símbolo con 0% EAR y se alinearon con los mismos fragmentos extraídos por pdfplumber. Se generó el embedding para ambos y se midió su distancia coseno.

### Hallazgos
La corrupción destruye el retrieval semántico. Fragmentos con `SUM`, `PRODUCT` y `TURNSTILE` corruptos registraron cosenos medios de ~0.55, cayendo muy por debajo del umbral estándar de 0.70.

### ¿Qué motivó el siguiente paso?
Cierra definitivamente el debate de si el LLM "puede inferir" el símbolo faltante por el contexto: el chunk corrupto nunca será recuperado por RAGFlow para entregárselo al LLM en primer lugar. La corrección determinística del OCR es un requisito duro.

---

## Exp 12 — DeepDoc Research Fase 6: Evaluación de Fuentes TTF

**Septiembre 2026** · `parser_analysis/probe_ttf.py` · [`parser_analysis/ttf_report.md`](../parser_analysis/ttf_report.md)

### Objetivo
Determinar si el fallo de extracción (Punto de Falla 1) es exclusivo de las fuentes CFF/Type1 con `MacRomanEncoding` (típico de LaTeX/Computer Modern), o si afecta de forma generalizada a PDFs modernos generados con fuentes TrueType (TTF).

### Diseño
Generación de un PDF sintético mediante ReportLab utilizando la fuente `Segoe UI Symbol` e incrustando todos los símbolos del catálogo. Evaluación cruzada con `pdfplumber`, `PyMuPDF` y `pypdf`.

### Hallazgos
**Preservación perfecta.** Todos los extractores (`pdfplumber`, `pypdf` y `PyMuPDF`) registraron un 100% de preservación (Global CPR 100.0%) en todo el conjunto clave de símbolos matemáticos (`∀`, `∃`, `⊢`, `⊨`, `∈`, `∪`, `∝`, `∇`, etc.). 

### ¿Qué motivó el siguiente paso?
El hallazgo acota dramáticamente la criticidad del proyecto: el bug es estrictamente un edge-case del ecosistema heredado de LaTeX y encodings Type1/CFF defectuosos (MacRomanEncoding). Los PDFs modernos no están afectados. Esto nos permite enfocar la solución en corregir o mapear específicamente esos encodings antiguos, en lugar de reconstruir los parsers desde cero.

---

## Exp 13 — Corpus arXiv Expandido + Análisis de Causa Raíz Glyph → Unicode

**Septiembre 2026** · `parser_analysis/arxiv_harvest.py` · `parser_analysis/probe_arxiv.py` · [`parser_analysis/arxiv_ear_report.md`](../parser_analysis/arxiv_ear_report.md)

### Objetivo
Validar estadísticamente si el fallo de `pdfplumber` en el corpus original (4/4 PDFs) se generaliza a un corpus más amplio de papers LaTeX de arXiv. Correlacionar los resultados con el análisis de la capa de mapeo Glyph → Unicode.

### Diseño
Descarga automática de 30 papers de arXiv en categorías `math.LO`, `math.GR`, `math.RA`, `cs.LO`, filtrados por fuentes Type1/Computer Modern. Pipeline EAR completo con `pdfplumber`, `PyMuPDF` y `pypdf`.

### Hallazgos
**7/30 papers (23%)** con alguna discrepancia. Los símbolos fallidos son exclusivamente `∑` (CMEX), `□` (LASY/MSAM) y `∏` (CMEX). Los 23/30 restantes muestran 100% de EAR con `WinAnsiEncoding`.

### Causa raíz identificada con precisión
El bug está en la **capa de mapeo Glyph → Unicode** de `pdfminer.six`. Los nombres de glyph de CMEX (`summationtext`, `producttext`) no están en el Adobe Glyph List estándar. Cuando no hay tabla `ToUnicode` CMap en el PDF, `pdfminer.six` no puede resolver esos glyphs y los omite. La solución canónica (según ISO 32000) es aplicar la TeX glyph list específica para fuentes CM*/CMEX*/LASY*.

### ¿Qué motivó el siguiente paso?
El diagnóstico está completamente cerrado. El método de reparación está claramente definido. La siguiente fase es la implementación de la solución técnica.

---

## Estado actual y próximas líneas

> Ver [`TODO.md`](../TODO.md) para el detalle actualizado de tareas pendientes.

### Hallazgos consolidados

| Hallazgo | Experimento | Relevancia para paper |
|---|---|---|
| **Terquedad Semántica** | Exp 2–3 | Límite estructural de RAG en dominios formales |
| **Instruction Hierarchy** | Exp 3 | System message rompe el sesgo, pero produce over-refusal en 4B |
| **Curva en U de fidelidad** | Exp 4 | Modelos medianos son los más peligrosos en experimentos de corrupcón |
| **Over-Alignment en Rebuild** | Exp 5 | Modelos < 4B alucinan ante matemáticas en ES |
| **Punto de Falla 1 confirmado** | Exp 6 | DeepDoc elimina símbolos antes del embedding |
| **Bug MacRomanEncoding** | Exp 9 | Causa raíz identificada — solución determinística posible |
| **Fallo Embedding Semántico** | Exp 11 | Coseno ~0.55: la corrupcón destruye el retrieval |
| **TTF = sin fallo** | Exp 12 | Bug acotado a PDFs LaTeX; TTF/Unicode nativo OK |
| **Scope estadístico confirmado** | Exp 13 | 23% de papers arXiv afectados (CMEX/LASY sin ToUnicode) |
| **Causa raíz precisa** | Exp 13 | Glyph names CMEX no están en Adobe Glyph List |

### Líneas abiertas
- **Línea A — Fix upstream:** PR a pdfminer.six y RAGFlow con EAR como evidencia técnica
- **Línea C — SLM Seq2Seq:** T5/BART fine-tuneado sobre pares (pdfplumber corrupto, pypdf limpio)

---

## Exp 14 — Análisis de Estrategia de Implementación

**Octubre 2026**

### Objetivo
Determinar la forma más pragmática y sostenible de aplicar el fix de TeX Glyph List al pipeline real de RAGFlow, sin esperar a un PR aceptado por los mantenedores de pdfminer.six.

### Hallazgos
- No existe fork mantenido de pdfminer.six con soporte explícito para TeX/CMEX glyph names.
- **Fuente canónica identificada:** Apache PDFBox [`additional.txt`](https://apache.googlesource.com/pdfbox/+/refs/tags/2.0.14/pdfbox/src/main/resources/org/apache/pdfbox/resources/glyphlist/additional.txt) contiene exactamente los mapeos faltantes: `summationtext → 2211`, `producttext → 220F`, `integraldisplay → 222B`, etc. No hace falta inventar la tabla desde cero.
- pdfminer.six tiene actividad upstream reciente en el área (PR #1213 sobre CMap types 6/10/12), lo que hace el PR eventual más viable.
- DeepDoc/RAGFlow ya detecta `(cid:X)` artifacts con `_CID_PATTERN`, pero **no detecta la corrupción silenciosa** (Unicode válido pero incorrecto) que es el caso de CMEX/LASY.
- Acceso SSH al servidor RAGFlow real disponible (`ubuntu@128.201.239.161 -p 2022`).

### Decisión de ruta
1. **PASO 1:** Monkey-patch local (`tex_glyph_patch.py`) para validar que la tabla PDFBox efectivamente corrige los 7 papers del corpus arXiv con discrepancias.
2. **PASO 2:** Fork formal de pdfminer.six con el parche incorporado a `glyphlist.py`.
3. **PASO 3:** Redirigir la dependencia en el servidor RAGFlow al fork.
4. **PASO 4 (opcional):** PR upstream con benchmark EAR y tests de regresión.

---

## Exp 15 — Implementación y Validación del Fix (Línea A)

**Septiembre 2026** · `parser_analysis/tex_glyph_patch.py` · `parser_analysis/probe_arxiv_patched.py` · `parser_analysis/pdfminer-fork/`

### Objetivo
Implementar, refactorizar y verificar el fix de TeX Glyph List en tres capas: (1) monkey-patch validado con métricas robustas, (2) fork formal de pdfminer.six con el parche integrado al source, (3) suite de tests que sirva como evidencia para el PR upstream.

### Fase A — Monkey-patch (`tex_glyph_patch.py`)

**Refactoring aplicado** (a partir del `code_review.md`):
- Separación en dos tablas: `SAFE_MATH_OPERATORS` (62 entradas de CMEX/CMSY/LASY con Unicode no-ASCII) y `EXTENSIBLE_DELIMITERS` (alias de delimitadores que mapean a ASCII, excluidos por defecto).
- `apply_patch(include_delimiters=False)` ahora retorna stats `{added, skipped_existing}` y es idempotente.
- Auto-aplicación al importar; diseñado para correr a startup, no por-request.

**Métrica refactorizada** (`probe_arxiv_patched.py`):
- Abandonado el EAR bilateral (era inválido cuando pdfplumber con patch supera a los extractores de referencia).
- Nueva clasificación por símbolo por documento: `resolved` / `still_failing` / `exclusive_detection` / `partial` / `absent`.
- "exclusive_detection": pdfplumber encuentra el símbolo pero ni pymupdf ni pypdf lo hacen.

### Hallazgos

| Métrica | Sin patch (Exp 13) | Con patch |
|---|---|---|
| PDFs con algún fallo | 7/30 (23%) | **0/30 (0%)** |
| PDFs con exclusivas a favor pdfplumber | — | 19/30 (63%) |

**Investigación de exclusivas:** Las 3 ocurrencias de `∑` en `2609.15879v1` que pdfplumber detecta y los otros no son **verdaderos positivos** confirmados manualmente. Ejemplos: `∑ |XS| ≤ 2|S||S|! < ∞` y `|X/G| ≤ ∑ |XTj|` — expresiones matemáticas válidas que CMEX renderiza con `summationtext`.

### Fase B — Fork de `pdfminer.six`

- Clonado en `parser_analysis/pdfminer-fork/`.
- Las 62 entradas TeX integradas directamente en `pdfminer/glyphlist.py` al final del dict `glyphname2unicode`, con bloque de comentario que documenta fuentes (TUG TeX Glyph List, CMEX10 tfm, LASY10).
- Tests en `tests/test_tex_glyphs.py`: **43 casos parametrizados** cubriendo presencia, round-trip por `name2unicode()`, idempotencia de entradas AGL previas, y exclusión de aliases ASCII.
- Commit local: `db4ddff` — mensaje de commit autosuficiente con benchmark y descripción de grupos.

### Estado al cierre de sesión

| Componente | Estado |
|---|---|
| `tex_glyph_patch.py` | ✅ Refactorizado y validado |
| `tests/test_tex_glyph_patch.py` | ✅ 9/9 tests pasando |
| `probe_arxiv_patched.py` | ✅ Métrica nueva, 0/30 fallos |
| `pdfminer-fork/pdfminer/glyphlist.py` | ✅ 62 entradas integradas |
| `pdfminer-fork/tests/test_tex_glyphs.py` | ✅ 43/43 tests pasando |
| Fork publicado en GitHub | ✅ [`Jyiro/pdfminer-lis`](https://github.com/Jyiro/pdfminer-lis) @ `db4ddff` |
| **Aplicar en servidor RAGFlow** | 🔴 BLOQUEADO |
| **Validar end-to-end** | 🔴 BLOQUEADO |

### Diagnóstico del servidor RAGFlow (`server-02-utn-ia`)

Se intentó aplicar el parche en producción. Hallazgos:

| Servicio | Estado |
|---|---|
| MySQL, Elasticsearch, MinIO, Redis | ✅ Corriendo (healthy) |
| `docker-ragflow-cpu-1` (`infiniflow/ragflow:v0.26.0`) | 🔴 Crashloop desde hace semanas |

**Causa del crashloop:** `exec ./entrypoint.sh: exec format error` — incompatibilidad de arquitectura. La imagen oficial de Docker Hub fue compilada para `amd64` pero el servidor corre en `arm64` (pendiente confirmar con `uname -m`).

**El parche de pdfminer no puede aplicarse** mientras el contenedor no arranque.

### Opciones para desbloquear (requiere coordinación con el equipo del servidor)

1. **Confirmar arquitectura:** `uname -m` en el servidor
2. **Si es `arm64`:** reconstruir la imagen desde el source disponible en `~/ragflow/` (ya está el repo clonado)
3. **Alternativa inmediata:** levantar RAGFlow localmente en una máquina con arquitectura conocida (`docker compose up` desde `~/ragflow/docker/`)

**Una vez que el contenedor esté corriendo**, el parche se aplica con:
```bash
sudo docker exec -it docker-ragflow-cpu-1 \
  pip install git+https://github.com/Jyiro/pdfminer-lis@master
sudo docker restart docker-ragflow-cpu-1
```
