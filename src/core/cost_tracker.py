# -------------------------------------------------------------
# Computes request cost using pricing.json rates.
# Provides a unified cost tracker for all provider/model pairs.
# Used throughout the pipeline for per-call and cumulative costing.
# -------------------------------------------------------------



from .config import load_pricing

class CostTracker:
    def __init__(self):
        self.pricing = load_pricing()

    def compute_cost_usd(self, provider_model: str, tokens_in: int, tokens_out: int) -> float:
        if provider_model not in self.pricing:
            return 0.0
        p = self.pricing[provider_model]
        cost_in = (tokens_in / 1_000_000) * p.input_per_million
        cost_out = (tokens_out / 1_000_000) * p.output_per_million
        return round(cost_in + cost_out, 6)
