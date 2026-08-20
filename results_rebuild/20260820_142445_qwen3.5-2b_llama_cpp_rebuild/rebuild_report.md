# Reporte de Experimento — Reconstrucción de Mojibake

| Campo | Valor |
|---|---|
| Modelo | `qwen3.5-2b` |
| Backend | `llama_cpp` |
| Run ID | `20260820_142445_qwen3.5-2b_llama_cpp_rebuild` |
| Fragmentos exactos | 3/7 |
| CER promedio | 0.081 |

---

## Resumen

| Fragmento | Dominio | Símbolos | Resultado | Dist | CER |
|---|---|---|:---:|---:|---:|
| `R1_logica_modal` | Lógica Modal | `□` `→` | 🟠 **PARCIAL** | 10 | 0.204 |
| `R2_calculo_integral` | Cálculo | `∀` `∈` `ℝ` `≥` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| `R3_conjuntos` | Teoría de Conjuntos | `⊂` `∀` `∈` `→` | 🟠 **PARCIAL** | 5 | 0.139 |
| `R4_fisica_optica` | Física / Óptica | `Å` `≥` | ✅ **PERFECTO** | 0 | 0.000 |
| `R5_quimica` | Química | `⇌` `∃!` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| `R6_logica_pred` | Lógica de Predicados | `∀` `∈` `ℝ` `∃!` `→` `↔` `≥` | 🟠 **PARCIAL** | 2 | 0.051 |
| `R7_musica_filologia` | Música / Filología | `♭` `·` `†` | 🟠 **PARCIAL** | 8 | 0.170 |

---

## Detalle por Fragmento

### 🟠 `R1_logica_modal` — Lógica Modal

**Símbolos probados:** `□` `→`

| | Texto |
|---|---|
| **Original** | `Si □P → P y □Q → Q, entonces □(P → Q) → (□P → □Q)` |
| **Corrupto** | `Si â–¡P â P y â–¡Q â Q, entonces â–¡(P â Q) â (â–¡P â â–¡Q)` |
| **LLM reconstruyó** | `Si →P →P y →Q →Q, entonces →(P →Q) →(→P →→Q)` |

> **PARCIAL** — Reconstrucción parcial — algunos símbolos fallaron (CER: 0.20, dist: 10).

### ✅ `R2_calculo_integral` — Cálculo

**Símbolos probados:** `∀` `∈` `ℝ` `≥` `×`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: si f(x) ≥ 0, entonces f × g es continua` |
| **Corrupto** | `âx â â: si f(x) â¥ 0, entonces f Ã g es continua` |
| **LLM reconstruyó** | `∀x ∈ ℝ: si f(x) ≥ 0, entonces f × g es continua` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### 🟠 `R3_conjuntos` — Teoría de Conjuntos

**Símbolos probados:** `⊂` `∀` `∈` `→`

| | Texto |
|---|---|
| **Original** | `A ⊂ B si y solo si ∀x: x ∈ A → x ∈ B` |
| **Corrupto** | `A âŠ‚ B si y solo si âx: x â A â x â B` |
| **LLM reconstruyó** | `A ⊂ B si y solo si ∀x: x ∈ A ∩ B` |

> **PARCIAL** — Reconstrucción parcial — algunos símbolos fallaron (CER: 0.14, dist: 5).

### ✅ `R4_fisica_optica` — Física / Óptica

**Símbolos probados:** `Å` `≥`

| | Texto |
|---|---|
| **Original** | `La longitud de onda λ = 550 Å satisface λ ≥ λ_min donde λ_min = 400 Å` |
| **Corrupto** | `La longitud de onda λ = 550 Ã… satisface λ â¥ λ_min donde λ_min = 400 Ã…` |
| **LLM reconstruyó** | `La longitud de onda λ = 550 Å satisface λ ≥ λ_min donde λ_min = 400 Å` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R5_quimica` — Química

**Símbolos probados:** `⇌` `∃!` `×`

| | Texto |
|---|---|
| **Original** | `La reacción A + B ⇌ C es reversible si ∃! equilibrio donde A × B = C` |
| **Corrupto** | `La reacción A + B â‡Œ C es reversible si â! equilibrio donde A Ã B = C` |
| **LLM reconstruyó** | `La reacción A + B ⇌ C es reversible si ∃! equilibrio donde A × B = C` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### 🟠 `R6_logica_pred` — Lógica de Predicados

**Símbolos probados:** `∀` `∈` `ℝ` `∃!` `→` `↔` `≥`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: ∃! y tal que x → y y y ↔ x ≥ 0` |
| **Corrupto** | `âx â â: â! y tal que x â y y y âÃ x â¥ 0` |
| **LLM reconstruyó** | `∀x ∈ ℝ: ∃! y tal que x → y y y → ∃x ≥ 0` |

> **PARCIAL** — Reconstrucción parcial — algunos símbolos fallaron (CER: 0.05, dist: 2).

### 🟠 `R7_musica_filologia` — Música / Filología

**Símbolos probados:** `♭` `·` `†`

| | Texto |
|---|---|
| **Original** | `La escala comienza en si♭ · omnia †vincit† amor` |
| **Corrupto** | `La escala comienza en siâ™­ Â· omnia â vincitâ  amor` |
| **LLM reconstruyó** | `La escala comienza en si♭ Â· omnia † amor` |

> **PARCIAL** — Reconstrucción parcial — algunos símbolos fallaron (CER: 0.17, dist: 8).

