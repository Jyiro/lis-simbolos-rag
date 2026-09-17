# Plan de Implementación y Validación — Monkey-Patch a pdfminer.six

> Documento de especificación técnica completa para el fix del bug de extracción de
> símbolos matemáticos LaTeX en pdfminer.six.
> Objetivo: suficientemente detallado para ser delegado a otra IA para implementación.

---

## 1. El Bug — Diagnóstico Definitivo

### Causa raíz (revisada)

El bug **no** es que pdfminer ignore el ToUnicode CMap.
El bug es que los **nombres de glifo propios de las fuentes TeX/Computer Modern**
no están en el Adobe Glyph List (AGL) que usa pdfminer internamente.

```
Cadena de resolución en pdfminer (PDFSimpleFont.__init__):

  PDF font spec contiene:
    /Encoding con /Differences: [9 /summationdisplay 10 /productdisplay ...]

  pdfminer llama a name2unicode("summationdisplay")
    → busca en glyphname2unicode (Adobe AGL)
    → NO ESTÁ → lanza PDFKeyError
    → el slot cid=9 queda vacío en cid2unicode
    → to_unichr(9) falla → emite "(cid:9)"

  pypdf llama al mismo slot pero también consulta la TeX Glyph List
    → "summationdisplay" → U+2211 (∑) ✅
```

### Qué tiene pdfminer vs qué falta

