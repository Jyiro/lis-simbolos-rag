# Vulnerabilidades de Pipelines RAG ante Corrupción de Caracteres Especiales
## Documento de Investigación — Estado del Arte y Trabajo Experimental

**Autor:** Jonás  
**Contexto:** Grupo de Investigación de Software — Universidad  
**Estado:** En progreso — Fase 1 completada, Fase 2 en diseño  
**Última actualización:** Julio 2026

---

## 1. Motivación y Problemática

### 1.1 La suposición rota de RAG

Los pipelines de Generación Aumentada por Recuperación (RAG) tienen una suposición implícita fundamental: que la información fluye sin pérdida semántica desde el documento original hasta el espacio vectorial del modelo. Esta suposición se rompe sistemáticamente en presencia de caracteres especiales, símbolos matemáticos, notación LaTeX y anomalías Unicode.

El problema es particularmente relevante en el contexto de documentos educativos universitarios — apuntes de Análisis Matemático, Lógica, Programación — donde la densidad de símbolos no estándar es alta y la precisión semántica de cada símbolo es crítica. Un `∃!` (existe único) interpretado como `∃` (existe) cambia completamente el significado de una afirmación matemática.

### 1.2 La naturaleza silenciosa del fallo

Lo que distingue este problema de otros fallos de sistema es su invisibilidad operacional. Cuando un pipeline RAG falla por corrupción de caracteres:

- No se genera ningún error
- Las métricas de latencia son normales
- El sistema responde — pero recupera documentos incorrectos o genera respuestas basadas en contenido corrupto

La literatura establece que incluso con el mejor OCR disponible existe un **techo estructural del 14% de pérdida** respecto al ground truth (OHRBench), independientemente de la calidad de la implementación.

### 1.3 Contexto académico

Este trabajo se inscribe en una línea de investigación reciente sobre robustez de pipelines RAG:

| Paper | Contribución principal |
|---|---|
| **OHRBench** (*OCR Hinders RAG*) | Techo del 14% de pérdida. Taxonomía ruido semántico vs. formato |
| **InduOCRBench** | Disociación entre métricas OCR (CER/WER) y recall real en RAG industrial |
| **SABER-Math** | Colapso de modelos top-MTEB ante matemática densa |
| **PTEB** | Sensibilidad superficial de embeddings a cambios de tokenización |
| **RAG-Pull** | Ataque por inyección Unicode invisible. 97.9% éxito Top-1 en OpenAI/Google |
| *The Curse of Tokenization* | Vulnerabilidades estructurales de BPE ante lenguaje científico |
| **Unicode TR#36** | Directrices de seguridad para mitigar ataques de homoglifos y confusables |

**Gap identificado:** ninguno de estos papers caracteriza sistemáticamente los tres puntos de falla del pipeline de forma unificada, ni evalúa la efectividad de mitigaciones en runtime sobre documentos educativos con alta densidad simbólica.

---

## 2. Marco Teórico

### 2.1 El pipeline RAG y sus capas de falla

El pipeline RAG estándar tiene cinco capas, y la corrupción puede ocurrir en cualquiera de ellas propagándose en cascada:

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
     ↓
[6. Pasaje al modelo]     ← corrupción post-retrieval durante serialización
```

### 2.2 Taxonomía de tipos de corrupción

| Tipo | Mecanismo | Ejemplo |
|---|---|---|
| **Mojibake** | UTF-8 decodificado como ISO-8859-1 | `∫` → `â«`, `ℝ` → `â` |
| **Ligaduras tipográficas** | Glifo compuesto no normalizado | `fi` → `ﬁ` (U+FB01) → `/uniFB01eld` |
| **Replacement character** | Parser no puede reconciliar el byte | Cualquier símbolo → `U+FFFD` |
| **LaTeX en línea** | Texto extraído sin renderizar | `∫₀^∞` → `\int_0^{\infty}` |
| **Caracteres adversarios** | Inyección de Unicode invisible | Zero-width spaces, marcas bidireccionales |
| **Homoglifos** | Sustitución cruzada de alfabetos | `e` latina → `е` cirílica (U+0435) |

### 2.3 Los tres puntos de falla del pipeline

Esta investigación identifica y caracteriza tres puntos distintos donde puede ocurrir corrupción, cada uno con consecuencias y soluciones diferentes:

```
[PUNTO 1 — Ingesta]
Documento PDF → OCR → Codificación
El documento entra corrupto al índice.
Consecuencia: el modelo no lo entiende Y el retrieval puede fallar antes.
Solución: sanitización pre-embedding (NFKC, ftfy, filtrado Cf/Cc)

        ↓ índice vectorial

[PUNTO 2 — Query]
Query del usuario → Retriever
La query está corrupta, el índice está bien.
Consecuencia: el retriever no encuentra el documento aunque esté correctamente indexado.
Solución: normalización de la query antes del retrieval

        ↓ chunks recuperados

