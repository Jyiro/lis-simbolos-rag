"""Genera un documento comparativo entre los dos modelos a partir de los JSONs de resultados."""

import json
import os
import glob

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

def cargar_json(patron):
    archivos = sorted(glob.glob(os.path.join(RESULTS_DIR, patron)))
    if not archivos:
        return None, None
    path = archivos[-1]  # el más reciente
    with open(path, encoding="utf-8") as f:
        return json.load(f), os.path.basename(path)

def icono(eval_auto):
    if "CORRECTO" in eval_auto:
        return "✓"
    if "CONFUNDIDO" in eval_auto:
        return "✗"
    return "?"

data_1b, fname_1b = cargar_json("*1.7b*.json")
data_4b, fname_4b = cargar_json("*4b*.json")

if not data_1b or not data_4b:
    print("No se encontraron ambos archivos de resultados.")
    exit(1)

# Indexar por (fragmento, condicion)
idx_1b = {(r["fragmento"], r["condicion"]): r for r in data_1b}
idx_4b = {(r["fragmento"], r["condicion"]): r for r in data_4b}

# Obtener todos los fragmentos y condiciones en orden
fragmentos_ord = list(dict.fromkeys(r["fragmento"] for r in data_1b))
condiciones_ord = list(dict.fromkeys(r["condicion"] for r in data_1b))

NIVELES = {r["fragmento"]: r.get("nivel", "?") for r in data_1b}

CATEGORIAS = {
    "efecto_principal":   ["A2_bicondicional", "B2_angstrom", "C3_musical"],
    "terquedad":          ["B3_modal", "B4_subconjunto"],
    "tokenizacion":       ["C1_ipa", "C2_interpunct"],
    "redundancia":        ["A1_desigualdad", "A3_cuantificador", "B1_equilibrio"],
    "otros":              ["A4_producto_cart", "C4_obelus"],
}
CAT_LABELS = {
    "efecto_principal": "✦ EFECTO PRINCIPAL — Validación de hipótesis",
    "terquedad":        "⚡ TERQUEDAD SEMÁNTICA — Pesos vs. instrucción RAG",
    "tokenizacion":     "🔤 TOKENIZACIÓN FORTUITA — Mojibake como separador",
    "redundancia":      "⚠ REDUNDANCIA CONTEXTUAL — Símbolo irrelevante",
    "otros":            "· OTROS",
}

lines = []
A = lines.append

A("# Comparativa de Modelos — Fase 1")
A(f"\n**Modelo A:** {fname_1b}")
A(f"**Modelo B:** {fname_4b}\n")
A("Leyenda: ✓ CORRECTO · ✗ CONFUNDIDO · ? SIN RESPUESTA\n")
A("---\n")

for cat_key, frags in CATEGORIAS.items():
    A(f"## {CAT_LABELS[cat_key]}\n")
    for frag_id in frags:
        if frag_id not in NIVELES:
            continue
        # Tomar prompt del primer resultado del fragmento (limpio)
        primer = idx_1b.get((frag_id, condiciones_ord[0]))
        prompt_limpio = primer["prompt"] if primer else "—"
        # Solo mostrar el documento (primeras 2 líneas del prompt)
        doc_lines = [l for l in prompt_limpio.splitlines() if l.strip() and not l.startswith("Pregunta") and l != "Texto:"]
        doc_texto = " | ".join(doc_lines[:3]) if doc_lines else "—"
        # Pregunta
        pregunta_lines = [l for l in prompt_limpio.splitlines() if l.startswith("Pregunta:")]
        pregunta = pregunta_lines[0].replace("Pregunta:", "").strip() if pregunta_lines else "—"

        A(f"### {frag_id}  *(nivel: {NIVELES[frag_id]})*")
        A(f"> **Documento:** `{doc_texto}`  ")
        A(f"> **Pregunta:** {pregunta}\n")

        # Tabla de condiciones
        A("| Condición | qwen3:1.7b | Respuesta 1.7b | qwen3:4b | Respuesta 4b | Extracción clave |")
        A("|---|:---:|---|:---:|---|---|")

        for cond in condiciones_ord:
            r1 = idx_1b.get((frag_id, cond))
            r4 = idx_4b.get((frag_id, cond))
            if not r1 and not r4:
                continue
            icon1 = icono(r1["evaluacion_auto"]) if r1 else "—"
            icon4 = icono(r4["evaluacion_auto"]) if r4 else "—"
            resp1 = r1["respuesta"].replace("\n", " ").strip()[:80] if r1 else "—"
            resp4 = r4["respuesta"].replace("\n", " ").strip()[:80] if r4 else "—"

            # Extracción automática de insights por combinación
            extraccion = ""
            if icon1 == "✓" and icon4 == "✓":
                extraccion = "Ambos correctos"
            elif icon1 == "✗" and icon4 == "✗":
                extraccion = "Ambos confundidos"
            elif icon1 == "?" and icon4 == "?":
                extraccion = "Ambos sin respuesta"
            elif icon1 != icon4:
                extraccion = f"Divergencia: 1.7b={icon1} / 4b={icon4}"

            # Condición corta para la tabla
            cond_corta = cond.split("|")[0].strip()
            A(f"| {cond_corta} | {icon1} | {resp1} | {icon4} | {resp4} | {extraccion} |")
        A("")

# Resumen por categoría
A("---\n## Resumen por Categoría\n")
A("| Categoría | Fragmentos | Patrón dominante 1.7b | Patrón dominante 4b |")
A("|---|---|---|---|")
for cat_key, frags in CATEGORIAS.items():
    validos = [f for f in frags if f in NIVELES]
    todos_1b = [icono(r["evaluacion_auto"]) for f in validos for r in data_1b if r["fragmento"] == f]
    todos_4b = [icono(r["evaluacion_auto"]) for f in validos for r in data_4b if r["fragmento"] == f]
    c1 = max(set(todos_1b), key=todos_1b.count) if todos_1b else "—"
    c4 = max(set(todos_4b), key=todos_4b.count) if todos_4b else "—"
    A(f"| {CAT_LABELS[cat_key]} | {', '.join(validos)} | {c1} | {c4} |")

output = "\n".join(lines)
out_path = os.path.join(RESULTS_DIR, "comparativa_modelos.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(output)
print(f"Documento generado: {out_path}")
