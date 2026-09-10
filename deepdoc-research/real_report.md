# Benchmark de Preservación Simbólica — EAR (Extractor Agreement Rate)

**Fase:** 2 (PDFs Reales)
**Fecha:** 2026-09-09 19:26

> **Extractor Agreement Rate (EAR)**: Mide el consenso entre extractores. EAR < 100% indica discrepancia,
> evidenciando que la extracción base no es confiable para ese símbolo en ese documento. DeepDoc (RAGFlow)
> hereda estas vulnerabilidades.

## 1. Resumen Ejecutivo por PDF

| Documento | Símbolos Presentes | Discrepancias | Peor Símbolo | Peor EAR |
|---|---|---|---|---|
| AbstractAlgebra | 23 | 3 | SUM | 0.0% |
| FirstOrderLogic | 15 | 1 | TURNSTILE | 33.8% |
| ModalLogicFundamentally | 22 | 1 | MODELS | 0.0% |
| ModalLogicalNeuralNetworks | 21 | 0 | - | 100.0% |

## 2. Tabla de EAR Cruzada

| Símbolo | Nombre | AbstractAlgebra | FirstOrderLogic | ModalLogicFundamentally | ModalLogicalNeuralNetworks |
|---|---| --- | --- | --- | --- |
| ∀ | FOR_ALL | — | 100% | 100% | 100% |
| ∃ | EXISTS | — | 100% | 100% | — |
| ¬ | NOT | — | 100% | 100% | 100% |
| ∧ | AND | — | 100% | 100% | 100% |
| ∨ | OR | — | 100% | 100% | 100% |
| → | IMPLIES | 100% | 100% | 100% | 100% |
| ↔ | IFF | — | 100% | — | 100% |
| ⊢ | TURNSTILE | — | **33.8%** | 100% | — |
| ⊨ | MODELS | — | — | **0.0%** | — |
| □ | NECESSARILY | — | — | — | 100% |
| ⊤ | TOP | — | — | 100% | 100% |
| ⊥ | BOTTOM | — | — | 100% | — |
| ⊕ | XOR | 100% | — | — | — |
| ∈ | ELEM_OF | 100% | 100% | 100% | 100% |
| ⊂ | SUBSET | 100% | 100% | — | — |
| ⊆ | SUBSETEQ | — | 100% | 100% | 100% |
| ∅ | EMPTY_SET | — | — | 100% | — |
| ∩ | INTERSECT | 100% | — | 100% | — |
| ∪ | UNION | — | 100% | 100% | — |
| ∑ | SUM | **0.0%** | — | — | — |
| ∏ | PRODUCT | **0.0%** | — | — | — |
| √ | SQRT | **98.4%** | — | — | — |
| ∞ | INFINITY | 100% | — | — | 100% |
| ≤ | LEQ | 100% | — | 100% | 100% |
| ≥ | GEQ | 100% | 100% | 100% | 100% |
| ≈ | APPROX | 100% | — | — | 100% |
| ≡ | EQUIV | 100% | — | — | 100% |
| ∂ | PARTIAL | 100% | — | — | 100% |
| ∇ | NABLA | — | — | — | 100% |
| α | ALPHA | 100% | — | 100% | 100% |
| β | BETA | 100% | — | 100% | 100% |
| γ | GAMMA | 100% | — | 100% | — |
| λ | LAMBDA | 100% | — | — | 100% |
| π | PI | 100% | — | 100% | — |
| φ | PHI | 100% | — | — | — |
| ψ | PSI | 100% | — | 100% | — |
| ω | OMEGA | 100% | — | — | — |
| Γ | GAMMA_UP | — | 100% | — | 100% |
| Σ | SIGMA_UP | — | 100% | — | — |
| Φ | PHI_UP | 100% | — | — | — |

## 3. Detalles de Discrepancias

### AbstractAlgebra

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | EAR |
|---|---|---|---|---|---|
| ∑ | SUM | 0 | 0 | 65 | **0.0%** |
| ∏ | PRODUCT | 0 | 0 | 19 | **0.0%** |
| √ | SQRT | 61 | 61 | 62 | **98.4%** |

### FirstOrderLogic

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | EAR |
|---|---|---|---|---|---|
| ⊢ | TURNSTILE | 640 | 216 | 640 | **33.8%** |

### ModalLogicFundamentally

| Símbolo | Nombre | pdfplumber | PyMuPDF | pypdf | EAR |
|---|---|---|---|---|---|
| ⊨ | MODELS | 0 | 2 | 2 | **0.0%** |
