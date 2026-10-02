"""
Monkey-patch de validación: inyecta la TeX Glyph List en pdfminer.six en runtime.
Fuente de la tabla: Apache PDFBox additional.txt
https://apache.googlesource.com/pdfbox/+/refs/tags/2.0.14/pdfbox/src/main/resources/org/apache/pdfbox/resources/glyphlist/additional.txt
"""
import pdfminer.glyphlist as _gl

# 1. Mapeos seguros: operadores matemáticos con Unicode no-ASCII propio
SAFE_MATH_OPERATORS = {
    # Operadores grandes (CMEX)
    "summationtext":        0x2211,  # ∑
    "summationdisplay":     0x2211,  # ∑
    "producttext":          0x220F,  # ∏
    "productdisplay":       0x220F,  # ∏
    "coproducttext":        0x2210,  # ∐
    "coproductdisplay":     0x2210,  # ∐
    "integraltext":         0x222B,  # ∫
    "integraldisplay":      0x222B,  # ∫
    "uniontext":            0x222A,  # ∪
    "uniondisplay":         0x222A,  # ∪
    "intersectiontext":     0x2229,  # ∩
    "intersectiondisplay":  0x2229,  # ∩
    "unionmultitext":       0x228E,  # ⊎
    "unionmultidisplay":    0x228E,  # ⊎
    "logicalandtext":       0x2227,  # ∧
    "logicalanddisplay":    0x2227,  # ∧
    "logicalortext":        0x2228,  # ∨
    "logicalordisplay":     0x2228,  # ∨
    "contintegraltext":     0x222E,  # ∮
    "contintegraldisplay":  0x222E,  # ∮
    "circledottext":        0x2299,  # ⊙
    "circledotdisplay":     0x2299,  # ⊙
    "circleplustext":       0x2295,  # ⊕
    "circleplusdisplay":    0x2295,  # ⊕
    "circlemultiplytext":   0x2297,  # ⊗
    "circlemultiplydisplay":0x2297,  # ⊗
    "hatwidest":            0x0302,  # combining circumflex
    "tildewidest":          0x0303,  # combining tilde
    # LASY / MSAM / MSBM — lógica modal y conjuntos
    "square":               0x25A1,  # □
    "squaresolid":          0x25A0,  # ■
    "diamond":              0x25C7,  # ◇
    "diamondsolid":         0x25C6,  # ◆
    "triangle":             0x25B3,  # △
    "trianglesolid":        0x25B2,  # ▲
    "triangleinv":          0x25BD,  # ▽
    "triangleinvsolid":     0x25BC,  # ▼
    "lozenge":              0x25CA,  # ◊
    "blacklozenge":         0x29EB,  # ⧫
    "smwhtcircle":          0x25E6,  # ◦
    "smblkcircle":          0x2022,  # •
    "circlesolid":          0x25CF,  # ●
    "circle":               0x25CB,  # ○
    "bullet":               0x2022,  # •
    # Flechas adicionales (CMSY)
    "arrowdblright":        0x21D2,  # ⇒
    "arrowdblboth":         0x21D4,  # ⇔
    "arrowdblup":           0x21D1,  # ⇑
    "arrowdbldown":         0x21D3,  # ⇓
    # Relaciones extra (CMSY)
    "approxequal":          0x2248,  # ≈
    "lessmuch":             0x226A,  # ≪
    "greatermuch":          0x226B,  # ≫
    "precedes":             0x227A,  # ≺
    "follows":              0x227B,  # ≻
    "precedesequal":        0x2AAF,  # ⪯
    "followsequal":         0x2AB0,  # ⪰
    "similarleftarrow":     0x2243,  # ≃
    "propersubset":         0x2282,  # ⊂
    "propersuperset":       0x2283,  # ⊃
    "reflexsubset":         0x2286,  # ⊆
    "reflexsuperset":       0x2287,  # ⊇
    "dotequal":             0x2250,  # ≐
    "doteq":                0x2250,
    "coloncolon":           0x2237,  # ∷
    "bardbl":               0x2016,  # ‖
    "arrowbothv":           0x2195,  # ↕
    "arrowboth":            0x2194,  # ↔
    "turnstileleft":        0x22A2,  # ⊢
    "turnstileright":       0x22A3,  # ⊣
    "forcesextra":          0x22A8,  # ⊨
    "forces":               0x22A8,
    "satisfies":            0x22A8,
    "truthvalue":           0x22A4,  # ⊤
    "perpendicular":        0x22A5,  # ⊥
    "angle":                0x2220,  # ∠
    "angbracketleft":       0x27E8,  # ⟨
    "angbracketright":      0x27E9,  # ⟩
    "triangleright":        0x22B3,  # ⊳
    "triangleleft":         0x22B2,  # ⊲
    "trianglerighteq":      0x22B5,  # ⊵
    "trianglelefteq":       0x22B4,  # ⊴
}