| Nombre de glifo     | En AGL de pdfminer | Debería mapear a |
|---------------------|--------------------|------------------|
| `summation`         | ✅ → ∑             | —                |
| `summationdisplay`  | ❌ NO ESTÁ         | ∑ (U+2211)       |
| `summationtext`     | ❌ NO ESTÁ         | ∑ (U+2211)       |
| `productdisplay`    | ❌ NO ESTÁ         | ∏ (U+220F)       |
| `producttext`       | ❌ NO ESTÁ         | ∏ (U+220F)       |
| `square`            | ❌ NO ESTÁ         | □ (U+25A1)       |
| `integraldisplay`   | ❌ NO ESTÁ         | ∫ (U+222B)       |
| `parenleftbig`      | ❌ NO ESTÁ         | ( (U+0028)       |
| `bardbl`            | ❌ NO ESTÁ         | ‖ (U+2016)       |

Las fuentes afectadas son las de la familia **Computer Modern** (LaTeX estándar):
`CMEX10`, `CMSY10`, `CMMI10`, `CMR10`, `LASY10`, etc.

---

## 2. El Fix — Monkey-Patch

### Estrategia

Inyectar la **TeX Glyph List** (nombres TeX → Unicode) en el diccionario
`pdfminer.glyphlist.glyphname2unicode` en tiempo de ejecución, antes de
cualquier extracción. Es un patch no-invasivo: no modifica ningún archivo
de la librería instalada.

### Punto de inyección en el código de pdfminer

```
pdfminer/encodingdb.py  línea 42-43:

    elif name in glyphname2unicode:   ← AQUÍ se consulta el diccionario
        return glyphname2unicode[name]

El patch hace: glyphname2unicode.update(TEX_EXTRA_GLYPHS)
antes de que se ejecute cualquier extracción.
El diccionario vive en memoria → la búsqueda ya incluye los nombres TeX.
```

---

## 3. Flujo de Validación — Diagrama

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROTOCOLO DE VALIDACIÓN                          │
└─────────────────────────────────────────────────────────────────────┘

CORPUS:
  ├── Corpus original (4 PDFs LaTeX con discrepancias conocidas)
  │     AbstractAlgebra, FirstOrderLogic, ModalLogicFundamentally,
  │     ModalLogicalNeuralNetworks
  └── Corpus arXiv (30 PDFs, 7 con discrepancias detectadas en Exp 13)


PASO 1 — MEDICIÓN BASELINE (sin patch)
══════════════════════════════════════
  PDF ──► pdfplumber (pdfminer sin patch) ──► texto con (cid:X)
                                                     │
  PDF ──► pypdf                           ──► texto limpio
                                                     │
  PDF ──► PyMuPDF                         ──► texto limpio
                                                     │
                              EAR(pdfplumber, pypdf, pymupdf)
                                                     │
                                              baseline_ear.json


PASO 2 — APLICAR PATCH
══════════════════════
  from tex_glyph_patch import apply_patch
  n = apply_patch()   # inyecta N entradas en glyphname2unicode
  # A partir de acá, pdfplumber usa el diccionario extendido


PASO 3 — MEDICIÓN POST-PATCH
════════════════════════════
  PDF ──► pdfplumber (pdfminer CON patch) ──► texto (¿limpio?)
                                                     │
  PDF ──► pypdf                           ──► texto limpio (referencia)
  PDF ──► PyMuPDF                         ──► texto limpio (referencia)
                                                     │
                              EAR(pdfplumber_patched, pypdf, pymupdf)
                                                     │
                                              patched_ear.json


PASO 4 — COMPARACIÓN Y REPORTE
═══════════════════════════════
  Para cada (símbolo, documento):
    ΔRecuperados = conteo_patched - conteo_baseline
    ΔEAR = ear_patched - ear_baseline

  Criterio de éxito:
    ∑ en AbstractAlgebra:    ear_patched == 100% (era 0%)   ✅/❌
    ∏ en AbstractAlgebra:    ear_patched == 100% (era 0%)   ✅/❌
    □ en arXiv docs:         ear_patched == 100% (era 0%)   ✅/❌
    Resto de docs (EAR 100% antes): ear_patched == 100%      ✅/❌ (sin regresiones)

  patch_validation_report.md  ←  tabla comparativa antes/después
```

---

## 4. Estructura de Archivos a Crear

```
deepdoc-research/
├── tex_glyph_patch.py          ← EL PATCH (módulo importable)
├── probe_patched.py            ← script de validación completa
└── patch_validation_report.md  ← generado automáticamente por probe_patched.py
```

---

## 5. Especificación de Código — `tex_glyph_patch.py`

### Propósito
Módulo que, al importarse, provee la función `apply_patch()`.
Cuando se llama, inyecta la TeX Glyph List en `pdfminer.glyphlist.glyphname2unicode`.

### Estructura completa

```python
"""
tex_glyph_patch.py
==================
Monkey-patch para pdfminer.six que agrega los nombres de glifo propios
de las fuentes Computer Modern / LaTeX (CMEX, CMSY, CMMI, LASY).

El Adobe Glyph List (AGL) que usa pdfminer no incluye los ~200 nombres
TeX-específicos que estas fuentes usan en sus /Differences arrays.
Este módulo inyecta esos nombres en el diccionario en-memoria de pdfminer
antes de cualquier extracción.

Uso:
    from tex_glyph_patch import apply_patch
    n = apply_patch()
    # A partir de acá, pdfplumber resuelve correctamente ∑, ∏, □, etc.

Referencias:
    - TeX Glyph List (TUG): https://tug.org/tex-glyph-list/
    - CMEX10 glyph table: https://ctan.org/pkg/cmex
    - fontname mapping: https://tug.org/fontname/fontname.pdf
"""

# TeX Glyph List — nombres de glifo TeX → carácter Unicode
# Organizado por fuente de origen para facilitar auditoría
TEX_EXTRA_GLYPHS: dict[str, str] = {

    # ── CMEX10 (símbolos matemáticos de tamaño variable) ──────────────────
    "summationdisplay":      "\u2211",  # ∑  (display size)
    "summationtext":         "\u2211",  # ∑  (text/inline size)
    "productdisplay":        "\u220f",  # ∏  (display size)
    "producttext":           "\u220f",  # ∏  (text/inline size)
    "coproductdisplay":      "\u2210",  # ∐
    "coproducttext":         "\u2210",  # ∐
    "integraldisplay":       "\u222b",  # ∫
    "integraltext":          "\u222b",  # ∫
    "contintegraldisplay":   "\u222e",  # ∮
    "contintegraltext":      "\u222e",  # ∮
    "uniondisplay":          "\u22c3",  # ⋃
    "uniontext":             "\u22c3",  # ⋃
    "intersectiondisplay":   "\u22c2",  # ⋂
    "intersectiontext":      "\u22c2",  # ⋂
    "unionmultidisplay":     "\u228e",  # ⊎
    "unionmultitext":        "\u228e",  # ⊎
    "logicalanddisplay":     "\u2227",  # ∧
    "logicalandtext":        "\u2227",  # ∧
    "logicalordisplay":      "\u2228",  # ∨
    "logicalortext":         "\u2228",  # ∨
    "circledotdisplay":      "\u2299",  # ⊙
    "circledottext":         "\u2299",  # ⊙
    "circleplusdisplay":     "\u2295",  # ⊕
    "circleplustext":        "\u2295",  # ⊕
    "circlemultiplydisplay": "\u2297",  # ⊗
    "circlemultiplytext":    "\u2297",  # ⊗

    # Delimitadores grandes (CMEX)
    "parenleftbig":          "(",       # (
    "parenrightbig":         ")",       # )
    "parenleftBig":          "(",
    "parenrightBig":         ")",
    "parenleftbigg":         "(",
    "parenrightbigg":        ")",
    "parenleftBigg":         "(",
    "parenrightBigg":        ")",
    "bracketleftbig":        "[",
    "bracketrightbig":       "]",
    "bracketleftBig":        "[",
    "bracketrightBig":       "]",
    "bracketleftbigg":       "[",
    "bracketrightbigg":      "]",
    "bracketleftBigg":       "[",
    "bracketrightBigg":      "]",
    "braceleftbig":          "{",
    "bracerightbig":         "}",
    "braceleftBig":          "{",
    "bracerightBig":         "}",
    "braceleftbigg":         "{",
    "bracerightbigg":        "}",
    "braceleftBigg":         "{",
    "bracerightBigg":        "}",
    "floorleftbig":          "\u230a",  # ⌊
    "floorrightbig":         "\u230b",  # ⌋
    "ceilingleftbig":        "\u2308",  # ⌈
    "ceilingrightbig":       "\u2309",  # ⌉
    "angbracketleftbig":     "\u27e8",  # ⟨
    "angbracketrightbig":    "\u27e9",  # ⟩
    "vextendsingle":         "|",
    "vextenddouble":         "\u2016",  # ‖
    "braceex":               "|",
    "arrowvertex":           "|",

    # ── CMSY10 (símbolos matemáticos) ─────────────────────────────────────
    "square":                "\u25a1",  # □  (modal NECESSARILY)
    "squaresolid":           "\u25a0",  # ■
    "diamond":               "\u22c4",  # ⋄  (sobreescribe ♦ del AGL)
    "diamondsolid":          "\u25c6",  # ◆
    "triangle":              "\u25b3",  # △
    "trianglesolid":         "\u25b2",  # ▲
    "triangledown":          "\u25bd",  # ▽
    "triangledownsolid":     "\u25bc",  # ▼
    "circlesolid":           "\u25cf",  # ●
    "circle":                "\u25cb",  # ○
    "bulletmath":            "\u2219",  # ∙
    "bardbl":                "\u2016",  # ‖
    "backslashmath":         "\u29f5",  # ⧵
    "dagger":                "\u2020",  # †
    "daggerdbl":             "\u2021",  # ‡
    "paragraph":             "\u00b6",  # ¶
    "section":               "\u00a7",  # §
    "club":                  "\u2663",  # ♣
    "heart":                 "\u2665",  # ♥
    "spade":                 "\u2660",  # ♠
    "diamondsuit":           "\u2666",  # ♦
    "flat":                  "\u266d",  # ♭
    "natural":               "\u266e",  # ♮
    "sharp":                 "\u266f",  # ♯

    # Relaciones (CMSY)
    "lessequivorelnt":       "\u2272",  # ≲
    "greaterequivorelnt":    "\u2273",  # ≳
    "precedesequivlnt":      "\u227e",  # ≾
    "followsequivlnt":       "\u227f",  # ≿
    "similarequal":          "\u2243",  # ≃
    "arrowleftright":        "\u2194",  # ↔
    "arrowdblleftright":     "\u21d4",  # ⇔
    "arrowdblup":            "\u21d1",  # ⇑
    "arrowdbldown":          "\u21d3",  # ⇓
    "nearrow":               "\u2197",  # ↗
    "searrow":               "\u2198",  # ↘
    "swarrow":               "\u2199",  # ↙
    "nwarrow":               "\u2196",  # ↖
    "proportional":          "\u221d",  # ∝
    "infinity":              "\u221e",  # ∞
    "angle":                 "\u2220",  # ∠
    "aleph":                 "\u2135",  # ℵ
    "hbar":                  "\u210f",  # ℏ
    "emptyset":              "\u2205",  # ∅
    "nabla":                 "\u2207",  # ∇
    "surd":                  "\u221a",  # √
    "top":                   "\u22a4",  # ⊤
    "bot":                   "\u22a5",  # ⊥
    "mho":                   "\u2127",  # ℧
    "dotplus":               "\u2214",  # ∔
    "backprime":             "\u2035",  # ‵
    "varnothing":            "\u2205",  # ∅

    # ── LASY10 (LaTeX symbols font) ───────────────────────────────────────
    "squaredot":             "\u22a1",  # ⊡
    "squaresmallsolid":      "\u25aa",  # ▪
    "squaretopblack":        "\u2b12",  # ⬒
    "triangleleft":          "\u25c3",  # ◃
    "triangleright":         "\u25b9",  # ▹
    "boxdot":                "\u22a1",  # ⊡
    "boxplus":               "\u229e",  # ⊞
    "boxtimes":              "\u22a0",  # ⊠
    "boxminus":              "\u229f",  # ⊟
    "leadsto":               "\u219d",  # ↝
    "Join":                  "\u2a1d",  # ⨝

    # ── CMMI10 (math italic — letras con encoding especial) ──────────────
    # (la mayoría están en el AGL estándar; solo los que faltan)
    "arrowleftbothalf":      "\u21bd",  # ↽
    "arrowlefttophalf":      "\u21bc",  # ↼
    "arrowrightbothalf":     "\u21c1",  # ⇁
    "arrowrighttophalf":     "\u21c0",  # ⇀
    "imath":                 "\u0131",  # ı (i sin punto)
    "jmath":                 "\u0237",  # ȷ (j sin punto)
}


def apply_patch() -> int:
    """
    Inyecta la TeX Glyph List en pdfminer.glyphlist.glyphname2unicode.

    Debe llamarse UNA VEZ antes de cualquier extracción con pdfplumber/pdfminer.
    Es idempotente: llamarla múltiples veces no causa problemas.

    Returns:
        int: número de entradas añadidas al diccionario.
    """
    from pdfminer.glyphlist import glyphname2unicode
    before = len(glyphname2unicode)
    glyphname2unicode.update(TEX_EXTRA_GLYPHS)
    added = len(glyphname2unicode) - before
    return added


def is_patched() -> bool:
    """Verifica si el patch ya fue aplicado."""
    from pdfminer.glyphlist import glyphname2unicode
    return "summationdisplay" in glyphname2unicode
```

---

## 6. Especificación de Código — `probe_patched.py`

### Propósito
Script de validación completa. Mide EAR antes y después del patch sobre ambos
corpus (original + arXiv). Genera `patch_validation_report.md`.

### Estructura

```python
"""
probe_patched.py
================
Valida el monkey-patch tex_glyph_patch comparando EAR antes y después
sobre el corpus original (4 PDFs) y el corpus arXiv (30 PDFs).

Uso:
    ~/.venv-ml/bin/python3 deepdoc-research/probe_patched.py

Output:
    deepdoc-research/patch_validation_report.md
"""

import json
from pathlib import Path
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

CORPUS_ORIGINAL = [
    "dataset-ragflow/corpus-ragflow/abstract-algebra/AbstractAlgebra_cap1-3_symbols.pdf",
    "dataset-ragflow/corpus-ragflow/FirstOrderLogic_complete.pdf",
    "dataset-ragflow/corpus-ragflow/ModalLogicFundamentally_complete.pdf",
    "dataset-ragflow/corpus-ragflow/ModalLogicalNeuralNetworks_complete.pdf",
]

# Los 7 PDFs de arXiv que tenían discrepancias en Exp 13
ARXIV_WITH_DISCREPANCIES = [
    "deepdoc-research/real_pdfs/arxiv/2609.16957v1_...pdf",  # □ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.17177v1_...pdf",  # ∑ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.17438v2_...pdf",  # □ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.18032v1_...pdf",  # ∏ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.18433v1_...pdf",  # □ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.18486v1_...pdf",  # ∑ EAR 0%
    "deepdoc-research/real_pdfs/arxiv/2609.18730v1_...pdf",  # ∑ EAR 0%
]

# Símbolos a auditar (nombre → carácter Unicode)
SYMBOLS_TO_AUDIT = {
    "SUM":         "∑",
    "PRODUCT":     "∏",
    "NECESSARILY": "□",
    "TURNSTILE":   "⊢",
    "MODELS":      "⊨",
    "INTEGRAL":    "∫",
}

# ─── FUNCIÓN DE EXTRACCIÓN ────────────────────────────────────────────────────

def count_symbols_pdfplumber(pdf_path: str, symbols: dict) -> dict[str, int]:
    """
    Extrae texto con pdfplumber y cuenta ocurrencias de cada símbolo.
    Devuelve {symbol_name: count}.
    """
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text += t
    return {name: text.count(char) for name, char in symbols.items()}


def count_symbols_pypdf(pdf_path: str, symbols: dict) -> dict[str, int]:
    """Extrae texto con pypdf y cuenta ocurrencias."""
    import pypdf
    text = ""
    reader = pypdf.PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return {name: text.count(char) for name, char in symbols.items()}


def compute_ear(count_a: dict, count_b: dict, count_c: dict) -> dict[str, float]:
    """
    Calcula EAR por símbolo: 100% si los tres extractores coinciden, 0% si no.
    (versión simplificada: EAR = 1.0 si plumber == pypdf == pymupdf, else 0.0)
    """
    ear = {}
    for name in count_a:
        vals = {count_a[name], count_b[name], count_c[name]}
        ear[name] = 1.0 if len(vals) == 1 else 0.0
    return ear

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def run_validation():
    all_pdfs = CORPUS_ORIGINAL  # + ARXIV_WITH_DISCREPANCIES  (descomentar)

    results_before = {}
    results_after  = {}

    # ── PASO 1: Medir SIN patch ──────────────────────────────────────────
    print("Midiendo baseline (sin patch)...")
    for pdf_path in all_pdfs:
        name = Path(pdf_path).stem[:40]
        plumber = count_symbols_pdfplumber(pdf_path, SYMBOLS_TO_AUDIT)
        pyp     = count_symbols_pypdf(pdf_path, SYMBOLS_TO_AUDIT)
        # pymupdf omitido por brevedad, se puede agregar
        results_before[name] = {"pdfplumber": plumber, "pypdf": pyp}
        print(f"  {name}: pdfplumber={plumber} | pypdf={pyp}")

    # ── PASO 2: Aplicar patch ────────────────────────────────────────────
    print("\nAplicando monkey-patch...")
    from tex_glyph_patch import apply_patch
    n_added = apply_patch()
    print(f"  Patch aplicado: {n_added} nuevas entradas en glyphname2unicode")

    # ── PASO 3: Medir CON patch ──────────────────────────────────────────
    print("\nMidiendo post-patch...")
    # IMPORTANTE: pdfplumber debe re-inicializarse para que tome el diccionario nuevo
    # Los módulos ya importados pueden tener cachés → reiniciar el resource manager
    import importlib, pdfminer.encodingdb, pdfminer.pdffont
    importlib.reload(pdfminer.encodingdb)  # fuerza re-lectura del glyphname2unicode

    for pdf_path in all_pdfs:
        name = Path(pdf_path).stem[:40]
        plumber = count_symbols_pdfplumber(pdf_path, SYMBOLS_TO_AUDIT)
        pyp     = count_symbols_pypdf(pdf_path, SYMBOLS_TO_AUDIT)
        results_after[name] = {"pdfplumber": plumber, "pypdf": pyp}
        print(f"  {name}: pdfplumber={plumber} | pypdf={pyp}")

    # ── PASO 4: Comparar y reportar ──────────────────────────────────────
    generate_report(results_before, results_after)


def generate_report(before: dict, after: dict):
    """Genera patch_validation_report.md con tabla comparativa."""
    lines = [
        "# Reporte de Validación — Monkey-Patch pdfminer.six",
        f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## Tabla de Resultados\n",
        "| Documento | Símbolo | Antes (plumber) | Después (plumber) | pypdf (ref) | ΔRecuperados | OK? |",
        "|---|---|---|---|---|---|---|",
    ]

    all_ok = True
    for doc in before:
        for sym in SYMBOLS_TO_AUDIT:
            b_count = before[doc]["pdfplumber"].get(sym, 0)
            a_count = after[doc]["pdfplumber"].get(sym, 0)
            ref     = before[doc]["pypdf"].get(sym, 0)
            delta   = a_count - b_count
            ok      = "✅" if a_count == ref else ("⚠️" if a_count > 0 else "❌")
            if a_count != ref:
                all_ok = False
            if b_count > 0 or ref > 0:  # solo mostrar si el símbolo existe en el doc
                lines.append(f"| {doc[:35]} | {sym} | {b_count} | {a_count} | {ref} | +{delta} | {ok} |")

    lines.append(f"\n## Resultado Global: {'✅ PATCH EXITOSO' if all_ok else '⚠️ PATCH PARCIAL — revisar'}")

    report_path = Path("deepdoc-research/patch_validation_report.md")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReporte generado: {report_path}")


if __name__ == "__main__":
    run_validation()
```

---

## 7. Criterios de Éxito

| Símbolo | Documento | EAR Antes | EAR Después esperado |
|---|---|---|---|
| `∑` summationdisplay | AbstractAlgebra | 0.0% | **100%** |
| `∏` productdisplay | AbstractAlgebra | 0.0% | **100%** |
| `□` square | arXiv (3 docs) | 0.0% | **100%** |
| `∑` summationdisplay | arXiv (3 docs) | 0.0% | **100%** |
| `∏` productdisplay | arXiv (1 doc) | 0.0% | **100%** |
| `⊢` | FirstOrderLogic | 33.8% | **100%** (si el bug es el mismo) |
| Todo lo demás | Todos | 100% | **100%** (sin regresiones) |

### Verificación de no-regresión

Debe correrse también `probe.py` (PDFs sintéticos) post-patch para confirmar que
el CPR sigue en 100% y el patch no rompió nada en el path de extracción normal.

---

## 8. Notas para quien implemente

1. **Fuentes de la TeX Glyph List:**
   - Lista oficial TUG: https://tug.org/tex-glyph-list/
   - CMEX table: https://mirror.ctan.org/fonts/cm/mf/cmex10.mf (comentarios con nombres)
   - Referencia fonttools: `fontTools.agl.AGL2UV` tiene algunos, completar con los TeX

2. **El problema del caché de pdfminer:**
   - El `EncodingDB` usa `ClassVar` (diccionario de clase que se inicializa al importar)
   - Si `EncodingDB.mac2unicode` ya está construido antes del patch, el patch solo
     afecta a las fuentes que usan el path `name2unicode()` en `Differences`
   - No afecta a fuentes que ya están completamente cacheadas en `cid2unicode`
   - Solución: aplicar el patch LO ANTES POSIBLE, antes del primer `import pdfplumber`

3. **Orden correcto de imports en el script de validación:**
   ```python
   # CORRECTO:
   from tex_glyph_patch import apply_patch
   apply_patch()                          # patch ANTES de importar pdfplumber
   import pdfplumber                      # ahora usa el diccionario extendido

   # INCORRECTO:
   import pdfplumber                      # ya cargó el AGL sin los nombres TeX
   from tex_glyph_patch import apply_patch
   apply_patch()                          # llega tarde para algunas fuentes
   ```

4. **Sobre el `importlib.reload()`:**
   - Si por alguna razón el patch se aplica después de haber importado pdfplumber,
     `importlib.reload(pdfminer.encodingdb)` puede forzar la re-inicialización
   - Pero es más limpio asegurar el orden correcto de imports desde el principio

5. **Sobre completitud de la lista TEX_EXTRA_GLYPHS:**
   - La lista del spec tiene ~80 entradas; la oficial tiene ~200
   - Para el PR a pdfminer.six, usar la lista completa
   - Para la validación experimental, alcanza con cubrir los símbolos del corpus

