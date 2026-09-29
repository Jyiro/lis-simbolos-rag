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

- [x] **[PASO 1] Monkey-patch de validación** — `deepdoc-research/tex_glyph_patch.py` implementado y validado. Corpus arXiv: **0/30 fallos** (era 7/30). 19/30 papers con pdfplumber superando a pymupdf/pypdf (exclusivas confirmadas como verdaderos positivos). Refactorizado con `SAFE_MATH_OPERATORS` / `EXTENSIBLE_DELIMITERS`. Suite de 9 tests en `deepdoc-research/tests/test_tex_glyph_patch.py` — todos pasan.
- [/] **[PASO 2] Fork de `pdfminer.six`** — Fork clonado localmente en `deepdoc-research/pdfminer-fork/`. Parche integrado directamente en `pdfminer/glyphlist.py` (62 entradas TeX, con comentario de fuentes). Tests del fork en `tests/test_tex_glyphs.py` — **43/43 pasan**. Commit local listo (`db4ddff`).
  - **⏳ PENDIENTE (hacer vos):**
    1. Ir a https://github.com/pdfminer/pdfminer.six → click **Fork** → seleccionar tu cuenta
    2. Desde PowerShell en `deepdoc-research/pdfminer-fork/`:
       ```powershell
       git remote add myfork https://github.com/<tu-usuario>/pdfminer.six.git
       git push myfork master
       ```
- [ ] **[PASO 3] Redirigir dependencia en RAGFlow** — En el servidor SSH (`ubuntu@128.201.239.161 -p 2022`, clave `IAutn2026`) reemplazar `pdfminer.six` del entorno de DeepDoc por:
  ```bash
  pip install git+https://github.com/<tu-usuario>/pdfminer.six@master
  ```
  Verificar que los tests del fork pasen en el server.
- [ ] **[PASO 4] Validar en RAGFlow real** — Con el parche activo en el server, subir los PDFs del corpus con LaTeX y corroborar que los símbolos ∑ ∏ □ se preservan en el texto extraído por DeepDoc.
- [ ] **[PASO 5 — opcional] PR upstream a pdfminer.six** — Enviar el arreglo con los 43 tests y el benchmark EAR (0/30 fallos) como evidencia. Referenciable contra PR #1213 (CMap types 6/10/12, fusionado en release 20260107).

---

## Investigación exploratoria

- [ ] **SLM Seq2Seq** — Experimento con T5/BART fine-tuneado sobre pares (texto pdfplumber corrupto, texto pypdf limpio) del corpus. Evaluar con CER como métrica.
