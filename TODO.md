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

- [x] **Parche dinámico (Monkey-Patch) a pdfminer.six** — Implementar `deepdoc-research/tex_glyph_patch.py` inyectando la TeX Glyph List (CMEX/LASY) en `pdfminer.glyphlist` en tiempo de ejecución.
- [x] **Validación automatizada del parche** — Script `probe_patched.py` ejecutado validando que el EAR subió a 100% exitosamente frente a pypdf.
- [ ] **Probar el arreglo con la librería de RAGFlow** — Validar cómo se comporta la inyección del parche interactuando directamente con el código base de RAGFlow / DeepDoc en un entorno local.
- [ ] **Averiguar alternativas sin modificar RAGFlow** — Investigar si existe alguna configuración, variable de entorno o método de inyección externo que permita pasarle el parche a la instancia de RAGFlow sin alterar su código fuente nativo.
- [ ] **Forkear dependencias** — Evaluar la viabilidad de hacer un fork de `pdfminer.six` (y/o `pdfplumber`), aplicar el parche del diccionario ahí mismo, y hacer que el entorno virtual apunte a este fork.
- [ ] **PR upstream a pdfminer.six** — Enviar el arreglo canónico a la librería original para solucionarlo a nivel ecosistema Python (aunque sabemos que hay resistencia por parte de los mantenedores).
- [ ] **Buscar PRs abiertas** — Investigar en los repositorios de `pdfminer.six`, `pdfplumber` y `ragflow` si ya existe algún Pull Request abierto intentando proponer esta misma solución para el bug de la Adobe Glyph List.

---

## Investigación exploratoria

- [ ] **SLM Seq2Seq** — Experimento con T5/BART fine-tuneado sobre pares (texto pdfplumber corrupto, texto pypdf limpio) del corpus. Evaluar con CER como métrica.
