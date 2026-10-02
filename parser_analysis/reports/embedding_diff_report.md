# Métrica de Diferencia de Embeddings (Fase 5)

Evalúa cuánto desplaza la corrupción de `pdfplumber` los vectores de embedding en comparación con la extracción correcta de `pypdf` usando `paraphrase-multilingual-MiniLM-L12-v2`.

| Símbolo | Documento | Muestras | Coseno Medio | < 0.70 |
|---|---|---|---|---|
| ∑ (SUM) | AbstractAlgebra | 19 | 0.558 | 18 |
| ∏ (PRODUCT) | AbstractAlgebra | 7 | 0.555 | 7 |
| ⊢ (TURNSTILE) | FirstOrderLogic | 7 | 0.536 | 5 |
| ⊨ (MODELS) | ModalLogicFundamentally | 1 | 0.936 | 0 |
| ⊢ (TURNSTILE) | ModalLogicFundamentally | 4 | 0.745 | 2 |

## Conclusión
Un coseno medio alto (>0.90) indica que la ausencia del símbolo *no desplaza* significativamente el vector (el retrieval seguiría funcionando). Un coseno < 0.70 indica que la corrupción destruye la representación semántica al punto de fallar un retrieval estándar.