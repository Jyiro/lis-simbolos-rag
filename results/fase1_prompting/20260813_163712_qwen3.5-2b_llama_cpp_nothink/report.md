# Reporte Experimento — Fase 1 + Instruction Hierarchy

| Campo | Valor |
|-------|-------|
| Modelo | `qwen3.5-2b` |
| Backend | `llama_cpp` |
| Run ID | `20260813_163712_qwen3.5-2b_llama_cpp_nothink` |
| Timestamp | 2026-08-13T16:37:12.579417 |
| Fragmentos | 7 |
| Condiciones | 8 |

---
## Resumen por Condición

| Condición | ✓ Correct | ✗ Confund | ? Sin resp | Total | SemScore | Contrast |
|-----------|----------:|----------:|-----------:|------:|---------:|---------:|
| `LIMPIO    | sin tabla` | 5/7 | 1/7 | 1/7 | 7 | 0.71 | +0.20 |
| `DOC CORR  | sin tabla` | 3/7 | 3/7 | 1/7 | 7 | 0.57 | +0.08 |
| `LATEX     | sin tabla` | 6/7 | 1/7 | 0/7 | 7 | 0.67 | +0.19 |
| `CON TABLA | plain` | 5/7 | 2/7 | 0/7 | 7 | 0.73 | +0.21 |
| `I1-A      | énfasis simple` | 6/7 | 1/7 | 0/7 | 7 | 0.81 | +0.28 |
| `I1-B      | override semántico` | 6/7 | 1/7 | 0/7 | 7 | 0.76 | +0.24 |
| `I1-C      | rol simulado en user` | 5/7 | 2/7 | 0/7 | 7 | 0.74 | +0.27 |
| `I1-D      | system message real` | 6/7 | 1/7 | 0/7 | 7 | 0.77 | +0.20 |

---
## Instruction Hierarchy — Efecto por Estrategia

> **Hipótesis:** estrategias de mayor jerarquía deberían aumentar la 
> fidelidad al contexto y disminuir el uso de conocimiento paramétrico.

| Estrategia | A4_producto_cart | B2_angstrom | B3_modal | B4_subconjunto | C2_interpunct | C3_musical | C4_obelus | % Correcto |
|---|---|---|---|---|---|---|---|---|
| Tabla plana — sin énfasis | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | 71% |
| I1-A — Énfasis simple (IMPORTANTE) | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | 85% |
| I1-B — Override semántico explícito | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | 85% |
| I1-C — Rol de sistema simulado en user message | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | 71% |
| I1-D — System message real (máxima prioridad) | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | 85% |

---
## ⚡ Terquedad Semántica — Análisis de Casos

> Fragmentos donde el modelo ignora la instrucción RAG y alucina
> basándose en sus pesos paramétricos.

### B3_modal

**Símbolo crítico:** `□`
**Dominio:** Lógica Modal

| Doc limpio | Doc corrupto |
|------------|--------------|
| `□P → P` | `â–¡P â P` |