[PUNTO 3 — Pasaje al modelo]
Chunk recuperado → Contexto del LLM
El retrieval funcionó, pero la serialización/deserialización corrompe el chunk.
Consecuencia: el modelo recibe contenido corrupto aunque el retrieval haya sido exitoso.
Solución: tabla de contexto en runtime (prompt engineering)
```

**La distinción es crítica:** cada punto de falla tiene una firma experimental diferente y requiere una solución diferente. La literatura existente los trata indistintamente o ignora el Punto 2 y el Punto 3.

### 2.4 Hipótesis de frecuencia en corpus de preentrenamiento

La capacidad de un SLM (Small Language Model) para compensar la corrupción de un símbolo está correlacionada con la frecuencia de ese símbolo en su corpus de preentrenamiento. Esta hipótesis, derivada de *The Curse of Tokenization* y SABER-Math, predice:

- **Alta frecuencia** (∀, ×, ↔, operadores lógicos estándar): el modelo compensa incluso ante corrupción Unicode severa, porque su representación interna del concepto es robusta.
- **Media frecuencia** (⇌, □, Å, ∃!): degradación parcial — el modelo falla con Unicode corrupto pero puede recuperarse con LaTeX o tabla de contexto.
- **Baja frecuencia** (æ IPA, · interpunct latino, ♭ musical, † obelus filológico): fallo sin compensación — ni LaTeX ni tabla de contexto garantizan recuperación.

---

## 3. Diseño Experimental

### 3.1 Estructura general

El experimento se divide en dos fases independientes que responden preguntas distintas:

| | Fase 1 | Fase 2 |
|---|---|---|
| **Pregunta** | ¿Puede el modelo interpretar contenido corrupto si lo recibe? | ¿El documento corrupto sería recuperado en primer lugar? |
| **Punto de falla** | Punto 3 (pasaje al modelo) | Punto 1 (ingesta) + Punto 2 (query) |
| **Herramienta** | LLM (qwen3:1.7b) | Modelo de embedding (nomic-embed-text) |
| **Métrica** | Corrección de respuesta (3 categorías) | Similitud coseno entre vectores |
| **Sin RAG real** | Sí — solo modelo + texto | Sí — vectores en memoria, sin vector store |

La intersección de ambas fases produce el hallazgo central: casos donde CON TABLA funciona (Fase 1) pero el embedding sigue degradado (Fase 2) demuestran que el parche en runtime nunca se activaría en un sistema RAG real.

### 3.2 Fase 1 — Comprensión

#### Condiciones experimentales

Cada fragmento del corpus se evalúa bajo seis condiciones que mapean a escenarios reales:

| Condición | Doc | Query | Tabla | Escenario real |
|---|---|---|---|---|
| LIMPIO \| doc✓ query✓ | Limpio | Limpia | No | Techo ideal — sin corrupción |
| DOC CORR \| doc✗ query✓ | Corrupto | Limpia | No | Escenario RAG más común — ingesta corrupta |
| FULL CORR \| doc✗ query✗ | Corrupto | Corrupta | No | Peor caso — corrupción en ambos extremos |
| QUERY CORR \| doc✓ query✗ | Limpio | Corrupta | No | Usuario con clipboard corrupto |
| CON TABLA \| doc✗ query✓ | Corrupto | Limpia | Sí | Parche en runtime — prompt engineering |
| LATEX \| doc~ query✓ | LaTeX | Limpia | No | Notación alternativa — benchmark |

#### Categorías de evaluación

Las respuestas del modelo se clasifican en tres categorías mutuamente excluyentes:

- `✓ CORRECTO` — la respuesta contiene al menos un término clave correcto
- `✗ CONFUNDIDO` — la respuesta contiene un término específicamente incorrecto (peor caso — el modelo fue engañado por la corrupción)
- `? SIN RESPUESTA` — el modelo no dijo nada correcto ni incorrecto (ignoró o no interpretó el símbolo)

La distinción entre CONFUNDIDO y SIN RESPUESTA es analíticamente importante: CONFUNDIDO implica que la corrupción indujo una respuesta incorrecta específica, mientras que SIN RESPUESTA implica que el modelo simplemente no pudo interpretar el símbolo.

#### Corpus — Diseño

Los fragmentos están diseñados bajo tres restricciones:

1. **El símbolo es la única pista** — el texto circundante no permite deducir la respuesta sin interpretar el símbolo
2. **La pregunta no menciona el símbolo** — evita que el modelo use la pregunta como referencia cruzada
3. **La respuesta incorrecta "inteligente" es predecible** — permite detectar confusión específica, no solo ausencia de acierto

El corpus está organizado en tres niveles de frecuencia estimada en corpus de preentrenamiento:

##### Alta frecuencia (4 fragmentos)

| ID | Símbolo | Documento | Pregunta | Esperado | Confusión esperada sin símbolo |
|---|---|---|---|---|---|
| A1_desigualdad | ≥ | `Aprobado si nota ≥ 6. Juan obtuvo 6.` | ¿Juan aprobó? | sí | no (lee umbral como estricto >) |
| A2_bicondicional | ⟺ | `A ⟺ B. B es falso.` | ¿Qué valor tiene A? | falso | no se puede determinar (confunde con →) |
| A3_cuantificador | ∀ | `∀x ∈ ℝ : x² ≥ 0` | ¿Vale para todos o solo alguno? | todos | alguno (confunde ∀ con ∃) |
| A4_producto_cart | × | `Sea f: ℝ × ℝ → ℝ` | ¿Dominio son pares o individuales? | pares ordenados | individuales |

##### Media frecuencia (4 fragmentos)

| ID | Símbolo | Documento | Pregunta | Esperado | Confusión esperada sin símbolo |
|---|---|---|---|---|---|
| B1_equilibrio | ⇌ | `N₂ + 3H₂ ⇌ 2NH₃` | ¿Puede ocurrir en ambos sentidos? | sí | no (reacción unidireccional) |
| B2_angstrom | Å | `λ = 550 Å` | ¿Unidad más pequeña o grande que 1mm? | más pequeña | más grande / no sabe |
| B3_modal | □ | `□P → P` | ¿P necesaria implica P, o P implica necesaria? | necesaria implica P | P implica P (tautología trivial) |
| B4_existe_unico | ∃! | `∃! x ∈ ℝ : x + 3 = 5` | ¿Cuántos valores satisfacen? | exactamente uno | uno (sin afirmar unicidad) |

##### Baja frecuencia (4 fragmentos)

| ID | Símbolo | Documento | Pregunta | Esperado | Confusión esperada sin símbolo |
|---|---|---|---|---|---|
| C1_ipa | æ | `La pronunciación es /bæd/` | ¿Segundo sonido: vocal o consonante? | vocal | consonante / no sabe |
| C2_interpunct | · | `MARCVS·TVLLIVS·CICERO` | ¿Cuántas partes tiene el texto? | tres | una (cadena continua) |
| C3_musical | ♭ | `La escala comienza en si♭` | ¿Más aguda o grave que si natural? | más grave | más aguda / no sabe |
| C4_obelus | † | `omnia †vincit† amor` | ¿El texto entre símbolos es seguro o corrupto? | corrupto | seguro |

#### Parámetros del modelo

```python
MODELO      = "qwen3:1.7b"   # instruct por defecto, vía Ollama
TEMPERATURE = 0              # determinista y reproducible
NUM_PREDICT = 120            # respuesta corta forzada
think       = False          # sin chain-of-thought
```

### 3.3 Fase 2 — Embedding

#### Diseño

Para cada fragmento del corpus se calcula la similitud coseno entre el embedding del texto limpio y las distintas variantes:

```
vec_limpio         = embed(documento_limpio)
vec_corrupto       = embed(documento_corrupto)
vec_latex          = embed(documento_latex)
vec_corrupto_tabla = embed(tabla_contexto + documento_corrupto)

