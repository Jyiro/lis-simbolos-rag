# LIS - Interpretación de Símbolos en Sistemas RAG

Repositorio de investigación sobre la degradación semántica de caracteres matemáticos y símbolos Unicode en las etapas de extracción de sistemas Retrieval-Augmented Generation (RAG).

Este proyecto aborda la problemática de la omisión y alteración de operadores formales (ej. `∑`, `∏`, `□`, `⊢`) durante el procesamiento inicial de documentos PDF generados vía LaTeX, y su impacto en las capacidades de recuperación y generación del sistema.

## 1. Hallazgos de la Investigación

1. **Impacto en la Recuperación Vectorial:** La omisión de operadores críticos durante el proceso de extracción (OCR/Parsing) altera significativamente la representación vectorial de las expresiones matemáticas. Se documentaron reducciones severas en la similitud del coseno (hasta `~0.55`) para los fragmentos afectados, impidiendo su correcta recuperación.
2. **Dependencia de Contexto en Modelos de Lenguaje:** Durante la inyección de tablas de corrección en contexto, se observó que modelos de lenguaje de menor escala (< 4B parámetros) presentan un sesgo hacia su conocimiento preentrenado ("Over-Alignment"). Esto los lleva a desestimar las correcciones provistas en el prompt, dificultando la mitigación del error en etapas posteriores.
3. **Análisis de Causa Raíz en el Parser:** Al examinar el proceso de extracción de texto (`pdfplumber` / `pdfminer.six`), se determinó que la falla se origina en documentos LaTeX cuyas fuentes (CMEX10/LASY, Type 1) utilizan `MacRomanEncoding` sin un diccionario `ToUnicode` embebido. El parser omite los caracteres al no encontrar correspondencia para los nombres de glifos TeX (ej: `summationtext`) en la especificación estándar (Adobe Glyph List).

## 2. Solución Técnica

Para resolver la inconsistencia en la extracción sin incurrir en costos computacionales adicionales (como el uso de OCR profundo), se desarrolló una extensión para el diccionario de glifos del parser base de Python.

- **Repositorio modificado:** [`Jyiro/pdfminer-lis`](https://github.com/Jyiro/pdfminer-lis)
- El parche integra las equivalencias de la especificación TeX, logrando una tasa de recuperación del 100% sobre un corpus de validación de 30 documentos académicos de arXiv.
- Para instrucciones de implementación en entornos de producción (ej. RAGFlow), consulte [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## 3. Arquitectura del Repositorio

La estructura del código refleja las distintas fases de la investigación:

- **`llm_evaluation/`**: Entorno de experimentación para evaluar las inferencias de los modelos de lenguaje (Llama.cpp, Ollama) frente a texto sintácticamente degradado y su capacidad de obedecer correcciones en contexto.
- **`parser_analysis/`**: Herramientas de evaluación comparativa para librerías de extracción de PDF (`pdfplumber`, `PyMuPDF`, `pypdf`). Incluye los scripts de diagnóstico para determinar la causalidad de pérdida de caracteres a nivel de CMap.
- **`results/`**: Datos empíricos, matrices de resultados (JSON) y reportes generados a lo largo de las evaluaciones.
- **`docs/`**: Bitácora cronológica del proyecto (`timeline.md`) y marcos teóricos.

## 4. Reproducibilidad

Por regulaciones de derechos de autor, el repositorio no incluye los documentos PDF originales utilizados en el corpus de evaluación empírica. Para reconstruir el corpus y ejecutar las validaciones localmente:

1. Active el entorno virtual del proyecto.
2. Acceda al directorio `parser_analysis/`.
3. Ejecute `python arxiv_harvest.py`. Este proceso descargará dinámicamente los documentos necesarios desde arXiv e iniciará la batería de pruebas.

Para más detalles sobre los pasos a seguir o el estado de implementación, refiérase a [`ROADMAP.md`](ROADMAP.md).
