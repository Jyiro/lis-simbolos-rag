# Reporte de Experimento — Reconstrucción de Mojibake (ES + EN)

| Campo | Valor |
|---|---|
| Modelo | `phi-4` |
| Backend | `llama_cpp` |
| Run ID | `20260820_164001_phi-4_llama_cpp_rebuild` |
| Total exactos | 10/14 |
| CER promedio global | 0.007 |
| CER promedio ES | 0.010 |
| CER promedio EN | 0.005 |

---

## Resumen (todos los fragmentos)

| Lang | Fragmento | Dominio | Símbolos | Resultado | Dist | CER |
|:---:|---|---|---|:---:|---:|---:|
| 🇪🇸 | `R1_logica_modal` | Lógica Modal | `□` `→` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇪🇸 | `R2_calculo_integral` | Cálculo | `∀` `∈` `ℝ` `≥` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇪🇸 | `R3_conjuntos` | Teoría de Conjuntos | `⊂` `∀` `∈` `→` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇪🇸 | `R4_fisica_optica` | Física / Óptica | `Å` `≥` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇪🇸 | `R5_quimica` | Química | `⇌` `∃!` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇪🇸 | `R6_logica_pred` | Lógica de Predicados | `∀` `∈` `ℝ` `∃!` `→` `↔` `≥` | 🟡 **CASI** | 1 | 0.026 |
| 🇪🇸 | `R7_musica_filologia` | Música / Filología | `♭` `·` `†` | 🟡 **CASI** | 2 | 0.041 |
| 🇬🇧 | `R1_modal_logic` | Modal Logic | `□` `→` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇬🇧 | `R2_calculus` | Calculus | `∀` `∈` `ℝ` `≥` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇬🇧 | `R3_set_theory` | Set Theory | `⊂` `∀` `∈` `→` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇬🇧 | `R4_optics` | Physics / Optics | `Å` `≥` | 🟡 **CASI** | 1 | 0.015 |
| 🇬🇧 | `R5_chemistry` | Chemistry | `⇌` `∃!` `×` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇬🇧 | `R6_predicate_logic` | Predicate Logic | `∀` `∈` `ℝ` `∃!` `→` `↔` `≥` | ✅ **PERFECTO** | 0 | 0.000 |
| 🇬🇧 | `R7_music_philology` | Music / Philology | `♭` `·` `†` | 🟡 **CASI** | 1 | 0.022 |

---

## Detalle — Español 🇪🇸

### ✅ `R1_logica_modal` — Lógica Modal

**Símbolos probados:** `□` `→`

| | Texto |
|---|---|
| **Original** | `Si □P → P y □Q → Q, entonces □(P → Q) → (□P → □Q)` |
| **Corrupto** | `Si â–¡P â P y â–¡Q â Q, entonces â–¡(P â Q) â (â–¡P â â–¡Q)` |
| **LLM reconstruyó** | `Si □P → P y □Q → Q, entonces □(P → Q) → (□P → □Q)` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R2_calculo_integral` — Cálculo

**Símbolos probados:** `∀` `∈` `ℝ` `≥` `×`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: si f(x) ≥ 0, entonces f × g es continua` |
| **Corrupto** | `âx â â: si f(x) â¥ 0, entonces f Ã g es continua` |
| **LLM reconstruyó** | `∀x ∈ ℝ: si f(x) ≥ 0, entonces f × g es continua` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R3_conjuntos` — Teoría de Conjuntos

**Símbolos probados:** `⊂` `∀` `∈` `→`

| | Texto |
|---|---|
| **Original** | `A ⊂ B si y solo si ∀x: x ∈ A → x ∈ B` |
| **Corrupto** | `A âŠ‚ B si y solo si âx: x â A â x â B` |
| **LLM reconstruyó** | `A ⊂ B si y solo si ∀x: x ∈ A → x ∈ B` |

> **PERFECTO** — Reconstrucción exacta del texto original.

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

### 🟡 `R6_logica_pred` — Lógica de Predicados

**Símbolos probados:** `∀` `∈` `ℝ` `∃!` `→` `↔` `≥`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: ∃! y tal que x → y y y ↔ x ≥ 0` |
| **Corrupto** | `âx â â: â! y tal que x â y y y âÃ x â¥ 0` |
| **LLM reconstruyó** | `∀x ∈ ℝ: ∃! y tal que x ∈ y y y ↔ x ≥ 0` |

