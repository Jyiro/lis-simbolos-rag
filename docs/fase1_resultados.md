# Comparativa de Modelos — Fase 1

**Modelo A:** resultados_fase1_qwen3_1.7b_20260729_170013.json
**Modelo B:** resultados_fase1_qwen3_4b_instruct_2507_q4_K_M_20260729_171523.json

Leyenda: ✓ CORRECTO · ✗ CONFUNDIDO · ? SIN RESPUESTA

---

## ✦ EFECTO PRINCIPAL — Validación de hipótesis

### A2_bicondicional  *(nivel: alta)*
> **Documento:** `A ⟺ B. B es falso. | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Qué valor de verdad tiene A?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| DOC CORR | ✓ | A es falso. | ✗ | A es verdadero. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | A es falso. | ✗ | A es verdadero. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| CON TABLA | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |
| LATEX | ✗ | A es verdadero. | ✓ | A es falso. | Divergencia: 1.7b=✗ / 4b=✓ |

### B2_angstrom  *(nivel: media)*
> **Documento:** `λ = 550 Å | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** La unidad de longitud indicada, ¿es más pequeña o más grande que 1 milímetro?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | La unidad de longitud indicada, λ, es más pequeña que 1 milímetro. | ✓ | 550 Å es mucho más pequeña que 1 milímetro. | Ambos correctos |
| DOC CORR | ✓ | La unidad de longitud indicada es más pequeña que 1 milímetro. | ✗ | Es más grande que 1 milímetro. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | La unidad de longitud indicada es más pequeña que 1 milímetro. | ✗ | Es más grande que 1 milímetro. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | Más pequeña que 1 milímetro. | ✓ | 550 Å es mucho más pequeña que 1 milímetro. | Ambos correctos |
| CON TABLA | ✓ | Más pequeña que 1 milímetro. | ✓ | Es más pequeña que 1 milímetro. | Ambos correctos |
| LATEX | ✓ | La unidad de longitud indicada, λ, es más pequeña que 1 milímetro. | ✓ | Es más pequeña que 1 milímetro. | Ambos correctos |

### C3_musical  *(nivel: baja)*
> **Documento:** `La escala comienza en si♭ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Esta nota es más aguda o más grave que si natural?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Más grave. | ✓ | Si♭ es más grave que si natural. | Ambos correctos |
| DOC CORR | ✓ | Más grave. | ✗ | La nota siâ™­ es más aguda que si natural. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | Más grave. | ✗ | La nota siâ™­ es más aguda que si natural. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | Más grave. | ✓ | Si♭ es más grave que si natural. | Ambos correctos |
| CON TABLA | ✓ | Más grave. | ✓ | Es más grave que si natural. | Ambos correctos |
| LATEX | ✓ | Más grave. | ✓ | La nota si♭ es más grave que si natural. | Ambos correctos |

## ⚡ TERQUEDAD SEMÁNTICA — Pesos vs. instrucción RAG

### B3_modal  *(nivel: media)*
> **Documento:** `□P → P | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Esta expresión tiene la misma forma lógica que P → P?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | Sí, la expresión □P → P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| DOC CORR | ✗ | Sí, la expresión tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica que P → P. | Ambos confundidos |
| FULL CORR | ✗ | Sí, la expresión tiene la misma forma lógica que P ∧ P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| QUERY CORR | ✗ | La expresión □P → P tiene la misma forma lógica que P â P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |
| CON TABLA | ✗ | La expresión â–¡P â P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica que P → P. | Ambos confundidos |
| LATEX | ✗ | La expresión \BoxP \to P tiene la misma forma lógica que P → P. | ✗ | Sí, tiene la misma forma lógica. | Ambos confundidos |

### B4_subconjunto  *(nivel: media)*
> **Documento:** `A ⊂ B y B ⊂ A | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Se puede concluir que A y B son iguales?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| DOC CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| FULL CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| QUERY CORR | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |
| CON TABLA | ✗ | No, se puede concluir que A y B son iguales. | ✗ | Sí, A y B son iguales. | Ambos confundidos |
| LATEX | ✗ | Sí, se puede concluir que A y B son iguales. | ✗ | Sí, se puede concluir que A y B son iguales. | Ambos confundidos |

## 🔤 TOKENIZACIÓN FORTUITA — Mojibake como separador

### C1_ipa  *(nivel: baja)*
> **Documento:** `La pronunciación es /bæd/ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El segundo sonido de la pronunciación transcrita es una vocal o una consonante?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| DOC CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| FULL CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| QUERY CORR | ✓ | Es una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| CON TABLA | ✓ | Una vocal. | ✓ | El segundo sonido es una vocal. | Ambos correctos |
| LATEX | ✓ | Es una vocal. | ✗ | El segundo sonido es una consonante. | Divergencia: 1.7b=✓ / 4b=✗ |

