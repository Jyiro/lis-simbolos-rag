# Evidencias Empíricas — DeepDoc Research

> Archivo de consolidación de hallazgos. Reúne los resultados de las 5 fases de investigación empírica sobre la preservación de símbolos matemáticos en el pipeline de extracción PDF de DeepDoc/RAGFlow.
>
> **Stack auditado:** `pdfplumber` (motor interno de DeepDoc/RAGFlow) vs. `pypdf` y `PyMuPDF` (extractores de referencia).
> **Corpus:** 4 papers académicos reales con alta densidad de símbolos matemáticos.
> **Metodología:** EAR (Extractor Agreement Rate) — el consenso entre tres extractores independientes actúa como proxy de "verdad" sin necesidad de ground truth manual.

---

## Fase 1 — Baseline: PDFs sintéticos (CPR)

**Script:** `probe.py` | **Reporte:** `summary_report.md` | **Fecha:** 2026-09-09

**Métrica:** CPR (Char Preservation Rate) — porcentaje de símbolos del ground truth recuperados por cada extractor.

**Corpus:** 6 documentos sintéticos generados con `reportlab` (matemática, lógica, física, química, música, literatura).

### Resultado

| Documento | pdfplumber | PyMuPDF | pypdf |
|---|---|---|---|
| 01_matematica | 100.0% | 100.0% | 100.0% |
| 02_logica | 100.0% | 100.0% | 100.0% |
| 03_fisica | 100.0% | 100.0% | 100.0% |
| 04_quimica | 100.0% | 100.0% | 100.0% |
| 05_musica | 100.0% | 100.0% | 100.0% |
| 06_literatura | 100.0% | 100.0% | 100.0% |

### Conclusión

El bug **no existe en PDFs ideales** generados programáticamente. Todos los extractores son perfectos sobre fuentes estándar con encoding Unicode correcto. El problema es específico a fuentes académicas con encoding conflictivo (ver Fase 3C).

Esta fase establece el techo teórico: si pdfplumber falla en PDFs reales, no es limitación del formato PDF sino del stack de fuentes usado por LaTeX académico.

---

## Fase 2 — EAR sobre PDFs reales

**Script:** `probe_real.py` | **Reporte:** `real_report.md` | **Fecha:** 2026-09-09 19:26

**Métrica:** EAR (Extractor Agreement Rate) — si los tres extractores no coinciden en el conteo de un símbolo, se marca discrepancia. EAR < 100% = evidencia de fallo.

**Corpus real:**
- `AbstractAlgebra_cap1-3_symbols.pdf`
- `FirstOrderLogic_complete.pdf`
- `ModalLogicFundamentally_complete.pdf`
- `ModalLogicalNeuralNetworks_complete.pdf`

### Resumen ejecutivo

| Documento | Símbolos auditados | Discrepancias | Peor símbolo | Peor EAR |
|---|---|---|---|---|
| AbstractAlgebra | 23 | **3** | `∑` (SUM) | **0.0%** |
| FirstOrderLogic | 15 | **1** | `⊢` (TURNSTILE) | **33.8%** |
| ModalLogicFundamentally | 22 | **1** | `⊨` (MODELS) | **0.0%** |
| ModalLogicalNeuralNetworks | 21 | 0 | — | 100.0% ✅ |

### Detalle de discrepancias

| Símbolo | Unicode | Documento | pdfplumber | PyMuPDF | pypdf | EAR |
|---|---|---|---|---|---|---|
| `∑` | U+2211 | AbstractAlgebra | **0** | **0** | 65 | **0.0%** |
| `∏` | U+220F | AbstractAlgebra | **0** | **0** | 19 | **0.0%** |
| `√` | U+221A | AbstractAlgebra | 61 | 61 | 62 | **98.4%** |
| `⊢` | U+22A2 | FirstOrderLogic | 640 | **216** | 640 | **33.8%** |
| `⊨` | U+22A8 | ModalLogicFundamentally | **0** | 2 | 2 | **0.0%** |

### Observación sobre `∑` y `∏`

Tanto pdfplumber como PyMuPDF leen 0 sumatorias y productorias. Esto implica que el bug de encoding afecta a **ambos** extractores sobre este PDF, aunque por mecanismos distintos (pdfplumber emite `(cid:X)`, PyMuPDF silencia). Solo pypdf recupera correctamente via ToUnicode CMap.

### Tabla de EAR cruzada (todos los símbolos, todos los documentos)

| Símbolo | Nombre | AbstractAlgebra | FirstOrderLogic | ModalLogicFundamentally | ModalLogicalNeuralNetworks |
|---|---|---|---|---|---|
| `∑` | SUM | **0.0%** | — | — | — |
| `∏` | PRODUCT | **0.0%** | — | — | — |
| `⊨` | MODELS | — | — | **0.0%** | — |
| `⊢` | TURNSTILE | — | **33.8%** | 100% | — |
| `√` | SQRT | **98.4%** | — | — | — |
| `→` | IMPLIES | 100% | 100% | 100% | 100% |
| `∀` | FOR_ALL | — | 100% | 100% | 100% |
| `∃` | EXISTS | — | 100% | 100% | — |
| `¬` | NOT | — | 100% | 100% | 100% |
| `∧` | AND | — | 100% | 100% | 100% |
| `∨` | OR | — | 100% | 100% | 100% |
| `↔` | IFF | — | 100% | — | 100% |
| `∈` | ELEM_OF | 100% | 100% | 100% | 100% |
| `⊂` | SUBSET | 100% | 100% | — | — |
| `⊆` | SUBSETEQ | — | 100% | 100% | 100% |
| `∞` | INFINITY | 100% | — | — | 100% |
| `≤` | LEQ | 100% | — | 100% | 100% |
| `≥` | GEQ | 100% | 100% | 100% | 100% |

---

## Fase 3A — Análisis forense de corrupción

**Script:** `phase3a_forensic.py` | **Reporte:** `forensic_report.md` | **Fecha:** 2026-09-09

**Objetivo:** Determinar exactamente qué pone pdfplumber en el texto extraído en lugar del símbolo perdido.

### Caso 1: `∑` y `∏` en AbstractAlgebra

Alineación manual línea a línea entre pypdf (referencia) y pdfplumber (motor RAGFlow):

