# docs/ — Documentación de la Investigación

Carpeta central de documentación del proyecto **RAG Symbol Experiment**.

> Para instrucciones de instalación y ejecución, ver el [`README.md`](../README.md) en la raíz.
> Para el historial de cambios de código, ver [`CHANGELOG.md`](../CHANGELOG.md).
> Para tareas pendientes, ver [`TODO.md`](../TODO.md).

---

## Índice

### 📅 Narrativa e historia

| Archivo | Descripción |
|---|---|
| [`timeline.md`](timeline.md) | **Empezá acá.** Cronología de los 9 experimentos — qué se preguntó, cómo se probó, qué se encontró y a qué llevó cada uno |

### 📐 Marco teórico y diseño

| Archivo | Descripción |
|---|---|
| [`investigacion.md`](investigacion.md) | Documento de investigación completo: motivación, marco teórico, diseño experimental, hipótesis, hoja de ruta |
| [`estrategias_prompt.md`](estrategias_prompt.md) | Ideación de las estrategias de Instruction Hierarchy (I1-A a I1-D) |

### 📊 Resultados y análisis

| Archivo | Descripción |
|---|---|
| [`fase1_analisis.md`](fase1_analisis.md) | Análisis metodológico de Fase 1: hallazgos, anomalías, conclusiones e implicaciones para Fase 2 |
| [`fase1_resultados.md`](fase1_resultados.md) | Tabla detallada de respuestas por fragmento, condición y modelo (1.7B vs 4B) |
| [`instruccion_hierarchy.md`](instruccion_hierarchy.md) | Análisis cualitativo exhaustivo de Instruction Hierarchy: Qwen3.5-2B vs Gemma-4B |

### ⚙️ Setup y configuración

| Archivo | Descripción |
|---|---|
| [`ragflow_setup.md`](ragflow_setup.md) | Guía paso a paso del setup híbrido RAGFlow: LLM en Kaggle via Ngrok + embedding local Ollama |

### 🎤 Material de presentación

| Archivo | Descripción |
|---|---|
| [`presentacion/outline.md`](presentacion/outline.md) | Estructura de slides: bloques temáticos y contenido por slide |
| [`presentacion/script.md`](presentacion/script.md) | Script de lo que decir en cada slide (~6 min) |
| [`presentacion/pipeline_y_estrategias.md`](presentacion/pipeline_y_estrategias.md) | Descripción técnica del pipeline experimental y estrategias de prompting |

### 🗄️ Archivo (histórico)

| Archivo | Descripción |
|---|---|
| [`archivo/contexto-experimento.md`](archivo/contexto-experimento.md) | Diario de diseño del experimento original (corpus de 8 fragmentos, v1.0). Reemplazado por `investigacion.md`. |
| [`archivo/manual_analysis.txt`](archivo/manual_analysis.txt) | Borrador de análisis manual en texto plano |

---

## ¿Por dónde empezar?

- **Si sos nuevo al proyecto** → [`timeline.md`](timeline.md) da el panorama completo en orden cronológico
- **Si querés entender el diseño teórico** → [`investigacion.md`](investigacion.md)
- **Si buscás resultados específicos** → [`fase1_resultados.md`](fase1_resultados.md)
- **Si querés levantar el entorno** → [`../README.md`](../README.md)
- **Si buscás los hallazgos de DeepDoc** → [`../deepdoc-research/evidencias.md`](../deepdoc-research/evidencias.md)
