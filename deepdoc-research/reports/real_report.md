# Benchmark de Preservación Simbólica — EAR (Extractor Agreement Rate)

**Fase:** 2 (PDFs Reales)
**Fecha:** 2026-09-16 19:20

> **Extractor Agreement Rate (EAR)**: Mide el consenso entre extractores. EAR < 100% indica discrepancia,
> evidenciando que la extracción base no es confiable para ese símbolo en ese documento. DeepDoc (RAGFlow)
> hereda estas vulnerabilidades.

## 1. Resumen Ejecutivo por PDF

| Documento | Símbolos Presentes | Discrepancias | Peor Símbolo | Peor EAR |
|---|---|---|---|---|
| AbstractAlgebra | 23 | 20 | SUM | 0.0% |
| FirstOrderLogic | 15 | 11 | IMPLIES | 26.3% |
| ModalLogicFundamentally | 22 | 11 | MODELS | 0.0% |
| ModalLogicalNeuralNetworks | 21 | 9 | PARTIAL | 25.0% |

## 2. Tabla de EAR Cruzada

| Símbolo | Nombre | AbstractAlgebra | FirstOrderLogic | ModalLogicFundamentally | ModalLogicalNeuralNetworks |
|---|---| --- | --- | --- | --- |
| ∀ | FOR_ALL | — | **69.8%** | **74.2%** | **33.3%** |
| ∃ | EXISTS | — | **80.0%** | **73.3%** | — |
| ¬ | NOT | — | **89.6%** | **88.5%** | 100% |
| ∧ | AND | — | **96.0%** | **88.5%** | 100% |
| ∨ | OR | — | **85.7%** | **69.2%** | 100% |
| → | IMPLIES | **76.3%** | **26.3%** | 100% | **96.4%** |
| ↔ | IFF | — | **33.3%** | — | 100% |
| ⊢ | TURNSTILE | — | **28.1%** | **65.4%** | — |
| ⊨ | MODELS | — | — | **0.0%** | — |
| □ | NECESSARILY | — | — | — | **86.7%** |
| ⊤ | TOP | — | — | 100% | 100% |
| ⊥ | BOTTOM | — | — | 100% | — |
| ⊕ | XOR | **25.0%** | — | — | — |
| ∈ | ELEM_OF | **83.1%** | **83.2%** | **95.8%** | **66.7%** |
| ⊂ | SUBSET | **79.2%** | 100% | — | — |
| ⊆ | SUBSETEQ | — | **80.0%** | **80.0%** | 100% |
| ∅ | EMPTY_SET | — | — | 100% | — |
| ∩ | INTERSECT | **52.2%** | — | 100% | — |
| ∪ | UNION | — | 100% | 100% | — |
| ∑ | SUM | **0.0%** | — | — | — |
| ∏ | PRODUCT | **0.0%** | — | — | — |
| √ | SQRT | **69.4%** | — | — | — |
| ∞ | INFINITY | **66.7%** | — | — | 100% |
| ≤ | LEQ | **49.2%** | — | **83.7%** | **83.3%** |
| ≥ | GEQ | **81.8%** | 100% | 100% | **72.2%** |
| ≈ | APPROX | **61.5%** | — | — | 100% |
| ≡ | EQUIV | **66.7%** | — | — | 100% |
| ∂ | PARTIAL | **0.0%** | — | — | **25.0%** |
| ∇ | NABLA | — | — | — | 100% |
| α | ALPHA | **76.9%** | — | 100% | 100% |
| β | BETA | **60.7%** | — | 100% | **96.8%** |
| γ | GAMMA | **83.3%** | — | 100% | — |
| λ | LAMBDA | **75.0%** | — | — | 100% |
| π | PI | 100% | — | 100% | — |
| φ | PHI | 100% | — | — | — |
| ψ | PSI | 100% | — | **69.5%** | — |
| ω | OMEGA | **85.1%** | — | — | — |
| Γ | GAMMA_UP | — | **77.6%** | — | **76.9%** |
| Σ | SIGMA_UP | — | 100% | — | — |
| Φ | PHI_UP | **55.1%** | — | — | — |

## 3. Detalles de Discrepancias

