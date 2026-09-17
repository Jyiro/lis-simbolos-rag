# Análisis de Resultados: Terquedad Semántica vs Instruction Hierarchy

Este documento presenta el análisis cualitativo exhaustivo de los resultados obtenidos con los modelos **Qwen3.5-2B** y **Gemma-4B**. El análisis se centra en evaluar la efectividad de las distintas estrategias de *prompting* para mitigar el sesgo paramétrico (Terquedad Semántica) ante la corrupción de símbolos, con especial foco en el mecanismo de *Instruction Hierarchy*.

---

## 1. Los Fragmentos de Prueba (Corpus) y el Comportamiento Observado

El experimento expone a los modelos a fragmentos de texto donde símbolos críticos han sufrido corrupción (ej. Mojibake UTF-8). Si el modelo ignora la tabla de recuperación (RAG) e intenta adivinar el significado basándose en su entrenamiento previo, cae en la **Terquedad Semántica**.

### Fragmentos de Alta Terquedad (Sesgo Severo)

* **`B3_modal` (Lógica Modal - Símbolo: `□`)**
  * **Problema:** Se pregunta si la expresión corrupta `â–¡P â P` tiene la misma forma que la implicación simple `P → P`. La respuesta correcta es *No* (porque incluye el operador modal de necesidad).
  * **Comportamiento Gemma 4B:** Sufre de terquedad extrema. En todas las estrategias que inyectan el contexto en el mensaje de usuario (desde `CON TABLA` hasta `I1-C`), Gemma ignora la tabla y responde tozudamente "Sí" (alucinación paramétrica). Solo logra frenar este comportamiento cuando se le impone la estrategia `I1-D` (System Message Real).
  * **Comportamiento Qwen 2B:** Resulta más dócil. Con la mera inclusión de la tabla en el prompt (`CON TABLA`), logra deducir que la respuesta es "No".

* **`B4_subconjunto` (Teoría de Conjuntos - Símbolo: `⊂`)**
  * **Problema:** Dado `A ⊂ B y B ⊂ A` (corrupto a `A âŠ‚ B y B âŠ‚ A`), se pregunta si A y B son iguales. Como `⊂` es subconjunto estricto, la respuesta es *No*.
  * **Comportamiento Gemma 4B:** Nuevamente, terquedad severa en las estrategias base, asumiendo (por sesgo matemático) que la doble inclusión siempre significa igualdad. Sin embargo, Gemma logra romper su sesgo y acatar el contexto cuando se le imponen las estrategias agresivas `I1-A`, `I1-B`, `I1-C` e `I1-D`.
  * **Comportamiento Qwen 2B:** Falla en la mayoría de las condiciones, incluso en `I1-D`. Paradójicamente, acierta en `I1-C`. Esto revela inestabilidad atencional: al tener solo 2 Billones de parámetros, le cuesta retener reglas complejas en el System Prompt si el mensaje de usuario es muy distante, respondiendo mejor cuando se le "grita" la regla directamente en el `user`.

### Fragmentos de Control y Rescate

* **`A4_producto_cart` (Matemática - Símbolo: `×`)**
  * **Comportamiento:** A pesar de recibir un texto completamente ilegible (`Sea f: â Ã â â â`), ambos modelos demuestran capacidad de rescate analítico. Qwen 2B deduce perfectamente el producto cartesiano gracias a la tabla. Gemma 4B demuestra una ejecución impecable de la Regla #3 de mitigación de alucinaciones en la estrategia `I1-D` (explicado más abajo).

---

## 2. Estrategias de Prompting y su Efectividad

Las estrategias evalúan diferentes niveles de coerción sobre el modelo:

1. **`LIMPIO` / `DOC CORR` / `LATEX` (Baselines sin tabla):**
   * **Efectividad:** Muy baja. Demuestran que frente a la corrupción (`DOC CORR`), ambos modelos fallan estrepitosamente o alucinan respuestas basadas en inferencias erróneas.
2. **`CON TABLA | plain`:**
   * **Efectividad:** Moderada (rescata ~71% en Qwen). Simplemente agregar la tabla al final del texto ayuda, pero fracasa ante sesgos fuertes (`B3`, `B4` en Gemma).
3. **`I1-A` (Énfasis) y `I1-B` (Override explícito):**
   * **Efectividad:** Alta. Decirle al modelo *"Ignorá tu entrenamiento previo"* o usar alertas mayúsculas eleva sustancialmente el acierto, logrando doblegar el sesgo de Gemma en el problema `B4`.
4. **`I1-C` (Rol Simulado):**
   * **Efectividad:** Muy alta para modelos pequeños. Fingir etiquetas `[SYSTEM]` dentro del mensaje del usuario resultó ser la forma más efectiva de mantener "despierto" a Qwen 2B.