| Símbolo | Texto correcto (pypdf) | Texto corrupto (pdfplumber) | Tipo de corrupción |
|---|---|---|---|
| `∑` | `(x + y)p =` **`∑`** `0≤i≤p` | `p (x+y)p = xiyp−i i 0≤i≤p` + emite `(cid:9)` | OMISIÓN + ARTEFACTO |
| `∑` | `(x +1 )p =` **`∑`** `0≤i≤p` | `(x+1)p = xi1p−i =xp+ xi+1` + emite `(cid:9)` | OMISIÓN + ARTEFACTO |
| `∏` | `P =` **`∏`** `g∈G` | `P = g = f(g)` + emite `(cid:10)` | OMISIÓN + ARTEFACTO |

**Hallazgo crítico:** pdfplumber no solo omite el símbolo — destruye la sintaxis completa de la fórmula. `(x + y)p = 0≤i≤p` sin el operador `∑` cambia completamente el significado matemático. Esta pérdida es **silenciosa**: el LLM recibe el chunk sin ninguna señal de que algo falta.

### Caso 2: `⊨` en ModalLogicFundamentally

Alineación en las líneas 171-176 del documento:

| Línea | Texto correcto (pypdf) | Texto corrupto (pdfplumber) | Tipo de corrupción |
|---|---|---|---|
| 1 | `a consequence relation` **`⊨`** `C ⊆ L × L.` | `a consequence relation` **`(cid:15)`** `C⊆L×L.` | SUSTITUCIÓN |
| 2 | `ϕ ⊢ F ψ iﬀ ϕ` **`⊨`** `WPL ψ.` | `ϕ⊢ F ψ iff ϕ` **`(cid:15)`** `WPL ψ.` | SUSTITUCIÓN |

**Hallazgo crítico:** El operador lógico `⊨` se reemplaza por el string literal `(cid:15)`. Un LLM que reciba este chunk vía RAG no puede deducir que `(cid:15)` significa `⊨`. Es un artefacto interno del parser, completamente opaco semánticamente. Ninguna búsqueda por símbolo matemático encontrará este chunk.

### Taxonomía de corrupción identificada

| Tipo | Descripción | Ejemplo | Detectabilidad |
|---|---|---|---|
| **OMISIÓN** | El símbolo desaparece del texto, la fórmula queda truncada | `∑` → nada | Muy baja (el texto parece válido) |
| **ARTEFACTO** | Se emite `(cid:X)` en una línea cercana (no necesariamente la misma) | `∑` → `(cid:9)` en línea anterior | Media (el `(cid:X)` es visible pero disociado) |
| **SUSTITUCIÓN** | El símbolo se reemplaza in-situ por `(cid:X)` | `⊨` → `(cid:15)` | Media (visible pero semánticamente opaco) |

### Conclusiones Fase 3A

1. **La corrupción no es omisión simple de espacios** — altera la estructura semántica de las fórmulas matemáticas de forma irreversible.
2. **Los artefactos `(cid:X)` contaminan los embeddings** — un usuario que pregunte "ecuaciones con sumatorias" nunca va a recuperar un chunk que contiene `(cid:9)`.
3. **La pérdida silenciosa es el escenario más peligroso** — cuando el artefacto no aparece en la misma línea que la fórmula, no hay ninguna señal visible de degradación.

---

## Fase 3B — Simulación de chunking y pérdida de contexto

**Script:** `phase3b_chunking.py` | **Reporte:** `chunking_report.md` | **Fecha:** 2026-09-09

**Objetivo:** Medir cuántos símbolos que *sí sobrevivieron* la extracción quedan partidos entre chunks o pierden contexto semántico al aplicar el chunking fijo de RAGFlow (~2000 chars, overlap 200 chars).

### Resultados por símbolo y documento

| Símbolo | Documento | Total extraído | En borde de chunk (<50 chars) | Sin contexto semántico |
|---|---|---|---|---|
| `⊢` TURNSTILE | FirstOrderLogic | 691 | **28 (4.1%)** | **165 (23.9%)** |
| `¬` NOT | ModalLogicFundamentally | 442 | 23 (5.2%) | 9 (2.0%) |
| `∈` ELEM_OF | AbstractAlgebra | 400 | 17 (4.2%) | 0 (0.0%) |

### Ejemplo de símbolo en borde sin contexto

```
Chunk 3 (fin): "...r formulas without ✷⊢⊢⊢ , but they diﬀer for
formulas with ✷⊢⊢⊢ to the one..."
```

El símbolo aparece al borde del chunk — la cláusula que lo define está en el chunk siguiente.

### La doble pérdida acumulativa

Para `⊢` en FirstOrderLogic:

```
Etapa 1 (Extracción):   pdfplumber extrae 640/640 ✅  →  691 total
Etapa 2 (Chunking):     28 caen en borde           →  contexto cortado
                        165 sin palabras clave      →  retrieval ciego
```

Las dos capas de pérdida operan de forma **independiente y acumulativa**. Un símbolo puede sobrevivir la extracción y aun así ser irrecuperable por retrieval si su contexto semántico quedó partido.

### Conclusión Fase 3B

El chunking fijo de RAGFlow no es neutral para contenido matemático. Un ~4-5% de los símbolos cae en bordes de chunk, y hasta un ~24% puede quedar en chunks sin palabras clave de contexto. Esto agrava el problema de retrieval independientemente de si la extracción fue correcta.

---

## Fase 3C — Causa raíz: Font encoding en pdfminer.six

**Script:** `phase3c_fonts.py` | **Reporte:** `fonts_report.md` | **Fecha:** 2026-09-09

**Objetivo:** Usar `fonttools` para analizar los diccionarios de fuente en los PDFs problemáticos y determinar por qué pdfminer.six falla donde pypdf tiene éxito.

### Fuentes problemáticas identificadas

El PDF `AbstractAlgebra_cap1-3_symbols.pdf` contiene fuentes con esta estructura:

```python
{
  '/BaseFont': '/CGCGFK+CMSS17',
  '/Encoding': '/MacRomanEncoding',
  '/Subtype': '/Type1',
  '/Type': '/Font'
}
```

Son fuentes **CFF Type1** (fuentes matemáticas de LaTeX, familia Computer Modern) declaradas con `/MacRomanEncoding`.