> **CASI** — Reconstrucción casi perfecta (CER: 0.03, dist: 1).

### 🟡 `R7_musica_filologia` — Música / Filología

**Símbolos probados:** `♭` `·` `†`

| | Texto |
|---|---|
| **Original** | `La escala comienza en si♭ · omnia †vincit† amor` |
| **Corrupto** | `La escala comienza en siâ™­ Â· omnia â vincitâ  amor` |
| **LLM reconstruyó** | `La escala comienza en si♭ · omnia † vincit † amor` |

> **CASI** — Reconstrucción casi perfecta (CER: 0.04, dist: 2).


---

## Detalle — English 🇬🇧

### ✅ `R1_modal_logic` — Modal Logic

**Símbolos probados:** `□` `→`

| | Texto |
|---|---|
| **Original** | `If □P → P and □Q → Q, then □(P → Q) → (□P → □Q)` |
| **Corrupto** | `If â–¡P â P and â–¡Q â Q, then â–¡(P â Q) â (â–¡P â â–¡Q)` |
| **LLM reconstruyó** | `If □P → P and □Q → Q, then □(P → Q) → (□P → □Q)` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R2_calculus` — Calculus

**Símbolos probados:** `∀` `∈` `ℝ` `≥` `×`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: if f(x) ≥ 0, then f × g is continuous` |
| **Corrupto** | `âx â â: if f(x) â¥ 0, then f Ã g is continuous` |
| **LLM reconstruyó** | `∀x ∈ ℝ: if f(x) ≥ 0, then f × g is continuous` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R3_set_theory` — Set Theory

**Símbolos probados:** `⊂` `∀` `∈` `→`

| | Texto |
|---|---|
| **Original** | `A ⊂ B if and only if ∀x: x ∈ A → x ∈ B` |
| **Corrupto** | `A âŠ‚ B if and only if âx: x â A â x â B` |
| **LLM reconstruyó** | `A ⊂ B if and only if ∀x: x ∈ A → x ∈ B` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### 🟡 `R4_optics` — Physics / Optics

**Símbolos probados:** `Å` `≥`

| | Texto |
|---|---|
| **Original** | `The wavelength λ = 550 Å satisfies λ ≥ λ_min where λ_min = 400 Å` |
| **Corrupto** | `The wavelength λ = 550 Ã… satisfies λ â¥ λ_min where λ_min = 400 Ã…` |
| **LLM reconstruyó** | `The wavelength λ = 550 Å satisfies λ ≥ λ_min where λ_min = 400 Å.` |

> **CASI** — Reconstrucción casi perfecta (CER: 0.02, dist: 1).

### ✅ `R5_chemistry` — Chemistry

**Símbolos probados:** `⇌` `∃!` `×`

| | Texto |
|---|---|
| **Original** | `The reaction A + B ⇌ C is reversible if ∃! equilibrium where A × B = C` |
| **Corrupto** | `The reaction A + B â‡Œ C is reversible if â! equilibrium where A Ã B = C` |
| **LLM reconstruyó** | `The reaction A + B ⇌ C is reversible if ∃! equilibrium where A × B = C` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### ✅ `R6_predicate_logic` — Predicate Logic

**Símbolos probados:** `∀` `∈` `ℝ` `∃!` `→` `↔` `≥`

| | Texto |
|---|---|
| **Original** | `∀x ∈ ℝ: ∃! y such that x → y and y ↔ x ≥ 0` |
| **Corrupto** | `âx â â: â! y such that x â y and y âÃ x â¥ 0` |
| **LLM reconstruyó** | `∀x ∈ ℝ: ∃! y such that x → y and y ↔ x ≥ 0` |

> **PERFECTO** — Reconstrucción exacta del texto original.

### 🟡 `R7_music_philology` — Music / Philology

**Símbolos probados:** `♭` `·` `†`

| | Texto |
|---|---|
| **Original** | `The scale starts on B♭ · omnia †vincit† amor` |
| **Corrupto** | `The scale starts on Bâ™­ Â· omnia â vincitâ  amor` |
| **LLM reconstruyó** | `The scale starts on B♭ · omnia † vincit† amor` |

> **CASI** — Reconstrucción casi perfecta (CER: 0.02, dist: 1).

