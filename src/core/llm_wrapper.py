# -------------------------------------------------------------
# Unified LLM wrapper that normalizes API calls across providers.
# Includes MockProvider for local testing.
# Logs latency, cost, and quality metrics to the database.
# -------------------------------------------------------------

from __future__ import annotations
import time, uuid
from dataclasses import dataclass
from typing import Optional, Protocol

from .metrics_db import insert_request, insert_response, SessionLocal
from .cost_tracker import CostTracker
from ..utils.text import normalize_text, sha256, type_token_ratio


# ---------- Provider interface ----------

class Provider(Protocol):
    name: str
    def generate(self, model: str, prompt: str, **kwargs) -> dict:
        """
        Must return:
          {
            "text": str,
            "tokens_in": int,
            "tokens_out": int
          }
        """
        ...


# ---------- Mock provider for local dev ----------

class MockProvider:
    name = "mock"
    def generate(self, model: str, prompt: str, **kwargs) -> dict:
        # crude token estimate: ~1 token per 4 characters
        tokens_in = max(1, len(prompt) // 4)
        scale = 1.0 if "small" in model else 2.0
        out_len = int(min(1200, max(30, len(prompt) * scale)))
        response_text = ("Response: " + prompt)[:out_len]
        tokens_out = max(1, len(response_text) // 4)
        time.sleep(0.05 + 0.05 * scale)   # simulate latency
        return {"text": response_text, "tokens_in": tokens_in, "tokens_out": tokens_out}


# ---------- Unified wrapper ----------

@dataclass
class CallResult:
    request_id: str
    provider: str
    model: str
    prompt: str
    response_text: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    cost_usd: float
    quality_proxy: float
    status: str
    error_msg: Optional[str] = None


class UnifiedLLM:
    def __init__(self, providers: dict[str, Provider], cost: Optional[CostTracker] = None):
        self.providers = providers
        self.cost = cost or CostTracker()

    def _quality_proxy(self, response: str) -> float:
        """Simple heuristic for early-stage quality."""
        ttr = type_token_ratio(response)
        length_score = min(len(response) / 1000.0, 1.0)
        return round(0.6 * ttr + 0.4 * length_score, 4)

    def call(self, provider: str, model: str, prompt: str, **params) -> CallResult:
        if provider not in self.providers:
            raise ValueError(f"Unknown provider '{provider}'")

        p = self.providers[provider]
        request_id = str(uuid.uuid4())
        norm_prompt = normalize_text(prompt)
        prompt_hash = sha256(norm_prompt)

        t0 = time.perf_counter()
        status, error_msg = "ok", None

        try:
            out = p.generate(model=model, prompt=norm_prompt, **params)
            response_text = out["text"]
            tokens_in, tokens_out = int(out["tokens_in"]), int(out["tokens_out"])
        except Exception as e:
            status, response_text, tokens_in, tokens_out, error_msg = "error", "", 0, 0, str(e)

        latency_ms = (time.perf_counter() - t0) * 1000
        cost_usd = self.cost.compute_cost_usd(f"{provider}:{model}", tokens_in, tokens_out)
        quality = self._quality_proxy(response_text) if status == "ok" else 0.0

        # persist to DB
        session = SessionLocal()
        try:
            insert_request(session, dict(
                request_id=request_id,
                provider=provider,
                model=model,
                prompt_hash=prompt_hash,
                prompt_len=len(norm_prompt),
                params=params,
                latency_ms=latency_ms,
                status=status,
                error_msg=error_msg
            ))
            insert_response(session, dict(
                request_id=request_id,
                response=response_text,
                usage_tokens_in=tokens_in,
                usage_tokens_out=tokens_out,
                cost_usd=cost_usd,
                quality_proxy=quality
            ))
            session.commit()
        finally:
            session.close()

        return CallResult(
            request_id=request_id, provider=provider, model=model, prompt=norm_prompt,
            response_text=response_text, tokens_in=tokens_in, tokens_out=tokens_out,
            latency_ms=latency_ms, cost_usd=cost_usd, quality_proxy=quality,
            status=status, error_msg=error_msg
        )
