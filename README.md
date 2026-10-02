# LIS - Interpretación de Símbolos en RAG

> Repositorio de investigación sobre la degradación semántica en la interpretación de caracteres matemáticos y símbolos Unicode en sistemas Retrieval-Augmented Generation (RAG).

Este proyecto surge al descubrir que los pipelines estándar de Ingestion RAG (como los utilizados en sistemas de producción) sufren de **corrupción silenciosa de símbolos matemáticos**. Específicamente, operadores formales (como `∑`, `∏`, `□`, `⊢`) suelen desaparecer o mutar en secuencias Unicode erróneas durante la etapa de extracción del texto desde archivos PDF generados vía LaTeX.

## 🚀 Hallazgos Principales

1. **La Corrupción Destruye el Retrieval:** Si un operador crítico (`∑`) desaparece durante el OCR/Parsing, el embedding vectorial de la ecuación queda truncado. Documentamos que fragmentos afectados sufren caídas severas de similitud de Coseno (hasta `~0.55`), volviéndose **invisibles para el retrieval**.
2. **Terquedad Semántica de los LLMs:** Aún cuando se logra recuperar un fragmento corrupto e inyectarle una tabla de traducción en contexto, los LLMs pequeños (< 4B parámetros) tienden a ignorar el contexto (Over-Alignment) y responden erróneamente asumiendo conocimientos de su preentrenamiento.
3. **Causa Raíz Determinística:** Aislando el pipeline de DeepDoc, descubrimos que el bug reside en la capa de parsing base de Python (`pdfminer.six`). Los PDFs compilados con LaTeX usando fuentes CMEX10/LASY (Type 1, MacRomanEncoding) carecen de un CMap ToUnicode interno. El parser falla silenciosamente al buscar los nombres de los glifos de TeX (ej: `summationtext`) en la Adobe Glyph List estándar.

## 🛠️ Solución Implementada (Fork de pdfminer)

La solución técnica no reside en cambiar de LLM, sino en parchear el parser OCR para que entienda las fuentes de TeX.
Publicamos un fix oficial que inyecta la lista de glifos faltante:

- **Repositorio parcheado:** [`Jyiro/pdfminer-lis`](https://github.com/Jyiro/pdfminer-lis)
- Se resolvieron el 100% de los fallos encontrados en un corpus de validación compuesto por 30 papers académicos extraídos de arXiv.
- Instrucciones de despliegue para RAGFlow: Ver [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

---

## 📂 Estructura del Repositorio

El repositorio se ha organizado en dos ramas de experimentación:

* **`experiments/`**: Contiene todos los scripts de prueba de LLMs locales (Fase 1 y Fase 2). Aquí se encuentran scripts como `rebuild_experiment.py` o `echo_experiment.py` diseñados para auditar la "Terquedad Semántica" y fidelidad de los modelos de lenguaje usando Llama.cpp y Ollama.
* **`deepdoc-research/`**: Contiene las herramientas forenses diseñadas para analizar la extracción desde PDFs (Fase 3). Scripts para comparar empíricamente la salida de extractores líderes (`pdfplumber`, `PyMuPDF`, `pypdf`) y determinar el punto de fallo (`probe_arxiv_patched.py`).
* **`results/`**: Directorio de evidencia que almacena los resúmenes y JSONs de los benchmarkings.
* **`docs/`**: Narrativa completa del proceso, incluyendo `timeline.md` donde se documentan todos los experimentos de investigación en orden cronológico.

## 📝 Reproducción Local

Debido a restricciones de copyright, los PDFs reales provenientes de arXiv que se utilizaron como corpus no se distribuyen junto a este repositorio de GitHub. Para reconstruir el corpus de pruebas y ejecutar las herramientas forenses:

1. Ejecuta el entorno virtual.
2. Navega a `deepdoc-research/`
3. Ejecuta `python arxiv_harvest.py` para descargar automáticamente los documentos fuente de prueba e iniciar el pipeline.

## Roadmap 

Los próximos pasos y pendientes de desarrollo están documentados en [`ROADMAP.md`](ROADMAP.md).
