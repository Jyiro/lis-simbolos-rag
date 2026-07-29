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

### 6.2 Fase 2A — Embedding degradado

- [ ] Implementar `fase2_embedding.py`
- [ ] Calcular similitud coseno limpio vs. corrupto para cada fragmento
- [ ] Medir efecto de tabla de contexto sobre la similitud coseno
- [ ] Comparar `nomic-embed-text` vs `mxbai-embed-large` sobre el mismo corpus

```python
# Pseudocódigo Fase 2A
for fragmento in corpus:
    vec_limpio         = embed(doc_limpio)
    vec_corrupto       = embed(doc_corrupto)
    vec_corrupto_tabla = embed(tabla + doc_corrupto)
    vec_latex          = embed(doc_latex)

    resultados[fragmento] = {
        "sim_corrupto":       cosine(vec_limpio, vec_corrupto),
        "sim_corrupto_tabla": cosine(vec_limpio, vec_corrupto_tabla),
        "sim_latex":          cosine(vec_limpio, vec_latex),
    }
```

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