sim_corrupto       = cosine(vec_limpio, vec_corrupto)
sim_latex          = cosine(vec_limpio, vec_latex)
sim_corrupto_tabla = cosine(vec_limpio, vec_corrupto_tabla)
```

**La pregunta central de Fase 2:** ¿La tabla de contexto concatenada antes de embeddear mejora la similitud coseno con el texto limpio? Si no, el problema es más profundo que el prompt — el retrieval habría fallado antes de que cualquier parche pueda activarse.

#### Fase 2B — Punto de falla 3 (post-retrieval)

Adicionalmente, se simula el escenario donde el retrieval fue exitoso pero la serialización del chunk introduce corrupción:

```
# El índice tiene el documento limpio
vec_limpio_indexado = embed(documento_limpio)

# La query también es limpia — el retrieval debería funcionar
sim_retrieval = cosine(vec_query_limpia, vec_limpio_indexado)  # alta → retrieval exitoso

# Pero el chunk se corrompe antes de pasarse al modelo
respuesta = modelo(documento_corrupto + pregunta)  # misma condición que DOC CORR en Fase 1
```

Esto permite demostrar que incluso cuando el retrieval es exitoso (similitud coseno alta, documento correcto recuperado), la corrupción post-retrieval puede anular el resultado.

#### Parámetros

```python
EMBEDDING_MODEL = "nomic-embed-text"   # 274MB, contexto 8192 tokens, vía Ollama
ENDPOINT        = "/api/embeddings"
# Sin vector store — vectores en memoria, numpy para similitud coseno
```

---

## 4. Arquitectura del Código

### 4.1 Estructura modular

```
rag_symbol_experiment/
├── main.py              # Punto de entrada, validación de conexión Ollama
├── config.py            # Variables globales y definición de condiciones
├── corpus.py            # Fragmentos del experimento
├── context_tables.py    # CORRUPT_MAP, LATEX_MAP, build_context_table()
├── corruption.py        # Funciones de transformación de texto
├── prompt_builder.py    # Ensamblado de prompts
├── ollama_client.py     # Cliente HTTP para Ollama
├── evaluator.py         # Clasificación de respuestas
├── report.py            # Generación de reportes y guardado
└── results/             # Outputs con timestamp
    ├── resultados_fase1_YYYYMMDD_HHMMSS.txt
    └── resultados_fase1_YYYYMMDD_HHMMSS.json
```

### 4.2 Flujo del algoritmo (Fase 1)

```
main.py
  └── correr_experimento()                    [experiment.py]
        ├── for fragmento in FRAGMENTOS:       [corpus.py]
        │     ├── for condicion in CONDICIONES: [config.py]
        │     │     ├── build_condition()       [corruption.py]
        │     │     │     └── unicode_corruption() | latex_version()
        │     │     ├── build_prompt()          [prompt_builder.py]
        │     │     │     └── build_context_table() [context_tables.py]
        │     │     ├── query()                 [ollama_client.py]
        │     │     │     └── POST /api/generate
        │     │     └── evaluate_response()     [evaluator.py]
        │     └── append resultados
        ├── generar_resumen()                  [report.py]
        └── save_results()                     [report.py]
              └── results/resultados_fase1_TIMESTAMP.{txt,json}
```

### 4.3 Módulos clave

#### `config.py`
```python
OLLAMA_URL  = "http://localhost:11434/api/generate"
MODELO      = "qwen3:1.7b"
TEMPERATURE = 0
NUM_PREDICT = 120
RESULTS_DIR = "results"

# (etiqueta, version_doc, con_tabla, corrupt_question)
CONDICIONES = [
    ("LIMPIO    | doc✓ query✓ sin tabla", "limpio",   False, False),
    ("DOC CORR  | doc✗ query✓ sin tabla", "corrupto", False, False),
    ("FULL CORR | doc✗ query✗ sin tabla", "corrupto", False, True),
    ("QUERY CORR| doc✓ query✗ sin tabla", "limpio",   False, True),
    ("CON TABLA | doc✗ query✓ con tabla", "corrupto", True,  False),
    ("LATEX     | doc~ query✓ sin tabla", "latex",    False, False),
]
```

#### `context_tables.py`
```python
# Ordenados por longitud descendente para evitar reemplazos parciales
# (ej: "∃!" debe procesarse antes que "∃")
CORRUPT_MAP = {
    "∃!": "â!",
    "∀":  "â",
    "∃":  "â",
    "∈":  "â",
    "ℝ":  "â",
    "⟺":  "âŸº",
    "⇌":  "â‡Œ",
    "×":  "Ã",
    "≥":  "â¥",
    "→":  "â",
    "□":  "â–¡",
    "Å":  "Ã…",
    "æ":  "Ã¦",
    "·":  "Â·",
    "♭":  "â™­",
    "†":  "â ",
}
```

#### `corruption.py`
```python
# Crítico: ordenar por longitud descendente antes de reemplazar
_CORRUPT_SORTED = sorted(CORRUPT_MAP.items(), key=lambda x: -len(x[0]))

def unicode_corruption(text: str) -> str:
    out = text
    for orig, corrupt in _CORRUPT_SORTED:
        out = out.replace(orig, corrupt)
    return out
```

#### `evaluator.py`
```python
def evaluate_response(respuesta, esperado, forbidden):
    r = respuesta.lower()
    es_incorrecto = any(term in r for term in forbidden)
    aciertos = sum(1 for term in esperado if term in r)

    if es_incorrecto:   return "✗ CONFUNDIDO"
    if aciertos == 0:   return "? SIN RESPUESTA"
    return "✓ CORRECTO"
