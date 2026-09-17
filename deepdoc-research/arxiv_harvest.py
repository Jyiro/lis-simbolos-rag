# -*- coding: utf-8 -*-
"""
arXiv Corpus Harvester
======================
Descarga papers de arXiv en categorías de matemática y lógica,
filtra los que usan fuentes Type1/Computer Modern (el perfil exacto
que dispara el bug de MacRomanEncoding en pdfminer.six), y los guarda
en dataset-ragflow/corpus-ragflow/.

Uso:
    python deepdoc-research/arxiv_harvest.py

Dependencias:
    pip install requests pymupdf feedparser
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUTPUT_DIR = Path(__file__).parent.parent / "dataset-ragflow" / "corpus-ragflow" / "arxiv-macroman"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = OUTPUT_DIR / "harvest_macroman_log.md"

ARXIV_API = "https://export.arxiv.org/api/query"

# Categorías y queries: matemática simbólica densa, amplio espectro
# Priorizamos categorías que históricamente generan PDFs con encodings más antiguos
QUERIES = [
    # Lógica matemática y formal
    ("math.LO", "modal logic kripke semantics"),
    ("math.LO", "first order logic completeness Godel"),
    ("math.LO", "set theory axioms forcing"),
    ("math.LO", "model theory definable sets"),
    ("math.LO", "descriptive set theory Borel"),
    # Álgebra
    ("math.GR", "group theory finite groups"),
    ("math.GR", "Lie groups representations"),
    ("math.RA", "commutative rings modules"),
    ("math.RA", "homological algebra derived categories"),
    ("math.AC", "commutative algebra ideals"),
    ("math.CT", "category theory functors"),
    ("math.KT", "K-theory algebraic"),
    # Topología y geometría
    ("math.AT", "algebraic topology homotopy"),
    ("math.GT", "geometric topology manifolds"),
    ("math.AG", "algebraic geometry schemes"),
    ("math.DG", "differential geometry Riemannian"),
    # Análisis
    ("math.CA", "real analysis measure theory"),
    ("math.FA", "functional analysis Banach spaces"),
    ("math.AP", "partial differential equations"),
    # Teoría de números
    ("math.NT", "number theory prime numbers"),
    ("math.NT", "algebraic number theory"),
    # Combinatoria y probabilidad
    ("math.CO", "combinatorics graph theory"),
    ("math.PR", "probability stochastic processes"),
    # Lógica en CS
    ("cs.LO", "type theory lambda calculus"),
    ("cs.LO", "proof theory sequent calculus"),
    ("cs.LO", "formal verification model checking"),
    # Física matemática
    ("math-ph", "quantum mechanics operators"),
    ("math-ph", "statistical mechanics partition function"),
]

# Síntomas que queremos: fuentes CM* o PL* con Type1
CM_PREFIXES = ("CMR", "CMMI", "CMSY", "CMBX", "CMTI", "CMSS", "CMEX",
               "MSAM", "MSBM", "LASY", "EUFM", "PLMath", "PLRoman",
               "NimbusRom", "NimbusSan", "SFRM")

CRITICAL_SYMBOLS = "∀∃∄∧∨→↔⊢⊨□◇⊤⊥⊕∈∉⊂⊆∅∩∪∑∏∫∂∇≤≥≠≈≡∝αβγλμπφψω"

MAX_PER_QUERY = 15
MAX_TOTAL = 200
MIN_SYMBOL_DENSITY = 0.0005

# Modo de búsqueda: 'macroman' solo acepta PDFs con MacRomanEncoding
#                   'any'      acepta todos los Type1/CM (comportamiento anterior)
HARVEST_MODE = "macroman"


def arxiv_search(category: str, query: str, max_results: int = 10) -> list[dict]:
    """Busca en arXiv y devuelve lista de papers {id, title, pdf_url}."""
    params = {
        "search_query": f"cat:{category} AND all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",  # papers más viejos primero = más probable MacRomanEncoding
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=20)
        resp.raise_for_status()
        content = resp.content
    except Exception as e:
        print(f"  [API error] {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(content)
    papers = []
    for entry in root.findall("atom:entry", ns):
        arxiv_id_raw = entry.find("atom:id", ns).text.strip()
        arxiv_id = arxiv_id_raw.split("/abs/")[-1].replace("/", "_")
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id.replace('_', '/')}"
        papers.append({"id": arxiv_id, "title": title, "pdf_url": pdf_url})
    return papers


def download_pdf(url: str, dest: Path, timeout: int = 40) -> bool:
    """Descarga un PDF. Devuelve True si tuvo éxito."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except Exception as e:
        print(f"    [download error] {e}")
        return False