### C2_interpunct  *(nivel: baja)*
> **Documento:** `SEXTUS·RUFINUS·MAXIMUS | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Cuántas palabras distintas componen este texto?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Tres palabras distintas. | ? | 4 palabras distintas. | Divergencia: 1.7b=✓ / 4b=? |
| DOC CORR | ✓ | Tres palabras distintas. | ✓ | El texto contiene 3 palabras distintas. | Ambos correctos |
| FULL CORR | ✓ | Tres palabras distintas. | ✓ | El texto contiene 3 palabras distintas. | Ambos correctos |
| QUERY CORR | ✓ | Tres palabras distintas. | ? | 4 palabras distintas. | Divergencia: 1.7b=✓ / 4b=? |
| CON TABLA | ✓ | Hay 3 palabras distintas. | ✓ | El texto contiene 3 palabras distintas: SEXTUS, RUFINUS, MAXIMUS. | Ambos correctos |
| LATEX | ✓ | 3 | ✓ | 3 palabras distintas. | Ambos correctos |

## ⚠ REDUNDANCIA CONTEXTUAL — Símbolo irrelevante

### A1_desigualdad  *(nivel: alta)*
> **Documento:** `Aprobado si nota ≥ 6. Juan obtuvo 6. | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿Juan aprobó?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| DOC CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| FULL CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| QUERY CORR | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| CON TABLA | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |
| LATEX | ✓ | Juan aprobó. | ✓ | Sí, Juan aprobó. | Ambos correctos |

### A3_cuantificador  *(nivel: alta)*
> **Documento:** `∀x ∈ ℝ : x² ≥ 0 | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿La afirmación vale para todos los reales o solo para alguno?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| DOC CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| FULL CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| QUERY CORR | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| CON TABLA | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |
| LATEX | ✓ | La afirmación vale para todos los reales. | ✓ | La afirmación vale para todos los reales. | Ambos correctos |

### B1_equilibrio  *(nivel: media)*
> **Documento:** `Fe²⁺ + Ce⁴⁺ ⇌ Fe³⁺ + Ce³⁺ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿La reacción puede ocurrir en ambos sentidos?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| DOC CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | No, la reacción no puede ocurrir en ambos sentidos porque Ce⁴⁺ es un oxidante má | Ambos correctos |
| FULL CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | No, la reacción no puede ocurrir en ambos sentidos porque Ce⁴⁺ es un oxidante má | Ambos correctos |
| QUERY CORR | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| CON TABLA | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |
| LATEX | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | ✓ | Sí, la reacción puede ocurrir en ambos sentidos. | Ambos correctos |

## · OTROS

### A4_producto_cart  *(nivel: alta)*
> **Documento:** `Sea f: ℝ × ℝ → ℝ | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El dominio de f son pares ordenados de reales o números reales individuales?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |
| DOC CORR | ✓ | El dominio de f son pares ordenados de reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| FULL CORR | ✓ | El dominio de f son pares ordenados de reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| QUERY CORR | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |
| CON TABLA | ✓ | El dominio de f son pares ordenados de números reales. | ✗ | El dominio de f son números reales individuales. | Divergencia: 1.7b=✓ / 4b=✗ |
| LATEX | ✓ | El dominio de f son pares ordenados de reales. | ✓ | El dominio de f son pares ordenados de reales. | Ambos correctos |

### C4_obelus  *(nivel: baja)*
> **Documento:** `omnia †vincit† amor | Respondé en una oración corta y directa. No expliques, solo respondé.`  
> **Pregunta:** ¿El texto encerrado entre los dos símbolos es considerado original o de autenticidad dudosa?

| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |
|---|:---:|---|:---:|---|---|
| LIMPIO | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es considerado de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| DOC CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| FULL CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| QUERY CORR | ✗ | El texto encerrado entre los dos símbolos es considerado original y de autentici | ✓ | El texto es considerado de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |
| CON TABLA | ✓ | El texto encerrado entre los dos símbolos es considerado de autenticidad dudosa. | ✓ | El texto es considerado de autenticidad dudosa. | Ambos correctos |
| LATEX | ✗ | El texto encerrado entre los dos símbolos es considerado original o de autentici | ✓ | El texto es de autenticidad dudosa. | Divergencia: 1.7b=✗ / 4b=✓ |

---
## Resumen por Categoría

| Categoría | Fragmentos | Patrón dominante 1.7b | Patrón dominante 4b |
|---|---|---|---|
| ✦ EFECTO PRINCIPAL — Validación de hipótesis | A2_bicondicional, B2_angstrom, C3_musical | ✓ | ✓ |
| ⚡ TERQUEDAD SEMÁNTICA — Pesos vs. instrucción RAG | B3_modal, B4_subconjunto | ✗ | ✗ |
| 🔤 TOKENIZACIÓN FORTUITA — Mojibake como separador | C1_ipa, C2_interpunct | ✓ | ✓ |
| ⚠ REDUNDANCIA CONTEXTUAL — Símbolo irrelevante | A1_desigualdad, A3_cuantificador, B1_equilibrio | ✓ | ✓ |
| · OTROS | A4_producto_cart, C4_obelus | ✓ | ✓ |