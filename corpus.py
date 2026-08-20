"""Corpus experimental — 7 fragmentos en tres roles experimentales.

Diseño de cada fragmento:
  - El símbolo es la única pista semántica para responder la pregunta.
  - El texto circundante no permite deducir la respuesta sin el símbolo.
  - La respuesta incorrecta "inteligente" sin el símbolo es predecible.
  - La pregunta no menciona el símbolo.

Roles en el experimento de Instruction Hierarchy:
  Terquedad semántica  → B3_modal, B4_subconjunto
    El modelo conoce el símbolo y lo confunde con una variante más común.
    Falla incluso con tabla. ¿Puede el system message (I1-D) romperlo?

  Efecto principal (control positivo) → A4_producto_cart, B2_angstrom, C3_musical, C4_obelus
    La corrupción causa confusión, la tabla la recupera.
    Sirve para verificar que las condiciones I1 no empeoran lo que ya funciona.

  Control de baja frecuencia → C2_interpunct
    Símbolo oscuro — el modelo sigue instrucciones sin resistencia.
    Permite comparar "obediencia perfecta" con los casos de terquedad.

Fragmentos eliminados respecto al corpus original (v1.1, 12 fragmentos):
  A1_desigualdad  → contexto lingüístico rescata siempre, sin efecto observable
  A2_bicondicional → 1.7b falla incluso limpio (límite del modelo, no del símbolo)
  A3_cuantificador → contexto lingüístico rescata siempre (x²≥0 es tautología obvia)
  B1_equilibrio    → reacción Fe/Ce: el modelo deduce reversibilidad por química general
  C1_ipa           → corrupción no afecta al modelo (tokenización fortuita robusta)
"""

