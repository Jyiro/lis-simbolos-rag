# Experimento 12 — Preservación con Fuentes TTF (Unicode nativo)

Generación de PDF sintético con fuente `DejaVuSans.ttf` embebida para comprobar si el bug de `pdfminer.six/pdfplumber` persiste al cambiar la codificación de fuente (desde Type1/CFF MacRoman a TrueType Unicode).

| Símbolo | Nombre | Ground Truth | pdfplumber | PyMuPDF | pypdf | CPR (plumber) |
|---|---|---|---|---|---|---|
| ∀ | FOR_ALL | 2 | 2 | 2 | 2 | 100% |
| ∃ | EXISTS | 2 | 2 | 2 | 2 | 100% |
| ∄ | NOT_EXISTS | 2 | 2 | 2 | 2 | 100% |
| ¬ | NOT | 2 | 2 | 2 | 2 | 100% |
| ∧ | AND | 2 | 2 | 2 | 2 | 100% |
| ∨ | OR | 2 | 2 | 2 | 2 | 100% |
| → | IMPLIES | 2 | 2 | 2 | 2 | 100% |
| ↔ | IFF | 2 | 2 | 2 | 2 | 100% |
| ⊢ | TURNSTILE | 2 | 2 | 2 | 2 | 100% |
| ⊨ | MODELS | 2 | 2 | 2 | 2 | 100% |
| □ | NECESSARILY | 2 | 2 | 2 | 2 | 100% |
| ◇ | POSSIBLY | 2 | 2 | 2 | 2 | 100% |
| ⊤ | TOP | 2 | 2 | 2 | 2 | 100% |
| ⊥ | BOTTOM | 2 | 2 | 2 | 2 | 100% |
| ⊕ | XOR | 2 | 2 | 2 | 2 | 100% |
| ∈ | ELEM_OF | 2 | 2 | 2 | 2 | 100% |
| ∉ | NOT_ELEM | 2 | 2 | 2 | 2 | 100% |
| ⊂ | SUBSET | 2 | 2 | 2 | 2 | 100% |
| ⊆ | SUBSETEQ | 2 | 2 | 2 | 2 | 100% |
| ∅ | EMPTY_SET | 2 | 2 | 2 | 2 | 100% |
| ∩ | INTERSECT | 2 | 2 | 2 | 2 | 100% |
| ∪ | UNION | 2 | 2 | 2 | 2 | 100% |
| ∑ | SUM | 2 | 2 | 2 | 2 | 100% |
| ∏ | PRODUCT | 2 | 2 | 2 | 2 | 100% |
| ∫ | INTEGRAL | 2 | 2 | 2 | 2 | 100% |
| √ | SQRT | 2 | 2 | 2 | 2 | 100% |
| ∞ | INFINITY | 2 | 2 | 2 | 2 | 100% |
| ≤ | LEQ | 2 | 2 | 2 | 2 | 100% |
| ≥ | GEQ | 2 | 2 | 2 | 2 | 100% |
| ≠ | NEQ | 2 | 2 | 2 | 2 | 100% |
| ≈ | APPROX | 2 | 2 | 2 | 2 | 100% |
| ≡ | EQUIV | 2 | 2 | 2 | 2 | 100% |
| ∝ | PROPORTIONAL | 2 | 2 | 2 | 2 | 100% |
| ∂ | PARTIAL | 2 | 2 | 2 | 2 | 100% |
| ∇ | NABLA | 2 | 2 | 2 | 2 | 100% |
| α | ALPHA | 2 | 2 | 2 | 2 | 100% |
| β | BETA | 2 | 2 | 2 | 2 | 100% |
| γ | GAMMA | 2 | 2 | 2 | 2 | 100% |
| λ | LAMBDA | 2 | 2 | 2 | 2 | 100% |
| μ | MU | 2 | 2 | 2 | 2 | 100% |
| π | PI | 2 | 2 | 2 | 2 | 100% |
| φ | PHI | 2 | 2 | 2 | 2 | 100% |
| ψ | PSI | 2 | 2 | 2 | 2 | 100% |
| ω | OMEGA | 2 | 2 | 2 | 2 | 100% |
| Γ | GAMMA_UP | 2 | 2 | 2 | 2 | 100% |
| Δ | DELTA_UP | 2 | 2 | 2 | 2 | 100% |
| Σ | SIGMA_UP | 2 | 2 | 1 | 2 | 100% |
| Φ | PHI_UP | 2 | 2 | 1 | 2 | 100% |

**Global CPR (pdfplumber):** 100.0%

## Conclusión
pdfplumber extrajo perfectamente todos los símbolos. Esto confirma que **el bug es exclusivo de fuentes CFF/Type1 con encodings defectuosos (como MacRomanEncoding en Computer Modern)**. PDFs modernos que usen fuentes TrueType u OpenType con mapas Unicode directos no se ven afectados.