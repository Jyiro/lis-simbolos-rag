"""Corpus experimental — 12 fragmentos en tres niveles de frecuencia estimada.

Diseño de cada fragmento:
  - El símbolo es la única pista semántica para responder la pregunta.
  - El texto circundante no permite deducir la respuesta sin el símbolo.
  - La respuesta incorrecta "inteligente" sin el símbolo es predecible.
  - La pregunta no menciona el símbolo.

Hipótesis experimental (descriptiva, observable):
  Alta frecuencia  → CONFUNDIDO bajo corrupción (el modelo tiene rep. interna activable)
  Baja frecuencia  → SIN RESPUESTA bajo corrupción (y posiblemente también en LIMPIO)
"""

FRAGMENTOS = [

    # ── Alta frecuencia ───────────────────────────────────────────────────
    {
        "id": "A1_desigualdad",
        "domain": "Matemática",
        "level": "alta",
        "critical_symbol": "≥",
        "document": "Aprobado si nota ≥ 6. Juan obtuvo 6.",
        "question": "¿Juan aprobó?",
        "context_definition": (
            "≥ significa 'mayor o igual que': el umbral incluye el valor exacto, "
            "un puntaje igual al mínimo requerido también aprueba."
        ),
        "expected": ["sí", "si", "aprobó", "pasó"],
        "forbidden": ["no aprobó", "reprobó", "insuficiente", "desaprobó"],
    },

    {
        "id": "A2_bicondicional",
        "domain": "Lógica",
        "level": "alta",
        "critical_symbol": "⟺",
        "document": "A ⟺ B. B es falso.",
        "question": "¿Qué valor de verdad tiene A?",
        "context_definition": (
            "⟺ es el bicondicional lógico: A ⟺ B significa que A y B tienen "
            "siempre el mismo valor de verdad."
        ),
        "expected": ["falso", "false", "falsa"],
        "forbidden": ["verdadero", "true", "verdadera", "no se puede", "indeterminado", "depende"],
    },

    {
        "id": "A3_cuantificador",
        "domain": "Matemática",
        "level": "alta",
        "critical_symbol": "∀",
        "document": "∀x ∈ ℝ : x² ≥ 0",
        "question": "¿La afirmación vale para todos los reales o solo para alguno?",
        "context_definition": (
            "∀ significa 'para todo': la afirmación se sostiene para cada elemento "
            "del conjunto, sin excepción."
        ),
        "expected": ["todos", "todo", "para todo", "cada", "cualquier"],
        "forbidden": ["alguno", "algunos", "existe", "hay algún", "solo para", "algún"],
    },

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
        "expected": ["pares ordenados", "pares", "par ordenado", "pares de reales"],
        "forbidden": ["números individuales", "individuales", "un número", "un solo número"],
    },

    # ── Media frecuencia ──────────────────────────────────────────────────
    {
        "id": "B1_equilibrio",
        "domain": "Química",
        "level": "media",
        "critical_symbol": "⇌",
        # Reacción redox real pero no famosa — evita conocimiento memorizado
        "document": "Fe²⁺ + Ce⁴⁺ ⇌ Fe³⁺ + Ce³⁺",
        "question": "¿La reacción puede ocurrir en ambos sentidos?",
        "context_definition": (
            "⇌ indica una reacción química reversible: puede ocurrir tanto en el "
            "sentido directo (reactivos → productos) como en el inverso."
        ),
        "expected": ["sí", "si", "ambos", "reversible", "bidireccional", "en ambos sentidos"],
        "forbidden": ["solo un sentido", "unidireccional", "irreversible", "un solo sentido"],
    },

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
        "expected": ["no", "no tiene", "no es igual", "distinta", "diferente", "no son iguales"],
        "forbidden": ["igual", "idéntica", "misma forma", "la misma"],
    },

    {
        "id": "B4_subconjunto",
        "domain": "Matemática / Teoría de conjuntos",
        "level": "media",
        # ∃! reemplazado: cualquier ecuación con solución única el modelo la resuelve
        # ⊂ (subconjunto estricto) vs ⊆ tiene bifurcación real: A⊂B y B⊂C no implica A=C
        "critical_symbol": "⊂",
        "document": "A ⊂ B y B ⊂ A",
        "question": "¿Se puede concluir que A y B son iguales?",
        "context_definition": (
            "⊂ denota subconjunto estricto: A ⊂ B significa que A está contenido "
            "en B pero A ≠ B. Es diferente de ⊆ que permite la igualdad."
        ),
        # Sin ⊂: el modelo conoce que A⊆B y B⊆A implica A=B (antisimetría) → dice "sí"
        # Con ⊂ estricto: A⊂B requiere A≠B, pero si A⊂B y B⊂A simultáneamente
        # es imposible (contradicción) → la premisa es inconsistente → no se puede concluir
        "expected": ["no", "no se puede", "imposible", "contradicción", "inconsistente"],
        "forbidden": ["sí", "si", "son iguales", "iguales", "se puede concluir"],
    },

    # ── Baja frecuencia ───────────────────────────────────────────────────
    {
        "id": "C1_ipa",
        "domain": "Lingüística / Fonética",
        "level": "baja",
        "critical_symbol": "æ",
        "document": "La pronunciación es /bæd/",
        "question": "¿El segundo sonido de la pronunciación transcrita es una vocal o una consonante?",
        "context_definition": (
            "æ (ash) es una vocal del Alfabeto Fonético Internacional (AFI): "
            "representa el sonido vocálico de palabras como 'bad' o 'cat' en inglés."
        ),
        "expected": ["vocal", "es una vocal", "sonido vocal", "vocálico"],
        "forbidden": ["consonante", "es una consonante", "sonido consonántico"],
    },

    {
        "id": "C2_interpunct",
        "domain": "Historia / Epigrafía",
        "level": "baja",
        "critical_symbol": "·",
        # Cicerón reemplazado — demasiado famoso, el modelo sabe que son 3 nombres
        # Sextus Rufinus Maximus: nombre romano real pero sin notoriedad suficiente
        "document": "SEXTUS·RUFINUS·MAXIMUS",
        "question": "¿Cuántas palabras distintas componen este texto?",
        "context_definition": (
            "· (interpunct o punto mediano) es el separador de palabras del latín "
            "clásico: divide el texto en unidades léxicas independientes."
        ),
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
        "expected": ["dudoso", "corrupto", "no es original", "cuestionado", "dudosa autenticidad", "dudosa"],
        "forbidden": ["original", "seguro", "auténtico", "es original", "genuino"],
    },
]