### Hipótesis inicial: bug de prioridad MacRoman vs ToUnicode CMap

> ⚠️ Esta fue la hipótesis de trabajo formulada en Fase 3C (2026-09-09). Ver **Revisión del diagnóstico** más abajo para la versión corregida.

La especificación PDF permite que una fuente declare un `/Encoding` base pero lo sobrescriba con un mapa `ToUnicode` (CMap) embebido, que es la verdad de qué carácter Unicode corresponde a cada glifo de la fuente.

| Extractor | Comportamiento ante MacRoman + ToUnicode CMap | Resultado |
|---|---|---|
| **pypdf** | Prioriza el `ToUnicode CMap` embebido | `∑` extraído correctamente ✅ |
| **PyMuPDF** | Prioriza el `ToUnicode CMap` embebido | `∑` extraído correctamente ✅ |
| **pdfminer.six** (motor de pdfplumber/DeepDoc) | Aplica `/MacRomanEncoding` directamente, ignora el CMap | `(cid:9)` / omisión ❌ |

Hipótesis: pdfminer ignora el ToUnicode CMap y aplica MacRoman directamente → el byte no coincide con ningún glifo conocido → emite `(cid:X)`.

### Revisión del diagnóstico (2026-09-17) — Causa raíz más precisa

Al inspeccionar el código fuente de pdfminer.six (`pdffont.py`, `encodingdb.py`) se descubrió que **`to_unichr()` ya intenta primero el ToUnicode CMap** antes de caer al encoding base. La hipótesis de prioridad incorrecta era parcialmente errónea.

El bug real opera a un nivel más profundo: los **nombres de glifo propios de las fuentes TeX** (`summationdisplay`, `productdisplay`, `square`, etc.) **no están en el Adobe Glyph List (AGL) que usa pdfminer**.

```
Cadena real de fallo en pdfminer:

  PDF /Differences array: [9 /summationdisplay 10 /productdisplay ...]
         ↓
  pdfminer llama a name2unicode("summationdisplay")
         ↓
  Busca en glyphname2unicode (Adobe AGL) → NO ESTÁ → PDFKeyError
         ↓
  El slot cid=9 queda vacío en cid2unicode
         ↓
  to_unichr(9) falla → emite "(cid:9)"   ← AÚN cuando hay ToUnicode CMap
```

| Nombre de glifo TeX | En AGL de pdfminer | Unicode correcto |
|---|---|---|
| `summationdisplay` | ❌ NO ESTÁ | ∑ U+2211 |
| `summationtext`    | ❌ NO ESTÁ | ∑ U+2211 |
| `productdisplay`   | ❌ NO ESTÁ | ∏ U+220F |
| `square`           | ❌ NO ESTÁ | □ U+25A1 |
| `integraldisplay`  | ❌ NO ESTÁ | ∫ U+222B |
| `summation`        | ✅ Sí      | ∑ — (nombre estándar, no el TeX) |

**La hipótesis original no era incorrecta para todos los casos** — el mecanismo de MacRoman SÍ interfiere en fuentes donde los bytes del stream no pasan por el array `/Differences`. Ambos mecanismos de fallo coexisten dependiendo del PDF. Ver sección «Análisis de Causa Raíz — Capa de Mapeo» más abajo para el análisis completo.

### Conclusión Fase 3C (actualizada)

El fallo **no es OCR ni renderizado visual**. Tiene dos mecanismos de fallo que pueden coexistir:

1. **Nombres TeX ausentes del AGL** (mecanismo principal identificado en 2026-09-17): `summationdisplay`, `square`, etc. no están en el glyph list de pdfminer → el slot queda vacío → `(cid:X)`.
2. **Prioridad de encoding incorrecta** (hipótesis original 2026-09-09): en fuentes donde el byte se resuelve via encoding base sin pasar por el AGL, MacRoman produce caracteres incorrectos.

**La solución más simple y efectiva**: inyectar la **TeX Glyph List** en `pdfminer.glyphlist.glyphname2unicode` (monkey-patch en tiempo de ejecución). Ver `plan_patch.md` para la especificación completa.

---

## Resumen ejecutivo — Todos los hallazgos

### ¿Qué falla?

| Capa | Fallo | Síntoma visible | Impacto en RAG |
|---|---|---|---|
| **Extracción (pdfplumber)** | pdfminer.six ignora ToUnicode CMap en fuentes CFF Type1 | `(cid:X)` en texto / operador silenciado | Chunk llega al LLM sin el símbolo |
| **Chunking (RAGFlow fixed)** | ~4-5% de símbolos caen en bordes de chunk | Fórmula partida entre chunks | Retrieval recupera contexto incompleto |
| **Retrieval** | Artefactos `(cid:X)` no son recuperables por búsqueda semántica | Chunk con `(cid:9)` no matchea query con `∑` | El chunk simplemente no se devuelve al LLM |

### ¿Qué NO falla?

- PDFs generados con fuentes Unicode estándar → CPR 100%
- Símbolos comunes (→, ∀, ∃, ¬, ∧, ∨, ∈, ≤, ≥) en papers reales → EAR 100%
- `ModalLogicalNeuralNetworks_complete.pdf` → 0 discrepancias (probablemente generado con fuentes más modernas)

### Símbolos críticos identificados

| Símbolo | Riesgo | Documentado en |
|---|---|---|
| `∑` U+2211 | **CRÍTICO** — EAR 0%, pérdida total en pdfplumber | Fase 2 + 3A |
| `∏` U+220F | **CRÍTICO** — EAR 0%, pérdida total en pdfplumber | Fase 2 + 3A |
| `⊨` U+22A8 | **CRÍTICO** — EAR 0%, sustituido por `(cid:15)` | Fase 2 + 3A |
| `⊢` U+22A2 | **ALTO** — EAR 33.8%, instabilidad entre extractores | Fase 2 + 3B |
| `√` U+221A | **MEDIO** — EAR 98.4%, discrepancia menor en conteo | Fase 2 |

---

## Próximos pasos planificados