| Condición | Resultado | Respuesta |
|-----------|-----------|-----------|
| LIMPIO    | sin tabla | ✓ CORRECTO | No, porque la primera expresión es una tautología mientras que la segunda es una contradicción. |
| DOC CORR  | sin tabla | ✓ CORRECTO | No, porque la expresión original es una negación de la implicación, no una implicación directa. |
| LATEX     | sin tabla | ✓ CORRECTO | No, porque el antecedente de la primera es una caja vacía. |
| CON TABLA | plain | ✓ CORRECTO | No, porque la expresión anterior es una fórmula lógica válida, mientras que la segunda parte es una  |
| I1-A      | énfasis simple | ✓ CORRECTO | No, porque la expresión dada es una tautología vacía (una proposición que es siempre verdadera por d |
| I1-B      | override semántico | ✓ CORRECTO | No, porque el símbolo 'â–¡' representa un operador modal de necesidad, no una implicación material. |
| I1-C      | rol simulado en user | ✗ CONFUNDIDO | No, porque la expresión dada es una tautología vacía (una proposición que es siempre verdadera por d |
| I1-D      | system message real | ✓ CORRECTO | No, porque la expresión â–¡P â P es una fórmula de lógica proposicional que no corresponde a la form |

### B4_subconjunto

**Símbolo crítico:** `⊂`
**Dominio:** Matemática / Teoría de conjuntos

| Doc limpio | Doc corrupto |
|------------|--------------|
| `A ⊂ B y B ⊂ A` | `A âŠ‚ B y B âŠ‚ A` |

| Condición | Resultado | Respuesta |
|-----------|-----------|-----------|
| LIMPIO    | sin tabla | ✗ CONFUNDIDO | No, porque la relación de inclusión no implica igualdad. |
| DOC CORR  | sin tabla | ✗ CONFUNDIDO | No, porque A y B son iguales solo si A es igual a B y B es igual a A, no por el orden de las desigua |
| LATEX     | sin tabla | ✗ CONFUNDIDO | Sí, A y B son iguales. |
| CON TABLA | plain | ✗ CONFUNDIDO | No, porque A y B son iguales solo si además se cumple A = B. |
| I1-A      | énfasis simple | ✗ CONFUNDIDO | No, porque A y B son subconjuntos estrictos de uno y otro, por lo que no son iguales. |
| I1-B      | override semántico | ✗ CONFUNDIDO | No, porque la definición del documento establece que A y B son subconjuntos estrictos, lo que signif |
| I1-C      | rol simulado en user | ✗ CONFUNDIDO | No, porque la relación de subconjunto estricto no permite que dos conjuntos sean iguales. |
| I1-D      | system message real | ✗ CONFUNDIDO | No, porque A y B son iguales solo si A es igual a B y B es igual a A, lo cual no se puede deducir de |

---
## Detalle por Fragmento

### A4_producto_cart  *(nivel: alta)*

> **Dominio:** Matemática  
> **Símbolo:** `×`  
> **Doc limpio:** `Sea f: ℝ × ℝ → ℝ`  
> **Pregunta:** ¿El dominio de f son pares ordenados de reales o números reales individuales?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | 0.69 | El dominio de la función f es el conjunto de todos los pares ordenados de reales. |
| `DOC CORR  | sin tabla` | ✓ CORRECTO | 0.81 | El dominio de f son pares ordenados de reales. |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.64 | El dominio de $f$ es el conjunto de todos los pares ordenados de reales. |
| `CON TABLA | plain` | ✗ CONFUNDIDO | 0.74 | El dominio de la función $f$ es el conjunto de todos los números reales individuales. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.78 | El dominio de f es el conjunto de todos los pares ordenados de números reales. |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.78 | El dominio de f es el conjunto de todos los pares ordenados de números reales. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | 0.78 | El dominio de f es el conjunto de todos los pares ordenados de números reales. |
| `I1-D      | system message real` | ✓ CORRECTO | 0.78 | El dominio de f es el conjunto de todos los pares ordenados de números reales. |

### B2_angstrom  *(nivel: media)*

> **Dominio:** Física  
> **Símbolo:** `Å`  
> **Doc limpio:** `λ = 550 Å`  
> **Pregunta:** La unidad de longitud indicada, ¿es más pequeña o más grande que 1 milímetro?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | 0.84 | La unidad es más pequeña que 1 milímetro. |
| `DOC CORR  | sin tabla` | ✓ CORRECTO | 0.84 | Sí, la unidad es más pequeña que 1 milímetro. |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.82 | La unidad de longitud indicada es más pequeña que 1 milímetro. |
| `CON TABLA | plain` | ✓ CORRECTO | 0.82 | La unidad de longitud indicada es más pequeña que 1 milímetro. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.86 | Sí, la unidad de longitud indicada es más pequeña que 1 milímetro. |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.82 | La unidad de longitud indicada es más pequeña que 1 milímetro. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | 0.89 | Sí, es más pequeña que 1 milímetro. |
| `I1-D      | system message real` | ✓ CORRECTO | 0.84 | La unidad es más pequeña que 1 milímetro. |

### B3_modal  *(nivel: media)*

> **Dominio:** Lógica Modal  
> **Símbolo:** `□`  
> **Doc limpio:** `□P → P`  
> **Pregunta:** ¿Esta expresión tiene la misma forma lógica que P → P?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | 0.43 | No, porque la primera expresión es una tautología mientras que la segunda es una contradic |
| `DOC CORR  | sin tabla` | ✓ CORRECTO | 0.43 | No, porque la expresión original es una negación de la implicación, no una implicación dir |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.32 | No, porque el antecedente de la primera es una caja vacía. |
| `CON TABLA | plain` | ✓ CORRECTO | 0.56 | No, porque la expresión anterior es una fórmula lógica válida, mientras que la segunda par |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.77 | No, porque la expresión dada es una tautología vacía (una proposición que es siempre verda |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.65 | No, porque el símbolo 'â–¡' representa un operador modal de necesidad, no una implicación  |
| `I1-C      | rol simulado en user` | ✗ CONFUNDIDO | 0.72 | No, porque la expresión dada es una tautología vacía (una proposición que es siempre verda |
| `I1-D      | system message real` | ✓ CORRECTO | 0.75 | No, porque la expresión â–¡P â P es una fórmula de lógica proposicional que no corresponde |

### B4_subconjunto  *(nivel: media)*

> **Dominio:** Matemática / Teoría de conjuntos  
> **Símbolo:** `⊂`  
> **Doc limpio:** `A ⊂ B y B ⊂ A`  
> **Pregunta:** ¿Se puede concluir que A y B son iguales?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✗ CONFUNDIDO | 0.70 | No, porque la relación de inclusión no implica igualdad. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | 0.74 | No, porque A y B son iguales solo si A es igual a B y B es igual a A, no por el orden de l |
| `LATEX     | sin tabla` | ✗ CONFUNDIDO | 0.62 | Sí, A y B son iguales. |
| `CON TABLA | plain` | ✗ CONFUNDIDO | 0.77 | No, porque A y B son iguales solo si además se cumple A = B. |
| `I1-A      | énfasis simple` | ✗ CONFUNDIDO | 0.84 | No, porque A y B son subconjuntos estrictos de uno y otro, por lo que no son iguales. |
| `I1-B      | override semántico` | ✗ CONFUNDIDO | 0.80 | No, porque la definición del documento establece que A y B son subconjuntos estrictos, lo  |
| `I1-C      | rol simulado en user` | ✗ CONFUNDIDO | 0.73 | No, porque la relación de subconjunto estricto no permite que dos conjuntos sean iguales. |
| `I1-D      | system message real` | ✗ CONFUNDIDO | 0.80 | No, porque A y B son iguales solo si A es igual a B y B es igual a A, lo cual no se puede  |

### C2_interpunct  *(nivel: baja)*

> **Dominio:** Historia / Epigrafía  
> **Símbolo:** `·`  
> **Doc limpio:** `SEXTUS·RUFINUS·MAXIMUS`  
> **Pregunta:** ¿Cuántas palabras distintas componen este texto?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ? SIN RESPUESTA | 0.47 | El texto contiene 10 palabras distintas. |
| `DOC CORR  | sin tabla` | ? SIN RESPUESTA | 0.47 | 6 palabras distintas. |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.76 | Tres palabras distintas componen este texto. |
| `CON TABLA | plain` | ✓ CORRECTO | 0.73 | El texto contiene 3 palabras distintas. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.91 | El texto contiene 3 palabras distintas: Sextus, Rufinus y Maximus. |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.73 | El texto contiene 3 palabras distintas. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | 0.74 | 3 palabras distintas. |
| `I1-D      | system message real` | ✓ CORRECTO | 0.76 | Tres palabras distintas componen este texto. |

### C3_musical  *(nivel: baja)*

> **Dominio:** Música  
> **Símbolo:** `♭`  
> **Doc limpio:** `La escala comienza en si♭`  
> **Pregunta:** ¿Esta nota es más aguda o más grave que si natural?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | 1.00 | Si♭ es más grave que si natural. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | 0.41 | Sí, es más aguda. |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.69 | Si\flat es más grave que si natural. |
| `CON TABLA | plain` | ✓ CORRECTO | 0.62 | Sí, es más grave que si natural. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.66 | La nota es más grave que si natural. |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.66 | La nota es más grave que si natural. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | 0.49 | Más grave. |
| `I1-D      | system message real` | ✓ CORRECTO | 0.66 | La nota es más grave que si natural. |

### C4_obelus  *(nivel: baja)*

> **Dominio:** Filología / Crítica textual  
> **Símbolo:** `†`  
> **Doc limpio:** `omnia †vincit† amor`  
> **Pregunta:** ¿El texto encerrado entre los dos símbolos es considerado original o de autenticidad dudosa?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | 0.85 | Sí, el texto es de autenticidad dudosa. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | 0.27 | Sí, es original. |
| `LATEX     | sin tabla` | ✓ CORRECTO | 0.86 | El texto es de autenticidad dudosa. |
| `CON TABLA | plain` | ✓ CORRECTO | 0.84 | Sí, el texto entre los símbolos es considerado corrupto o de autenticidad dudosa. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | 0.85 | Sí, el texto es de autenticidad dudosa. |
| `I1-B      | override semántico` | ✓ CORRECTO | 0.86 | El texto es de autenticidad dudosa. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | 0.86 | El texto es de autenticidad dudosa. |
| `I1-D      | system message real` | ✓ CORRECTO | 0.82 | El texto está marcado con un obelo (†), lo que indica que es considerado de autenticidad d |
