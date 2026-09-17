# Pipeline de Evaluación RAG: Análisis de Terquedad Semántica e Instruction Hierarchy

El siguiente documento detalla la arquitectura del pipeline de evaluación experimental, las estrategias de mitigación implementadas mediante *prompt engineering* y la infraestructura subyacente. 

---

## 1. Infraestructura y Modelos Evaluados

El marco de experimentación utiliza una arquitectura de inferencia desacoplada (Patrón Adaptador) que permite transicionar sin fricción entre entornos de desarrollo locales y hardware dedicado.

### Motores de Inferencia (Backends)
El sistema abstrae las llamadas a los LLMs a través de la interfaz `LLMBackend`, orquestando dos motores principales:
1. **`llama_cpp` (Local):** Ejecuta un servidor en C++ (`llama-server`) optimizado para baja latencia. Permite la carga de modelos cuantizados (GGUF `Q4_K_M`) e implementa un *streaming adaptativo* capaz de capturar e independizar los tokens de razonamiento interno del modelo (`delta.reasoning_content`) respecto a la respuesta final evaluable.
2. **`ollama` (Distribuido):** Instancia externa conectada vía API REST (puerto 11434), orientada al despliegue en entornos con mayor capacidad de cómputo (GPU).

### Modelos Seleccionados
Se analizan modelos compactos (2B a 9B de parámetros) para evaluar el impacto del conocimiento paramétrico frente al contexto provisto:
* **Familia Qwen 3.5 (2B, 4B, 9B):** Modelos *Instruction-Tuned* con alta capacidad deductiva y tendencia nativa al razonamiento extendido (*Extended Thinking*).
* **Gemma 4B:** Proveedor base de Google, utilizado como grupo de contraste dada su arquitectura orientada a la respuesta directa sin fases explícitas de pensamiento interno.

---

## 2. Instruction Hierarchy frente a la Terquedad Semántica

El fenómeno de "Terquedad Semántica" ocurre cuando el conocimiento paramétrico de un LLM sobre un símbolo específico (ej. "□" o "⊂") posee mayor peso estadístico que el contexto inyectado mediante RAG, particularmente si la ingesta del texto resulta en una corrupción de formato (ej. Mojibake UTF-8).

Para contrarrestar esto, se implementaron **Estrategias de Prompting** progresivas que evalúan el concepto de *Instruction Hierarchy* (Jerarquía de Instrucciones):

| Estrategia | Canal / Rol API | Implementación y Objetivo |
| :--- | :--- | :--- |
| **`plain`** | `user` | **Línea base (Baseline):** Se provee exclusivamente el texto corrupto y la pregunta, sin mitigación alguna, para cuantificar el grado de fallo base. |
| **`table_plain`** | `user` | **Tabla de Contexto:** Se incluye una tabla de notación en el prompt, evaluando la capacidad del modelo para inferir las equivalencias sin instrucciones coercitivas. |
| **`i1_a`** | `user` | **Énfasis Visual:** Se enmarca la tabla con advertencias explícitas de criticidad. |
| **`i1_b`** | `user` | **Override Semántico:** Se exige explícitamente al modelo descartar cualquier significado aprendido previamente asociado a los símbolos del dominio. |
| **`i1_c`** | `user` | **Rol Simulado:** Emula el canal de sistema insertando etiquetas como `[SYSTEM INSTRUCTION]` dentro del mensaje del usuario. |
| **`i1_d`** | `system` + `user` | **Instruction Hierarchy Real:** Desacopla técnicamente la instrucción: las definiciones y reglas de prioridad absoluta se inyectan en el canal de máxima jerarquía (`role: "system"`), dejando exclusivamente el texto y la pregunta en el canal del usuario (`role: "user"`). Es la prueba definitiva para forzar al modelo a acatar el RAG sobre su entrenamiento previo. |

---

## 3. Flujo Automático del Pipeline Experimental

El módulo `main.py` orquesta la ejecución íntegra del experimento en una matriz exhaustiva de 56 evaluaciones (7 fragmentos $\times$ 8 condiciones), dividida en cuatro etapas secuenciales:

1. **Pre-procesamiento (Generación de Variantes):** 
   El módulo `corruption.py` toma los fragmentos limpios del corpus y genera, para cada iteración, versiones que simulan la pérdida de codificación (Mojibake UTF-8) o transformaciones a sintaxis LaTeX.
2. **Construcción Dinámica del Prompt:** 
   El módulo `prompt_strategies` recibe el texto degradado y ensambla el prompt final según la estrategia correspondiente, distribuyendo el contexto entre los canales `user` y `system` según corresponda.
3. **Inferencia Asíncrona (Streaming):** 
   Se invoca al backend configurado. El sistema intercepta el flujo SSE en tiempo real, diferenciando visualmente la etapa de razonamiento del LLM de su resolución final, y registrando la latencia total del proceso en milisegundos.
4. **Evaluación y Persistencia:** 
   El módulo `evaluator.py` analiza la respuesta final del LLM contrastándola contra diccionarios semánticos de éxito (`expected`) y fracaso (`forbidden`). Finalmente, `report.py` consolida los 56 registros en tres formatos de persistencia (`.json`, `.txt`, `.md`) para su posterior análisis estadístico y revisión cualitativa.
