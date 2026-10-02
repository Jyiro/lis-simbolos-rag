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
- [x] **[PASO 2] Fork de `pdfminer.six`** — Fork publicado en [`Jyiro/pdfminer-lis`](https://github.com/Jyiro/pdfminer-lis). Parche integrado en `pdfminer/glyphlist.py` (62 entradas TeX). Tests: **43/43 pasan**. Commit: [`db4ddff`](https://github.com/Jyiro/pdfminer-lis/commit/db4ddff32b228e31562c3fe530dc7b0d55a01d56).
- [/] **[PASO 3] Redirigir dependencia en RAGFlow** — **BLOQUEADO** por problema de infraestructura en el servidor.

  **Diagnóstico del servidor (`ubuntu@128.201.239.161 -p 2022`):**
  - RAGFlow corre como contenedor Docker: `docker-ragflow-cpu-1` (imagen `infiniflow/ragflow:v0.26.0`)
  - El contenedor lleva semanas en **crashloop**: `exec ./entrypoint.sh: exec format error`
  - Causa: **incompatibilidad de arquitectura** — la imagen oficial fue compilada para `amd64` pero el servidor probablemente corre `arm64`
  - El parche de pdfminer **no puede aplicarse** mientras el contenedor no arranque

  **Cómo desbloquear (requiere coordinación con el equipo del servidor):**
  1. Confirmar arquitectura del server: `uname -m`
  2. Si es `arm64`: reconstruir la imagen desde el source en `~/ragflow` o usar `--platform linux/amd64` con emulación QEMU
  3. Alternativa: levantar RAGFlow localmente en tu máquina (arquitectura conocida, más control)

  **Una vez que el contenedor esté corriendo**, aplicar el parche es un comando:
  ```bash
  sudo docker exec -it docker-ragflow-cpu-1 \
    pip install git+https://github.com/Jyiro/pdfminer-lis@master
  sudo docker restart docker-ragflow-cpu-1
  ```

  > ⚠️ **Posible punto de fallo — compatibilidad de versiones**
  >
  > El fork está basado en la versión más reciente del upstream (`20260108`).
  > Si el contenedor tiene una versión muy anterior, pip puede traer dependencias
  > incompatibles. Fallback: copiar `tex_glyph_patch.py` al contenedor e importarlo
  > en `deepdoc/__init__.py` sin cambiar la versión instalada de pdfminer.six.

- [ ] **[PASO 4] Validar en RAGFlow real** — **BLOQUEADO** (depende del Paso 3). Una vez activo el parche, subir los PDFs del corpus LaTeX y verificar que ∑ ∏ □ aparecen en los chunks de DeepDoc.
- [ ] **[PASO 5 — opcional] PR upstream a pdfminer.six** — Enviar el arreglo con los 43 tests y el benchmark EAR (0/30 fallos) como evidencia. Referenciable contra PR #1213 (CMap types 6/10/12, fusionado en release 20260107).

---

## Investigación exploratoria

- [ ] **SLM Seq2Seq** — Experimento con T5/BART fine-tuneado sobre pares (texto pdfplumber corrupto, texto pypdf limpio) del corpus. Evaluar con CER como métrica.
