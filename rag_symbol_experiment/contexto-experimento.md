# Contexto del experimento — RAG y caracteres especiales

## Quién soy y qué estoy investigando

Soy estudiante universitario en Argentina. Estoy participando en un grupo de investigación de software donde estoy explorando las vulnerabilidades de los pipelines RAG (Retrieval-Augmented Generation) ante caracteres especiales, símbolos matemáticos, notación LaTeX y anomalías Unicode.

El contexto académico es documentos educativos de nivel universitario: apuntes de Análisis Matemático, Lógica, Programación — materiales con alta densidad de LaTeX, símbolos griegos, operadores lógicos y notación matemática especializada.

---

## El problema que investigo

Los pipelines RAG tienen una suposición implícita: que la información fluye sin pérdida semántica desde el documento original hasta el espacio vectorial. Esa suposición se rompe sistemáticamente en presencia de caracteres especiales.

El pipeline tiene cinco capas donde ocurren errores en cascada:

```
Documento PDF
     ↓
[1. Extracción / OCR]     ← ligaduras, tablas, fórmulas mal extraídas
     ↓
[2. Codificación]         ← mojibake, fuentes subconjunto, U+FFFD
     ↓
[3. Tokenización BPE]     ← fragmentación de símbolos matemáticos
     ↓
[4. Embedding]            ← vectores desplazados geométricamente
     ↓
[5. Recuperación]         ← falsos negativos silenciosos
```

Los errores son silenciosos — el sistema no tira error, simplemente recupera mal o no recupera.

### Tipos de corrupción que estudio

- **Mojibake**: UTF-8 decodificado como ISO-8859-1. Ej: `é` → `Ã©`, `∫` → `â«`, `ℝ` → `â`
- **Ligaduras tipográficas**: `fi` como glifo `ﬁ` (U+FB01) que parsers no normalizan → `/uniFB01eld`
- **U+FFFD**: carácter de reemplazo cuando el parser no puede reconciliar un byte
- **LaTeX en línea**: texto extraído como `\int_a^b f(x)dx` sin renderizar
- **Caracteres adversarios**: zero-width spaces, marcas Unicode invisibles (RAG-Pull attack)

### Papers de referencia principales

| Paper | Qué aporta |
|---|---|
| OHRBench (*OCR Hinders RAG*) | Techo del 14% de pérdida incluso con mejor OCR. Taxonomía ruido semántico vs formato |
| InduOCRBench | Disociación métricas CER/WER vs recall real en RAG industrial |
| SABER-Math | Colapso de modelos top-MTEB ante matemática densa |
| PTEB | Sensibilidad superficial de embeddings a cambios de tokenización |
| RAG-Pull | Ataque por inyección Unicode invisible. 97.9% éxito Top-1 |
| *The Curse of Tokenization* | Vulnerabilidades estructurales de BPE ante lenguaje científico |

---

## El experimento actual

Me sugirieron explorar el problema con **prompts con tablas de contexto**: darle al modelo una tabla de referencia que mapea símbolo corrupto → símbolo real → significado, y medir si eso resuelve la degradación con vs sin prompt.

El experimento tiene **dos fases independientes**:

### Fase 1 — Comprensión
Mide si el modelo *entiende* el contenido cuando los símbolos están corruptos. No hay RAG, no hay embeddings. Solo: texto corrupto + pregunta → ¿responde correctamente?

**Cuatro condiciones por fragmento:**
1. Texto limpio, sin tabla → techo del experimento
2. Texto corrupto, sin tabla → piso del experimento  
3. Texto corrupto, con tabla de contexto → efecto del prompt engineering
4. Texto LaTeX bien formado, sin tabla → ¿LaTeX es más interpretable que Unicode corrupto?

### Fase 2 — Embedding (pendiente)
Mide si el *vector* del texto corrupto está cerca o lejos del vector del texto limpio en el espacio vectorial. Esto determina si el documento sería recuperado en un RAG real.

Para cada par (limpio, corrupto) se calcula similitud coseno entre sus embeddings. Si da baja, ese documento nunca sería recuperado aunque el modelo pudiera interpretarlo perfectamente.

**La pregunta clave que conecta ambas fases:** ¿Los casos donde el modelo SÍ comprende con tabla de contexto coinciden con casos donde el embedding NO mejora con la tabla? Si es así, hay evidencia de que en RAG real el documento nunca llegaría al modelo aunque este pudiera interpretarlo.

