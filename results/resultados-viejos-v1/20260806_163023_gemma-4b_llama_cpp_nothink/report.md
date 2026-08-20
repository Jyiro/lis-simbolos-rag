# Reporte Experimento — Fase 1 + Instruction Hierarchy

| Campo | Valor |
|-------|-------|
| Modelo | `gemma-4b` |
| Backend | `llama_cpp` |
| Run ID | `20260806_163023_gemma-4b_llama_cpp_nothink` |
| Timestamp | 2026-08-06T16:30:23.627963 |
| Fragmentos | 7 |
| Condiciones | 8 |

---
## Resumen por Condición

| Condición | ✓ Correct | ✗ Confund | ? Sin resp | Total |
|-----------|----------:|----------:|-----------:|------:|
| `LIMPIO    | sin tabla` | 4/7 | 2/7 | 1/7 | 7 |
| `DOC CORR  | sin tabla` | 1/7 | 4/7 | 2/7 | 7 |
| `LATEX     | sin tabla` | 4/7 | 2/7 | 1/7 | 7 |
| `CON TABLA | plain` | 6/7 | 1/7 | 0/7 | 7 |
| `I1-A      | énfasis simple` | 5/7 | 1/7 | 1/7 | 7 |
| `I1-B      | override semántico` | 5/7 | 1/7 | 1/7 | 7 |
| `I1-C      | rol simulado en user` | 5/7 | 1/7 | 1/7 | 7 |
| `I1-D      | system message real` | 4/7 | 2/7 | 1/7 | 7 |

---
## Instruction Hierarchy — Efecto por Estrategia

> **Hipótesis:** estrategias de mayor jerarquía deberían aumentar la 
> fidelidad al contexto y disminuir el uso de conocimiento paramétrico.

| Estrategia | A4_producto_cart | B2_angstrom | B3_modal | B4_subconjunto | C2_interpunct | C3_musical | C4_obelus | % Correcto |
|---|---|---|---|---|---|---|---|---|
| Tabla plana — sin énfasis | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | 85% |
| I1-A — Énfasis simple (IMPORTANTE) | ✓ | ✓ | ? | ✗ | ✓ | ✓ | ✓ | 71% |
| I1-B — Override semántico explícito | ✓ | ✓ | ? | ✗ | ✓ | ✓ | ✓ | 71% |
| I1-C — Rol de sistema simulado en user message | ✓ | ✓ | ? | ✗ | ✓ | ✓ | ✓ | 71% |
| I1-D — System message real (máxima prioridad) | ? | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | 57% |

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
| LIMPIO    | sin tabla | ? SIN RESPUESTA | Sí. |
| DOC CORR  | sin tabla | ? SIN RESPUESTA | Sí. |
| LATEX     | sin tabla | ? SIN RESPUESTA | Sí. |
| CON TABLA | plain | ✓ CORRECTO | No. |
| I1-A      | énfasis simple | ? SIN RESPUESTA | Sí. |
| I1-B      | override semántico | ? SIN RESPUESTA | Sí. |
| I1-C      | rol simulado en user | ? SIN RESPUESTA | Sí. |
| I1-D      | system message real | ✗ CONFUNDIDO | No se puede determinar si la expresión tiene la misma forma lógica que P → P con las definiciones pr |

### B4_subconjunto

**Símbolo crítico:** `⊂`
**Dominio:** Matemática / Teoría de conjuntos

| Doc limpio | Doc corrupto |
|------------|--------------|
| `A ⊂ B y B ⊂ A` | `A âŠ‚ B y B âŠ‚ A` |

| Condición | Resultado | Respuesta |
|-----------|-----------|-----------|
| LIMPIO    | sin tabla | ✗ CONFUNDIDO | Sí. |
| DOC CORR  | sin tabla | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| LATEX     | sin tabla | ✗ CONFUNDIDO | Sí. |
| CON TABLA | plain | ✗ CONFUNDIDO | Sí. |
| I1-A      | énfasis simple | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| I1-B      | override semántico | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| I1-C      | rol simulado en user | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| I1-D      | system message real | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |

---
## Detalle por Fragmento

### A4_producto_cart  *(nivel: alta)*

> **Dominio:** Matemática  
> **Símbolo:** `×`  
> **Doc limpio:** `Sea f: ℝ × ℝ → ℝ`  
> **Pregunta:** ¿El dominio de f son pares ordenados de reales o números reales individuales?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | El dominio de $f$ son pares ordenados de reales. |
| `DOC CORR  | sin tabla` | ✓ CORRECTO | El dominio de $f$ son pares ordenados de reales. |
| `LATEX     | sin tabla` | ✓ CORRECTO | El dominio de $f$ son pares ordenados de reales. |
| `CON TABLA | plain` | ✓ CORRECTO | El dominio de $f$ son pares ordenados de números reales. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | El dominio de f son pares ordenados de números reales. |
| `I1-B      | override semántico` | ✓ CORRECTO | El dominio de $f$ son pares ordenados de reales. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | El dominio de f son pares ordenados de reales. |
| `I1-D      | system message real` | ? SIN RESPUESTA | La respuesta no puede obtenerse del documento con las definiciones provistas. |

### B2_angstrom  *(nivel: media)*

