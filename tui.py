"""Interfaz TUI basada en Textual para streaming en vivo y layouts en columnas.

Soporta tanto el experimento principal como el modo echo.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, RichLog, DataTable, Label
from textual import work

if TYPE_CHECKING:
    from backends.base import LLMBackend


class ExperimentTUIApp(App):
    """Aplicación Textual TUI para visualización interactiva de experimentos."""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #status-bar {
        height: 3;
        background: $primary-background;
        color: $text;
        border: solid $primary;
        padding: 0 1;
        content-align: center middle;
    }

    #main-columns {
        height: 1fr;
        margin: 1 0;
    }

    .column-box {
        width: 1fr;
        height: 100%;
        border: round $secondary;
        margin: 0 1;
        padding: 0 1;
    }

    .column-box Title {
        text-style: bold;
        color: $accent;
    }

    #results-table-container {
        height: 10;
        border: solid $accent;
        margin: 0 1;
    }

    RichLog {
        height: 100%;
        overflow-y: scroll;
    }
    """

    BINDINGS = [
        ("q", "quit", "Salir"),
    ]

    def __init__(
        self,
        backend: LLMBackend,
        modelo_id: str,
        backend_name: str,
        modo: str = "experimento",
        thinking_mode: bool = False,
        fragmentos_filter: list[str] | None = None,
        condiciones_filter: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.backend = backend
        self.modelo_id = modelo_id
        self.backend_name = backend_name
        self.modo = modo
        self.thinking_mode = thinking_mode
        self.fragmentos_filter = fragmentos_filter
        self.condiciones_filter = condiciones_filter
        
        self.run_id = ""
        self.results = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        mode_title = "EXPERIMENTO PRINCIPAL" if self.modo == "experimento" else "MODO ECHO (FIDELIDAD)"
        yield Static(
            f"🚀 [bold cyan]{mode_title}[/bold cyan] | Modelo: [green]{self.modelo_id}[/green] | Backend: [yellow]{self.backend_name}[/yellow]",
            id="status-bar",
        )
        
        with Horizontal(id="main-columns"):
            with Container(classes="column-box"):
                yield Label("📌 Input / Prompt", classes="col-title")
                yield RichLog(id="log-prompt", highlight=True, markup=True)
                
            with Container(classes="column-box"):
                yield Label("💭 Thinking (Razonamiento)", classes="col-title")
                yield RichLog(id="log-thinking", highlight=True, markup=True)
                
            with Container(classes="column-box"):
                yield Label("→ Respuesta & Eval", classes="col-title")
                yield RichLog(id="log-response", highlight=True, markup=True)
                
        with Container(id="results-table-container"):
            yield DataTable(id="table-summary")
            
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table-summary", DataTable)
        if self.modo == "experimento":
            table.add_columns("Fragmento", "Condición", "Resultado", "Timing (ms)")
        else:
            table.add_columns("Símbolo", "Corrupto", "Evaluación", "Detalle")
            
        # Iniciar el worker background
        self.run_experiment_worker()

    @work(thread=True)
    def run_experiment_worker(self) -> None:
        """Ejecuta el experimento en un thread secundario y actualiza la UI."""
        if self.modo == "echo":
            self.run_echo_worker()
        else:
            self.run_main_experiment_worker()

    def run_main_experiment_worker(self) -> None:
        from experiment import correr_experimento, ExperimentResult
        from report import save_all
        from corpus import FRAGMENTOS
        from config import CONDICIONES
        from corruption import build_condition, corrupt_question
        from prompt_strategies import get_strategy
        from evaluator import evaluate_response
        import time

        think_tag = "think" if self.thinking_mode else "nothink"
        self.run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.modelo_id}_{self.backend_name}_{think_tag}"
        
        fragmentos = FRAGMENTOS
        if self.fragmentos_filter:
            fragmentos = [f for f in fragmentos if f["id"] in self.fragmentos_filter]

        condiciones = CONDICIONES
        if self.condiciones_filter:
            condiciones = [c for c in condiciones if c.strategy_id in self.condiciones_filter]

        total = len(fragmentos) * len(condiciones)
        current = 0

        for frag in fragmentos:
            doc_limpio = frag["document"]
            for cond in condiciones:
                current += 1
                doc_text = build_condition(doc_limpio, cond.doc_version)
                question = frag["question"]
                if cond.corrupt_query:
                    question = corrupt_question(question)

                strategy = get_strategy(cond.strategy_id)
                prompt = strategy.build(frag, doc_text, question)

                # Reset UI logs
                self.call_from_thread(self._clear_logs)
                
                # Update status
                status_msg = f"[{current}/{total}] Fragmento: [bold]{frag['id']}[/bold] | Condición: [yellow]{cond.label}[/yellow]"
                self.call_from_thread(self._update_status, status_msg)

                # Log prompt
                prompt_text = f"[bold yellow]USER:[/bold yellow]\n{prompt.user_prompt}"
                if prompt.system_prompt:
                    prompt_text = f"[bold magenta]SYSTEM:[/bold magenta]\n{prompt.system_prompt}\n\n" + prompt_text
                self.call_from_thread(self._append_log, "#log-prompt", prompt_text)

                # Callbacks
                def on_thinking(t: str) -> None:
                    self.call_from_thread(self._append_log, "#log-thinking", t, end="")

                def on_answer(t: str) -> None:
                    self.call_from_thread(self._append_log, "#log-response", t, end="")

                try:
                    resp = self.backend.query(
                        user_prompt=prompt.user_prompt,
                        system_prompt=prompt.system_prompt,
                        on_token=on_answer,
                        on_thinking_token=on_thinking,
                    )
                    resp_text = resp.text
                    resp_thinking = resp.thinking_text
                    timing_ms = resp.timing_ms
                except Exception as e:
                    resp_text = f"[ERROR: {e}]"
                    resp_thinking = ""
                    timing_ms = 0.0

                eval_res = evaluate_response(resp_text, frag["expected"], frag["forbidden"])
                
                # Update table
                self.call_from_thread(
                    self._add_table_row,
                    frag["id"],
                    cond.label.strip(),
                    eval_res.result,
                    f"{timing_ms:.0f}ms",
                )

                res_obj = ExperimentResult(
                    run_id=self.run_id,
                    model_id=self.modelo_id,
                    backend_name=self.backend_name,
                    timestamp=datetime.now().isoformat(),
                    fragment_id=frag["id"],
                    fragment_level=frag.get("level", "?"),
                    fragment_domain=frag.get("domain", "?"),
                    critical_symbol=frag["critical_symbol"],
                    condition_label=cond.label,
                    doc_version=cond.doc_version,
                    strategy_id=cond.strategy_id,
                    strategy_label=strategy.label,
                    corrupt_query=cond.corrupt_query,
                    doc_limpio=doc_limpio,
                    doc_corrupto=build_condition(doc_limpio, "corrupto"),
                    doc_latex=build_condition(doc_limpio, "latex"),
                    prompt_user=prompt.user_prompt,
                    prompt_system=prompt.system_prompt,
                    question_used=question,
                    response=resp_text,
                    thinking_text=resp_thinking,
                    timing_ms=timing_ms,
                    eval_result=eval_res.result,
                    eval_matched_expected=eval_res.matched_expected,
                    eval_matched_forbidden=eval_res.matched_forbidden,
                    eval_expected_terms=frag["expected"],
                    eval_forbidden_terms=frag["forbidden"],
                )
                self.results.append(res_obj)

        # Save all results
        save_all(self.results, self.run_id, self.modelo_id, self.backend_name)
        self.call_from_thread(self._update_status, f"✅ EXPERIMENTO COMPLETADO | Guardado en results/{self.run_id}/")

    def run_echo_worker(self) -> None:
        from echo_experiment import build_echo_corpus, evaluate_echo, EchoResult, save_echo_results, _string_to_hex, ECHO_PROMPT_TEMPLATE

        self.run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.modelo_id}_{self.backend_name}_echo"
        corpus = build_echo_corpus()
        total = len(corpus)

        for i, item in enumerate(corpus, 1):
            sym = item["symbol"]
            corrupt_ctx = item["corrupted_context"]
            prompt = ECHO_PROMPT_TEMPLATE.format(corrupt_text=corrupt_ctx)

            self.call_from_thread(self._clear_logs)
            status_msg = f"[{i}/{total}] ECHO test símbolo: [bold cyan]{sym}[/bold cyan] -> [yellow]{item['corrupted']}[/yellow]"
            self.call_from_thread(self._update_status, status_msg)

            self.call_from_thread(self._append_log, "#log-prompt", prompt)

            def on_thinking(t: str) -> None:
                self.call_from_thread(self._append_log, "#log-thinking", t, end="")

            def on_answer(t: str) -> None:
                self.call_from_thread(self._append_log, "#log-response", t, end="")

            try:
                resp = self.backend.query(
                    user_prompt=prompt,
                    system_prompt=None,
                    on_token=on_answer,
                    on_thinking_token=on_thinking,
                )
                resp_text = resp.text
            except Exception as e:
                resp_text = f"[ERROR: {e}]"

            eval_res, eval_det = evaluate_echo(corrupt_ctx.strip(), resp_text.strip(), sym)

            self.call_from_thread(
                self._add_table_row,
                sym,
                item["corrupted"],
                eval_res,
                eval_det,
            )

            res_obj = EchoResult(
                run_id=self.run_id,
                model_id=self.modelo_id,
                backend_name=self.backend_name,
                timestamp=datetime.now().isoformat(),
                symbol_clean=sym,
                symbol_corrupt=item["corrupted"],
                context_clean=item["context"],
                context_corrupt=item["corrupted_context"],
                prompt_sent=prompt,
                response_raw=resp_text,
                response_clean=resp_text.strip(),
                sent_bytes=_string_to_hex(corrupt_ctx.strip()),
                received_bytes=_string_to_hex(resp_text.strip()),
                eval_result=eval_res,
                eval_detail=eval_det,
            )
            self.results.append(res_obj)

        save_echo_results(self.results, self.run_id, self.modelo_id, self.backend_name)
        self.call_from_thread(self._update_status, f"✅ MODO ECHO COMPLETADO | Guardado en results_echo/{self.run_id}/")

    # ── Helpers UI ─────────────────────────────────────────────────────────────

    def _clear_logs(self) -> None:
        self.query_one("#log-prompt", RichLog).clear()
        self.query_one("#log-thinking", RichLog).clear()
        self.query_one("#log-response", RichLog).clear()

    def _update_status(self, msg: str) -> None:
        self.query_one("#status-bar", Static).update(msg)

    def _append_log(self, target_id: str, text: str, end: str = "\n") -> None:
        log = self.query_one(target_id, RichLog)
        log.write(text, shrink=False)

    def _add_table_row(self, *args: str) -> None:
        table = self.query_one("#table-summary", DataTable)
        table.add_row(*args)
        table.scroll_end()
