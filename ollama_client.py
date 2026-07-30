"""Cliente mínimo para consultar Ollama."""

import requests
from config import OLLAMA_URL, MODELO as _MODELO_DEFAULT, TEMPERATURE, NUM_PREDICT


def query(prompt: str, modelo: str = None, timeout: int = 60) -> str:
    _modelo = modelo or _MODELO_DEFAULT
    payload = {
        "model": _modelo,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT,
        },
        "think": False,
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", "").strip()