---

## Setup técnico

- **Hardware**: laptop con recursos limitados (segunda PC, la principal tiene más potencia)
- **Modelo de comprensión**: `qwen3:1.7b` vía Ollama (instruct por defecto, `think: false`)
- **Modelo de embedding**: `nomic-embed-text` vía Ollama (274MB, 8192 tokens de contexto)
- **Lenguaje**: Python con `requests` a la API local de Ollama en `localhost:11434`
- **Sin RAG real**: los vectores viven en memoria, se comparan con numpy, no hay vector store

---

## Script actual (Fase 1)

Archivo: `fase1_comprension.py`

El script:
1. Define un corpus de 8 fragmentos matemáticos
2. Para cada fragmento corre las 4 condiciones llamando a Ollama via API REST
3. Evalúa las respuestas con tres categorías: `✓ CORRECTO`, `✗ CONFUNDIDO`, `? SIN RESPUESTA`
4. Guarda resultados en `resultados_fase1.txt` y `resultados_fase1.json`

### Evaluador
- `✓ CORRECTO`: la respuesta contiene al menos un término clave esperado
- `✗ CONFUNDIDO`: la respuesta contiene un término específicamente incorrecto (peor caso)
- `? SIN RESPUESTA`: el modelo no dijo nada correcto ni incorrecto (ignoró el símbolo)

### Tabla de contexto usada en el prompt
```
Tabla de notación (usá esta referencia para interpretar el texto):
- â / \circ          →  ∘  (composición de funciones: f ∘ g aplica g primero, luego f)
- â¤ / \mathbb{Z}    →  ℤ  (conjunto de los números enteros: ...-2,-1,0,1,2...)
- â  / \mathbb{R}    →  ℝ  (conjunto de los números reales)
- â¡ / \equiv        →  ≡  (congruencia modular)
- â! / \exists!      →  ∃! (existe un único / exactamente uno)
- â  / \exists       →  ∃  (existe al menos uno)
- â  / \forall       →  ∀  (para todo)
- âÃ / \leftrightarrow → ↔ (bicondicional)
- â  / \to           →  →  (implicación o función)
- â§ / \land         →  ∧  (conjunción lógica)
- Ã  / \times        →  ×  (producto cartesiano)
- âvâ / \|v\|       →  ‖v‖ (norma de un vector, siempre ≥ 0)
```

---

## Corpus actual (8 fragmentos)

Diseñados para que **sin el símbolo la respuesta sea imposible o ambigua** — el texto no da pistas lingüísticas suficientes.

| ID | Símbolo crítico | Corrupto como | Pregunta | Esperado |
|---|---|---|---|---|
| F1_composicion | ∘ | â | ¿cuál función se aplica primero? | g |
| F2_enteros_vs_reales | ℤ | â¤ | ¿puede x valer 2.5? | no |
| F3_existe_unico | ∃! | â! | ¿cuántos valores satisfacen? | exactamente uno |
| F4_bicondicional | ↔ | âÃ | ¿qué se concluye sobre P? | falso |
| F5_cuantificadores | ∀∃ | â â | ¿para cada x o único y? | para cada x |
| F6_norma | ‖v‖ | âvâ | ¿puede ser negativo? | no |
| F7_producto_cartesiano | × | Ã | ¿dominio son pares o individuales? | pares ordenados |
| F8_implicacion | ∧ → | â§ â | ¿puede A verdadero y B falso? | sí |

---

## Resultados de Fase 1 (ya corrido)

```
Condición                       ✓ Correct  ✗ Confund  ? Sin resp  Total
────────────────────────────────────────────────────────────────────────
LIMPIO   | sin tabla               6/8        1/8         1/8       8
CORRUPTO | sin tabla               5/8        1/8         2/8       8
CORRUPTO | con tabla               7/8        1/8         0/8       8
LATEX    | sin tabla               6/8        1/8         1/8       8
```

### Análisis por fragmento

**F3 y F7 son los casos más limpios e interesantes:**

- **F3 (∃!)**: Limpio → correcto. Corrupto sin tabla → `? SIN RESPUESTA` (el modelo hedgeó sin comprometerse). Corrupto con tabla → correcto. La corrupción de `∃!` a `â!` causó pérdida real de información, la tabla la recuperó.

