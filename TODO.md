# TODO — RAG Symbol Vulnerabilities

Formato: `[ ]` pendiente · `[/]` en progreso · `[x]` completado

---

## deepdoc-research — Próximos experimentos

- [ ] **pymupdf4llm** — Evaluar si la salida Markdown de `pymupdf4llm` (PyMuPDF → Markdown estructurado para LLMs) preserva mejor los símbolos matemáticos que pdfplumber. Comparar EAR sobre el corpus real.

- [ ] **Métrica: diferencia de embeddings** — Para cada símbolo crítico, calcular la distancia coseno entre el embedding del chunk *correcto* (extraído con pypdf) y el chunk *corrupto* (extraído con pdfplumber). Cuantifica cuánto daño semántico real causa la corrupción en el espacio vectorial, no solo a nivel de caracteres.

- [ ] **Probar con RAGFlow ya configurado** — Validar los hallazgos end-to-end sobre el RAGFlow real (con el setup Ollama + Kaggle documentado en `ragflow_setup.md`). Subir los PDFs del corpus, hacer queries sobre los símbolos críticos y documentar si las respuestas del LLM reflejan la corrupción detectada en Fase 2/3.

- [ ] **Probar con otras codificaciones** — Expandir el corpus con PDFs que usen símbolos matemáticos en codificación Unicode directa (no vía fuentes LaTeX/CFF Type1). Verificar si el bug de pdfminer.six solo afecta a fuentes CFF con MacRomanEncoding o si hay otros casos de encoding conflictivo.

---

## Implementación — Soluciones

- [ ] **Hybrid fallback (Opción A)** — Script standalone `deepdoc-research/hybrid_fallback.py` que re-extrae con pypdf las páginas que superen el umbral de artefactos `(cid:X)`. Validar contra el corpus antes de proponer el PR a RAGFlow.

- [ ] **PR a RAGFlow** — Integrar el hybrid fallback en `deepdoc/parser/pdf_parser.py`. Incluir el benchmark EAR como evidencia técnica del bug.

- [ ] **PR a pdfminer.six** — Parche para que priorice ToUnicode CMap sobre `/Encoding` en fuentes CFF Type1 cuando fonttools está disponible.

---

## Investigación exploratoria

- [ ] **SLM Seq2Seq** — Experimento con T5/BART fine-tuneado sobre pares (texto pdfplumber corrupto, texto pypdf limpio) del corpus. Evaluar con CER como métrica.
