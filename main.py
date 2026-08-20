"""Punto de entrada del experimento.

Uso:
    # Corrida completa (defaults de config.py)
    python main.py

    # Especificar modelo y backend
    python main.py --modelo qwen3.5-2b --backend llama_cpp
    python main.py --modelo qwen3-4b   --backend ollama    # PC de escritorio

    # Filtrar fragmentos (corrida focalizada)
    python main.py --fragmentos B3_modal B4_subconjunto

    # Filtrar condiciones (solo Instruction Hierarchy)
    python main.py --condiciones i1_a i1_b i1_c i1_d

    # Combinar filtros
    python main.py --fragmentos B3_modal B4_subconjunto --condiciones i1_d

    # Listar opciones disponibles
    python main.py --list-modelos
    python main.py --list-estrategias
    python main.py --list-backends
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from config import (
    MODEL_REGISTRY,
    DEFAULT_MODEL,
    DEFAULT_BACKEND,
    LLAMA_CPP_URL,
    OLLAMA_URL,
    TEMPERATURE,
    MAX_TOKENS,
)
from backends import get_backend, list_backends
from prompt_strategies import list_strategies
from experiment import correr_experimento
from echo_experiment import correr_echo, save_echo_results
from report import save_all


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Experimento RAG — Comprensión + Instruction Hierarchy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--modelo",
        default=DEFAULT_MODEL,
        metavar="ID",
        help=f"ID del modelo en MODEL_REGISTRY (default: {DEFAULT_MODEL}). "
             f"Disponibles: {', '.join(MODEL_REGISTRY)}",
    )
    parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND,
        choices=list_backends(),
        help=f"Backend LLM a usar (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--fragmentos",
        nargs="+",
        metavar="ID",
        default=None,
        help="IDs de fragmentos a correr (default: todos). "
             "Ej: --fragmentos B3_modal B4_subconjunto",
    )
    parser.add_argument(
        "--condiciones",
        nargs="+",
        metavar="STRATEGY_ID",
        default=None,
        help="IDs de estrategias a correr (default: todas). "
             "Ej: --condiciones i1_a i1_b i1_c i1_d",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        default=False,
        help="Habilitar thinking mode (razonamiento interno del modelo). "
             "Requiere modelos compatibles (Qwen3). "
             "El run_id incluirá '_think' o '_nothink' según esta opción.",
    )
    parser.add_argument(
        "--modo",
        choices=["experimento", "echo"],
        default="experimento",
        help=(
            "Modo de ejecución: "
            "'experimento' (default) corre el experimento principal (7 fragmentos × 8 condiciones). "
            "'echo' corre el experimento de fidelidad de caracteres: verifica si el modelo "
            "reproduce las cadenas corruptas sin normalizarlas."
        ),
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        default=False,
        help="Lanzar la interfaz visual interactiva basada en Textual (TUI con paneles y columnas).",
    )
    parser.add_argument(
        "--list-modelos",
        action="store_true",
        help="Lista los modelos disponibles y sale.",
    )
    parser.add_argument(
        "--list-estrategias",
        action="store_true",
        help="Lista las estrategias de prompt disponibles y sale.",
    )
    parser.add_argument(
        "--list-backends",
        action="store_true",
        help="Lista los backends disponibles y sale.",
    )

    return parser


# ── Helpers de listado ────────────────────────────────────────────────────────

def cmd_list_modelos():
    print("\nModelos registrados:\n")
    print(f"  {'ID':<15} {'GGUF':<45} {'Ollama':<20} {'Disponible'}")
    print("  " + "─" * 90)
    for m in MODEL_REGISTRY.values():
        disponible = "✅" if m.available else "🔲 (stub)"
        print(f"  {m.id:<15} {m.gguf_name:<45} {m.ollama_name:<20} {disponible}")
        if m.notes:
            print(f"  {'':15} {m.notes}")
    print()


def cmd_list_estrategias():
    print("\nEstrategias de prompt registradas:\n")
    for s in list_strategies():
        print(f"  {s['id']:<15} {s['label']}")
    print()


def cmd_list_backends():
    print("\nBackends disponibles:\n")
    for b in list_backends():
        print(f"  {b}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args   = parser.parse_args()

    # Comandos de listado (salen inmediatamente)
    if args.list_modelos:
        cmd_list_modelos(); return
    if args.list_estrategias:
        cmd_list_estrategias(); return
    if args.list_backends:
        cmd_list_backends(); return

    # Validar modelo
    if args.modelo not in MODEL_REGISTRY:
        print(f"❌ Modelo '{args.modelo}' no registrado.")
        cmd_list_modelos()
        sys.exit(1)

    model_cfg = MODEL_REGISTRY[args.modelo]
    if not model_cfg.available:
        print(
            f"❌ Modelo '{args.modelo}' marcado como stub (aún no descargado).\n"
            f"   Actualizá 'available=True' en config.py cuando esté listo."
        )
        sys.exit(1)

    # Construir el backend
    backend_kwargs: dict = {
        "temperature":   TEMPERATURE,
        "max_tokens":    MAX_TOKENS,
        "thinking_mode": args.thinking,
    }

    if args.backend == "llama_cpp":
        backend_kwargs["base_url"] = LLAMA_CPP_URL
        backend_kwargs["model_id"] = model_cfg.gguf_name
    elif args.backend == "ollama":
        backend_kwargs["base_url"] = OLLAMA_URL
        backend_kwargs["model"]    = model_cfg.ollama_name

    print(f"\nConectando con backend '{args.backend}'...")
    backend = get_backend(args.backend, **backend_kwargs)

    if not backend.health_check():
        if args.backend == "llama_cpp":
            print(
                f"❌ llama-server no responde en {LLAMA_CPP_URL}.\n"
                f"   Lanzalo con: ./serve.sh {args.modelo}"
            )
        else:
            print(
                f"❌ Ollama no responde en {OLLAMA_URL}.\n"
                f"   Lanzalo con: ollama serve"
            )
        sys.exit(1)

    print(f"✅ Backend activo | modelo: {args.modelo}\n")

    if args.tui:
        from tui import ExperimentTUIApp
        app = ExperimentTUIApp(
            backend=backend,
            modelo_id=args.modelo,
            backend_name=args.backend,
            modo=args.modo,
            thinking_mode=args.thinking,
            fragmentos_filter=args.fragmentos,
            condiciones_filter=args.condiciones,
        )
        app.run()
        return

    if args.modo == "echo":
        run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.modelo}_{args.backend}_echo"

        results = correr_echo(
            backend=backend,
            modelo_id=args.modelo,
            run_id=run_id,
        )

        json_path, txt_path, md_path = save_echo_results(
            results=results,
            run_id=run_id,
            modelo_id=args.modelo,
            backend_name=args.backend,
        )

        print(f"\n{'='*72}")
        print(f"✅ Resultados de eco guardados en results_echo/{run_id}/")
        print(f"   JSON:     {json_path}")
        print(f"   TXT:      {txt_path}")
        print(f"   Markdown: {md_path}")

    else:
        # Run ID único por corrida — incluye si thinking está activo
        think_tag = "think" if args.thinking else "nothink"
        run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.modelo}_{args.backend}_{think_tag}"

        # Correr el experimento
        results = correr_experimento(
            backend=backend,
            modelo_id=args.modelo,
            run_id=run_id,
            thinking_mode=args.thinking,
            fragmentos_filter=args.fragmentos,
            condiciones_filter=args.condiciones,
        )

        # Guardar resultados
        json_path, txt_path, md_path = save_all(
            results=results,
            run_id=run_id,
            modelo_id=args.modelo,
            backend_name=args.backend,
        )

        print(f"\n{'='*72}")
        print(f"✅ Resultados guardados en results/{run_id}/")
        print(f"   JSON:     {json_path}")
        print(f"   TXT:      {txt_path}")
        print(f"   Markdown: {md_path}")


if __name__ == "__main__":
    main()
