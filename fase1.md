# Fase 1: Comprensión y Vulnerabilidad Generativa en RAG

Este documento detalla el diseño, la ejecución y los hallazgos de la Fase 1 del experimento sobre vulnerabilidades de pipelines RAG ante la corrupción de caracteres especiales.

---

## 1. Diseño Experimental

### 1.1 Objetivo y Contexto Teórico
El pipeline RAG tiene una vulnerabilidad estructural ante textos densos en simbología matemática o especial. La Fase 1 aísla la **capa final del pipeline (Generación)**. 
Asume que el retriever ya falló parcialmente al ingestar un documento corrupto (por problemas de OCR o codificación) y le pasa ese texto ruidoso (mojibake) al LLM. 

El objetivo es evaluar:
1. Si el LLM es capaz de comprender el documento cuando el símbolo crítico está corrupto.
2. Si el fallo es ruidoso (el modelo declara "no sé") o silencioso (el modelo alucina una respuesta lógica pero matemáticamente incorrecta).
3. Si estrategias de mitigación en tiempo de inferencia (proveer una tabla RAG de mapeo o usar LaTeX) logran restaurar la comprensión semántica.

### 1.2 Hipótesis
* **Hipótesis Principal:** El tipo de falla ante la corrupción varía sistemáticamente con la familiaridad del modelo con el símbolo. Para símbolos conocidos, la corrupción genera un **fallo silencioso** (CONFUNDIDO), donde el modelo usa el contexto para adivinar una respuesta errónea.
* **Hipótesis de Mitigación:** Proveer el contexto explícito del símbolo (Condición "Con Tabla") o normalizar la entrada (Condición "LaTeX") recuperará el rendimiento a niveles de la versión limpia.

### 1.3 Metodología
Se construyó un corpus de 12 fragmentos de texto (matemática, lógica, física, fonética) divididos en tres niveles de frecuencia estimada (Alta, Media, Baja). Cada fragmento fue diseñado de modo que el símbolo crítico sea la *única* pista semántica para responder la pregunta correctamente.

Cada fragmento se evaluó bajo 6 condiciones:
1. **LIMPIO:** Documento y query originales. *(Control de conocimiento base del modelo)*
2. **DOC CORR:** Símbolo corrupto en el documento, query limpia.
3. **FULL CORR:** Símbolo corrupto en documento y query.
4. **QUERY CORR:** Documento limpio, query corrupta.
5. **CON TABLA:** `DOC CORR` + prompt instruccional que mapea el mojibake a su definición semántica original.
6. **LATEX:** Documento con el símbolo convertido a su macro de LaTeX (`\forall`, `\geq`, etc.).

Se utilizaron dos modelos locales para el análisis comparativo (`qwen3:1.7b` y `qwen3:4b`), permitiendo separar las limitaciones de capacidad del modelo (límite paramétrico) del efecto puro de la corrupción.

---

## 2. Resultados y Hallazgos

Los resultados de las ejecuciones (`qwen3:1.7b` y `qwen3:4b`) validaron la hipótesis principal en un subconjunto de los fragmentos, pero también revelaron interacciones complejas e inesperadas entre el conocimiento previo del modelo, la tokenización y las instrucciones RAG. A continuación se detallan los hallazgos consolidados.

### 2.1 El Efecto Principal (Validación de Hipótesis)
**Fragmentos representativos:** A2 (⟺), B2 (Å), C3 (♭)

Estos casos mostraron la curva de degradación y recuperación perfecta:
* **Limpio:** CORRECTO (el modelo entiende el símbolo).
* **Doc Corrupto:** CONFUNDIDO (la comprensión se rompe, el modelo alucina la respuesta contraria de forma predecible).
* **Con Tabla y LaTeX:** CORRECTO (el rescate por inyección de contexto funciona).

### 2.2 Anomalía 1: Terquedad Semántica (Semantic Stubbornness)
**Fragmentos representativos:** B3 (□ operador modal), B4 (⊂ subconjunto estricto)

**Hallazgo:** RAG asume que la inyección de contexto en el prompt sobreescribe los pesos paramétricos del modelo. Sin embargo, para relaciones lógico-matemáticas profundamente arraigadas en el pre-entrenamiento, el LLM **ignora activamente la tabla RAG** y alucina en base a sus pesos internos. 
* En B4, la tabla definía explícitamente que `A ⊂ B significa A ≠ B`. El modelo, condicionado por la propiedad de antisimetría de `⊆`, respondió que A y B son iguales en todas las condiciones, contradiciendo la instrucción RAG frontalmente.
* **Impacto para el paper:** Demuestra un límite estructural empírico de las soluciones RAG "plug-and-play" en dominios formales.