### AbstractAlgebra

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | pymupdf4llm | EAR |
|---|---|---|---|---|---|---|
| ∑ | SUM | 0 | 0 | 65 | 0 | **0.0%** |
| ∏ | PRODUCT | 0 | 0 | 19 | 0 | **0.0%** |
| ∂ | PARTIAL | 2 | 2 | 2 | 0 | **0.0%** |
| ⊕ | XOR | 24 | 24 | 24 | 6 | **25.0%** |
| ≤ | LEQ | 59 | 59 | 59 | 29 | **49.2%** |
| ∩ | INTERSECT | 23 | 23 | 23 | 12 | **52.2%** |
| Φ | PHI_UP | 49 | 49 | 49 | 27 | **55.1%** |
| β | BETA | 112 | 112 | 112 | 68 | **60.7%** |
| ≈ | APPROX | 52 | 52 | 52 | 32 | **61.5%** |
| ∞ | INFINITY | 12 | 12 | 12 | 8 | **66.7%** |
| ≡ | EQUIV | 3 | 3 | 3 | 2 | **66.7%** |
| √ | SQRT | 61 | 61 | 62 | 43 | **69.4%** |
| λ | LAMBDA | 8 | 8 | 8 | 6 | **75.0%** |
| → | IMPLIES | 156 | 156 | 156 | 119 | **76.3%** |
| α | ALPHA | 454 | 454 | 454 | 349 | **76.9%** |
| ⊂ | SUBSET | 48 | 48 | 48 | 38 | **79.2%** |
| ≥ | GEQ | 11 | 11 | 11 | 9 | **81.8%** |
| ∈ | ELEM_OF | 361 | 361 | 361 | 300 | **83.1%** |
| γ | GAMMA | 12 | 12 | 12 | 10 | **83.3%** |
| ω | OMEGA | 47 | 47 | 47 | 40 | **85.1%** |

### FirstOrderLogic

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | pymupdf4llm | EAR |
|---|---|---|---|---|---|---|
| → | IMPLIES | 19 | 19 | 19 | 5 | **26.3%** |
| ⊢ | TURNSTILE | 640 | 216 | 640 | 180 | **28.1%** |
| ↔ | IFF | 9 | 9 | 9 | 3 | **33.3%** |
| ∀ | FOR_ALL | 53 | 53 | 53 | 37 | **69.8%** |
| Γ | GAMMA_UP | 67 | 67 | 67 | 52 | **77.6%** |
| ∃ | EXISTS | 10 | 10 | 10 | 8 | **80.0%** |
| ⊆ | SUBSETEQ | 5 | 5 | 5 | 4 | **80.0%** |
| ∈ | ELEM_OF | 125 | 125 | 125 | 104 | **83.2%** |
| ∨ | OR | 28 | 28 | 28 | 24 | **85.7%** |
| ¬ | NOT | 48 | 48 | 48 | 43 | **89.6%** |
| ∧ | AND | 25 | 25 | 25 | 24 | **96.0%** |

### ModalLogicFundamentally

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | pymupdf4llm | EAR |
|---|---|---|---|---|---|---|
| ⊨ | MODELS | 0 | 2 | 2 | 2 | **0.0%** |
| ⊢ | TURNSTILE | 52 | 52 | 52 | 34 | **65.4%** |
| ∨ | OR | 39 | 39 | 39 | 27 | **69.2%** |
| ψ | PSI | 59 | 59 | 59 | 41 | **69.5%** |
| ∃ | EXISTS | 45 | 45 | 45 | 33 | **73.3%** |
| ∀ | FOR_ALL | 31 | 31 | 31 | 23 | **74.2%** |
| ⊆ | SUBSETEQ | 15 | 15 | 15 | 12 | **80.0%** |
| ≤ | LEQ | 208 | 208 | 208 | 174 | **83.7%** |
| ¬ | NOT | 410 | 410 | 410 | 363 | **88.5%** |
| ∧ | AND | 61 | 61 | 61 | 54 | **88.5%** |
| ∈ | ELEM_OF | 265 | 265 | 265 | 254 | **95.8%** |

### ModalLogicalNeuralNetworks

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | pymupdf4llm | EAR |
|---|---|---|---|---|---|---|
| ∂ | PARTIAL | 8 | 8 | 8 | 2 | **25.0%** |
| ∀ | FOR_ALL | 3 | 3 | 3 | 1 | **33.3%** |
| ∈ | ELEM_OF | 24 | 24 | 24 | 16 | **66.7%** |
| ≥ | GEQ | 18 | 18 | 18 | 13 | **72.2%** |
| Γ | GAMMA_UP | 13 | 13 | 13 | 10 | **76.9%** |
| ≤ | LEQ | 24 | 24 | 24 | 20 | **83.3%** |
| □ | NECESSARILY | 83 | 83 | 83 | 72 | **86.7%** |
| → | IMPLIES | 55 | 55 | 55 | 53 | **96.4%** |
| β | BETA | 31 | 31 | 31 | 30 | **96.8%** |
