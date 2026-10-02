# Reporte Experimento — Fase 1 + Instruction Hierarchy

| Campo | Valor |
|-------|-------|
| Modelo | `qwen3.5-2b` |
| Backend | `llama_cpp` |
| Run ID | `20260813_145907_qwen3.5-2b_llama_cpp_nothink` |
| Timestamp | 2026-08-13T14:59:07.636673 |
| Fragmentos | 1 |
| Condiciones | 1 |

---
## Resumen por Condición

| Condición | ✓ Correct | ✗ Confund | ? Sin resp | Total | SemScore | Contrast |
|-----------|----------:|----------:|-----------:|------:|---------:|---------:|
| `CON TABLA | plain` | 1/1 | 0/1 | 0/1 | 1 | --- | --- |

---
## Instruction Hierarchy — Efecto por Estrategia

> **Hipótesis:** estrategias de mayor jerarquía deberían aumentar la 
> fidelidad al contexto y disminuir el uso de conocimiento paramétrico.

| Estrategia | A4_producto_cart | % Correcto |
|---|---|---|
| Tabla plana — sin énfasis | ✓ | 100% |

---
## Detalle por Fragmento

### A4_producto_cart  *(nivel: alta)*

> **Dominio:** Matemática  
> **Símbolo:** `×`  
> **Doc limpio:** `Sea f: ℝ × ℝ → ℝ`  
> **Pregunta:** ¿El dominio de f son pares ordenados de reales o números reales individuales?

| Condición | Resultado | SemScore | Respuesta |
|-----------|:---------:|:--------:|-----------|
| `CON TABLA | plain` | ✓ CORRECTO | --- | El dominio de la función f es el conjunto de todos los pares ordenados de números reales. |