### 2.3 Anomalía 2: Tokenización Fortuita (Fortuitous Tokenization)
**Fragmentos representativos:** C1 (æ), C2 (· interpunct)

**Hallazgo:** La corrupción de caracteres (mojibake) interactúa de formas altamente contraintuitivas con el tokenizador BPE, a veces *mejorando* el rendimiento.
* **Separación Visual (C2):** El mojibake `Â·` funcionó como un separador visual más efectivo para el LLM que el interpunct original limpio (`·`). El modelo falló en la versión limpia al leer los tokens como una cadena continua, pero respondió correctamente al texto corrupto.
* **Destrucción Fonética vs Tipeo (C1):** En transcripciones fonéticas IPA (`/bæd/`), la conversión a LaTeX limpia (`/b\aed/`) destruyó completamente el parseo subword, confundiendo al modelo. Por el contrario, el Unicode corrupto (`/bÃ¦d/`) fue exitosamente procesado por el modelo como un error ortográfico benigno.
* **Impacto para el paper:** Evidencia empírica cualitativa de las vulnerabilidades documentadas del tokenizador BPE (alineado con la literatura *The Curse of Tokenization*), demostrando que la representación en bytes es el verdadero cuello de botella.

### 2.4 Confounds Identificados: Redundancia Contextual
**Fragmentos representativos:** A1 (≥), A3 (∀), B1 (⇌)

**Hallazgo:** En símbolos de muy alta frecuencia, el contexto circundante en los fragmentos (ej. el proceso de Haber-Bosch para química, o el teorema `x² ≥ 0`) resultó ser tan predecible que el modelo dedujo la respuesta correcta incluso sin el símbolo, anulando el efecto de la corrupción.
* **Acción:** Estos fragmentos deben rediseñarse hacia contextos 100% abstractos o hipotéticos para futuros experimentos de control, de modo que el símbolo sea un cuello de botella informacional estricto.

### 2.5 Análisis Comparativo (Efecto del Escalado Paramétrico: 1.7B vs 4B)
**Hallazgo:** Las vulnerabilidades estructurales se mantienen consistentes a través de las escalas, pero el volumen paramétrico altera cómo se manifiesta la obediencia al RAG.
* **Terquedad Compartida:** El modelo de 1.7B sufrió exactamente el mismo problema de "Terquedad Semántica" en B1, B3 y B4, ignorando la tabla RAG a favor de su conocimiento de la antisimetría y las tautologías modales.
* **Obediencia en la Ignorancia:** Un patrón fascinante observado en el modelo 1.7B es que **los fragmentos de baja frecuencia se comportaron mejor que los de media frecuencia**. Esto sugiere que cuando el modelo *carece completamente* de preconceptos semánticos sobre un símbolo oscuro, es más propenso a seguir la instrucción inyectada (Tabla RAG) de forma obediente. Cuando tiene un conocimiento fuerte o parcial (media frecuencia), intenta reconciliar el prompt con sus pesos, fallando.
* **Compensación por Capacidad:** El modelo 4B pudo compensar la corrupción en casos redundantes (A1) puramente por su mayor volumen paramétrico, lo que actuó como un confound al ocultar el efecto del símbolo.

---

## 3. Conclusiones de Fase 1 e Implicaciones para Fase 2

1. **La corrupción semántica es predecible y peligrosa:** Cuando el contexto no rescata al documento, la corrupción no produce un fallo por "error de sistema", sino una alucinación lógica invertida.
2. **RAG no es infalible:** La mitigación mediante diccionarios inyectados por prompt (Tabla RAG) no puede superar el conocimiento paramétrico fuertemente sesgado ("Terquedad Semántica").
3. **El Tokenizador como Variable Oculta:** Las anomalías de tokenización exigen que cualquier solución real al problema deba ocurrir antes o durante el *embedding* (Fase 2), y no solo en la generación. 

*Esta fase motiva directamente la necesidad de la Fase 2: si los LLMs ya tienen tantas dificultades procesando texto corrupto que llega hasta ellos, ¿qué sucede en el espacio vectorial del Retriever donde los embeddings se forman a partir de estas mismas subwords rotas?*