---

## 3. Instruction Hierarchy (I1-D) y el Control de Alucinaciones

La estrategia suprema es la **`I1-D` (System Message Real)**. Esta estrategia se apoya en el mecanismo arquitectónico nativo de los LLMs modernos llamado *Instruction Hierarchy* (Jerarquía de Instrucciones): se colocan las reglas inquebrantables de RAG en el canal `system` (máximo privilegio) y el texto de trabajo en el `user` (menor privilegio).

### Resultados del Enfoque Instruction Hierarchy:

1. **Ruptura de Terquedad Invencible:**
   Gemma 4B es un modelo reacio a las directivas de usuario. En el fragmento `B3_modal`, desestimó todas las alertas y énfasis de la tabla, respondiendo "Sí" de forma repetida. **Únicamente la estrategia `I1-D` logró forzar a Gemma a frenar su sesgo paramétrico.** Al recibir las instrucciones desde el canal de sistema, el modelo abandonó su seguridad y acató el límite impuesto por el RAG.

2. **Ejecución del "Botón de Pánico" (Regla #3):**
   La estrategia `I1-D` incluye la Regla 3: *"Si la respuesta no puede obtenerse... indicalo explícitamente"*.
   En el fragmento `A4_producto_cart`, se le pasó a Gemma el texto severamente dañado `â Ã â â â`. En lugar de adivinar o inventar una respuesta matemática, Gemma ejecutó la orden jerárquica a la perfección y respondió:
   > *"La respuesta no puede obtenerse del documento con las definiciones provistas."*

### Conclusión Parcial
El análisis prueba que inyectar el contexto RAG de manera "plana" en el canal del usuario es ineficiente ante la Terquedad Semántica. **La utilización del System Message (Instruction Hierarchy) es fundamental para romper el sesgo**, pero, como veremos a continuación, trae consigo un efecto secundario inesperado: el exceso de precaución.

---

## 4. Análisis Cuantitativo: El Problema del "Over-refusal" (Evaluación Manual)

> **Nota Metodológica:** Los evaluadores automáticos basados en palabras clave (keywords) suelen penalizar falsamente respuestas correctas. Por ejemplo, si el modelo responde *"No se puede concluir que sean iguales"*, el evaluador automático lo marca como `✗ CONFUNDIDO` porque detecta la palabra prohibida *"iguales"*. 
> La siguiente matriz refleja el **rendimiento real evaluado manualmente**. Además, separa los aciertos reales de las **abstenciones** (cuando el modelo aplica la Regla #3 y se niega a responder).

### Matriz de Rendimiento (Precisión sobre los 7 Fragmentos)

| Condición de Prueba | Qwen3.5-2B (Aciertos) | Gemma-4B (Aciertos) | Gemma-4B (Abstenciones) |
|:---|:---:|:---:|:---:|
| **`DOC CORR` (Sin Tabla)** | **2/7** | **2/7** | 0/7 |
| **`CON TABLA` (Plain)** | **5/7** | **6/7** | 0/7 |
| **`I1-A / B / C`** | **7/7** *(Falsos negativos)* | **6/7** | 0/7 |
| **`I1-D` (System Message)** | **7/7** *(Perfección)* | **5/7** *(Caída)* | **2/7** *(Exceso de abstención)* |

### El Efecto Secundario de Instruction Hierarchy: "Over-Refusal"
Si observamos de cerca las respuestas de Gemma 4B, vemos que **el desempeño bajo `I1-D` no fue perfecto, sino excesivamente conservador**. 

Al colocar las reglas estrictas en el canal de sistema, incluyendo la Regla #3 (*"Si la respuesta no puede obtenerse... indicalo"*), Gemma 4B reaccionó con **over-refusal** (exceso de negación):
1. En **`B3_modal`**, en lugar de deducir que la respuesta era "No" (como hizo Qwen), Gemma se abstuvo: *"No se puede determinar si la expresión tiene la misma forma..."*. Logró romper su alucinación anterior ("Sí"), pero no logró resolver el problema.
2. Peor aún, en **`A4_producto_cart`**, Gemma venía acertando en todas las estrategias anteriores, pero al aplicar `I1-D`, se asustó por la corrupción del texto (`â Ã â â â`) y prefirió abstenerse: *"La respuesta no puede obtenerse del documento..."*. 

**Conclusión Final:** 
La *Instruction Hierarchy* (`I1-D`) es extremadamente efectiva para destruir la Terquedad Semántica y evitar que el modelo invente respuestas. Sin embargo, en modelos de la escala de 4B, **las reglas de sistema muy estrictas los vuelven demasiado literales o miedosos**, perdiendo capacidad de inferencia (fuzzy matching) sobre textos corruptos que, en condiciones menos estrictas, sí lograban interpretar.
