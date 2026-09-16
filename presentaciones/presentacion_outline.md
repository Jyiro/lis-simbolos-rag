# Outline de Presentación — RAG y Simbología Matemática

> **Objetivo de la presentación:** Mostrar el proceso de investigación desde la detección del problema en RAGFlow hasta la identificación de la causa raíz y las posibles soluciones.

---

## BLOQUE 1 — Contexto y Motivación

### Slide 1: El Problema Central
- **Contexto:** ¿Qué pasa cuando un sistema RAG procesa papers académicos con matemáticas complejas?
- **El Síntoma:** El usuario hace una consulta sobre una ecuación, y el LLM responde con información truncada o incorrecta.
- **Hipótesis:** El fallo no es una "alucinación" del LLM. El fallo ocurre mucho antes, en la capa de extracción de texto.

### Slide 2: El Stack Auditado (RAGFlow / DeepDoc)
- Breve introducción a RAGFlow (sistema RAG open source líder).
- El motor de procesamiento de PDFs: **DeepDoc**.
- **El flujo:** PDF → DeepDoc (Extracción) → Chunks → Embeddings → Vector Store → LLM.
- Aquí es donde enfocamos la lupa: en la extracción.

### Slide 3: Metodología (Simulación de DeepDoc)
- Limitación: RAGFlow completo requiere ~16GB de RAM.
- Solución: Aislar el parser subyacente. DeepDoc utiliza la librería `pdfplumber` (que a su vez usa `pdfminer.six`).
- Creamos un entorno de investigación autónomo reproduciendo este componente exacto, sin la sobrecarga del LLM.

---

## BLOQUE 2 — Pruebas Iniciales (El Baseline)

### Slide 4: Fase 1 - PDFs Sintéticos y la métrica CPR
- Generamos 6 PDFs por código (Python/ReportLab) en dominios como lógica, matemática y física.
- **Métrica usada:** CPR (Char Preservation Rate). Porcentaje de retención con un *ground truth* conocido.
- **Resultado:** 100% de éxito en todos los extractores probados (`pdfplumber`, `pypdf`, `PyMuPDF`).
- **Conclusión temprana:** El parser funciona perfecto en PDFs "ideales". El bug debe ser específico a cómo se codifican los papers académicos reales.

---

## BLOQUE 3 — El Corpus Real y el Descubrimiento

### Slide 5: Fase 2 - El Corpus Académico
- Seleccionamos 4 papers intensivos en matemáticas (ej. Álgebra Abstracta, Lógica de Primer Orden).
- **El estándar de facto:** Estos papers están generados con LaTeX, usando fuentes de la familia **Computer Modern** (el estándar desde los 80s).
- **La nueva métrica (EAR - Extractor Agreement Rate):** Ante la falta de *ground truth*, usamos el consenso entre 3 extractores distintos. Si no coinciden, hay una discrepancia.

### Slide 6: Los Números que Impactan
- Resultados de EAR en símbolos críticos:
  - `∑` (Sumatoria): pypdf ve 65. **pdfplumber ve 0 (EAR 0%)**.
  - `∏` (Productoria): pypdf ve 19. **pdfplumber ve 0 (EAR 0%)**.
  - `⊨` (Models): pypdf ve 2. **pdfplumber ve 0 (EAR 0%)**.
  - `⊢` (Turnstile): Discrepancias masivas entre extractores (EAR 33.8%).
- **El golpe de realidad:** DeepDoc es literalmente "ciego" a las sumatorias en estos documentos.

### Slide 7: La Magnitud Oculta
- El EAR inicial solo medía los símbolos de nuestro catálogo.
- Al hacer una auditoría profunda descubrimos **~2785 artefactos de error** solo en el paper de Álgebra Abstracta.
- La corrupción no solo afecta a símbolos raros; fuentes enteras del texto ordinario están comprometidas.

---

## BLOQUE 4 — Análisis Forense (Por qué y Cómo Falla)