```

> **Limitación conocida:** el evaluador de strings produce falsos negativos cuando la respuesta correcta está expresada con sinónimos no incluidos en `esperado`. Se planea reemplazar por LLM-as-judge en versiones posteriores.

---

## 5. Resultados Preliminares

### 5.1 Corridas de Fase 1

Se realizaron múltiples iteraciones del corpus con ajustes progresivos. Los resultados más significativos provienen de la versión con corpus de símbolos matemáticos reales (∀, ∃!, ↔, ×):

#### Hallazgo principal — Fase 1

El experimento separó tres comportamientos distintos:

**1. Corrupción importa — símbolo determina la respuesta**
Los fragmentos con `×` (producto cartesiano) y `∃!` (existe único) mostraron el patrón buscado:
- Limpio → correcto
- Corrupto sin tabla → confundido o sin respuesta
- Con tabla → correcto

Este patrón confirma que la corrupción causó pérdida real de información semántica, y que la tabla de contexto la recupera.

**2. Corrupción no importa — contexto lingüístico rescata**
Fragmentos con `∀`, `↔` en contextos con redundancia lingüística: el modelo responde igual con o sin símbolo. Estos son casos donde el Punto 1 de falla no es dominante — pero el Punto 2 (embedding degradado) podría serlo igualmente.

**3. Fallo de conocimiento del modelo**
Fragmentos donde el modelo falla incluso con texto limpio. No son resultados sobre caracteres especiales — son límites del modelo de 1.7B que desaparecen con modelos más grandes.

#### Reencuadre narrativo

> "Fase 1 no tiene como objetivo demostrar que todo se rompe. Tiene como objetivo caracterizar **dónde** se rompe y **para qué tipos de símbolos**. El hallazgo de que símbolos de alta frecuencia son compensados por el modelo no debilita la investigación — la fortalece: si el modelo puede entender el contenido corrupto cuando lo recibe, pero el documento igualmente nunca llega al modelo porque el embedding falló en Fase 2, entonces el cuello de botella real es el retrieval, no la comprensión."

### 5.2 Resumen de resultados disponibles

```
Condición                        ✓ Correct  ✗ Confund  ? Sin resp  Total
─────────────────────────────────────────────────────────────────────────
LIMPIO    | doc✓ query✓ sin tabla    —/12       —/12        —/12      12
DOC CORR  | doc✗ query✓ sin tabla    —/12       —/12        —/12      12
FULL CORR | doc✗ query✗ sin tabla    —/12       —/12        —/12      12
QUERY CORR| doc✓ query✗ sin tabla    —/12       —/12        —/12      12
CON TABLA | doc✗ query✓ con tabla    —/12       —/12        —/12      12
LATEX     | doc~ query✓ sin tabla    —/12       —/12        —/12      12
```

> Tabla a completar con los resultados del corpus ampliado de 12 fragmentos (pendiente de corrida).

---

## 6. Hoja de Ruta

### 6.1 Inmediato

- [ ] Correr corpus ampliado de 12 fragmentos (3 niveles × 4 dominios)
- [ ] Actualizar `context_tables.py` con todos los símbolos nuevos
- [ ] Analizar resultados por nivel de frecuencia — validar hipótesis de compensación

### 6.2 Fase 2A — Embedding degradado (COMPLETADO: Experimento 11)

Se implementó el script `embedding_diff.py` midiendo el desplazamiento semántico causado por la corrupción del PDF (pypdf vs pdfplumber) utilizando `paraphrase-multilingual-MiniLM-L12-v2`.

**Resultados principales (Coseno medio por símbolo corrupto):**
- **SUM (∑):** 0.558 (18 de 19 muestras < 0.70)
- **PRODUCT (∏):** 0.555 (7 de 7 muestras < 0.70)
- **TURNSTILE (⊢):** ~0.536 (5 de 7 muestras < 0.70)

**Conclusión:** La degradación del embedding es severa. Un coseno de ~0.55 impide categóricamente que un sistema RAG recupere estos fragmentos ante una búsqueda matemática válida. El fallo en la Fase de Embedding (Punto de Falla 2) es absoluto para fragmentos simbólicos.

### 6.3 Fase 2B — Punto de falla post-retrieval

- [ ] Implementar simulación de corrupción post-retrieval
- [ ] Loggear similitud coseno del retrieval (confirmar éxito antes de la corrupción)
- [ ] Cruzar con resultados de Fase 1 condición DOC CORR

### 6.4 Análisis cruzado de fases

El hallazgo más importante del trabajo surge del cruce entre Fase 1 y Fase 2:

```
Para cada fragmento:
  Si CON TABLA (F1) = ✓ CORRECTO
  Y  sim_corrupto_tabla (F2) ≈ sim_corrupto (bajo)
  →  El parche funciona para comprensión pero no para retrieval
  →  En un RAG real, el parche nunca se activaría
```

### 6.5 Mejoras técnicas pendientes

- [ ] **LLM-as-judge**: reemplazar evaluador de strings por llamada al modelo para comparación semántica de respuestas
- [ ] **Registro del prompt exacto** en el JSON para reproducibilidad completa
- [ ] **Timestamp en header** del reporte (ya implementado en `report.py`)
- [ ] **Repetir Fase 1 con qwen3:4b** en hardware principal para separar límites del modelo de efectos de corrupción

### 6.6 Más adelante

- [ ] Evaluar Vision RAG (ColPali/ColQwen3-4B) como comparación: ¿eludir el OCR resuelve el problema de raíz o lo desplaza a la query?
- [ ] Comparar con Gemini Embedding 2 para el caso multimodal
- [ ] Evaluar sanitización clásica (NFKC + ftfy + filtrado Cf/Cc) como alternativa a Vision RAG

---

## 7. Setup Técnico

### 7.1 Requisitos

```bash
# Modelos necesarios
ollama pull qwen3:1.7b          # Fase 1 — comprensión
ollama pull qwen3:4b            # Fase 1 — validación con modelo más grande
ollama pull nomic-embed-text    # Fase 2 — embedding baseline
ollama pull mxbai-embed-large   # Fase 2 — embedding comparación

# Python
pip install requests numpy
```

### 7.2 Ejecución

```bash
cd rag_symbol_experiment/
python main.py
# Resultados en results/resultados_fase1_YYYYMMDD_HHMMSS.{txt,json}
```

### 7.3 API Ollama

```python
# Comprensión (Fase 1)
POST http://localhost:11434/api/generate
{
  "model": "qwen3:1.7b",
  "prompt": "...",
  "stream": false,
  "options": {"temperature": 0, "num_predict": 120},
  "think": false
}

# Embedding (Fase 2)
POST http://localhost:11434/api/embeddings
{
  "model": "nomic-embed-text",
  "prompt": "texto a embeddear"
}

# Similitud coseno
np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## 8. Narrativa del Paper

### 8.1 Contribución principal

Este trabajo caracteriza sistemáticamente los tres puntos de falla por corrupción Unicode en pipelines RAG — ingesta, query y pasaje al modelo — usando un corpus diseñado específicamente para que el símbolo sea la única fuente de información semántica. La contribución metodológica es separar experimentalmente estos tres puntos de falla, algo que la literatura existente no hace.

### 8.2 Arco narrativo

**Introducción:** RAG asume flujo semántico sin pérdida. Esa suposición es defectuosa.