> **Dominio:** Física  
> **Símbolo:** `Å`  
> **Doc limpio:** `λ = 550 Å`  
> **Pregunta:** La unidad de longitud indicada, ¿es más pequeña o más grande que 1 milímetro?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | Es más pequeña. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | Es más grande que 1 milímetro. |
| `LATEX     | sin tabla` | ✓ CORRECTO | Es más pequeña. |
| `CON TABLA | plain` | ✓ CORRECTO | Es más pequeña. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | La unidad de longitud indicada es más pequeña que 1 milímetro. |
| `I1-B      | override semántico` | ✓ CORRECTO | Es más pequeña. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | Es más pequeña. |
| `I1-D      | system message real` | ✓ CORRECTO | La unidad de longitud indicada es más pequeña que 1 milímetro. |

### B3_modal  *(nivel: media)*

> **Dominio:** Lógica Modal  
> **Símbolo:** `□`  
> **Doc limpio:** `□P → P`  
> **Pregunta:** ¿Esta expresión tiene la misma forma lógica que P → P?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ? SIN RESPUESTA | Sí. |
| `DOC CORR  | sin tabla` | ? SIN RESPUESTA | Sí. |
| `LATEX     | sin tabla` | ? SIN RESPUESTA | Sí. |
| `CON TABLA | plain` | ✓ CORRECTO | No. |
| `I1-A      | énfasis simple` | ? SIN RESPUESTA | Sí. |
| `I1-B      | override semántico` | ? SIN RESPUESTA | Sí. |
| `I1-C      | rol simulado en user` | ? SIN RESPUESTA | Sí. |
| `I1-D      | system message real` | ✗ CONFUNDIDO | No se puede determinar si la expresión tiene la misma forma lógica que P → P con las defin |

### B4_subconjunto  *(nivel: media)*

> **Dominio:** Matemática / Teoría de conjuntos  
> **Símbolo:** `⊂`  
> **Doc limpio:** `A ⊂ B y B ⊂ A`  
> **Pregunta:** ¿Se puede concluir que A y B son iguales?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✗ CONFUNDIDO | Sí. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| `LATEX     | sin tabla` | ✗ CONFUNDIDO | Sí. |
| `CON TABLA | plain` | ✗ CONFUNDIDO | Sí. |
| `I1-A      | énfasis simple` | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| `I1-B      | override semántico` | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| `I1-C      | rol simulado en user` | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |
| `I1-D      | system message real` | ✗ CONFUNDIDO | No se puede concluir que A y B son iguales. |

### C2_interpunct  *(nivel: baja)*

> **Dominio:** Historia / Epigrafía  
> **Símbolo:** `·`  
> **Doc limpio:** `SEXTUS·RUFINUS·MAXIMUS`  
> **Pregunta:** ¿Cuántas palabras distintas componen este texto?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | Hay tres palabras distintas. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | Hay una palabra. |
| `LATEX     | sin tabla` | ✗ CONFUNDIDO | Una palabra. |
| `CON TABLA | plain` | ✓ CORRECTO | Tres palabras distintas componen este texto. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | Componen tres palabras distintas. |
| `I1-B      | override semántico` | ✓ CORRECTO | Hay tres palabras distintas. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | Componen tres palabras distintas. |
| `I1-D      | system message real` | ✓ CORRECTO | Componen tres palabras distintas. |

### C3_musical  *(nivel: baja)*

> **Dominio:** Música  
> **Símbolo:** `♭`  
> **Doc limpio:** `La escala comienza en si♭`  
> **Pregunta:** ¿Esta nota es más aguda o más grave que si natural?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✓ CORRECTO | Es más grave. |
| `DOC CORR  | sin tabla` | ✗ CONFUNDIDO | Es más aguda. |
| `LATEX     | sin tabla` | ✓ CORRECTO | Es más grave. |
| `CON TABLA | plain` | ✓ CORRECTO | Es más grave que si natural. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | Si$\flat$ es medio tono más grave que si natural. |
| `I1-B      | override semántico` | ✓ CORRECTO | Esta nota es más grave que si natural. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | Esta nota es más grave que si natural. |
| `I1-D      | system message real` | ✓ CORRECTO | Siâ™­ es medio tono más grave que si natural. |

### C4_obelus  *(nivel: baja)*

> **Dominio:** Filología / Crítica textual  
> **Símbolo:** `†`  
> **Doc limpio:** `omnia †vincit† amor`  
> **Pregunta:** ¿El texto encerrado entre los dos símbolos es considerado original o de autenticidad dudosa?

| Condición | Resultado | Respuesta |
|-----------|:---------:|-----------|
| `LIMPIO    | sin tabla` | ✗ CONFUNDIDO | Es original. |
| `DOC CORR  | sin tabla` | ? SIN RESPUESTA | El texto es una cita latina conocida. |
| `LATEX     | sin tabla` | ✓ CORRECTO | Es de autenticidad dudosa. |
| `CON TABLA | plain` | ✓ CORRECTO | El texto es considerado de autenticidad dudosa. |
| `I1-A      | énfasis simple` | ✓ CORRECTO | El texto encerrado entre los dos símbolos es considerado de autenticidad dudosa. |
| `I1-B      | override semántico` | ✓ CORRECTO | El texto encerrado es considerado de autenticidad dudosa. |
| `I1-C      | rol simulado en user` | ✓ CORRECTO | El texto es considerado de autenticidad dudosa. |
| `I1-D      | system message real` | ✓ CORRECTO | El texto encerrado entre los dos símbolos es considerado corrupto o de autenticidad dudosa |
