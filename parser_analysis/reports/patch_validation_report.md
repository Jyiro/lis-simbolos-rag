# Reporte de Validación — Monkey-Patch pdfminer.six (4 Extractores)

**Fecha:** 2026-09-17 16:36

> **Nota:** `pypdf` funciona como ground-truth. `fitz` y `pymupdf4llm` se incluyen para demostrar que el parche de `pdfminer` (que arregla a `pdfplumber` y RAGFlow) no los afecta, pues su falla es por un motor C++ diferente.

## Tabla de Resultados

| Documento | Símbolo | pdfplumber (Antes) | pdfplumber (Después) | pypdf (Ref) | PyMuPDF | pymupdf4llm | Δ (plumber) | OK? |
|---|---|---|---|---|---|---|---|---|
| AbstractAlgebra_cap1-3_symbols | **SUM** | 0 | **65** | 65 | 0 | 0 | +65 | ✅ |
| AbstractAlgebra_cap1-3_symbols | **PRODUCT** | 0 | **19** | 19 | 0 | 0 | +19 | ✅ |
| FirstOrderLogic_complete | **TURNSTILE** | 640 | **640** | 640 | 216 | 178 | +0 | ✅ |
| ModalLogicFundamentally_comple | **TURNSTILE** | 52 | **52** | 52 | 52 | 52 | +0 | ✅ |
| ModalLogicFundamentally_comple | **MODELS** | 0 | **2** | 2 | 2 | 2 | +2 | ✅ |
| ModalLogicalNeuralNetworks_com | **NECESSARILY** | 83 | **83** | 83 | 83 | 71 | +0 | ✅ |
| 2609.16957v1_Reduction_techniq | **NECESSARILY** | 0 | **26** | 26 | 26 | 11 | +26 | ✅ |
| 2609.17177v1_Finite_Borel_asym | **SUM** | 0 | **10** | 10 | 0 | 0 | +10 | ✅ |
| 2609.17438v2_Quandles_associat | **SUM** | 0 | **6** | 6 | 0 | 0 | +6 | ✅ |
| 2609.17438v2_Quandles_associat | **NECESSARILY** | 0 | **17** | 17 | 17 | 16 | +17 | ✅ |
| 2609.17438v2_Quandles_associat | **TURNSTILE** | 3 | **3** | 3 | 3 | 2 | +0 | ✅ |
| 2609.18032v1_Scott_topologies_ | **PRODUCT** | 0 | **29** | 29 | 0 | 0 | +29 | ✅ |
| 2609.18032v1_Scott_topologies_ | **NECESSARILY** | 25 | **25** | 25 | 25 | 22 | +0 | ✅ |
| 2609.18433v1_Generating_the_tw | **NECESSARILY** | 0 | **1** | 1 | 1 | 1 | +1 | ✅ |
| 2609.18486v1_Towards_a_Proof-T | **SUM** | 0 | **3** | 3 | 0 | 0 | +3 | ✅ |
| 2609.18730v1_A_minimal_type_of | **SUM** | 0 | **9** | 9 | 0 | 0 | +9 | ✅ |
| 2609.18730v1_A_minimal_type_of | **NECESSARILY** | 11 | **11** | 11 | 11 | 7 | +0 | ✅ |

## Resultado Global: ⚠️ PATCH PARCIAL — revisar