### Slide 8: Fase 3A - ¿Qué pone el parser en lugar del símbolo?
- Alineación línea a línea entre una extracción exitosa y una fallida.
- **Taxonomía de la corrupción:**
  1. **Sustitución:** El símbolo se cambia in-situ (ej. `⊨` se convierte en un string literal `(cid:15)`).
  2. **Omisión:** El símbolo simplemente desaparece y la fórmula se rompe.
  3. **Artefacto disociado:** El símbolo desaparece, pero un código residual (ej. `(cid:9)`) aparece en otra línea.

### Slide 9: La Salvación está en la "Huella" (PUNTO CLAVE)
- Aunque la omisión y sustitución son catastróficas para el LLM, el hecho de que el parser emita el string **`(cid:X)`** (un Artefacto Residual) es fundamental.
- **No es un fallo silencioso:** El parser deja una *huella*.
- Ese `(cid:X)` es el ID interno del glifo. Con la información adecuada del diccionario del PDF original, podemos usar esta huella para **reconstruir determinísticamente** el símbolo perdido.

### Slide 10: Fase 3B - El problema secundario del Chunking
- Incluso cuando el símbolo sobrevive la extracción, el fragmentado (chunking) de RAGFlow (~2000 caracteres) hace estragos.
- ~24% de los símbolos `⊢` (Turnstile) quedaron aislados en chunks que no contenían el contexto semántico necesario para explicarlos.
- Una "doble pérdida" acumulativa.

### Slide 11: Fase 3C - La Causa Raíz
- El PDF contiene la respuesta: Las fuentes afectadas son tipo *CFF Type1* con codificación *MacRomanEncoding*.
- Pero el PDF también incluye un diccionario **ToUnicode CMap** que dice exactamente qué carácter es cada glifo.
- `pypdf` lee este diccionario. `pdfminer.six` (DeepDoc) **lo ignora y aplica MacRoman directamente**, fallando y escupiendo el `(cid:X)`.
- No es un problema de OCR, es un bug de priorización de diccionarios de fuentes.

---

## BLOQUE 5 — Opciones de Solución

### Slide 12: Dónde intervenir en el Pipeline
- Mostrar esquema: PDF → `pdf_parser.py` → **[PUNTO DE INTERVENCIÓN]** → Chunker.
- Hay que intervenir antes del chunking, cuando el PDF original y su contexto de fuentes aún están disponibles.

### Slide 13: Soluciones Determinísticas (Las más robustas)
- **Opción A: Hybrid Fallback (Recomendada a corto plazo)**
  - Detectar la "huella" (contar `(cid:X)` por página). Si supera un umbral, descartar esa página y re-extraerla con `pypdf`.
  - *Pros:* No invasivo, usa lo que ya funciona.
- **Opción B: Post-Procesador con Fonttools**
  - Usar la huella `(cid:X)` para buscar el símbolo en el diccionario usando otra librería.
  - *Contras:* Ambigüedad. El glifo `9` puede ser `∑` en una fuente, y la letra `A` en otra. Se pierde el contexto de qué fuente estaba activa.
- **Opción C: Parchear pdfminer.six (Ideal a largo plazo)**
  - Corregir el bug en la librería open source original para que respete el ToUnicode CMap.

### Slide 14: Soluciones Probabilísticas (ML / LLMs)
- ¿Qué pasa si no tenemos el PDF original (solo el texto corrupto)?
- **D1:** Usar un LLM para que adivine el símbolo por contexto (costoso, alucina).
- **D2:** Entrenar un Clasificador ML con el corpus de errores que generamos.
- **D3:** Fine-tuning de un Small Language Model (SLM) especializado en "des-corromper" texto matemático.

---

## BLOQUE 6 — Conclusiones y Próximos Pasos

### Slide 15: Hoja de Ruta
1. **Inmediato:** Implementar y validar el *Hybrid Fallback* como script independiente.
2. **Mediano Plazo:** Presentar un PR (Pull Request) a RAGFlow proponiendo este fallback, usando la métrica EAR como evidencia irrefutable del fallo.
3. **Largo Plazo:** Proponer el parche en la librería base (`pdfminer.six`), lo cual beneficia a todo el ecosistema de procesamiento de PDFs en Python (arXiv, IEEE, tesinas).
