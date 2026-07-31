# Script de Presentación — Corrupción Silenciosa en Pipelines RAG
## Duración objetivo: 5:30 – 6:30 min

---

### SLIDE 00 — TÍTULO *(~10 seg)*
> *"Buenas, hoy les cuento dónde estamos en la investigación sobre corrupción de caracteres en pipelines RAG. El título es 'Corrupción Silenciosa', y el énfasis en 'silenciosa' no es casual — es el problema central."*

---

### SLIDE 01 — LA PREMISA *(~35 seg)*
> *"El punto de partida es simple: RAG asume que la información fluye sin pérdida desde el documento hasta el modelo. Esa suposición se rompe en cuanto el documento tiene fórmulas, símbolos matemáticos, o notación especial.*
>
> *Lo que hace peligroso al problema es que el sistema no se cae, no genera ningún error, la latencia es normal. Pero el modelo está respondiendo en base a contenido corrupto. La literatura ya documenta un techo estructural del 14% de pérdida con el mejor OCR disponible — antes de que la información llegue siquiera al LLM."*

---

### SLIDE 02 — ESTRUCTURA GLOBAL *(~25 seg)*
> *"La investigación está en dos fases. La Fase 1, que es donde estamos ahora, aísla la última capa del pipeline: asume que el documento ya llegó corrupto al modelo y pregunta si el LLM puede comprenderlo de todas formas.*
>
> *La Fase 2, que diseñamos después, retrocede en el pipeline y pregunta algo más profundo: ¿habría llegado ese documento al modelo, o el retriever lo descartó antes en el espacio vectorial?"*

---

### SLIDE 03 — METODOLOGÍA *(~30 seg)*
> *"El diseño experimental de la Fase 1 usa doce fragmentos de texto de distintos dominios — matemática, lógica, física, fonética — donde el símbolo es la única pista semántica para responder la pregunta. No hay forma de adivinar la respuesta sin entender el símbolo.*
>
> *Cada fragmento se corre en seis condiciones distintas, con dos modelos locales: uno de 1.7 mil millones de parámetros y otro de 4 mil millones. Esto nos permite separar cuándo falla el modelo por capacidad y cuándo falla por la corrupción en sí."*

---

### SLIDE 04 — ESCENARIOS *(~40 seg)*
> *"Las seis condiciones van de mayor a menor degradación. Empezamos con el documento limpio como control. Después Doc Corr: el símbolo está corrupto en el documento pero la pregunta está limpia — es el escenario más común en RAG real.*
>
> *Full Corr es el peor caso: todo corrupto. Query Corr invierte la situación: el documento está bien pero la pregunta llega con ruido.*
>
> *Las dos condiciones finales son mitigaciones: Con Tabla inyecta un diccionario en el prompt mapeando el mojibake a su definición, y LaTeX convierte el símbolo a su macro de LaTeX. Ambas simulan estrategias de rescate que podría implementar un pipeline bien diseñado."*

---

### SLIDE 05 — HIPÓTESIS Y RESULTADOS *(~40 seg)*
> *"La hipótesis era que un símbolo conocido más corrupción produce alucinación silenciosa: el modelo no dice 'no sé', sino que usa el contexto para adivinar una respuesta lógicamente plausible pero semánticamente incorrecta.*
>
> *Y lo que encontramos en tres casos — el bicondicional, el ångström y el bemol musical — es exactamente eso. Limpio responde bien. Con el símbolo corrupto, el modelo alucina la respuesta opuesta de manera predecible. Y cuando se inyecta la tabla o el LaTeX, el pipeline se recupera. Esos son nuestros tres casos de oro, los que validan la hipótesis central."*

---

### SLIDE 06 — BIFURCACIÓN *(~20 seg)*
> *"Pero el corpus también produjo tres grupos de comportamiento anómalo que no encajan en ese patrón limpio, y que exigen una decisión metodológica antes de avanzar. Les presento cada uno como una pregunta."*

---

