# -------------------------------------------------------------
# Runs N benchmark requests across mock or real providers.
# Saves results to CSV and produces latency/cost plots.
# -------------------------------------------------------------
from __future__ import annotations
import os, csv, time, random, argparse
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from ..core.metrics_db import init_db
from ..core.llm_wrapper import UnifiedLLM, MockProvider
# (Later you can import real providers here.)

def load_prompts(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default=os.path.join(os.path.dirname(__file__), "prompts.csv"))
    parser.add_argument("--n", type=int, default=100, help="total requests to run")
    parser.add_argument("--out_csv", default="baseline_results.csv")
    parser.add_argument("--plot_prefix", default="baseline")
    args = parser.parse_args()

    # Ensure DB exists
    init_db()

    # --- Providers
    providers = {"mock": MockProvider()}
    llm = UnifiedLLM(providers)

    # --- Models (simulate multiple tiers)
    matrix = [("mock", "small-latest"), ("mock", "large-latest")]

    prompts = load_prompts(args.prompts)
    records = []

    print(f"Running {args.n} total requests across {len(matrix)} provider-model pairs...")
    for i in tqdm(range(args.n)):
        prov, model = random.choice(matrix)
        prompt = random.choice(prompts)["prompt"]
        res = llm.call(prov, model, prompt)
        records.append({
            "provider": res.provider,
            "model": res.model,
            "latency_ms": res.latency_ms,
            "tokens_in": res.tokens_in,
            "tokens_out": res.tokens_out,
            "cost_usd": res.cost_usd,
            "quality_proxy": res.quality_proxy,
            "status": res.status
        })
        time.sleep(0.02)  # pacing

    df = pd.DataFrame(records)
    df.to_csv(args.out_csv, index=False)
    print(f"✅  Saved {len(df)} rows → {args.out_csv}")

    # --- Aggregate stats
    agg = df.groupby(["provider","model"]).agg(
        p50_latency=("latency_ms","median"),
        p95_latency=("latency_ms", lambda s: s.quantile(0.95)),
        avg_cost=("cost_usd","mean"),
        avg_quality=("quality_proxy","mean")
    ).reset_index()
    print("\n=== Summary ===\n", agg)

    # --- Plots
    plt.figure()
    for _, row in agg.iterrows():
        label = f"{row['provider']}:{row['model']}"
        plt.scatter(row["avg_cost"], row["p50_latency"])
        plt.text(row["avg_cost"], row["p50_latency"], label)
    plt.xlabel("Avg Cost (USD/request)")
    plt.ylabel("p50 Latency (ms)")
    plt.title("Cost vs Latency (p50)")
    plt.tight_layout()
    plt.savefig(f"{args.plot_prefix}_cost_vs_latency.png", dpi=150)

    plt.figure()
    agg.plot(x="model", y="avg_quality", kind="bar", legend=False)
    plt.ylabel("Avg Quality Proxy")
    plt.title("Quality Proxy by Model")
    plt.tight_layout()
    plt.savefig(f"{args.plot_prefix}_quality.png", dpi=150)
    print("✅  Plots saved.")

if __name__ == "__main__":
    main()