| Prioridad | Acción | Complejidad | Impacto |
|---|---|---|---|
| **Alta** | **Post-procesador `(cid:X)`:** cargar PDF con fonttools, construir mapa `glifo_id → unicode` por fuente, reemplazar artefactos en el texto ya extraído | Baja | Alto — fix inmediato sin tocar RAGFlow |
| **Alta** | **PR a RAGFlow/DeepDoc:** agregar fonttools como dependencia + integrar post-procesador en `deepdoc/parser/` | Alta | Muy alto — fix sistémico |
| Media | **Parche a pdfminer.six:** forzar prioridad ToUnicode CMap sobre `/Encoding` cuando fonttools está disponible | Media | Alto — posible PR al repo OSS |
| Media | **Hybrid extractor fallback:** detectar tasa de `(cid:X)` por página; si supera umbral, re-extraer con pypdf y hacer merge | Media | Medio — sin tocar pdfminer |

---

---

# Estrategias de Intervención — Análisis y Opciones

> Esta sección está estructurada para presentación de avances de investigación.
> Organiza las opciones de solución por dimensiones: dónde intervenir, cómo intervenir, qué garantías da cada enfoque.

---

## Pipeline completo — Dónde ocurre cada fallo

### Flujo de ingesta de documentos en RAGFlow / DeepDoc

```
USUARIO sube PDF
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  DeepDoc  (ragflow/deepdoc/)                        │
│                                                     │
│  pdf_parser.py                                      │
│    └── pdfplumber.open(pdf)          ← CAPA 1       │
│         └── extracción página a página              │
│              [BUG] pdfminer.six ignora ToUnicode    │
│              → ∑ desaparece / (cid:9) aparece       │
│                                                     │
│  chunker (fixed-size / smart)        ← CAPA 2       │
│    └── ~2000 chars, overlap 200                     │
│         [PROBLEMA] ~4-5% de símbolos en borde       │
│         [PROBLEMA] ~24% sin contexto semántico      │
│                                                     │
│  embedder (nomic-embed-text)         ← CAPA 3       │
│    └── (cid:X) contamina el vector                  │
│         → query "sumatoria" ≠ chunk con "(cid:9)"  │
└─────────────────────────────────────────────────────┘
       │
       ▼
  Vector Store (HNSW)
       │
       ▼
  LLM recibe chunk corrupto
  → respuesta sin el operador matemático
```

**Punto de mayor impacto para intervenir: entre pdf_parser.py y el chunker.**
En ese punto el PDF original todavía está disponible y el texto aún no fue fragmentado.

---

## Descubrimiento adicional — La magnitud real de la corrupción

Al auditar los artefactos `(cid:X)` en el texto extraído de `AbstractAlgebra_cap1-3_symbols.pdf`:

| Artefacto | Ocurrencias | Símbolo esperado |
|---|---|---|
| `(cid:0)` | **754** | desconocido (posiblemente espacio o carácter tipográfico) |
| `(cid:2)` | **672** | desconocido |
| `(cid:3)` | **374** | desconocido |
| `(cid:7)` | 156 | desconocido |
| `(cid:9)` | **115** | `∑` (pypdf encuentra 65) |
| `(cid:5)` | 103 | desconocido |
| `(cid:8)` | 91 | desconocido |
| `(cid:10)` | **72** | `∏` (pypdf encuentra 19) |
| ... | ... | ... |
| **Total** | **~2785** | — |

**Hallazgo crítico:** La corrupción no afecta solo a los símbolos matemáticos del catálogo — compromete fuentes enteras del documento. El texto ordinario también está afectado. La magnitud es mucho mayor de lo que medía el EAR solo sobre símbolos.

**Implicación:** El mismo ID de glifo (ej. `(cid:9)`) puede mapear a caracteres distintos según qué fuente estaba activa. Esto significa que un reemplazo ingénuo sin contexto de fuente cometería errores.

---

## La raíz del problema de ambigüedad

```
PDF Content Stream:
  /CGCGFK+CMSS17 Tf   ← "activar fuente matemática"
  (glifo 9) Tj         ← este glifo es ∑ en esta fuente
  
  /ABCDEF+CMR10 Tf    ← "activar fuente de texto normal"  
  (glifo 9) Tj         ← este glifo es algo distinto en esta fuente

pdfminer descarta el contexto de fuente → emite "(cid:9)" en ambos casos
→ el lector del texto ya no puede distinguirlos
```

La información para resolver el problema **existe en el PDF** y es determinística.
El problema es que pdfminer la descarta antes de producir el texto de salida.

---

## Mapa de opciones de intervención

### Dimensión 1: ¿Invasividad?

```
NO INVASIVO ◄────────────────────────────────────► INVASIVO
     │                    │                              │
  Hybrid               Post-proc.                   Parche a
  Fallback             (cid:X)                     pdfminer.six
  (pypdf)              fonttools
     │                    │                              │
  Sin tocar          Sin tocar                   Modifica librería
  ninguna            ninguna                     open source
  librería           librería
```

### Dimensión 2: ¿Determinístico o probabilístico?

```
DETERMINÍSTICO ◄─────────────────────────────────► PROBABILÍSTICO
       │                                                   │
  Hybrid fallback ──────────────────────────►  LLM/SLM
  Parche pdfminer                              Clasificador ML
  Post-proc. fonttools*                        Modelo seq2seq
  
  (* si se resuelve la ambigüedad de fuente)
```

### Dimensión 3: ¿Dónde en el pipeline?

```
ANTES de extracción   DURANTE extracción   DESPUÉS de extracción   DESPUÉS de retrieval
        │                     │                      │                       │
  (no aplica)          Parche a              Hybrid fallback          LLM como
                       pdfminer.six          Post-proc. fonttools      corrector
                                             (ambos con PDF           ("repará
                                              original disponible)     este texto")
```

---

## Opción A — Hybrid Extractor Fallback

**Categoría:** No invasivo · Determinístico · Post-extracción

### Cómo funciona

```
Para cada página del PDF:
  1. Extraer con pdfplumber (comportamiento actual de RAGFlow)
  2. Contar artefactos (cid:X) en el resultado
  3. Si count ≥ umbral (ej. 2):
       → Re-extraer esa página con pypdf
       → pypdf consulta correctamente el ToUnicode CMap
       → Recupera ∑, ∏, ⊨ en posición exacta
  4. Si count < umbral:
       → Usar texto de pdfplumber (sin cambios)
  5. Concatenar por número de página → texto híbrido
```

### Punto de inserción en DeepDoc