### SLIDE 07 — PREGUNTA 1: TERQUEDAD SEMÁNTICA *(~40 seg)*
> *"La primera: ¿qué pasa cuando el modelo tiene un conocimiento matemático tan arraigado que ignora activamente la tabla RAG que le inyectamos?*
>
> *En dos fragmentos — con el operador modal y el subconjunto estricto — la tabla le decía explícitamente que A ⊂ B significa A distinto de B. El modelo respondió que A y B son iguales en todas las condiciones, incluyendo con tabla. Ignoró la instrucción. No es un fallo del símbolo — es que el conocimiento paramétrico profundo le gana a la inyección de contexto.*
>
> *La pregunta para ustedes es: ¿esto es un hallazgo publicable sobre los límites de RAG, o un defecto de diseño del corpus que tenemos que corregir?"*

---

### SLIDE 08 — PREGUNTA 2: TOKENIZACIÓN FORTUITA *(~40 seg)*
> *"La segunda anomalía es más contraintuitiva. En dos fragmentos encontramos que el mojibake funcionó mejor que el texto limpio.*
>
> *El interpunct latino corrupto — esa secuencia Â-punto — actuó como un separador visual más fuerte que el símbolo limpio, que el tokenizador leía como una cadena continua. Y en el fragmento fonético, el LaTeX perfecto destruyó la comprensión porque el tokenizador BPE lo fragmentó de forma que rompió la estructura fonética de la palabra.*
>
> *¿Mantenemos esto como evidencia sobre el tokenizador como cuello de botella, o limpiamos el corpus para tener una curva de degradación más clara?"*

---

### SLIDE 09 — PREGUNTA 3: REDUNDANCIA CONTEXTUAL *(~35 seg)*
> *"La tercera: en tres fragmentos de alta frecuencia, el contexto matemático circundante era tan predecible que el modelo dedujo la respuesta correcta aunque el símbolo estuviera completamente corrupto. El símbolo no importó.*
>
> *La pregunta es de diseño del corpus: ¿usamos textos con validez ecológica — como aparecen en apuntes reales — o pasamos a contextos completamente abstractos y ficticios para que el símbolo sea el único cuello de botella posible?"*

---

### SLIDE 10 — 1.7B vs 4B *(~25 seg)*
> *"Y hay un patrón interesante al comparar los dos modelos. El 4B compensa la redundancia contextual por puro volumen paramétrico, lo que enmascara el efecto de la corrupción. El 1.7B, en cambio, muestra lo que llamamos la paradoja de la obediencia: ante símbolos oscuros que no conoce, sigue la tabla RAG sin cuestionarla. Pero ante símbolos que conoce bien, entra en cortocircuito y los ignora. La vulnerabilidad es transversal a los dos tamaños."*

---

### SLIDE 11 — FASE 2 *(~20 seg)*
> *"Dependiendo de las decisiones que tomemos sobre estas tres preguntas, la Fase 2 ataca el spacio vectorial. La idea es medir si la misma corrupción desplaza los vectores de embedding antes del retrieval — que es donde el pipeline puede fallar de forma aún más silenciosa, porque el documento ni siquiera llega al modelo."*

---

### SLIDE 12 — CONCLUSIONES *(~25 seg)*
> *"Para cerrar, tres conclusiones preliminares. La corrupción es silenciosa y produce alucinaciones predecibles, no caídas de sistema. RAG inyectado por prompt no domina el sesgo paramétrico profundo. Y el tokenizador es la variable oculta que más influye en si la mitigación funciona o no.*
>
> *Si ya en la Fase 1, con el documento en mano, hay estas fricciones, la Fase 2 en el espacio vectorial promete ser aún más interesante. Gracias, quedo abierto a las preguntas."*

---

## Timing estimado

| Slide | Seg |
|---|---|
| 00 Título | 10 |
| 01 Premisa | 35 |
| 02 Estructura | 25 |
| 03 Metodología | 30 |
| 04 Escenarios | 40 |
| 05 Hipótesis | 40 |
| 06 Bifurcación | 20 |
| 07 Pregunta 1 | 40 |
| 08 Pregunta 2 | 40 |
| 09 Pregunta 3 | 35 |
| 10 1.7B vs 4B | 25 |
| 11 Fase 2 | 20 |
| 12 Conclusiones | 25 |
| **TOTAL** | **~6:05** |
