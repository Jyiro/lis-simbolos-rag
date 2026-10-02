# Fase 1: Análisis de Degeneración Semántica en Modelos Generativos RAG

Este documento describe la metodología, ejecución y resultados de la Fase 1 del experimento orientado a evaluar la robustez semántica de la etapa generativa en arquitecturas Retrieval-Augmented Generation (RAG) frente a perturbaciones de caracteres.

---

## 1. Diseño Experimental

### 1.1 Objetivo y Contexto Teórico

Las arquitecturas RAG presentan vulnerabilidades inherentes cuando procesan documentos con alta densidad de simbología matemática. La Fase 1 aísla la **capa final del flujo (Generación)**.
Se establece como premisa un escenario donde la etapa de recuperación (Retrieval) ha procesado y suministrado un fragmento con alteraciones sintácticas (debido a deficiencias en el motor OCR o en la decodificación) al Modelo de Lenguaje Grande (LLM).

Los objetivos específicos son:
1. Determinar la resiliencia del LLM para preservar la coherencia semántica frente a alteraciones en símbolos críticos.
2. Clasificar los modos de falla: divergencia explícita (el modelo rechaza la inferencia por falta de contexto) frente a divergencia silenciosa (el modelo genera aserciones lógicamente válidas pero matemáticamente inconsistentes).
3. Evaluar la eficacia de estrategias de mitigación en tiempo de inferencia, tales como la inyección de tablas de mapeo en el contexto o conversiones a formato LaTeX.

### 1.2 Estructura del Prompt

El experimento diseña un prompt que fuerza al LLM a depender estrictamente del contexto provisto (documento perturbado). 
Se divide en:

1. **Directiva de Aislamiento Contextual:** Instrucciones estrictas para anular el sesgo de preentrenamiento del modelo.
2. **Contexto Controlado:** Un texto base donde símbolos formales (`∑`, `⊢`, `∀`, etc.) han sido deliberadamente reemplazados por secuencias espurias (`(cid:10)`, `[ERR]`, o ruido Unicode).
3. **Pregunta de Extracción:** Una consulta determinística (Ej: "Según el texto, ¿qué significa (cid:10)?").

### 1.3 Corpus Sintético

Para esta fase inicial, se generó un corpus sintético de fragmentos matemáticos donde las relaciones símbolo-significado son inequívocas pero ficticias (ej. `[SÍMBOLO_A]` representa "Velocidad Angular" en lugar de `ω`), garantizando que el LLM no pueda resolver la tarea apelando a convenciones de su entrenamiento.

---

## 2. Ejecución y Métricas

La ejecución se realiza de manera automatizada utilizando la suite desarrollada en `llm_evaluation/`. Se evalúan iterativamente diferentes familias y escalas de modelos (ej. Llama, Qwen, Phi) contra el corpus.

### 2.1 Métricas de Evaluación (Fidelidad Contextual)

El desempeño de cada modelo se clasifica de acuerdo al alineamiento con el contexto distorsionado:

* **Adherencia Estricta (Éxito):** El modelo obedece la tabla de mapeo y responde utilizando el significado provisto en el prompt, ignorando la rareza del símbolo distorsionado.
* **Over-Alignment / Pre-training Bias (Fallo):** El modelo descarta el contexto suministrado e impone una respuesta basada en su entrenamiento general (ej. afirmar que `(cid:10)` es un error de decodificación en lugar de acatar la definición de la tabla en contexto).
* **Alucinación Silenciosa (Fallo Crítico):** El modelo deduce lógicamente sobre premisas inventadas que no existen en el contexto ni en su preentrenamiento, fabricando una respuesta plausible pero falsa.

---

## 3. Conclusiones Preliminares

Los resultados empíricos completos se encuentran documentados en `docs/fase1_resultados.md`. 
Las observaciones iniciales indican una correlación directa entre el tamaño parametral del modelo y su propensión al "Over-Alignment", donde los modelos compactos (<4B) tienden a ignorar las correcciones en contexto cuando se enfrentan a distorsiones severas, requiriendo estrategias de prompting más robustas para forzar la fidelidad semántica.