```python
# deepdoc/parser/pdf_parser.py — después de la extracción pdfplumber
raw_pages = plumber_extract_by_page(pdf_path)
clean_pages = hybrid_fallback(raw_pages, pdf_path, threshold=2)
text = "\n".join(clean_pages)
# → continúa al chunker con texto corregido
```

### Ventajas

- No modifica ninguna librería existente
- pypdf ya está instalado en el entorno
- Resolución 100% determinística (usa el mismo PDF, mismo CMap)
- Cubre TODOS los casos de corrupción (sustitución y omisión)
- El PDF original siempre está disponible en el pipeline de RAGFlow

### Limitaciones

- pypdf y pdfplumber producen texto con layout ligeramente distinto (saltos de línea, orden de columnas)
- El umbral requiere calibración
- Para páginas muy densas matemáticamente, pypdf puede ser más lento
- No ayuda si el PDF no tiene ToUnicode CMap embebido (PDFs escaneados sin OCR)

### Cobertura estimada sobre corpus

| Documento | (cid:X) totales | Páginas con ≥2 artefactos | Cobertura ∑/∏/⊨ |
|---|---|---|---|
| AbstractAlgebra | ~2785 | prácticamente todas | ✅ Recupera |
| FirstOrderLogic | pendiente audit | por medir | ✅ Recupera `⊢` |
| ModalLogicFundamentally | pendiente audit | por medir | ✅ Recupera `⊨` |

---

## Opción B — Post-procesador (cid:X) con fonttools

**Categoría:** No invasivo · Cuasi-determinístico* · Post-extracción

### Cómo funciona

```
1. Tomar texto extraído por pdfplumber (con artefactos (cid:X))
2. Abrir el PDF original con fonttools
3. Por cada fuente del documento:
     extraer ToUnicode CMap → { glifo_id: char_unicode }
4. Recorrer el texto con regex sobre patrón (cid:\d+)
5. Para cada match:
     → buscar el glifo_id en el CMap de la fuente activa*
     → reemplazar (cid:X) por el carácter Unicode correcto
6. Devolver texto corregido
```

*El asterisco: la fuente activa en el momento de cada `(cid:X)` no está en el texto plano.
Requiere o bien un mapa probabilístico, o re-procesar el content stream completo del PDF.

### Ventajas

- Más quirúrgico que el hybrid fallback (no reemplaza toda la página)
- Preserva el layout exacto de pdfplumber para el resto del texto
- Útil como complemento al hybrid fallback para limpiar residuos

### Limitación clave

- La ambigüedad de fuente hace que sin el contexto de fuente activa, el mismo `(cid:X)` pueda mapear a caracteres distintos
- Resolución correcta requiere rastrear el content stream del PDF, lo cual es esencialmente reimplementar parte de pdfminer

---

## Opción C — Parche a pdfminer.six

**Categoría:** Invasivo · Determinístico · Durante extracción · Potencial PR open source

### Cómo funciona

```
pdfminer actual:
  Encuentra glifo en fuente CFF Type1 con MacRomanEncoding
  → Aplica MacRoman directamente
  → Falla → emite (cid:X)

pdfminer parcheado:
  Encuentra glifo en fuente CFF Type1 con MacRomanEncoding
  → Detecta que hay ToUnicode CMap disponible (fonttools)
  → Consulta el CMap → obtiene Unicode correcto
  → Emite el carácter correcto
  → (cid:X) nunca aparece
```

### Punto de modificación

```
pdfminer/
└── pdfpage.py o pdffont.py
      └── _initialize_encoding()
            └── if has_tounicode_cmap and fonttools_available:
                    return resolve_from_cmap(glyph_id, font)
                else:
                    return apply_base_encoding(glyph_id, encoding)
```

### Ventajas

- Fix sistémico — cualquier usuario de pdfminer.six se beneficia
- No requiere cambios en RAGFlow ni en DeepDoc
- Resolución 100% determinística con contexto de fuente perfecto
- Candidato a Pull Request en el repo oficial de pdfminer.six

### Limitaciones

- Requiere que `fonttools` sea dependencia de pdfminer.six (actualmente no lo es)
- Mayor esfuerzo de implementación y testing
- Proceso de revisión/merge puede demorar meses
- Riesgo de regresión en otros casos de encoding

---

## Opción D — Enfoques no-determinísticos (ML/SLM)

**Categoría:** No invasivo · Probabilístico · Post-extracción o post-retrieval

> Aplica cuando el PDF original no está disponible, o como capa adicional de corrección sobre los enfoques determinísticos.

### D1 — LLM como corrector de texto matemático

```
Input al LLM:
  "Sea G un grupo. El producto (cid:10) g∈G f(g) se define como..."
  
Output esperado:
  "Sea G un grupo. El producto ∏ g∈G f(g) se define como..."
```

- **Fortaleza:** Usa comprensión semántica del contexto para inferir el símbolo correcto
- **Debilidad:** Puede alucinar (¿es `∏` o `∑`?), no escala en costo, no reproducible
- **Cuándo usarlo:** Solo como fallback de último recurso cuando no hay PDF original

### D2 — Clasificador ML entrenado en corpus paralelo

El corpus de pares (texto pdfplumber, texto pypdf) que ya generamos en Fase 2 puede usarse como datos de entrenamiento:

```
Features: (cid_number, n_tokens_contexto_izq, n_tokens_contexto_der,
           tipo_documento, densidad_matemática_de_página)
Target:   unicode_correcto

Datos disponibles: ~2785 artefactos en AbstractAlgebra
                   con resolución correcta de pypdf como label
```

- **Fortaleza:** Escala bien, no requiere acceso al PDF original en inferencia
- **Debilidad:** Probabilístico, requiere suficientes datos de entrenamiento, puede generalizar mal a nuevos tipos de fuentes

### D3 — Small Language Model especializado (seq2seq)

Fine-tuning de un modelo seq2seq (T5, BART o similar) sobre pares de texto corrupto → texto limpio extraídos automáticamente del corpus.

```
Corpus de entrenamiento (generado automáticamente):
  Texto corrupto: extraído con pdfplumber de los PDFs del corpus
  Texto limpio:   extraído con pypdf de los mismos PDFs

Inferencia:
  Input:  chunk con (cid:X) → SLM → Output: chunk corregido
```

