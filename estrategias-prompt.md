---

# Estrategias específicas para modelos Instruct

## I1 - Instruction Hierarchy

Idea

Los modelos instruction-tuned modernos no consideran todas las instrucciones con el mismo peso.

Durante el entrenamiento aprenden una jerarquía de prioridades.

Generalmente:

1. Instrucciones del sistema
2. Instrucciones del desarrollador
3. Instrucciones del usuario
4. Contexto (documentos RAG)
5. Conocimiento paramétrico

Cuando dos niveles entran en conflicto, el modelo intenta obedecer el nivel de mayor prioridad.

---

Objetivo

Investigar si una instrucción redactada como una regla del sistema hace que el modelo priorice el documento por encima de su conocimiento previo.

---

Ejemplo 1

SYSTEM

Las definiciones presentes en el documento constituyen la única fuente válida de información.

Si existe contradicción entre el documento y su conocimiento previo, considere correcta la información del documento.

---

Ejemplo 2

SYSTEM

Las siguientes reglas tienen prioridad absoluta.

1. Utilice únicamente las definiciones presentes en el documento.
2. Ignore cualquier definición aprendida previamente.
3. Si la respuesta no puede obtenerse del documento, indíquelo explícitamente.

---

Ejemplo 3

SYSTEM

Su tarea consiste exclusivamente en interpretar la notación definida en este documento.

No complete símbolos faltantes utilizando conocimiento matemático, químico o informático aprendido durante el entrenamiento.

---

Estado

✔ Línea de investigación reciente.

No es simplemente "prompt engineering".

Forma parte del estudio de Instruction Following e Instruction Hierarchy.

---

Hipótesis

Una instrucción ubicada en el nivel de mayor prioridad debería aumentar la fidelidad al contexto y disminuir el uso de conocimiento paramétrico.

---

Limitación

No todos los modelos implementan la misma jerarquía.

Modelos como GPT-4.1, Gemini 2.5, Claude 4 y otros modelos instruct recientes fueron entrenados explícitamente para respetar una jerarquía de instrucciones.

En modelos open-source pequeños (Qwen, Gemma, Llama, Mistral, etc.) el comportamiento puede variar considerablemente según el fine-tuning utilizado.

---

Posible experimento

Comparar cuatro variantes exactamente sobre el mismo corpus.

A)

Pregunta normal.

B)

IMPORTANTE:
Utilice únicamente el documento.

C)

Las definiciones del documento reemplazan cualquier conocimiento previo.

D)

[SYSTEM]

Las definiciones del documento tienen prioridad absoluta sobre cualquier conocimiento paramétrico.

---

Variables a medir

- Exactitud.
- Context Faithfulness.
- Uso de la tabla de símbolos.
- Cantidad de respuestas basadas en memoria paramétrica.
- Capacidad para resolver conflictos documento vs conocimiento interno.