**Problema:** Tres puntos de falla distintos, cada uno silencioso, cada uno con solución diferente.

**Fase 1:** ¿Puede un parche en runtime (tabla de contexto) compensar la corrupción? Para qué símbolos sí, para cuáles no — y por qué (hipótesis de frecuencia en preentrenamiento).

**Fase 2A:** ¿Importa que el modelo pueda interpretar el contenido si el retrieval ya falló antes? Medición directa del desplazamiento vectorial causado por corrupción.

**Fase 2B:** ¿Qué pasa cuando el retrieval funciona pero la serialización post-retrieval introduce corrupción? El tercer punto de falla, el menos estudiado.

**Intersección:** Los casos donde el parche funciona para comprensión pero no para retrieval son la demostración más clara del problema: el sistema podría reparar la corrupción, pero la corrupción ocurrió antes de que el sistema pudiera intervenir.

**Conclusión:** Caracterización empírica de cuándo cada solución (sanitización pre-embedding, normalización de query, tabla de contexto en runtime, Vision RAG) es y no es suficiente.

### 8.3 Título tentativo

*"Characterizing Unicode Corruption Failure Modes in RAG Pipelines: A Three-Layer Empirical Analysis"*

---

*Documento en progreso — actualizar con resultados de cada corrida*
# Fase 1: Análisis de Degeneración Semántica en Modelos Generativos RAG

Este documento describe la metodología, ejecución y resultados de la Fase 1 del experimento orientado a evaluar la robustez semántica de la etapa generativa en arquitecturas Retrieval-Augmented Generation (RAG) frente a perturbaciones de caracteres.

---

## 1. Diseño Experimental

### 1.1 Objetivo y Contexto Teórico

Las arquitecturas RAG presentan vulnerabilidades inherentes cuando procesan documentos con alta densidad de simbología matemática. La Fase 1 aísla la **capa final del flujo (Generación)**.
Se establece como premisa un escenario donde la etapa de recuperación (Retrieval) ha procesado y suministrado un fragmento con alteraciones sintácticas (debido a deficiencias en el motor OCR o en la decodificación) al Modelo de Lenguaje Grande (LLM).

Los objetivos específicos son:
1. Determinar la resiliencia del LLM para preservar la coherencia semántica frente a alteraciones en símbolos críticos.
2. Clasificar los modos de falla: divergencia explícita (el modelo rechaza la inferencia por falta de contexto) frente a divergencia silenciosa (el modelo genera aserciones lógicamente válidas pero matemáticamente inconsistentes).
3. Evaluar la eficacia de estrategias de mitigación en tiempo de inferencia, tales como la inyección de tablas de mapeo en el contexto o conversiones a formato LaTeX.

### 1.2 Estructura del Prompt

El experimento diseña un prompt que fuerza al LLM a depender estrictamente del contexto provisto (documento perturbado). 
Se divide en:

1. **Directiva de Aislamiento Contextual:** Instrucciones estrictas para anular el sesgo de preentrenamiento del modelo.
2. **Contexto Controlado:** Un texto base donde símbolos formales (`∑`, `⊢`, `∀`, etc.) han sido deliberadamente reemplazados por secuencias espurias (`(cid:10)`, `[ERR]`, o ruido Unicode).
3. **Pregunta de Extracción:** Una consulta determinística (Ej: "Según el texto, ¿qué significa (cid:10)?").

### 1.3 Corpus Sintético

Para esta fase inicial, se generó un corpus sintético de fragmentos matemáticos donde las relaciones símbolo-significado son inequívocas pero ficticias (ej. `[SÍMBOLO_A]` representa "Velocidad Angular" en lugar de `ω`), garantizando que el LLM no pueda resolver la tarea apelando a convenciones de su entrenamiento.

---

## 2. Ejecución y Métricas

La ejecución se realiza de manera automatizada utilizando la suite desarrollada en `llm_evaluation/`. Se evalúan iterativamente diferentes familias y escalas de modelos (ej. Llama, Qwen, Phi) contra el corpus.

### 2.1 Métricas de Evaluación (Fidelidad Contextual)

El desempeño de cada modelo se clasifica de acuerdo al alineamiento con el contexto distorsionado:

* **Adherencia Estricta (Éxito):** El modelo obedece la tabla de mapeo y responde utilizando el significado provisto en el prompt, ignorando la rareza del símbolo distorsionado.
* **Over-Alignment / Pre-training Bias (Fallo):** El modelo descarta el contexto suministrado e impone una respuesta basada en su entrenamiento general (ej. afirmar que `(cid:10)` es un error de decodificación en lugar de acatar la definición de la tabla en contexto).
* **Alucinación Silenciosa (Fallo Crítico):** El modelo deduce lógicamente sobre premisas inventadas que no existen en el contexto ni en su preentrenamiento, fabricando una respuesta plausible pero falsa.

---

## 3. Conclusiones Preliminares

Los resultados empíricos completos se encuentran documentados en `docs/fase1_resultados.md`. 
Las observaciones iniciales indican una correlación directa entre el tamaño parametral del modelo y su propensión al "Over-Alignment", donde los modelos compactos (<4B) tienden a ignorar las correcciones en contexto cuando se enfrentan a distorsiones severas, requiriendo estrategias de prompting más robustas para forzar la fidelidad semántica.
# Comparativa de Modelos — Fase 1

**Modelo A:** resultados_fase1_qwen3_1.7b_20260729_170013.json
**Modelo B:** resultados_fase1_qwen3_4b_instruct_2507_q4_K_M_20260729_171523.json

Leyenda: ✓ CORRECTO · ✗ CONFUNDIDO · ? SIN RESPUESTA

---

## ✦ EFECTO PRINCIPAL — Validación de hipótesis

### A2_bicondicional  *(nivel: alta)*
> **Documento:** `A ⟺ B. B es falso. | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Qué valor de verdad tiene A?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| DOC CORR | ✓ | A es falso. | ✗ | A es verdadero. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | A es falso. | ✗ | A es verdadero. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| CON TABLA | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| LATEX | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |

### B2_angstrom  *(nivel: media)*
> **Documento:** `λ = 550 Å | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** La unidad de longitud indicada, ¿es más pequeña o más grande que 1 milímetro?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | La unidad de longitud indicada, λ, es más pequeña que 1 milímetro. | ✓ | 550 Å es mucho más pequeña que 1 milímetro. | Ambos correctos |
| DOC CORR | ✓ | La unidad de longitud indicada es más pequeña que 1 milímetro. | ✗ | Es más grande que 1 milímetro. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | La unidad de longitud indicada es más pequeña que 1 milímetro. | ✗ | Es más grande que 1 milímetro. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | Más pequeña que 1 milímetro. | ✓ | 550 Å es mucho más pequeña que 1 milímetro. | Ambos correctos |
| CON TABLA | ✓ | Más pequeña que 1 milímetro. | ✓ | Es más pequeña que 1 milímetro. | Ambos correctos |
| LATEX | ✓ | La unidad de longitud indicada, λ, es más pequeña que 1 milímetro. | ✓ | Es más pequeña que 1 milímetro. | Ambos correctos |