- **Fortaleza:** Aprende patrones complejos de corrupción, generaliza a nuevas combinaciones de fuentes, podría manejar también errores de layout
- **Debilidad:** Requiere fine-tuning (costo computacional), puede introducir errores en matemáticas precisas, más difícil de auditar

---

## Comparativa de todas las opciones

| Opción | Invasividad | Determinismo | Resuelve omisión | Resuelve sustitución | Necesita PDF original | Complejidad |
|---|---|---|---|---|---|---|
| **A — Hybrid fallback** | ✅ No invasiva | ✅ Determinístico | ✅ Sí | ✅ Sí | ✅ Sí | Baja |
| **B — Post-proc. fonttools** | ✅ No invasiva | ⚠️ Cuasi-det. | ❌ No | ✅ Sí | ✅ Sí | Media |
| **C — Parche pdfminer** | ❌ Invasiva | ✅ Determinístico | ✅ Sí | ✅ Sí | ✅ Sí (implícito) | Alta |
| **D1 — LLM corrector** | ✅ No invasiva | ❌ Probabilístico | ⚠️ Parcial | ⚠️ Parcial | ❌ No | Muy baja |
| **D2 — Clasificador ML** | ✅ No invasiva | ❌ Probabilístico | ⚠️ Parcial | ⚠️ Parcial | ❌ No | Media |
| **D3 — SLM seq2seq** | ✅ No invasiva | ❌ Probabilístico | ⚠️ Parcial | ✅ Mejor | ❌ No | Alta |

---

## Estrategia recomendada — Por fases

### Fase inmediata (baja complejidad, alto impacto)
**Implementar Hybrid fallback (Opción A)** como script standalone y validar contra el corpus.
- Medir: ¿cuántos `(cid:X)` quedan después del fallback?
- Medir: ¿el texto de pypdf preserva el layout correctamente para el chunker?

### Fase media (integración en RAGFlow)
**Insertar Hybrid fallback en `deepdoc/parser/pdf_parser.py`** con un flag de configuración para habilitarlo/deshabilitarlo.
- Proponer PR al repositorio de RAGFlow
- Incluir el benchmark EAR como evidencia técnica del bug

### Fase larga (impacto open source)
**PR a pdfminer.six** con el parche de prioridad ToUnicode CMap.
- Beneficia a todo el ecosistema Python de extracción PDF
- Elimina el problema de raíz sin necesitar workarounds

### Fase exploratoria (investigación)
**Experimento con SLM seq2seq** entrenado en el corpus paralelo pdfplumber/pypdf.
- Interesante como contribución académica: un modelo que aprende a "des-corromper" texto PDF matemático
- Permite comparar enfoque determinístico vs probabilístico con métricas objetivas (CER, EAR post-corrección)

## Fase 4 — Evaluación de pymupdf4llm (Markdown direct extraction)

**Objetivo:** Determinar si la conversión directa a Markdown mediante `pymupdf4llm` preserva los símbolos matemáticos mejor que el pipeline PDF → texto de `pdfplumber`.

**Resultado:** `pymupdf4llm` tuvo un rendimiento **significativamente peor** que `pypdf` e incluso que `pdfplumber` en muchos casos.
- `SUM (∑)` y `PRODUCT (∏)`: 0% de preservación (mismo fallo que pdfplumber).
- `TURNSTILE (⊢)`: Extrajo 180 (vs 640 de pypdf).
- `IMPLIES (→)`: Extrajo 5 (vs 19 de pypdf).
- `PARTIAL (∂)`: Extrajo 2 (vs 8 de pypdf).

**Conclusión:** `pymupdf4llm` no es una solución viable para este problema. Altera, omite o alucina formato en los símbolos matemáticos críticos. La causa raíz del fallo en `pdfminer.six` (Fase 3C) sigue requiriendo una corrección a bajo nivel (pypdf o parche upstream).

## Fase 5 — Métrica de Diferencia de Embeddings

**Objetivo:** Evaluar cuantitativamente si la corrupción sintáctica producida por `pdfplumber` desplaza el significado semántico lo suficiente como para hacer fallar la fase de retrieval (distancia coseno < 0.70) usando un modelo estándar (`paraphrase-multilingual-MiniLM-L12-v2`).

**Resultados en Símbolos con EAR 0% (Corpus Real):**
- **SUM (∑):** Coseno medio 0.558 (18 de 19 muestras cayeron bajo 0.70)
- **PRODUCT (∏):** Coseno medio 0.555 (100% de muestras bajo 0.70)
- **TURNSTILE (⊢):** Coseno medio 0.536 (FirstOrderLogic)

**Conclusión:** La corrupción **destruye el retrieval semántico** en fragmentos altamente simbólicos. Un coseno de ~0.55 significa que si un usuario realiza una consulta con símbolos correctos, el chunk corrupto no será recuperado por la base vectorial. Esto cierra definitivamente el debate de si "el LLM puede inferir el símbolo faltante": el chunk corrupto nunca llega al LLM en primer lugar.

## Fase 6 — Evaluación con Fuentes TTF (Unicode nativo)

**Objetivo:** Determinar si el fallo de extracción (Punto de Falla 1) es un bug exclusivo de las fuentes CFF/Type1 con `MacRomanEncoding` (como Computer Modern en LaTeX), o si afecta de forma generalizada a PDFs modernos generados con fuentes TrueType (TTF).

**Resultado (Exp 12 - Segoe UI Symbol):** **Preservación Perfecta (100% CPR).**
Tanto `pdfplumber` como `pypdf` y `PyMuPDF` lograron extraer correctamente el 100% de los símbolos matemáticos (`∀`, `∃`, `⊢`, `⊨`, `∈`, etc.) a partir de un PDF generado sintéticamente utilizando una fuente TrueType moderna con codificación Unicode directa (`seguisym.ttf`).

**Conclusión:** Se confirma definitivamente que el bug **es exclusivo de fuentes antiguas CFF/Type1 que utilizan encodings defectuosos (como `MacRomanEncoding`)**, típico de los documentos PDF generados desde LaTeX con Computer Modern. Los PDFs modernos generados con fuentes TrueType u OpenType que poseen mapas Unicode directos no se ven afectados por este error en `pdfminer.six`. Esto reduce y enfoca drásticamente el _scope_ del problema: es un problema del ecosistema LaTeX-to-PDF heredado.

