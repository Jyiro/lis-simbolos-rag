"""Evaluadores simples para las respuestas del modelo."""


def evaluate_response(respuesta: str, esperado: list, no_esperado: list) -> str:
    r = respuesta.lower()

    es_incorrecto = any(term in r for term in no_esperado)
    aciertos = sum(1 for term in esperado if term in r)

    if es_incorrecto:
        return "✗ CONFUNDIDO"
    elif aciertos == 0:
        return "? SIN RESPUESTA"
    elif aciertos >= 1:
        return "✓ CORRECTO"

    return "△ PARCIAL"
