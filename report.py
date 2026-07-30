"""Generación de reportes y guardado de resultados."""

import json
import os
from datetime import datetime
from collections import defaultdict
from config import RESULTS_DIR


def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def save_results(resultados: list, log_lines: list, modelo: str = "default"):
    ensure_results_dir()
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    modelo_limpio = modelo.replace(":", "_").replace("-", "_")
    txt_path  = os.path.join(RESULTS_DIR, f"resultados_fase1_{modelo_limpio}_{fecha}.txt")
    json_path = os.path.join(RESULTS_DIR, f"resultados_fase1_{modelo_limpio}_{fecha}.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    return txt_path, json_path


def generar_resumen(resultados: list) -> str:
    lineas = [f"\n{'='*70}\nRESUMEN\n{'='*70}"]

    por_condicion = defaultdict(list)
    for r in resultados:
        por_condicion[r["condicion"]].append(r["evaluacion_auto"])

    lineas.append(
        f"\n{'Condición':<30} {'✓ Correct':>10} {'✗ Confund':>10} {'? Sin resp':>11} Total"
    )
    lineas.append("─" * 68)

    for condicion, evaluaciones in por_condicion.items():
        correctos   = evaluaciones.count("✓ CORRECTO")
        confundidos = evaluaciones.count("✗ CONFUNDIDO")
        sin_resp    = evaluaciones.count("? SIN RESPUESTA")
        total       = len(evaluaciones)
        lineas.append(
            f"{condicion:<30} {correctos:>5}/{total:<4} {confundidos:>5}/{total:<4} {sin_resp:>6}/{total:<4} {total}"
        )

    # Resumen por nivel de frecuencia
    lineas.append(f"\n{'─'*68}")
    lineas.append("Por nivel (condición LIMPIO):")
    por_nivel = defaultdict(list)
    for r in resultados:
        if "LIMPIO" in r["condicion"]:
            por_nivel[r.get("nivel", "?")].append(r["evaluacion_auto"])
    for nivel, evals in sorted(por_nivel.items()):
        c = evals.count("✓ CORRECTO")
        x = evals.count("✗ CONFUNDIDO")
        s = evals.count("? SIN RESPUESTA")
        t = len(evals)
        lineas.append(f"  {nivel:<6} → ✓{c}/{t}  ✗{x}/{t}  ?{s}/{t}")

    lineas.append("""
Categorías:
  ✓ CORRECTO      → respondió con al menos un término clave correcto
  ✗ CONFUNDIDO    → respondió con un término específicamente incorrecto
  ? SIN RESPUESTA → no dijo nada correcto ni incorrecto

Condiciones:
  LIMPIO    | doc✓ query✓ → techo: modelo con símbolos perfectos
  DOC CORR  | doc✗ query✓ → escenario RAG más común
  FULL CORR | doc✗ query✗ → peor caso
  QUERY CORR| doc✓ query✗ → usuario con clipboard corrupto
  CON TABLA | doc✗ query✓ → efecto del prompt engineering
  LATEX     | doc~ query✓ → notación LaTeX alternativa
""")

    return "\n".join(lineas)