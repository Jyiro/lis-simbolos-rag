# Reporte Forense — Fase 3A (Caracterización de Corrupción)

**Fecha:** 2026-09-09
**Objetivo:** Determinar exactamente qué ocurre con el texto extraído por `pdfplumber` (motor base de DeepDoc/RAGFlow) cuando falla en reconocer un símbolo matemático, en comparación con una extracción exitosa (`pypdf`).

---

## 1. El caso de la Sumatoria (`∑`) y Productoria (`∏`) en Álgebra Abstracta

En el documento `AbstractAlgebra_cap1-3_symbols.pdf`, la métrica EAR detectó una pérdida total (0%) de las sumatorias y productorias usando `pdfplumber`.

Al alinear el texto extraído por ambos motores (alrededor de la línea 640 y 720 del PDF original), obtenemos la siguiente evidencia forense:

| Símbolo | Texto extraído por `pypdf` (Correcto) | Texto extraído por `pdfplumber` (Corrupto) |
|---|---|---|
| **SUM (`∑`)** | `(x + y)p =` **`∑`** `0≤i≤p` | `p (x+y)p = xiyp−i i 0≤i≤p` (además emitió `(cid:9)`) |
| **SUM (`∑`)** | `(x +1 )p =` **`∑`** `0≤i≤p` | `(x+1)p = xi1p−i =xp+ xi+1` (además emitió `(cid:9)`) |
| **PRODUCT (`∏`)** | `P =` **`∏`** `g∈G` | `P = g = f(g)` (además emitió `(cid:10)`) |

**Hallazgo:**
`pdfplumber` no solo omite el símbolo `∑` y `∏` en la línea matemática, destruyendo la sintaxis de las ecuaciones (ej. `(x + y)p = 0≤i≤p`), sino que en una línea anterior **escupió los tokens en crudo `(cid:9)` y `(cid:10)`**.
`pdfminer` (el motor subyacente) usa el formato `(cid:X)` cuando no puede mapear un glifo de una fuente CFF Type1 a su valor Unicode real. Como resultado, la fórmula matemática queda completamente rota y desprovista de su operador central.

---

## 2. El caso de la Satisfactibilidad (`⊨`) en Lógica Modal

En el documento `ModalLogicFundamentally_complete.pdf`, el símbolo `⊨` (Models) tuvo un EAR de 0.0% con `pdfplumber`.

Buscando las líneas equivalentes (Líneas 171-176) obtenemos esta alineación forense:

| # | Texto extraído por `pypdf` (Correcto) | Texto extraído por `pdfplumber` (Corrupto) | Tipo de Corrupción |
|---|---|---|---|
| 1 | `a consequence relation` **`⊨`** `C ⊆ L × L.` | `a consequence relation` **`(cid:15)`** `C⊆L×L.` | SUBSTITUTION |
| 2 | `ϕ ⊢ F ψ iﬀ ϕ` **`⊨`** `WPL ψ.` | `ϕ⊢ F ψ iff ϕ` **`(cid:15)`** `WPL ψ.` | SUBSTITUTION |

**Hallazgo:**
En este PDF, `pdfplumber` reemplaza el operador lógico `⊨` con el string literal **`(cid:15)`**. Un modelo de lenguaje (LLM) que reciba este chunk a través de RAG no tiene absolutamente ninguna forma de deducir que `(cid:15)` significa `⊨`, ya que este código es un artefacto interno del parser de PDFs, no un estándar matemático.

---

## Conclusiones de la Fase 3A

1. **La corrupción no es una simple omisión de espacios:** Cuando DeepDoc usa `pdfplumber` sobre papers académicos, los símbolos matemáticos complejos se pierden de forma catastrófica.
2. **Artefactos `(cid:X)`:** El texto resultante se llena de artefactos como `(cid:9)`, `(cid:10)` o `(cid:15)` que "ensucian" los embeddings e imposibilitan la recuperación (retrieval) por símbolo. Un usuario que pregunte "Muestra las ecuaciones con sumatorias" nunca encontrará el chunk `(cid:9)`.
3. **Pérdida Semántica Silenciosa:** Cuando el artefacto `(cid:X)` no se emite en la misma línea (como ocurrió con la sumatoria), la fórmula matemática simplemente pierde su operador, cambiando completamente su significado semántico de manera indetectable para el LLM.

Esta evidencia confirma que **es imperativo abordar el encoding de fuentes en la capa de extracción (Fase 3C)** para habilitar aplicaciones RAG en dominios científicos.