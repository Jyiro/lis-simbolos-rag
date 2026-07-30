"""Configuración global del experimento."""

OLLAMA_URL  = "http://localhost:11434/api/generate"
MODELO      = "qwen3:1.7b"
TEMPERATURE = 0
NUM_PREDICT = 120
RESULTS_DIR = "results"

# Condiciones experimentales
# Cada tupla: (etiqueta, version_documento, con_tabla, corrupt_question)
#
# Escenarios cubiertos:
#   1. LIMPIO    | doc limpio,   query limpia,   sin tabla  → techo ideal
#   2. DOC CORR  | doc corrupto, query limpia,   sin tabla  → escenario RAG más común
#   3. FULL CORR | doc corrupto, query corrupta, sin tabla  → peor caso
#   4. QUERY CORR| doc limpio,   query corrupta, sin tabla  → usuario con clipboard corrupto
#   5. CON TABLA | doc corrupto, query limpia,   con tabla  → efecto del prompt engineering
#   6. LATEX     | doc latex,    query limpia,   sin tabla  → benchmark notación alternativa

CONDICIONES = [
    ("LIMPIO    | doc✓ query✓ sin tabla", "limpio",   False, False),
    ("DOC CORR  | doc✗ query✓ sin tabla", "corrupto", False, False),
    ("FULL CORR | doc✗ query✗ sin tabla", "corrupto", False, True),
    ("QUERY CORR| doc✓ query✗ sin tabla", "limpio",   False, True),
    ("CON TABLA | doc✗ query✓ con tabla", "corrupto", True,  False),
    ("LATEX     | doc~ query✓ sin tabla", "latex",    False, False),
]