# 2. Delimitadores extensibles: mapean a ASCII/caracteres comunes
# Por defecto NO se aplican; son opcionales via apply_patch(include_delimiters=True)
EXTENSIBLE_DELIMITERS = {
    "parenleftbig":         0x0028,  # (
    "parenrightbig":        0x0029,  # )
    "bracketleftbig":       0x005B,  # [
    "bracketrightbig":      0x005D,  # ]
    "braceleftbig":         0x007B,  # {
    "bracerightbig":        0x007D,  # }
    "parenleftbigg":        0x0028,
    "parenrightbigg":       0x0029,
    "bracketleftbigg":      0x005B,
    "bracketrightbigg":     0x005D,
    "braceleftbigg":        0x007B,
    "bracerightbigg":       0x007D,
    "parenleftBig":         0x0028,
    "parenrightBig":        0x0029,
    "parenleftBigg":        0x0028,
    "parenrightBigg":       0x0029,
    "floorleftbig":         0x230A,  # ⌊
    "floorrightbig":        0x230B,  # ⌋
    "ceilingleftbig":       0x2308,  # ⌈
    "ceilingrightbig":      0x2309,  # ⌉
    "radicalBig":           0x221A,  # √
    "radicalbigg":          0x221A,
    "radicalbig":           0x221A,
    "radicalBigg":          0x221A,
    "radicalbt":            0x221A,
    "radicaltp":            0x221A,
    "backslashBig":         0x005C,
    "backslashbigg":        0x005C,
    "slashBig":             0x002F,
    "slashbigg":            0x002F,
    "slashBigg":            0x002F,
    "backslashBigg":        0x005C,
    "arrowhorizex":         0x2015,  # ―
    "arrowvertex":          0x23D0,  # ⏐
}


def apply_patch(include_delimiters: bool = False) -> dict:
    """
    Inyecta la TeX Glyph List en pdfminer.glyphlist.glyphname2unicode.
    
    IMPORTANTE: Debe llamarse al inicio del proceso (startup),
    no en el handler de cada request.
    
    Args:
        include_delimiters: Si True, también inyecta los delimitadores 
                            extensibles (parenleftbig, etc.). Por defecto 
                            False porque mapean a ASCII y pueden inflacionar 
                            conteos en texto plano.
    Returns:
        dict con stats: {'added': int, 'skipped_existing': int}
    """
    to_add = dict(SAFE_MATH_OPERATORS)
    if include_delimiters:
        to_add.update(EXTENSIBLE_DELIMITERS)
    
    added = 0
    skipped = 0
    for name, codepoint in to_add.items():
        if name not in _gl.glyphname2unicode:
            _gl.glyphname2unicode[name] = chr(codepoint)
            added += 1
        else:
            skipped += 1
            
    print(f"[tex_glyph_patch] Aplicado: +{added} entradas, {skipped} salteadas "
          f"(total en glyphname2unicode: {len(_gl.glyphname2unicode)})")
          
    return {"added": added, "skipped_existing": skipped}

# Auto-aplicar al importar (por defecto solo los matemáticos seguros)
apply_patch(include_delimiters=False)