def score_pdf(pdf_path: Path) -> dict:
    """
    Abre el PDF y devuelve un score de adecuación:
    - has_type1: bool — contiene fuentes Type1
    - has_cm_fonts: bool — tiene fuentes Computer Modern
    - has_macroman: bool — tiene MacRomanEncoding (el bug específico)
    - symbol_density: float — proporción de símbolos críticos en el texto
    - pages: int
    """
    result = {
        "has_type1": False,
        "has_cm_fonts": False,
        "has_macroman": False,
        "symbol_density": 0.0,
        "pages": 0,
        "font_summary": [],
    }
    try:
        doc = fitz.open(str(pdf_path))
        result["pages"] = len(doc)

        # Analizar fuentes de las primeras 5 páginas
        fonts_seen = set()
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            for font in page.get_fonts(full=True):
                xref, ext, font_type, basefont, name, encoding, _ = font
                key = (basefont, font_type, encoding)
                if key in fonts_seen:
                    continue
                fonts_seen.add(key)
                if font_type == "Type1":
                    result["has_type1"] = True
                if any(basefont.upper().lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ+").startswith(p)
                       or p in basefont for p in CM_PREFIXES):
                    result["has_cm_fonts"] = True
                if encoding == "MacRomanEncoding":
                    result["has_macroman"] = True
                result["font_summary"].append(f"{basefont} | {font_type} | {encoding}")

        # Medir densidad de símbolos en texto completo (hasta 10 páginas)
        full_text = ""
        for page_num in range(min(10, len(doc))):
            full_text += doc[page_num].get_text() or ""

        if full_text:
            symbol_count = sum(full_text.count(c) for c in CRITICAL_SYMBOLS)
            result["symbol_density"] = symbol_count / len(full_text)

        doc.close()
    except Exception as e:
        result["error"] = str(e)

    return result


def is_good_candidate(score: dict) -> bool:
    """Decide si el PDF vale la pena conservar en el corpus."""
    base = (
        score["has_type1"]
        and score["has_cm_fonts"]
        and score["pages"] >= 5
        and score["symbol_density"] >= MIN_SYMBOL_DENSITY
    )
    if HARVEST_MODE == "macroman":
        return base and score["has_macroman"]
    return base


def main():
    print("=" * 60)
    print("arXiv Corpus Harvester — Búsqueda de papers LaTeX/Type1")
    print("=" * 60)

    seen_ids = set()
    accepted = []
    rejected = []
    log_entries = []

    for category, query in QUERIES:
        if len(accepted) >= MAX_TOTAL:
            break

        print(f"\n🔍 Buscando: cat:{category} AND '{query}'")
        papers = arxiv_search(category, query, max_results=MAX_PER_QUERY)
        print(f"   Encontrados: {len(papers)}")

        for paper in papers:
            if len(accepted) >= MAX_TOTAL:
                break
            if paper["id"] in seen_ids:
                continue
            seen_ids.add(paper["id"])

            print(f"\n  → {paper['id']}: {paper['title'][:60]}...")
            tmp_path = OUTPUT_DIR / f"_tmp_{paper['id']}.pdf"

            print(f"    Descargando desde {paper['pdf_url']} ...")
            ok = download_pdf(paper["pdf_url"], tmp_path)
            if not ok or not tmp_path.exists() or tmp_path.stat().st_size < 10_000:
                print("    ✗ Descarga fallida o PDF demasiado pequeño")
                if tmp_path.exists():
                    tmp_path.unlink()
                continue

            print(f"    Analizando fuentes y símbolos...")
            score = score_pdf(tmp_path)

            if "error" in score:
                print(f"    ✗ Error al leer PDF: {score['error']}")
                tmp_path.unlink()
                continue

            verdict = "✓ ACEPTADO" if is_good_candidate(score) else "✗ RECHAZADO"
            print(f"    {verdict} | Type1={score['has_type1']} CM={score['has_cm_fonts']} "
                  f"MacRoman={score['has_macroman']} "
                  f"SymDensity={score['symbol_density']:.4f} "
                  f"Pages={score['pages']}")

            if is_good_candidate(score):
                # Renombrar con un nombre limpio
                safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in paper["title"])
                safe_title = safe_title.strip().replace(" ", "_")[:60]
                final_name = f"{paper['id']}_{safe_title}.pdf"
                final_path = OUTPUT_DIR / final_name
                tmp_path.rename(final_path)
                accepted.append({"paper": paper, "score": score, "file": final_name})

                log_entries.append(
                    f"| ✓ | [{paper['id']}]({paper['pdf_url']}) | "
                    f"{paper['title'][:50]}... | "
                    f"CM={score['has_cm_fonts']} MacRoman={score['has_macroman']} | "
                    f"{score['symbol_density']:.4f} | {score['pages']}pp |"
                )
            else:
                tmp_path.unlink()
                rejected.append(paper["id"])

            time.sleep(3)  # Respetar rate limit de arXiv

    # Generar log
    log = ["# arXiv Harvest — Log de Descarga", "",
           f"Papers aceptados: **{len(accepted)}** / rechazados: {len(rejected)}", "",
           "| Estado | arXiv ID | Título | Fuentes | SymDensity | Páginas |",
           "|---|---|---|---|---|---|",
           *log_entries, ""]
    LOG_FILE.write_text("\n".join(log), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Completado: {len(accepted)} papers aceptados en {OUTPUT_DIR}")
    print(f"Log guardado en: {LOG_FILE.name}")


if __name__ == "__main__":
    main()
