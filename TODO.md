# TODO — RAG Symbol Vulnerabilities

Formato: `[ ]` pendiente · `[/]` en progreso · `[x]` completado

---

## deepdoc-research — Próximos experimentos

- [ ] **pymupdf4llm** — Evaluar si la salida Markdown de `pymupdf4llm` (PyMuPDF → Markdown estructurado para LLMs) preserva mejor los símbolos matemáticos que pdfplumber. Comparar EAR sobre el corpus real.

- [x] **Métrica: diferencia de embeddings** — Exp 11: Coseno ~0.55 demuestra destrucción semántica real en el espacio vectorial debido a la corrupción.

- [x] **Probar con otras codificaciones** — Exp 12 y Exp 13: Se demostró que el bug solo afecta a fuentes Type1/LaTeX (CM*/LASY). TTF/Unicode directo funciona bien. También se probó que no depende solo de MacRomanEncoding: el bug está en la falta de TeX Glyph List en el AGL de pdfminer.six.

- [ ] **Probar con RAGFlow ya configurado** — Validar los hallazgos end-to-end sobre el RAGFlow real (con el setup Ollama + Kaggle documentado en `ragflow_setup.md`). Subir los PDFs del corpus, hacer queries sobre los símbolos críticos y documentar si las respuestas del LLM reflejan la corrupción detectada en Fase 2/3.

---

## Implementación — Solución Técnica (Línea A)

**Ruta elegida:** Monkey-patch local para validar → Fork de `pdfminer.six` → Redirigir dependencia en RAGFlow → PR upstream opcional.
**Fuente para la tabla:** Apache PDFBox `additional.txt` ya tiene los mapeos TeX necesarios (`summationtext`, `producttext`, `logicalanddisplay`, etc.).

- [ ] **[PASO 1] Monkey-patch de validación** — Implementar `deepdoc-research/tex_glyph_patch.py` inyectando la TeX Glyph List (fuente: PDFBox `additional.txt`) en `pdfminer.glyphlist.glyphname2unicode` en tiempo de ejecución. Correr sobre los 7 papers arXiv con discrepancias: si EAR sube a 100%, el fix está validado.
- [ ] **[PASO 2] Fork de `pdfminer.six`** — Forkear [`pdfminer/pdfminer.six`](https://github.com/pdfminer/pdfminer.six), agregar los mapeos TeX a `pdfminer/glyphlist.py` en una branch `fix-tex-glyph-list`.
- [ ] **[PASO 3] Redirigir dependencia en RAGFlow** — En `requirements.txt` del entorno RAGFlow reemplazar `pdfminer.six==X.Y` por `pdfminer.six @ git+https://github.com/TuUser/pdfminer.six@fix-tex-glyph-list`. Aplicar en el servidor SSH disponible.
- [ ] **[PASO 4] Validar en RAGFlow real** — Con el parche activo en el server, subir los PDFs del corpus con LaTeX y corroborar que los símbolos ∑ ∏ □ se preservan en el texto extraído por DeepDoc.
- [ ] **[PASO 5] PR upstream a pdfminer.six** — Enviar el arreglo con tests y benchmark EAR como evidencia. Referenciable contra el trabajo de PR #1213 (CMap types 6/10/12, fusionado en release 20260107).
- [ ] **Buscar PRs abiertas equivalentes** — Code search en GitHub: `"summationtext" "pdfminer"`, `"producttext" "glyphname2unicode"`. Si existe un PR previo, contribuir sobre él en vez de crear otro.

---

## Investigación exploratoria

- [ ] **SLM Seq2Seq** — Experimento con T5/BART fine-tuneado sobre pares (texto pdfplumber corrupto, texto pypdf limpio) del corpus. Evaluar con CER como métrica.
