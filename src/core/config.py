# -------------------------------------------------------------
# Loads environment variables and model pricing configuration.
# Defines ModelPricing dataclass and helper to load pricing.json.
# Central hub for DB connection URL and path management.
# -------------------------------------------------------------

import json, os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("LLMOPT_DB_URL", "sqlite:///llmopt_stage1.sqlite")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICING_PATH = os.path.join(BASE_DIR, "pricing.json")

@dataclass(frozen=True)
class ModelPricing:
    model: str
    input_per_million: float
    output_per_million: float

def load_pricing() -> dict[str, ModelPricing]:
    with open(PRICING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        name: ModelPricing(
            model=name,
            input_per_million=float(v["input_per_million"]),
            output_per_million=float(v["output_per_million"])
        )
        for name, v in data.items()
    }