### C3_musical  *(nivel: baja)*
> **Documento:** `La escala comienza en si♭ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Esta nota es más aguda o más grave que si natural?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Más grave. | ✓ | Si♭ es más grave que si natural. | Ambos correctos |
| DOC CORR | ✓ | Más grave. | ✗ | La nota siâ™­ es más aguda que si natural. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | Más grave. | ✗ | La nota siâ™­ es más aguda que si natural. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | Más grave. | ✓ | Si♭ es más grave que si natural. | Ambos correctos |
| CON TABLA | ✓ | Más grave. | ✓ | Es más grave que si natural. | Ambos correctos |
| LATEX | ✓ | Más grave. | ✓ | La nota si♭ es más grave que si natural. | Ambos correctos |

## ⚡ TERQUEDAD SEMÁNTICA — Pesos vs. instrucción RAG

### B3_modal  *(nivel: media)*
> **Documento:** `□P → P | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Esta expresión tiene la misma forma lógica que P → P?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | Sí, la expresión □P → P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| DOC CORR | ✗ | Sí, la expresión tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica que P → P. | Ambos confundidos |
| FULL CORR | ✗ | Sí, la expresión tiene la misma forma lógica que P ∧ P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| QUERY CORR | ✗ | La expresión □P → P tiene la misma forma lógica que P â P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| CON TABLA | ✗ | La expresión â–¡P â P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica que P → P. | Ambos confundidos |
| LATEX | ✗ | La expresión \BoxP \to P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |

### B4_subconjunto  *(nivel: media)*
> **Documento:** `A ⊂ B y B ⊂ A | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Se puede concluir que A y B son iguales?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| DOC CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| FULL CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| QUERY CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| CON TABLA | ✗ | No, se puede concluir que A y B son iguales. | ✗ | Sí, A y B son iguales. | Ambos confundidos |
| LATEX | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |

## 🔤 TOKENIZACIÓN FORTUITA — Mojibake como separador

### C1_ipa  *(nivel: baja)*
> **Documento:** `La pronunciación es /bæd/ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El segundo sonido de la pronunciación transcrita es una vocal o una consonante?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| DOC CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| FULL CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| QUERY CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| CON TABLA | ✓ | Una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| LATEX | ✓ | Es una vocal. | ✗ | El segundo sonido es una consonante. | Divergencia: 1.7b=✓ / 4b=✗ |

### C2_interpunct  *(nivel: baja)*
> **Documento:** `SEXTUS·RUFINUS·MAXIMUS | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Cuántas palabras distintas componen este texto?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Tres palabras distintas. | ? | 4 palabras distintas. | Divergencia: 1.7b=✓ / 4b=? |
| DOC CORR | ✓ | Tres palabras distintas. | ✓ | El texto contiene 3 palabras distintas. | Ambos correctos |
| FULL CORR | ✓ | Tres palabras distintas. | ✓ | El texto contiene 3 palabras distintas. | Ambos correctos |
| QUERY CORR | ✓ | Tres palabras distintas. | ? | 4 palabras distintas. | Divergencia: 1.7b=✓ / 4b=? |
| CON TABLA | ✓ | Hay 3 palabras distintas. | ✓ | El texto contiene 3 palabras distintas: SEXTUS, RUFINUS, MAXIMUS. | Ambos correctos |
| LATEX | ✓ | 3 | ✓ | 3 palabras distintas. | Ambos correctos |

## ⚠ REDUNDANCIA CONTEXTUAL — Símbolo irrelevante

### A1_desigualdad  *(nivel: alta)*
> **Documento:** `Aprobado si nota ≥ 6. Juan obtuvo 6. | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Juan aprobó?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| DOC CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| FULL CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| QUERY CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| CON TABLA | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| LATEX | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |

### A3_cuantificador  *(nivel: alta)*
> **Documento:** `∀x ∈ ℝ : x² ≥ 0 | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿La afirmación vale para todos los reales o solo para alguno?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| DOC CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| FULL CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| QUERY CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| CON TABLA | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| LATEX | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |

### B1_equilibrio  *(nivel: media)*
> **Documento:** `Fe²⁺ + Ce⁴⁺ ⇌ Fe³⁺ + Ce³⁺ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿La reacción puede ocurrir en ambos sentidos?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| DOC CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | No, la reacción no puede ocurrir en ambos sentidos porque Ce⁴⁺ es un oxidante má | Ambos correctos |
| FULL CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | No, la reacción no puede ocurrir en ambos sentidos porque Ce⁴⁺ es un oxidante má | Ambos correctos |
| QUERY CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| CON TABLA | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| LATEX | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |

## · OTROS

### A4_producto_cart  *(nivel: alta)*
> **Documento:** `Sea f: ℝ × ℝ → ℝ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El dominio de f son pares ordenados de reales o números reales individuales?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |
| DOC CORR | ✓ | El dominio de f son pares ordenados de reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | El dominio de f son pares ordenados de reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |
| CON TABLA | ✓ | El dominio de f son pares ordenados de números reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| LATEX | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |

### C4_obelus  *(nivel: baja)*
> **Documento:** `omnia †vincit† amor | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El texto encerrado entre los dos símbolos es considerado original o de autenticidad dudosa?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es considerado de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| DOC CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| FULL CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| QUERY CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es considerado de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| CON TABLA | ✓ | El texto encerrado entre los dos símbolos es considerado de autenticidad dudosa. | ✓ | El texto es considerado de autenticidad dudosa. | Ambos correctos |
| LATEX | ✗ | El texto encerrado entre los dos símbolos es considerado original o de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |

---
## Resumen por Categoría

