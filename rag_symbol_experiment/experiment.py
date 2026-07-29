"""Coordinador del experimento: recorre el corpus y registra resultados."""

from datetime import datetime

from corpus import FRAGMENTOS
from config import CONDICIONES, MODELO as MODELO_DEFAULT
from corruption import build_condition
from prompt_builder import build_prompt
from ollama_client import query
from evaluator import evaluate_response
from report import generar_resumen, save_results


def correr_experimento(modelo: str = None):
    modelo = modelo or MODELO_DEFAULT
    resultados = []
    lineas_log = []

    header = (
        f"\n{'='*70}\n"
        f"EXPERIMENTO FASE 1 — COMPRENSIÓN\n"
        f"Modelo: {modelo}\n"
        f"Fecha:  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'='*70}\n"
    )
    print(header)
    lineas_log.append(header)

    for frag in FRAGMENTOS:
        bloque = f"\n{'─'*70}\n📄 {frag['id']}\n{'─'*70}"
        print(bloque)
        lineas_log.append(bloque)

        frag_info = (
            f"Pregunta:    {frag['question']}\n"
            f"Esperado:    {' / '.join(frag['expected'])}\n"
            f"Incorrecto:  {' / '.join(frag['forbidden'])}\n"
        )
        print(frag_info)
        lineas_log.append(frag_info)

        for etiqueta, version, con_tabla, corrupt_question in CONDICIONES:
            texto = build_condition(frag['document'], version, frag['critical_symbol'])
            print(f"  [{etiqueta}] ...", end=" ", flush=True)

            prompt = build_prompt(
                frag,
                texto,
                frag['question'],
                con_tabla,
                corrupt_question=corrupt_question,
            )

            try:
                respuesta = query(prompt, modelo=modelo)
            except Exception as e:
                respuesta = f"[ERROR: {e}]"

            evaluacion = evaluate_response(respuesta, frag['expected'], frag['forbidden'])

            linea = (
                f"\n  [{etiqueta}]\n"
                f"  Respuesta:  {respuesta}\n"
                f"  Resultado:  {evaluacion}"
            )
            print(evaluacion)
            lineas_log.append(linea)

            resultados.append({
                "fragmento":        frag["id"],
                "nivel":            frag.get("level", "?"),
                "condicion":        etiqueta,
                "version_doc":      version,
                "con_tabla":        con_tabla,
                "corrupt_question": corrupt_question,
                "prompt":           prompt,
                "respuesta":        respuesta,
                "esperado":         frag["expected"],
                "evaluacion_auto":  evaluacion,   # provisional — revisar manualmente
            })

    resumen = generar_resumen(resultados)
    print(resumen)
    lineas_log.append(resumen)

    txt_path, json_path = save_results(resultados, lineas_log, modelo)
    print(f"\n✅ Resultados guardados en {txt_path} y {json_path}")

    return resultados