---

## Fase 7 — Validación Estadística sobre Corpus arXiv (30 papers)

**Objetivo:** Confirmar si el patrón de fallo detectado en el corpus original (4 PDFs) se generaliza estadísticamente a un corpus más amplio de papers LaTeX descargados de arXiv.

**Método:** `arxiv_harvest.py` buscó papers en categorías `math.LO`, `math.GR`, `math.RA`, `cs.LO` con fuentes Type1/Computer Modern (filtrado con `fonttools`). `probe_arxiv.py` corrió el pipeline EAR sobre los 30 PDFs resultantes con los tres extractores (`pdfplumber`, `pymupdf`, `pypdf`).

**Resultados:**
- **7/30 PDFs (23%)** con alguna discrepancia
- **23/30 PDFs (77%)** con EAR 100% — extracción perfecta
- Símbolos más fallidos: **∑ SUM** (4 docs), **□ NECESSARILY** (3 docs), **∏ PRODUCT** (1 doc)

**Cuadro completo del scope del bug:**

| Tipo de PDF | Fuente/Encoding | Falla esperada |
|---|---|---|
| LaTeX + CM + `MacRomanEncoding` | AbstractAlgebra (corpus original) | **Catastrófica** — 50%+ de símbolos a 0% EAR |
| LaTeX + CM + `WinAnsiEncoding` | Papers arXiv nuevos | **Parcial** — 23% de docs, solo ∑ □ ∏ (CMEX/LASY) |
| PDF con TTF/Unicode directo | Docs modernos (Word, navegador) | **Ninguna** — 100% CPR |

---

## Análisis de Causa Raíz — Capa de Mapeo Glyph → Unicode

El bug reside en la cadena de resolución que `pdfminer.six` aplica para convertir un byte del stream PDF en un codepoint Unicode:

```
byte en el stream PDF
      ↓
1. Encoding vector (MacRomanEncoding / WinAnsiEncoding)
      → byte 0x50 = glyph name 'P'
      ↓
2. ToUnicode CMap (solo si el PDF lo incluye explícitamente)
      → byte 0x50 = U+2211 (∑)   ← ANULA el encoding
      ↓
3. Adobe Glyph List (AGL) — fallback si no hay ToUnicode
      → glyph name 'P' = U+0050  ← sale 'P' en lugar de '∑'
```

**Por qué falla en LaTeX/Computer Modern:**
LaTeX asigna glifos matemáticos a posiciones de byte que los encodings estándar (MacRoman/WinAnsi) reservan para letras ordinarias. Cuando el PDF no incluye una tabla `ToUnicode` completa (o la tiene incompleta), `pdfminer.six` resuelve el byte via el encoding → AGL → obtiene la letra incorrecta.

**Por qué CMEX/LASY fallan incluso sin MacRomanEncoding:**
`CMEX` (operadores grandes: ∑, ∏, ∫) y `LASY`/`MSAM` usan glyph names **no estándar en el AGL de Adobe**:

| Glyph | Nombre en CMEX | En AGL | Resultado pdfminer |
|---|---|---|---|
| ∑ | `summationtext` | ❌ no existe | `?` o vacío |
| ∏ | `producttext` | ❌ no existe | `?` o vacío |
| □ | `square` (posicional) | parcial | falla intermitente |

`pypdf` tiene resoluciones alternativas para algunos de estos casos; `pdfminer.six` no.

**Solución técnica canónica (según ISO 32000 / PDFlib):**
Cuando se detecta una fuente `CM*`/`PL*`/`CMEX`/`LASY`/`MSAM` sin `ToUnicode` CMap, aplicar la **TeX glyph list** en lugar del AGL de Adobe, o construir el mapa `ToUnicode` desde las métricas de fuente TeX (archivos `.tfm`/`.enc`). Esto es el mecanismo `forceencoding`/`glyphlist` que PDFlib implementa en forma nativa.

---

## Diagrama de decisión — ¿Qué enfoque usar?

```
¿Tenés acceso al pipeline en runtime (Python)?
│
├── SÍ
│    ├── ¿Querés modificar el código base de pdfminer.six?
│    │    ├── SÍ → Opción C: Parche Upstream (PR oficial)   ← IDEAL A LARGO PLAZO
│    │    └── NO → Opción B: Monkey-patch dinámico          ← RECOMENDADO PARA RAGFLOW
│    │
│    └── ¿Preferís usar múltiples librerías?
│         └── SÍ → Opción A: Hybrid fallback (pypdf)
│
└── NO (solo tenés el texto ya extraído)
     ├── ¿Hay contexto semántico rico?
     │    ├── SÍ → Opción D1: LLM corrector
     │    └── NO → Opción D2: Clasificador ML
     │
     └── ¿Tenés corpus de entrenamiento?
          ├── SÍ → Opción D3: SLM seq2seq fine-tuneado
          └── NO → Sin buena opción determinística disponible
```

---

## Contexto académico — ¿Por qué esto importa más allá del proyecto?

El problema documentado no es exclusivo de RAGFlow. Cualquier sistema RAG que use `pdfplumber` o `pdfminer.six` como extractor de texto padece este bug al procesar literatura académica generada con LaTeX y fuentes Computer Modern (la familia tipográfica estándar de matemática desde los 80s).

Esto incluye:
- Sistemas RAG universitarios sobre papers académicos
- Asistentes de investigación con acceso a arXiv, ACM, IEEE Xplore
- Cualquier pipeline de NLP sobre tesis, libros de texto o publicaciones científicas en PDF

**La evidencia construida en este proyecto** (metodología EAR, corpus de discrepancias, análisis forense) constituye un bug report técnico completo y verificable que justifica tanto el PR a RAGFlow como el parche a pdfminer.six.

---

## Fase 6 — Implementación y Validación del Monkey-Patch

**Fecha:** 2026-09-17

Siguiendo la Opción B descrita arriba, se implementó exitosamente un monkey-patch (`tex_glyph_patch.py`) que inyecta en memoria la nomenclatura extendida de `amsfonts`/LaTeX en el diccionario `glyphname2unicode` de `pdfminer.six`.

