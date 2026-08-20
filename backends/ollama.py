"""Backend para Ollama — para la PC de escritorio con más recursos.

Usa /api/chat para soporte nativo de system prompt.
Streaming: NDJSON — cada línea es {"message":{"content":"..."}, "done":false}
"""
from __future__ import annotations

import json
import time
from typing import Callable

import requests

from .base import LLMResponse


class OllamaBackend:
    """Adapter para Ollama.

    A diferencia de llama.cpp, en Ollama el modelo se especifica en cada
    request — no requiere reiniciar un servidor para cambiar de modelo.
    """

    NAME = "ollama"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = "qwen3.5:2b",
        temperature: float = 0,
        max_tokens: int = 1024,
        timeout: int = 300,
        thinking_mode: bool = False,
    ) -> None:
        self.base_url      = base_url.rstrip("/")
        self.model         = model
        self.temperature   = temperature
        self.max_tokens    = max_tokens
        self.timeout       = timeout
        self.thinking_mode = thinking_mode

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def query(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        on_token: Callable[[str], None] | None = None,
        on_thinking_token: Callable[[str], None] | None = None,
    ) -> LLMResponse:
        """Consulta al modelo. Si on_token se provee, hace streaming."""
        messages = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        use_stream = on_token is not None or on_thinking_token is not None

        payload = {
            "model":    self.model,
            "messages": messages,
            "stream":   use_stream,
            "options":  {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            "think": self.thinking_mode,
        }

        t0 = time.monotonic()

        if use_stream:
            text, thinking_text, extra = self._stream(payload, on_token, on_thinking_token)
        else:
            text, thinking_text, extra = self._blocking(payload)

        elapsed_ms = (time.monotonic() - t0) * 1000.0

        return LLMResponse(
            text=text,
            timing_ms=elapsed_ms,
            model=self.model,
            backend=self.NAME,
            thinking_text=thinking_text,
            extra=extra,
        )

    # ── Implementación interna ────────────────────────────────────────────────

    def _blocking(self, payload: dict) -> tuple[str, str, dict]:
        """Llamada sin streaming."""
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        text          = data["message"]["content"].strip()
        thinking_text = data["message"].get("thinking", "").strip()
        return text, thinking_text, {
            "eval_count":       data.get("eval_count"),
            "eval_duration_ms": data.get("eval_duration", 0) / 1e6,
            "done_reason":      data.get("done_reason"),
        }

    def _stream(
        self,
        payload: dict,
        on_token: Callable[[str], None] | None,
        on_thinking_token: Callable[[str], None] | None,
    ) -> tuple[str, str, dict]:
        """Llamada con streaming NDJSON.

        Ollama retorna thinking en message.thinking y respuesta en message.content.
        """
        full_text     = ""
        thinking_text = ""
        final_data: dict = {}

        with requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=self.timeout,
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = chunk.get("message", {})

                # Tokens de razonamiento (thinking mode)
                t_token = msg.get("thinking", "")
                if t_token:
                    thinking_text += t_token
                    if on_thinking_token:
                        on_thinking_token(t_token)

                # Tokens de respuesta visible
                a_token = msg.get("content", "")
                if a_token:
                    full_text += a_token
                    if on_token:
                        on_token(a_token)

                if chunk.get("done"):
                    final_data = chunk
                    break

        return full_text.strip(), thinking_text.strip(), {
            "eval_count":       final_data.get("eval_count"),
            "eval_duration_ms": final_data.get("eval_duration", 0) / 1e6,
            "done_reason":      final_data.get("done_reason"),
        }

    # ── Health / Info ─────────────────────────────────────────────────────────

    def health_check(self) -> bool:
        try:
            r = requests.get(self.base_url, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def info(self) -> dict:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])] if r.ok else []
        except Exception:
            models = []
        return {
            "backend":          self.NAME,
            "base_url":         self.base_url,
            "model":            self.model,
            "thinking_mode":    self.thinking_mode,
            "models_available": models,
        }
