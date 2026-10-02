# Benchmark de Preservación Simbólica — Extracción Base

**Corpus:** 6 documentos (matemática, lógica, física, química, música, literatura)

**Fase:** Baseline — Extracción de texto Unicode nativo

**Extractores:** pdfplumber, PyMuPDF, pypdf

**Fecha:** 2026-09-09 18:05


> **Nota metodológica:** pdfplumber es el motor interno de RAGFlow/DeepDoc para PDFs

> con texto Unicode nativo. Sus resultados representan el **techo teórico de preservación**

> de la capa de extracción. Si pdfplumber pierde un símbolo, DeepDoc tampoco puede recuperarlo.


## 1. Tabla Resumen — Domain CPR por Documento


| Documento | pdfplumber | PyMuPDF | pypdf |

|---|---|---|---|
| 01_matematica | 100.0% | 100.0% | 100.0% |
| 02_logica | 100.0% | 100.0% | 100.0% |
| 03_fisica | 100.0% | 100.0% | 100.0% |
| 04_quimica | 100.0% | 100.0% | 100.0% |
| 05_musica | 100.0% | 100.0% | 100.0% |
| 06_literatura | 100.0% | 100.0% | 100.0% |

## 2. Detalles (02_logica)

| Símbolo | Nombre | GT Count | pdfplumber | PyMuPDF | pypdf |

|---|---|---|---|---|---|
| → | ARROW_RIGHT | 46 | 46 (100.0%) | 46 (100.0%) | 46 (100.0%) |
| ∈ | ELEM_OF | 31 | 31 (100.0%) | 31 (100.0%) | 31 (100.0%) |
| ⊂ | SUBSET | 1 | 1 (100.0%) | 1 (100.0%) | 1 (100.0%) |
| ≤ | LEQ | 2 | 2 (100.0%) | 2 (100.0%) | 2 (100.0%) |
| ≥ | GEQ | 1 | 1 (100.0%) | 1 (100.0%) | 1 (100.0%) |
| ≠ | NEQ | 2 | 2 (100.0%) | 2 (100.0%) | 2 (100.0%) |
| ∀ | FOR_ALL | 51 | 51 (100.0%) | 51 (100.0%) | 51 (100.0%) |
| ∃ | EXISTS | 30 | 30 (100.0%) | 30 (100.0%) | 30 (100.0%) |
| ∄ | NOT_EXISTS | 1 | 1 (100.0%) | 1 (100.0%) | 1 (100.0%) |
| ¬ | NOT | 58 | 58 (100.0%) | 58 (100.0%) | 58 (100.0%) |
| ∧ | AND | 51 | 51 (100.0%) | 51 (100.0%) | 51 (100.0%) |
| ∨ | OR | 30 | 30 (100.0%) | 30 (100.0%) | 30 (100.0%) |
| ↔ | IFF | 43 | 43 (100.0%) | 43 (100.0%) | 43 (100.0%) |
| ⊕ | XOR | 1 | 1 (100.0%) | 1 (100.0%) | 1 (100.0%) |
| ⊢ | TURNSTILE | 12 | 12 (100.0%) | 12 (100.0%) | 12 (100.0%) |
| ⊨ | MODELS | 6 | 6 (100.0%) | 6 (100.0%) | 6 (100.0%) |
| ⊆ | SUBSETEQ | 8 | 8 (100.0%) | 8 (100.0%) | 8 (100.0%) |
| □ | NECESSARILY | 9 | 9 (100.0%) | 9 (100.0%) | 9 (100.0%) |
| ◇ | POSSIBLY | 5 | 5 (100.0%) | 5 (100.0%) | 5 (100.0%) |
| ⊤ | TOP | 6 | 6 (100.0%) | 6 (100.0%) | 6 (100.0%) |
| ⊥ | BOTTOM | 6 | 6 (100.0%) | 6 (100.0%) | 6 (100.0%) |