- **F7 (×)**: Limpio → correcto. Corrupto sin tabla → `✗ CONFUNDIDO` (dijo "números individuales", la respuesta opuesta). Corrupto con tabla → correcto. Es el caso más limpio: corrupción de `×` a `Ã` causó respuesta incorrecta específica, tabla la corrigió completamente.

**Fragmentos problemáticos identificados:**

- **F1 (∘)**: el modelo falla incluso con texto limpio — no sabe que f∘g aplica g primero. Es límite del 1.7B, no problema de símbolo. Con 4B probablemente desaparece.
- **F6 (‖v‖)**: el modelo responde `No, ‖v‖ puede ser negativo` — contradictorio consigo mismo. Fallo de conocimiento del modelo, no del símbolo.
- **F2, F4, F5, F8**: el modelo responde igual con o sin símbolo porque el contexto lingüístico rescata la respuesta. Los fragmentos están mal diseñados — no son suficientemente dependientes del símbolo.

### Categorización de resultados

El experimento separó tres tipos de fragmentos involuntariamente:

1. **Corrupción sí importa** (F3, F7): símbolo corrupto causó degradación real. Tabla lo recuperó. → Casos relevantes para la investigación.

2. **Corrupción no importa — contexto rescata** (F2, F4, F5, F8): el modelo responde igual independientemente del símbolo. → Fragmentos mal diseñados, hay que cerrar los "escapes" contextuales.

3. **Fallo de conocimiento del modelo** (F1, F6): falla incluso con texto limpio. → No son resultados sobre caracteres especiales.

---

## Próximos pasos

### Inmediato — Mejorar corpus para Fase 1

Reemplazar F2, F4, F5, F8 por fragmentos donde el contexto lingüístico no alcance para rescatar la respuesta. El símbolo tiene que ser la única pista posible.

Reemplazar F1 y F6 por fragmentos que el 1.7B maneje bien en texto limpio.

Opcionalmente, repetir Fase 1 con `qwen3:4b` en la PC principal para ver cuántos fallos de F1 y F6 desaparecen con más capacidad.

### Siguiente — Fase 2: Embedding

Script `fase2_embedding.py` a construir:

```python
# Pseudocódigo de lo que hace
for fragmento in corpus:
    vec_limpio   = embed(fragmento["limpio"])
    vec_corrupto = embed(fragmento["corrupto"])
    vec_latex    = embed(fragmento["latex"])
    
    sim_corrupto = cosine_similarity(vec_limpio, vec_corrupto)
    sim_latex    = cosine_similarity(vec_limpio, vec_latex)
    
    # Repetir con tabla de contexto concatenada al texto
    vec_corrupto_tabla = embed(TABLA_CONTEXTO + fragmento["corrupto"])
    sim_corrupto_tabla = cosine_similarity(vec_limpio, vec_corrupto_tabla)
```

Modelo de embedding: `nomic-embed-text` via Ollama (`http://localhost:11434/api/embeddings`).
No se necesita vector store — los vectores viven en memoria, numpy calcula el coseno.

**La pregunta clave de Fase 2:** ¿La tabla de contexto concatenada al texto antes de embeddear mejora la similitud coseno con el texto limpio? Si sí, el prompt engineering no solo ayuda a la comprensión sino también al retrieval. Si no, el problema es más profundo que el prompt.

**El resultado más interesante posible:** casos donde Fase 1 muestra que el modelo SÍ comprende con tabla, pero Fase 2 muestra que el embedding NO mejora. Eso sería evidencia directa de que en un RAG real el documento nunca llegaría al modelo aunque este pudiera interpretarlo correctamente.

### Más adelante

- Comparar `nomic-embed-text` vs `mxbai-embed-large` sobre el mismo corpus (ambos descargados)
- Repetir con corpus más grande y variado
- Evaluar Vision RAG (ColPali/ColQwen) como comparación: ¿eludir el OCR resuelve el problema de raíz o solo lo desplaza a la query?

---

## Notas de implementación

- Ollama corre en `http://localhost:11434`
- Para comprensión: POST a `/api/generate` con `"think": false` y `"temperature": 0`
- Para embeddings: POST a `/api/embeddings` con `{"model": "nomic-embed-text", "prompt": texto}`
- Similitud coseno con numpy: `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))`
- Los resultados de Fase 1 están en `resultados_fase1.json` — útil para cruzar con resultados de Fase 2 por fragmento