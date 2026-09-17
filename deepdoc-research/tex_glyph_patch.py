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
    
    # Turnstiles y lógica extra (amsfonts / mathabx)
    "satisfies":             "\u22a8",  # ⊨
    "forces":                "\u22a9",  # ⊩
    "notforces":             "\u22ae",  # ⊮
    "notturnstile":          "\u22ac",  # ⊬
    "turnstileleft":         "\u22a3",  # ⊣
    "latticetop":            "\u22a4",  # ⊤

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
