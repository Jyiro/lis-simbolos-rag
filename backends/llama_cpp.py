"""Backend para llama-server (llama.cpp) — API compatible con OpenAI.

Uso típico:
    ./serve.sh qwen3.5-2b          # terminal 1
    backend = LlamaCppBackend()    # terminal 2, Python

Endpoint: POST http://localhost:8080/v1/chat/completions
Health:   GET  http://localhost:8080/health

Thinking mode (Qwen3):
  - Disabled (default): payload incluye {"thinking": {"type": "disabled"}}
    Los tokens van a delta.content — streaming normal.
  - Enabled:            payload incluye {"thinking": {"type": "enabled"}}
    Tokens de razonamiento → delta.reasoning_content (on_thinking_token)
    Tokens de respuesta   → delta.content            (on_token)
"""
from __future__ import annotations

import json
import time
from typing import Callable

import requests

from .base import LLMResponse


class LlamaCppBackend:
    """Adapter para llama-server (llama.cpp)."""

    NAME = "llama_cpp"
    DEFAULT_BASE_URL = "https://debrief-wife-bully.ngrok-free.dev"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model_id: str = "local",
        temperature: float = 0,
        max_tokens: int = 1024,
        timeout: int = 300,
        thinking_mode: bool = False,
    ) -> None:
        import os
        env_url = os.environ.get("LLAMA_CPP_URL")
        if env_url:
            self.base_url = env_url.rstrip("/")
        else:
            self.base_url = base_url.rstrip("/")
        self.model_id      = model_id
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
        """Consulta al modelo con soporte de streaming y thinking mode.

        Si thinking_mode=False (default):
          - El modelo responde directamente sin razonamiento interno.
          - Todos los tokens van a on_token.

        Si thinking_mode=True:
          - El modelo piensa antes de responder (Qwen3 "Extended Thinking").
          - Tokens de razonamiento → on_thinking_token (solo se muestran, no se evalúan).
          - Tokens de respuesta   → on_token (estos son los que se evalúan).
        """
        messages = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        use_stream = on_token is not None or on_thinking_token is not None

        thinking_payload = (
            {"type": "enabled"}
            if self.thinking_mode
            else {"type": "disabled"}
        )

        payload = {
            "model":       self.model_id,
            "messages":    messages,
            "temperature": self.temperature,
            "max_tokens":  self.max_tokens,
            "stream":      use_stream,
            "thinking":    thinking_payload,
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
            model=self.model_id,
            backend=self.NAME,
            thinking_text=thinking_text,
            extra=extra,
        )

    # ── Implementación interna ────────────────────────────────────────────────

    def _blocking(self, payload: dict) -> tuple[str, str, dict]:
        """Llamada sin streaming — espera la respuesta completa."""
        resp = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data   = resp.json()
        choice = data["choices"][0]
        msg    = choice.get("message", {})
        text         = msg.get("content", "").strip()
        thinking_text = msg.get("reasoning_content", "").strip()
        return text, thinking_text, {
            "finish_reason": choice.get("finish_reason"),
            "usage":         data.get("usage", {}),
        }

    def _stream(
        self,
        payload: dict,
        on_token: Callable[[str], None] | None,
        on_thinking_token: Callable[[str], None] | None,
    ) -> tuple[str, str, dict]:
        """Llamada con streaming SSE.

        - delta.reasoning_content → thinking (solo mostrar, no evaluar)
        - delta.content           → respuesta real (evaluar)
        """
        full_text     = ""
        thinking_text = ""
        finish_reason = None

        with requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=self.timeout,
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choice = chunk.get("choices", [{}])[0]
                delta  = choice.get("delta", {})

                # ── Tokens de razonamiento (solo en thinking_mode=True) ────────
                t_token = delta.get("reasoning_content", "")
                if t_token:
                    thinking_text += t_token
                    if on_thinking_token:
                        on_thinking_token(t_token)

                # ── Tokens de respuesta visible (siempre evaluados) ───────────
                a_token = delta.get("content", "")
                if a_token:
                    full_text += a_token
                    if on_token:
                        on_token(a_token)

                finish_reason = choice.get("finish_reason") or finish_reason

        return full_text.strip(), thinking_text.strip(), {"finish_reason": finish_reason}

    # ── Health / Info ─────────────────────────────────────────────────────────

    def health_check(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def info(self) -> dict:
        try:
            r = requests.get(f"{self.base_url}/v1/models", timeout=5)
            models = r.json().get("data", []) if r.ok else []
        except Exception:
            models = []
        return {
            "backend":      self.NAME,
            "base_url":     self.base_url,
            "model_id":     self.model_id,
            "thinking_mode": self.thinking_mode,
            "models":       models,
        }