FRAGMENTOS = [

    # ── Alta frecuencia ───────────────────────────────────────────────────────
    {
        "id": "A4_producto_cart",
        "domain": "Matemática",
        "level": "alta",
        "critical_symbol": "×",
        "document": "Sea f: ℝ × ℝ → ℝ",
        "question": "¿El dominio de f son pares ordenados de reales o números reales individuales?",
        "context_definition": (
            "× entre conjuntos denota el producto cartesiano: ℝ × ℝ es el conjunto "
            "de todos los pares ordenados de números reales."
        ),
        "reference_answers": [
            "El dominio son pares ordenados de reales.",
            "El dominio de f son pares (x, y) con x e y en ℝ, no reales individuales.",
            "f toma como entrada pares de números reales, no valores individuales.",
        ],
        "wrong_reference": "El dominio son números reales individuales, no pares.",
        "expected": ["pares ordenados", "pares", "par ordenado", "pares de reales"],
        "forbidden": ["números individuales", "individuales", "un número", "un solo número"],
    },

    # ── Media frecuencia ──────────────────────────────────────────────────────
    {
        "id": "B2_angstrom",
        "domain": "Física",
        "level": "media",
        "critical_symbol": "Å",
        "document": "λ = 550 Å",
        "question": "La unidad de longitud indicada, ¿es más pequeña o más grande que 1 milímetro?",
        "context_definition": (
            "Å es el ångström: unidad de longitud equivalente a 10⁻¹⁰ metros "
            "(0,0000001 mm), usada para longitudes de onda de luz visible."
        ),
        "reference_answers": [
            "Es mucho más pequeña que un milímetro.",
            "El ångström es mucho menor que 1 mm; equivale a 10⁻¹⁰ metros.",
            "La unidad es más chica que un milímetro, es una unidad subatómica de longitud.",
        ],
        "wrong_reference": "La unidad es más grande que un milímetro.",
        "expected": ["más pequeña", "menor", "mucho menor", "más chica", "inferior"],
        "forbidden": ["más grande", "mayor", "superior", "grande"],
    },

    {
        "id": "B3_modal",
        "domain": "Lógica Modal",
        "level": "media",
        "critical_symbol": "□",
        "document": "□P → P",
        "question": "¿Esta expresión tiene la misma forma lógica que P → P?",
        "context_definition": (
            "□ es el operador modal de necesidad: □P se lee 'P es necesariamente "
            "verdadero', que es una afirmación más fuerte que P solo."
        ),
        "reference_answers": [
            "No, no tienen la misma forma lógica. □P introduce el operador modal de necesidad, que es más fuerte que P simple.",
            "No son iguales: □P → P dice que lo necesariamente verdadero implica lo verdadero, lo cual es distinto de P → P.",
            "No. La forma lógica es diferente porque □ agrega una capa modal que P → P no tiene.",
        ],
        "wrong_reference": "Sí, tienen la misma forma lógica, es equivalente a P → P.",
        "expected": ["no", "no tiene", "no es igual", "distinta", "diferente", "no son iguales"],
        "forbidden": ["igual", "idéntica", "misma forma", "la misma"],
    },

    {
        "id": "B4_subconjunto",
        "domain": "Matemática / Teoría de conjuntos",
        "level": "media",
        # ⊂ (subconjunto estricto): A⊂B y B⊂A es imposible (contradicción)
        # El modelo conoce A⊆B ∧ B⊆A → A=B (antisimetría) y confunde ⊂ con ⊆
        "critical_symbol": "⊂",
        "document": "A ⊂ B y B ⊂ A",
        "question": "¿Se puede concluir que A y B son iguales?",
        "context_definition": (
            "⊂ denota subconjunto estricto: A ⊂ B significa que A está contenido "
            "en B pero A ≠ B. Es diferente de ⊆ que permite la igualdad."
        ),
        # Con ⊂ estricto: A⊂B y B⊂A simultáneamente es imposible → premisa inconsistente
        "reference_answers": [
            "No, no se puede concluir que son iguales. Con subconjunto estricto, A⊂B y B⊂A es una contradicción.",
            "No. La premisa es inconsistente: ⊂ estricto prohíbe la igualdad, por lo que A⊂B y B⊂A no pueden ser simultáneamente verdaderos.",
            "Es imposible concluir la igualdad; de hecho la premisa misma es una contradicción con subconjunto estricto.",
        ],
        "wrong_reference": "Sí, se puede concluir que A y B son iguales por antisimetría.",
        "expected": ["no", "no se puede", "imposible", "contradicción", "inconsistente"],
        "forbidden": ["sí", "si", "son iguales", "iguales", "se puede concluir"],
    },

    # ── Baja frecuencia ───────────────────────────────────────────────────────
    {
        "id": "C2_interpunct",
        "domain": "Historia / Epigrafía",
        "level": "baja",
        "critical_symbol": "·",
        # Nombre romano real pero sin notoriedad: el modelo no puede inferir por conocimiento
        "document": "SEXTUS·RUFINUS·MAXIMUS",
        "question": "¿Cuántas palabras distintas componen este texto?",
        "context_definition": (
            "· (interpunct o punto mediano) es el separador de palabras del latín "
            "clásico: divide el texto en unidades léxicas independientes."
        ),
        "reference_answers": [
            "El texto tiene tres palabras: SEXTUS, RUFINUS y MAXIMUS.",
            "Son tres palabras distintas separadas por el interpunct.",
            "Tres palabras. El punto mediano actúa como separador de palabras en latín clásico.",
        ],
        "wrong_reference": "El texto es una sola palabra.",
        "expected": ["tres", "3", "tres palabras", "tres partes"],
        "forbidden": ["una", "uno", "dos", "2", "cuatro", "una sola"],
    },

    {
        "id": "C3_musical",
        "domain": "Música",
        "level": "baja",
        "critical_symbol": "♭",
        "document": "La escala comienza en si♭",
        "question": "¿Esta nota es más aguda o más grave que si natural?",
        "context_definition": (
            "♭ (bemol) baja la nota un semitono: si♭ es medio tono más grave "
            "(más bajo en frecuencia) que si natural."
        ),
        "reference_answers": [
            "Si♭ es más grave que si natural.",
            "Es más baja en frecuencia: el bemol baja la nota un semitono.",
            "Más grave. El bemol indica que la nota baja medio tono respecto al si natural.",
        ],
        "wrong_reference": "Si♭ es más aguda que si natural porque el bemol sube la nota.",
        "expected": ["más grave", "grave", "más baja", "inferior", "menor", "más bajo"],
        "forbidden": ["más aguda", "aguda", "más alta", "superior", "igual", "lo mismo"],
    },

    {
        "id": "C4_obelus",
        "domain": "Filología / Crítica textual",
        "level": "baja",
        "critical_symbol": "†",
        "document": "omnia †vincit† amor",
        "question": "¿El texto encerrado entre los dos símbolos es considerado original o de autenticidad dudosa?",
        "context_definition": (
            "† (obelo) es una marca editorial en textos clásicos: indica que el "
            "texto así delimitado es considerado corrupto o de autenticidad dudosa."
        ),
        "reference_answers": [
            "Es de autenticidad dudosa. El obelo marca texto corrupto o cuestionado.",
            "El texto encerrado es considerado corrupto o de dudosa autenticidad por los editores.",
            "No es original; el símbolo † indica que ese fragmento es de procedencia incierta.",
        ],
        "wrong_reference": "El texto encerrado es auténtico y original.",
        "expected": ["dudoso", "corrupto", "no es original", "cuestionado", "dudosa autenticidad", "dudosa"],
        "forbidden": ["original", "seguro", "auténtico", "es original", "genuino"],
    },
]