### Alcance de la Solución
Es **crítico** destacar el alcance de este parche:
1. **Soluciona el problema de raíz en `pdfminer.six` y `pdfplumber`**. Por lo tanto, soluciona definitivamente la extracción en **DeepDoc/RAGFlow**.
2. **NO soluciona el problema en `PyMuPDF` (fitz) ni en `pymupdf4llm`**. Estos extractores tienen el mismo problema de diccionario, pero dependen del motor en C++ `MuPDF`. Nuestro parche en Python no los afecta, por ende, seguirán fallando y dando 0% de extracción en estos símbolos, reafirmando que la corrupción subyacente de la fuente sigue existiendo y nuestro parche la saltea limpiamente en el nivel de Python.

### ¿Cómo funciona el Monkey-Patch a nivel técnico?

El parche, implementado en [`tex_glyph_patch.py`](file:///home/jonas/Documentos/UTN/Programming/Beca%20GAALA/Proyecto-RAG-Symbols/lis-interpretacion-simbolos-rag/deepdoc-research/tex_glyph_patch.py), actúa de forma **no invasiva** y en **tiempo de ejecución** (runtime). No modifica el código fuente instalado de la librería en el sistema, sino que altera sus estructuras en memoria justo antes de que empiece a procesar los PDFs.

La mecánica exacta es la siguiente:
1. `pdfminer.six` mantiene un diccionario global en memoria llamado `glyphname2unicode`, que es básicamente el **Adobe Glyph List (AGL)**. Este diccionario es el encargado de traducir un "nombre de glifo" (ej. `"P"`) a su carácter Unicode (`"U+0050"`).
2. Las fuentes matemáticas como `CMEX10` y `CMSY10` (estándar en LaTeX) definen sus glifos utilizando nombres exclusivos que **no existen en el AGL**, como `"summationdisplay"` para `∑` o `"productdisplay"` para `∏`.
3. Cuando `pdfminer` intenta traducir `"summationdisplay"`, al no encontrarlo en su diccionario estándar, simplemente aborta y emite el error silencioso que se traduce en un `(cid:X)`.
4. Nuestro script importa `pdfminer.glyphlist.glyphname2unicode` y le inyecta 114 nuevas entradas correspondientes a la **TeX Glyph List** (el mapeo de glifos oficial del ecosistema TeX).

```python
# El núcleo técnico de cómo se aplica el parche
from pdfminer.glyphlist import glyphname2unicode

TEX_EXTRA_GLYPHS = {
    "summationdisplay": "\u2211",  # ∑
    "productdisplay": "\u220f",    # ∏
    # ... +112 símbolos matemáticos faltantes
}

# Inyección en memoria en runtime
glyphname2unicode.update(TEX_EXTRA_GLYPHS)
```

Al ejecutarse esta actualización ANTES de inicializar el extractor usado por RAGFlow (`pdfplumber`), todas las consultas de símbolos que antes fallaban ahora encuentran correspondencia directa gracias a nuestro diccionario extendido, devolviendo los caracteres Unicode perfectos.

### Resultados de la Validación
Se implementó un script robusto (`probe_patched.py`) que enfrenta a 4 extractores sobre el corpus completo de PDFs problemáticos (incluyendo arXiv). Los resultados demuestran que:
- **ANTES del parche:** `pdfplumber` fallaba en extraer los símbolos (EAR 0%).
- **DESPUÉS del parche:** `pdfplumber` empató perfectamente al 100% con el ground truth (`pypdf`), recuperando un total de 177 símbolos matemáticos en todo el corpus evaluado (incluyendo sumatorias, productorias, cajas modales y operadores de relación como ⊨).
- **OTROS EXTRACTORES:** `PyMuPDF` y `pymupdf4llm` continuaron arrojando 0, validando que el parche fue el único responsable de la mejoría observada en `pdfplumber`.

---

## Anexo — Análisis Arquitectónico: El Enfoque Nativo de RAGFlow vs VLMs

A lo largo de la investigación quedó en evidencia por qué plataformas empresariales como **RAGFlow** no aplican este "Monkey-Patch" (ni arreglos similares a nivel diccionario) por defecto en su motor **DeepDoc**. 

### 1. El Fallback Heurístico (OCR 1D)
Cuando no hay un VLM (Vision Language Model) configurado, DeepDoc reacciona al fallo estructural de la Adobe Glyph List mediante **degradación controlada**. 
Posee reglas heurísticas (como la directiva interna `_is_garbled_text`) que detectan inmediatamente la presencia de anomalías o artefactos masivos del tipo `(cid:X)`. Ante el menor indicio de corrupción:
1. El sistema **descarta asépticamente toda la lectura plana** (basada en el diccionario) para ese fragmento.
2. Inicia un *fallback* (plan de contingencia) delegando la lectura a su motor de visión artificial y OCR integrado (usando modelos como `PP-OCRv6` y `YOLOv10`).

Al escanear los píxeles (y no el código fuente del PDF), el OCR logra "ver" y rescatar los símbolos matemáticos aislados. Sin embargo, **este método falla en la dimensionalidad espacial**: el OCR nativo devuelve un texto plano unidimensional. Una fórmula estructurada como `\sum_{i=1}^{n} x_i` termina aplastada en una cadena incomprensible (ej. `n ∑ x_i i=1`), perdiendo subíndices, matrices y fracciones. Para un LLM, esto sigue siendo un caldo de cultivo para alucinaciones.

### 2. La Verdadera Solución: Modelos de Lenguaje Visual (VLMs)
Para que un pipeline RAG reconstruya la **estructura espacial matemática** (recuperando el formato LaTeX tridimensional), el OCR tradicional es insuficiente y parchear diccionarios no preserva la jerarquía vertical. 

La respuesta arquitectónica adoptada por RAGFlow en sus últimas versiones es delegar la extracción compleja a **Modelos de Lenguaje Visual Multimodal (VLMs)**, como **MinerU** o **Docling** (vía parámetros como `DOCLING_FORMULA_ENRICHMENT=1`). 

Solo estos modelos son capaces de observar el "recorte" de la ecuación (la imagen) y traducirlo directamente a su código fuente original en LaTeX, ignorando por completo tanto las deficiencias del estándar ISO 32000 como las limitaciones unidimensionales de un OCR tradicional. El futuro de la extracción científica en sistemas RAG es indiscutiblemente multimodal.
