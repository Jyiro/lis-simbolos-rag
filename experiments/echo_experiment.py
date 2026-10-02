"""Módulo para el experimento de fidelidad de eco de caracteres corruptos.

Verifica si el LLM normaliza (sanitiza) los caracteres corruptos (Mojibake)
antes de procesarlos y responder, lo cual invalidaría la premisa del experimento.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backends.base import LLMBackend

from config import ECHO_RESULTS_DIR
from context_tables import CORRUPT_MAP
from corpus import FRAGMENTOS


ECHO_PROMPT_TEMPLATE = """\
Copiá el siguiente texto exactamente como aparece, \
carácter por carácter, sin modificarlo, corregirlo ni interpretarlo.
No agregues ningún texto adicional. Solo copiá:

{corrupt_text}"""


@dataclass
class EchoResult:
    """Resultado de una prueba de fidelidad de eco."""
    run_id:           str
    model_id:         str
    backend_name:     str
    timestamp:        str

    symbol_clean:     str   # símbolo limpio original (ej: "□")
    symbol_corrupt:   str   # versión mojibake enviada (ej: "â–¡")
    context_clean:    str   # fragmento de contexto limpio (ej: "□P → P")
    context_corrupt:  str   # fragmento con mojibake aplicado (ej: "â–¡P â P")

    prompt_sent:      str   # prompt completo enviado al modelo
    response_raw:     str   # respuesta cruda del modelo
    response_clean:   str   # respuesta stripped

    # Comparación byte a byte
    sent_bytes:       str   # hex de la cadena enviada (context_corrupt)
    received_bytes:   str   # hex de lo que el modelo devolvió
    
    # Resultado de la evaluación
    levenshtein_dist: int   # Distancia de edición entre enviado y recibido
    eval_result:      str   # "FIEL" | "NORMALIZADO" | "PARCIAL" | "IRRECONOCIBLE"
    eval_detail:      str   # explicación del resultado


def _string_to_hex(s: str) -> str:
    """Convierte un string a su representación hexadecimal UTF-8."""
    return " ".join([f"{b:02x}" for b in s.encode('utf-8')])


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula la distancia de edición (Levenshtein) entre dos cadenas."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def evaluate_echo(sent: str, received: str, symbol_clean: str) -> tuple[int, str, str]:
    """Evalúa la respuesta del modelo comparando lo enviado vs lo recibido."""
    sent_clean = sent.strip()
    received_clean = received.strip()
    dist = levenshtein_distance(sent_clean, received_clean)

    if dist == 0:
        return dist, "FIEL", "El modelo reprodujo la cadena corrupta exactamente."
    
    # Si no es exacto, veamos si "corrigió" el símbolo
    if symbol_clean in received_clean and symbol_clean not in sent_clean:
        return dist, "NORMALIZADO", f"El modelo reemplazó el mojibake por el símbolo limpio '{symbol_clean}'."
    
    # Veamos si al menos devolvió una cadena similar pero no exacta
    # Usamos la distancia normalizada (Character Error Rate)
    max_len = max(len(sent_clean), len(received_clean))
    cer = dist / max_len if max_len > 0 else 1.0
    
    if cer < 0.5:
         return dist, "PARCIAL", f"El modelo alteró algunos caracteres pero mantuvo la estructura (CER: {cer:.2f})."
         
    return dist, "IRRECONOCIBLE", f"La respuesta difiere significativamente del input esperado (CER: {cer:.2f})."


def build_echo_corpus() -> list[dict]:
    """Construye el corpus de prueba para eco basado en los símbolos críticos."""
    # Extraer los símbolos críticos usados en el corpus principal
    critical_symbols = {f["critical_symbol"] for f in FRAGMENTOS}
    
    # Filtrar solo los que están en CORRUPT_MAP
    echo_corpus = []
    
    # Para tener contexto realista, buscamos un documento de ejemplo para cada símbolo
    for sym in critical_symbols:
        if sym not in CORRUPT_MAP:
            continue
            
        corrupt = CORRUPT_MAP[sym]
        
        # Encontrar el primer fragmento que use este símbolo
        doc_clean = next((f["document"] for f in FRAGMENTOS if f["critical_symbol"] == sym), sym)
        
        # Corromper SOLO el símbolo crítico para esta prueba (para que sea una prueba aislada)
        # o aplicar corrupción completa? Mejor aplicar corrupción a la ocurrencia del símbolo.
        doc_corrupt = doc_clean.replace(sym, corrupt)
        
        echo_corpus.append({
            "symbol": sym,
            "corrupted": corrupt,
            "context": doc_clean,
            "corrupted_context": doc_corrupt
        })
        
    return sorted(echo_corpus, key=lambda x: x["symbol"])


def correr_echo(
    backend: LLMBackend,
    modelo_id: str,
    run_id: str,
) -> list[EchoResult]:
    """Ejecuta el experimento de eco."""
    from datetime import datetime
    
    corpus = build_echo_corpus()
    results = []
    
    print(f"\nIniciando experimento de ECO con {len(corpus)} fragmentos...")
    
    for item in corpus:
        sym = item["symbol"]
        corrupt_ctx = item["corrupted_context"]
        
        print(f"  Procesando símbolo '{sym}' -> '{item['corrupted']}'...")
        
        prompt = ECHO_PROMPT_TEMPLATE.format(corrupt_text=corrupt_ctx)
        
        # Llamar al backend
        timestamp = datetime.now().isoformat()
        
        thinking_started = [False]
        answer_started   = [False]

        def _on_thinking(t: str, _ts=thinking_started) -> None:
            if not _ts[0]:
                print("   💭 ", end="", flush=True)
                _ts[0] = True
            print(t, end="", flush=True)

        def _on_answer(t: str, _ts=thinking_started, _as=answer_started) -> None:
            if not _as[0]:
                sep = "\n" if _ts[0] else ""
                print(f"{sep}   → ", end="", flush=True)
                _as[0] = True
            print(t, end="", flush=True)

        try:
            resp = backend.query(
                user_prompt=prompt,
                system_prompt=None,
                on_token=_on_answer,
                on_thinking_token=_on_thinking,
            )
            response_raw = resp.text
            print() # newline after streaming
        except Exception as e:
            response_raw = f"[ERROR] {e}"
            
        response_clean = response_raw.strip()
        sent_clean = corrupt_ctx.strip()
        
        dist, eval_res, eval_det = evaluate_echo(sent_clean, response_clean, sym)
        
        res = EchoResult(
            run_id=run_id,
            model_id=modelo_id,
            backend_name=backend.NAME,
            timestamp=timestamp,
            symbol_clean=sym,
            symbol_corrupt=item["corrupted"],
            context_clean=item["context"],
            context_corrupt=item["corrupted_context"],
            prompt_sent=prompt,
            response_raw=response_raw,
            response_clean=response_clean,
            sent_bytes=_string_to_hex(sent_clean),
            received_bytes=_string_to_hex(response_clean),
            levenshtein_dist=dist,
            eval_result=eval_res,
            eval_detail=eval_det
        )
        results.append(res)
        
    return results


def save_echo_results(
    results: list[EchoResult],
    run_id: str,
    modelo_id: str,
    backend_name: str,
) -> tuple[str, str, str]:
    """Guarda los resultados del experimento de eco."""
    run_dir = os.path.join(ECHO_RESULTS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    json_path = os.path.join(run_dir, "echo_results.json")
    txt_path = os.path.join(run_dir, "echo_summary.txt")
    md_path = os.path.join(run_dir, "echo_report.md")
    
    # JSON
    payload = {
        "metadata": {
            "run_id": run_id,
            "model_id": modelo_id,
            "backend": backend_name,
            "total_results": len(results)
        },
        "results": [asdict(r) for r in results]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    # TXT
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"REPORTE ECHO TEST - {run_id}\n")
        f.write(f"{'='*85}\n")
        f.write(f"{'SYM':<5} {'CORRUPT':<10} {'EVAL':<15} {'DIST':<5} {'RECIBIDO':<30}\n")
        f.write(f"{'-'*85}\n")
        for r in results:
            recibido = r.response_clean[:27] + "..." if len(r.response_clean) > 30 else r.response_clean
            recibido = recibido.replace("\n", " ")
            f.write(f"{r.symbol_clean:<5} {r.symbol_corrupt:<10} {r.eval_result:<15} {r.levenshtein_dist:<5} {recibido:<30}\n")
            
    # MD
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Reporte de Experimento ECHO\n\n")
        f.write(f"- **Modelo:** `{modelo_id}`\n")
        f.write(f"- **Backend:** `{backend_name}`\n")
        f.write(f"- **Run ID:** `{run_id}`\n\n")
        
        f.write("## Resumen de Fidelidad\n\n")
        f.write("| Símbolo | Corrupto | Distancia | Resultado | Texto Enviado | Texto Recibido |\n")
        f.write("|:---:|:---:|:---:|:---|:---|:---|\n")
        for r in results:
            send = r.context_corrupt.replace("\n", " ")
            recv = r.response_clean.replace("\n", " ")
            f.write(f"| `{r.symbol_clean}` | `{r.symbol_corrupt}` | {r.levenshtein_dist} | **{r.eval_result}** | `{send}` | `{recv}` |\n")
            
        f.write("\n## Detalle Hexadecimal (Auditoría Byte a Byte)\n\n")
        for r in results:
            f.write(f"### Símbolo: `{r.symbol_clean}`\n\n")
            f.write(f"- **Enviado (UTF-8 Hex):** `{r.sent_bytes}`\n")
            f.write(f"- **Recibido (UTF-8 Hex):** `{r.received_bytes}`\n")
            f.write(f"- **Detalle:** {r.eval_detail}\n\n")
            f.write(f"**Comparación de texto:**\n")
            f.write("```text\n")
            f.write(f"[SEND]: {r.context_corrupt}\n")
            f.write(f"[RECV]: {r.response_clean}\n")
            f.write("```\n\n")
            
    return json_path, txt_path, md_path
