# EAR sobre Corpus arXiv Expandido

**Fecha:** 2026-09-16 23:10  
**Total de PDFs analizados:** 30  
**PDFs con al menos una discrepancia:** 7 (23%)  
**Extractores:** `pdfplumber`, `pymupdf`, `pypdf`  

## Síntesis por documento

| Documento | Símbolos | Discrepancias | EAR medio | Peor símbolo | Peor EAR |
|---|---|---|---|---|---|
| 2609.15879v1_Finite_Dependence_and_Invariance | 23 | 0 | 100% | — | 100.0% |
| 2609.16280v1_Regular_Sublattices_O_Closed_Ide | 15 | 0 | 100% | — | 100.0% |
| 2609.16442v1_A_Differential_Algebraic_Framewo | 15 | 0 | 100% | — | 100.0% |
| 2609.16632v1_The_prime_spectrum_of_the_talent | 21 | 0 | 100% | — | 100.0% |
| 2609.16798v1_On_Models_of_the_Planar_Lambda_C | 8 | 0 | 100% | — | 100.0% |
| 2609.16881v1_An_extension_of_Subcomplete_Forc | 22 | 0 | 100% | — | 100.0% |
| 2609.16957v1_Reduction_techniques_for_the_der | 15 | 1 | 0% | NECESSARILY | 0.0% |
| 2609.17087v1_The_Boolean_Prime_Ideal_Theorem_ | 13 | 0 | 100% | — | 100.0% |
| 2609.17153v1_Two_variants_of_minimality_in_fo | 16 | 0 | 100% | — | 100.0% |
| 2609.17177v1_Finite_Borel_asymptotic_dimensio | 13 | 1 | 0% | SUM | 0.0% |
| 2609.17324v1_Universal_Properties_of_Petri_Ne | 10 | 0 | 100% | — | 100.0% |
| 2609.17364v1_The_Classical_Weisfeiler-Leman_A | 19 | 0 | 100% | — | 100.0% |
| 2609.17438v2_Quandles_associated_with_group_a | 18 | 2 | 0% | NECESSARILY | 0.0% |
| 2609.17767v1_Fuzzy_subhyperspaces_generated_b | 15 | 0 | 100% | — | 100.0% |
| 2609.17828v1_On_definable_Galois_theory_and_d | 20 | 0 | 100% | — | 100.0% |
| 2609.17879v1_Entropy_and_Translation_Length_i | 17 | 0 | 100% | — | 100.0% |
| 2609.17994v1_Almost-everywhere_computation_of | 24 | 0 | 100% | — | 100.0% |
| 2609.18001v1_1-genericity_and_almost_everywhe | 13 | 0 | 100% | — | 100.0% |
| 2609.18032v1_Scott_topologies_on_products_of_ | 19 | 1 | 0% | PRODUCT | 0.0% |
| 2609.18144v1_Growth_functions_of_algebras_and | 12 | 0 | 100% | — | 100.0% |
| 2609.18371v1_Coding_is_non-robust | 27 | 0 | 100% | — | 100.0% |
| 2609.18380v1_A_computational_framework_for_mu | 15 | 0 | 100% | — | 100.0% |
| 2609.18433v1_Generating_the_twist_subgroup_of | 10 | 1 | 0% | NECESSARILY | 0.0% |
| 2609.18484v1_Rational_Reductions_and_Regular_ | 25 | 0 | 100% | — | 100.0% |
| 2609.18486v1_Towards_a_Proof-Theoretic_Analys | 13 | 1 | 0% | SUM | 0.0% |
| 2609.18513v1_Finite_groups_with_large_power-a | 9 | 0 | 100% | — | 100.0% |
| 2609.18630v1_An_order_automorphism_of_a_Dlab_ | 17 | 0 | 100% | — | 100.0% |
| 2609.18681v1_A_parity_obstruction_to_complete | 13 | 0 | 100% | — | 100.0% |
| 2609.18730v1_A_minimal_type_of_Morley_rank_ω_ | 16 | 1 | 0% | SUM | 0.0% |
| 2609.19086v1_On_the_number_of_modular_pairs_i | 15 | 0 | 100% | — | 100.0% |

## Síntesis por símbolo (frecuencia de fallo total en pdfplumber)

Un 'fallo' se cuenta cuando pdfplumber extrae 0 ocurrencias de un símbolo
que sí es detectado por pymupdf o pypdf en ese documento.

| Símbolo | Nombre | Docs con fallo pdfplumber | % de docs |
|---|---|---|---|
| ∑ | SUM | 4/30 | 13% |
| □ | NECESSARILY | 3/30 | 10% |
| ∏ | PRODUCT | 1/30 | 3% |

## Conclusión

Esta tabla permite confirmar si el patrón de fallo de `pdfplumber` observado en el corpus
original (4 PDFs LaTeX) se generaliza estadísticamente al corpus ampliado de arXiv (30 PDFs).