# run_agents.py
from src.agents.coordinator_agent import CoordinatorAgent

def main():
    print("🚀 Running Multi-Agent Decision System...")
    coord = CoordinatorAgent(latency_threshold=150)
    decision = coord.run()

    print("\n🤖 Final Decision:", decision["chosen_model"])
    print("\n📬 Agent Messages:")
    for msg in decision["agent_messages"]:
        print(msg)

from src.core.llm_wrapper import UnifiedLLM, MockProvider

def simulate_prompt(prompt: str):
    providers = {"mock": MockProvider()}
    llm = UnifiedLLM(providers)
    coord = CoordinatorAgent(latency_threshold=150)
    decision = coord.run()
    chosen_model = decision["chosen_model"]

    print(f"\n🧩 Routing '{prompt}' → {chosen_model}")
    result = llm.call("mock", chosen_model, prompt)
    print(f"Response ({len(result.response_text)} chars, quality={result.quality_proxy})")

if __name__ == "__main__":
    simulate_prompt("Explain the concept of transformers in 3 lines.")


if __name__ == "__main__":
    main()