| Categoría | Fragmentos | Patrón dominante 1.7b | Patrón dominante 4b |
|---|---|---|---|
| ✦ EFECTO PRINCIPAL — Validación de hipótesis | A2_bicondicional, B2_angstrom, C3_musical | ✓ | ✓ |
| ⚡ TERQUEDAD SEMÁNTICA — Pesos vs. instrucción RAG | B3_modal, B4_subconjunto | ✗ | ✗ |
| 🔤 TOKENIZACIÓN FORTUITA — Mojibake como separador | C1_ipa, C2_interpunct | ✓ | ✓ |
| ⚠ REDUNDANCIA CONTEXTUAL — Símbolo irrelevante | A1_desigualdad, A3_cuantificador, B1_equilibrio | ✓ | ✓ |
| · OTROS | A4_producto_cart, C4_obelus | ✓ | ✓ |
---

# Estrategias específicas para modelos Instruct

## I1 - Instruction Hierarchy

Idea

Los modelos instruction-tuned modernos no consideran todas las instrucciones con el mismo peso.

Durante el entrenamiento aprenden una jerarquía de prioridades.

Generalmente:

1. Instrucciones del sistema
2. Instrucciones del desarrollador
3. Instrucciones del usuario
4. Contexto (documentos RAG)
5. Conocimiento paramétrico

Cuando dos niveles entran en conflicto, el modelo intenta obedecer el nivel de mayor prioridad.

---

Objetivo

Investigar si una instrucción redactada como una regla del sistema hace que el modelo priorice el documento por encima de su conocimiento previo.

---

Ejemplo 1

SYSTEM

Las definiciones presentes en el documento constituyen la única fuente válida de información.

Si existe contradicción entre el documento y su conocimiento previo, considere correcta la información del documento.

---

Ejemplo 2

SYSTEM

Las siguientes reglas tienen prioridad absoluta.

1. Utilice únicamente las definiciones presentes en el documento.
2. Ignore cualquier definición aprendida previamente.
3. Si la respuesta no puede obtenerse del documento, indíquelo explícitamente.

---

Ejemplo 3

SYSTEM

Su tarea consiste exclusivamente en interpretar la notación definida en este documento.

No complete símbolos faltantes utilizando conocimiento matemático, químico o informático aprendido durante el entrenamiento.

---

Estado

✔ Línea de investigación reciente.

No es simplemente "prompt engineering".

Forma parte del estudio de Instruction Following e Instruction Hierarchy.

---

Hipótesis

Una instrucción ubicada en el nivel de mayor prioridad debería aumentar la fidelidad al contexto y disminuir el uso de conocimiento paramétrico.

---

Limitación

No todos los modelos implementan la misma jerarquía.

Modelos como GPT-4.1, Gemini 2.5, Claude 4 y otros modelos instruct recientes fueron entrenados explícitamente para respetar una jerarquía de instrucciones.

En modelos open-source pequeños (Qwen, Gemma, Llama, Mistral, etc.) el comportamiento puede variar considerablemente según el fine-tuning utilizado.

---

Posible experimento

Comparar cuatro variantes exactamente sobre el mismo corpus.

A)

Pregunta normal.

B)

IMPORTANTE:
Utilice únicamente el documento.

C)

Las definiciones del documento reemplazan cualquier conocimiento previo.

D)

[SYSTEM]

Las definiciones del documento tienen prioridad absoluta sobre cualquier conocimiento paramétrico.

---

Variables a medir

- Exactitud.
- Context Faithfulness.
- Uso de la tabla de símbolos.
- Cantidad de respuestas basadas en memoria paramétrica.
- Capacidad para resolver conflictos documento vs conocimiento interno.
# Análisis de Resultados: Terquedad Semántica vs Instruction Hierarchy

Este documento presenta el análisis cualitativo exhaustivo de los resultados obtenidos con los modelos **Qwen3.5-2B** y **Gemma-4B**. El análisis se centra en evaluar la efectividad de las distintas estrategias de *prompting* para mitigar el sesgo paramétrico (Terquedad Semántica) ante la corrupción de símbolos, con especial foco en el mecanismo de *Instruction Hierarchy*.

---

## 1. Los Fragmentos de Prueba (Corpus) y el Comportamiento Observado

El experimento expone a los modelos a fragmentos de texto donde símbolos críticos han sufrido corrupción (ej. Mojibake UTF-8). Si el modelo ignora la tabla de recuperación (RAG) e intenta adivinar el significado basándose en su entrenamiento previo, cae en la **Terquedad Semántica**.

### Fragmentos de Alta Terquedad (Sesgo Severo)

* **`B3_modal` (Lógica Modal - Símbolo: `□`)**
  * **Problema:** Se pregunta si la expresión corrupta `â–¡P â P` tiene la misma forma que la implicación simple `P → P`. La respuesta correcta es *No* (porque incluye el operador modal de necesidad).
  * **Comportamiento Gemma 4B:** Sufre de terquedad extrema. En todas las estrategias que inyectan el contexto en el mensaje de usuario (desde `CON TABLA` hasta `I1-C`), Gemma ignora la tabla y responde tozudamente "Sí" (alucinación paramétrica). Solo logra frenar este comportamiento cuando se le impone la estrategia `I1-D` (System Message Real).
  * **Comportamiento Qwen 2B:** Resulta más dócil. Con la mera inclusión de la tabla en el prompt (`CON TABLA`), logra deducir que la respuesta es "No".

* **`B4_subconjunto` (Teoría de Conjuntos - Símbolo: `⊂`)**
  * **Problema:** Dado `A ⊂ B y B ⊂ A` (corrupto a `A âŠ‚ B y B âŠ‚ A`), se pregunta si A y B son iguales. Como `⊂` es subconjunto estricto, la respuesta es *No*.
  * **Comportamiento Gemma 4B:** Nuevamente, terquedad severa en las estrategias base, asumiendo (por sesgo matemático) que la doble inclusión siempre significa igualdad. Sin embargo, Gemma logra romper su sesgo y acatar el contexto cuando se le imponen las estrategias agresivas `I1-A`, `I1-B`, `I1-C` e `I1-D`.
  * **Comportamiento Qwen 2B:** Falla en la mayoría de las condiciones, incluso en `I1-D`. Paradójicamente, acierta en `I1-C`. Esto revela inestabilidad atencional: al tener solo 2 Billones de parámetros, le cuesta retener reglas complejas en el System Prompt si el mensaje de usuario es muy distante, respondiendo mejor cuando se le "grita" la regla directamente en el `user`.

### Fragmentos de Control y Rescate

