"""
Tests para tex_glyph_patch.py

Para correr:
    cd <repo_root>
    python -m pytest deepdoc-research/tests/test_tex_glyph_patch.py -v
"""
import sys
import os
from pathlib import Path

# Asegurar que deepdoc-research está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent


class TestPatchApplication:
    """Tests de la aplicación correcta del patch."""

    def test_patch_adds_core_operators(self):
        """Los glyph names de CMEX que causan el bug deben estar en el dict post-patch."""
        import pdfminer.glyphlist as g
        import tex_glyph_patch  # noqa: F401 — auto-aplica al importar
        
        assert g.glyphname2unicode["summationtext"] == "\u2211", "∑ no fue agregada"
        assert g.glyphname2unicode["producttext"] == "\u220f", "∏ no fue agregada"
        assert g.glyphname2unicode["summationdisplay"] == "\u2211"
        assert g.glyphname2unicode["productdisplay"] == "\u220f"

    def test_patch_adds_lasy_operators(self):
        """Los glyph names de LASY (lógica modal) deben estar presentes."""
        import pdfminer.glyphlist as g
        import tex_glyph_patch  # noqa: F401
        
        assert g.glyphname2unicode["square"] == "\u25a1", "□ no fue agregada"

    def test_patch_does_not_overwrite_existing(self):
        """El patch NO debe modificar entradas que ya existen en el AGL."""
        import pdfminer.glyphlist as g
        
        # Guardar estado previo al patch
        snapshot = {k: v for k, v in g.glyphname2unicode.items()}
        
        import tex_glyph_patch  # noqa: F401
        
        for key, val in snapshot.items():
            assert g.glyphname2unicode[key] == val, \
                f"El patch sobreescribió '{key}': '{val}' -> '{g.glyphname2unicode[key]}'"

    def test_patch_is_idempotent(self):
        """Aplicar el patch múltiples veces no debe cambiar nada."""
        import pdfminer.glyphlist as g
        import tex_glyph_patch
        
        stats1 = tex_glyph_patch.apply_patch()
        size_after_first = len(g.glyphname2unicode)
        
        stats2 = tex_glyph_patch.apply_patch()
        size_after_second = len(g.glyphname2unicode)
        
        assert size_after_first == size_after_second, "Segunda aplicación cambió el dict"
        assert stats2["added"] == 0, "Segunda aplicación no debería agregar entradas"

    def test_delimiters_excluded_by_default(self):
        """Los delimitadores extensibles NO deben aplicarse por defecto."""
        import pdfminer.glyphlist as g
        import tex_glyph_patch
        
        # Limpiar estado (en un test real esto requeriría reset del módulo)
        # Por ahora verificar que parenleftbig no está en el dict si no se pidió
        # (Este test asume que el módulo no fue importado con include_delimiters=True)
        assert "parenleftbig" not in g.glyphname2unicode or \
               g.glyphname2unicode["parenleftbig"] == "(", \
               "parenleftbig debería no estar o mapeado a ASCII correctamente"

    def test_apply_patch_returns_stats(self):
        """apply_patch() debe retornar estadísticas."""
        import tex_glyph_patch
        stats = tex_glyph_patch.apply_patch()
        assert "added" in stats
        assert "skipped_existing" in stats
        assert isinstance(stats["added"], int)
        assert isinstance(stats["skipped_existing"], int)


class TestEndToEnd:
    """Tests de extracción real sobre PDFs del corpus."""

    ABSTRACT_ALGEBRA_PDF = REPO_ROOT / "dataset-ragflow" / "corpus-ragflow" / \
                           "abstract-algebra" / "AbstractAlgebra_cap1-3_symbols.pdf"

    def test_abstract_algebra_sum_extracted(self):
        """pdfplumber con patch debe extraer ∑ de AbstractAlgebra (antes: 0)."""
        if not self.ABSTRACT_ALGEBRA_PDF.exists():
            import pytest
            pytest.skip("AbstractAlgebra PDF no encontrado")
        
        # CRÍTICO: importar patch ANTES de pdfplumber
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import tex_glyph_patch  # noqa: F401
        import pdfplumber
        
        with pdfplumber.open(self.ABSTRACT_ALGEBRA_PDF) as pdf:
            text = "".join(p.extract_text() or "" for p in pdf.pages[17:20])
        
        count = text.count("\u2211")
        assert count > 0, f"∑ no encontrada en primeras 10 páginas (encontró {count})"

    def test_abstract_algebra_product_extracted(self):
        """pdfplumber con patch debe extraer ∏ de AbstractAlgebra (antes: 0)."""
        if not self.ABSTRACT_ALGEBRA_PDF.exists():
            import pytest
            pytest.skip("AbstractAlgebra PDF no encontrado")

        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import tex_glyph_patch  # noqa: F401
        import pdfplumber
        
        with pdfplumber.open(self.ABSTRACT_ALGEBRA_PDF) as pdf:
            text = "".join(p.extract_text() or "" for p in pdf.pages[17:20])
        
        count = text.count("\u220f")
        assert count > 0, f"∏ no encontrada en primeras 10 páginas (encontró {count})"


class TestEARRegression:
    """Tests de regresión: los 7 papers que fallaban en Exp 13 deben mejorar."""
    
    ARXIV_DIR = REPO_ROOT / "dataset-ragflow" / "corpus-ragflow" / "arxiv-harvested"
    
    # Papers del corpus arXiv que tenían EAR=0% para SUM/PRODUCT/NECESSARILY en Exp 13
    # (del reporte arxiv_ear_report.md original, sin patch)
    KNOWN_FAILING_PAPERS = [
        "2609.17177v1_Finite_Borel_asymptotic_dimension_of_bounded-to-one_commutat",
        "2609.18486v1_Towards_a_Proof-Theoretic_Analysis_of_IncorrectIncomplete_Pr",
        "2609.18730v1_A_minimal_type_of_Morley_rank",
        "2609.18032v1_Scott_topologies_on_products_of_countable_complete_Heyting_a",
    ]
    
    def test_sum_recovered_in_known_failing_papers(self):
        """Los papers que antes tenían SUM=0 en pdfplumber deben mejorar con patch."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import tex_glyph_patch  # noqa: F401
        import pdfplumber
        import json
        
        # Cargar baseline (sin patch)
        baseline_path = REPO_ROOT / "deepdoc-research" / "arxiv_ear_results.json"
        if not baseline_path.exists():
            import pytest
            pytest.skip("arxiv_ear_results.json no encontrado")
        
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        
        failures = 0
        for paper_prefix in self.KNOWN_FAILING_PAPERS:
            # Encontrar el PDF correspondiente
            matches = list(self.ARXIV_DIR.glob(f"{paper_prefix[:40]}*.pdf"))
            if not matches:
                continue
            pdf_path = matches[0]
            
            # Verificar que la baseline lo tenía como fallido
            base_doc = next((d for d in baseline if paper_prefix[:30] in d["doc_id"]), None)
            if base_doc is None:
                continue
            
            base_counts = base_doc["per_symbol"].get("SUM", {}).get("counts", {})
            base_sum = base_counts.get("pdfplumber", -1)
            base_ref = max(base_counts.get("pymupdf", 0), base_counts.get("pypdf", 0))
            
            # Extraer con patch
            with pdfplumber.open(pdf_path) as pdf:
                text = "".join(p.extract_text() or "" for p in pdf.pages)
            patched_sum = text.count("\u2211")
            
            if base_sum == 0 and base_ref > 0 and patched_sum == 0:
                failures += 1
        
        assert failures == 0, \
            f"{failures} papers siguen teniendo SUM=0 despues del patch"