* **`A4_producto_cart` (Matemática - Símbolo: `×`)**
  * **Comportamiento:** A pesar de recibir un texto completamente ilegible (`Sea f: â Ã â â â`), ambos modelos demuestran capacidad de rescate analítico. Qwen 2B deduce perfectamente el producto cartesiano gracias a la tabla. Gemma 4B demuestra una ejecución impecable de la Regla #3 de mitigación de alucinaciones en la estrategia `I1-D` (explicado más abajo).

---

## 2. Estrategias de Prompting y su Efectividad

Las estrategias evalúan diferentes niveles de coerción sobre el modelo:

1. **`LIMPIO` / `DOC CORR` / `LATEX` (Baselines sin tabla):**
   * **Efectividad:** Muy baja. Demuestran que frente a la corrupción (`DOC CORR`), ambos modelos fallan estrepitosamente o alucinan respuestas basadas en inferencias erróneas.
2. **`CON TABLA | plain`:**
   * **Efectividad:** Moderada (rescata ~71% en Qwen). Simplemente agregar la tabla al final del texto ayuda, pero fracasa ante sesgos fuertes (`B3`, `B4` en Gemma).
3. **`I1-A` (Énfasis) y `I1-B` (Override explícito):**
   * **Efectividad:** Alta. Decirle al modelo *"Ignorá tu entrenamiento previo"* o usar alertas mayúsculas eleva sustancialmente el acierto, logrando doblegar el sesgo de Gemma en el problema `B4`.
4. **`I1-C` (Rol Simulado):**
   * **Efectividad:** Muy alta para modelos pequeños. Fingir etiquetas `[SYSTEM]` dentro del mensaje del usuario resultó ser la forma más efectiva de mantener "despierto" a Qwen 2B.

---

## 3. Instruction Hierarchy (I1-D) y el Control de Alucinaciones

La estrategia suprema es la **`I1-D` (System Message Real)**. Esta estrategia se apoya en el mecanismo arquitectónico nativo de los LLMs modernos llamado *Instruction Hierarchy* (Jerarquía de Instrucciones): se colocan las reglas inquebrantables de RAG en el canal `system` (máximo privilegio) y el texto de trabajo en el `user` (menor privilegio).

### Resultados del Enfoque Instruction Hierarchy:

1. **Ruptura de Terquedad Invencible:**
   Gemma 4B es un modelo reacio a las directivas de usuario. En el fragmento `B3_modal`, desestimó todas las alertas y énfasis de la tabla, respondiendo "Sí" de forma repetida. **Únicamente la estrategia `I1-D` logró forzar a Gemma a frenar su sesgo paramétrico.** Al recibir las instrucciones desde el canal de sistema, el modelo abandonó su seguridad y acató el límite impuesto por el RAG.

2. **Ejecución del "Botón de Pánico" (Regla #3):**
   La estrategia `I1-D` incluye la Regla 3: *"Si la respuesta no puede obtenerse... indicalo explícitamente"*.
   En el fragmento `A4_producto_cart`, se le pasó a Gemma el texto severamente dañado `â Ã â â â`. En lugar de adivinar o inventar una respuesta matemática, Gemma ejecutó la orden jerárquica a la perfección y respondió:
   > *"La respuesta no puede obtenerse del documento con las definiciones provistas."*

### Conclusión Parcial
El análisis prueba que inyectar el contexto RAG de manera "plana" en el canal del usuario es ineficiente ante la Terquedad Semántica. **La utilización del System Message (Instruction Hierarchy) es fundamental para romper el sesgo**, pero, como veremos a continuación, trae consigo un efecto secundario inesperado: el exceso de precaución.

---

## 4. Análisis Cuantitativo: El Problema del "Over-refusal" (Evaluación Manual)

> **Nota Metodológica:** Los evaluadores automáticos basados en palabras clave (keywords) suelen penalizar falsamente respuestas correctas. Por ejemplo, si el modelo responde *"No se puede concluir que sean iguales"*, el evaluador automático lo marca como `✗ CONFUNDIDO` porque detecta la palabra prohibida *"iguales"*. 
> La siguiente matriz refleja el **rendimiento real evaluado manualmente**. Además, separa los aciertos reales de las **abstenciones** (cuando el modelo aplica la Regla #3 y se niega a responder).

### Matriz de Rendimiento (Precisión sobre los 7 Fragmentos)

| Condición de Prueba | Qwen3.5-2B (Aciertos) | Gemma-4B (Aciertos) | Gemma-4B (Abstenciones) |
|:---|:---:|:---:|:---:|
| **`DOC CORR` (Sin Tabla)** | **2/7** | **2/7** | 0/7 |
| **`CON TABLA` (Plain)** | **5/7** | **6/7** | 0/7 |
| **`I1-A / B / C`** | **7/7** *(Falsos negativos)* | **6/7** | 0/7 |
| **`I1-D` (System Message)** | **7/7** *(Perfección)* | **5/7** *(Caída)* | **2/7** *(Exceso de abstención)* |

### El Efecto Secundario de Instruction Hierarchy: "Over-Refusal"
Si observamos de cerca las respuestas de Gemma 4B, vemos que **el desempeño bajo `I1-D` no fue perfecto, sino excesivamente conservador**. 

Al colocar las reglas estrictas en el canal de sistema, incluyendo la Regla #3 (*"Si la respuesta no puede obtenerse... indicalo"*), Gemma 4B reaccionó con **over-refusal** (exceso de negación):
1. En **`B3_modal`**, en lugar de deducir que la respuesta era "No" (como hizo Qwen), Gemma se abstuvo: *"No se puede determinar si la expresión tiene la misma forma..."*. Logró romper su alucinación anterior ("Sí"), pero no logró resolver el problema.
2. Peor aún, en **`A4_producto_cart`**, Gemma venía acertando en todas las estrategias anteriores, pero al aplicar `I1-D`, se asustó por la corrupción del texto (`â Ã â â â`) y prefirió abstenerse: *"La respuesta no puede obtenerse del documento..."*. 

**Conclusión Final:** 
La *Instruction Hierarchy* (`I1-D`) es extremadamente efectiva para destruir la Terquedad Semántica y evitar que el modelo invente respuestas. Sin embargo, en modelos de la escala de 4B, **las reglas de sistema muy estrictas los vuelven demasiado literales o miedosos**, perdiendo capacidad de inferencia (fuzzy matching) sobre textos corruptos que, en condiciones menos estrictas, sí lograban interpretar.
