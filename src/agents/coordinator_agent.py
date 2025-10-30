# src/agents/coordinator_agent.py
from .cost_agent import CostAnalyzerAgent
from .latency_agent import LatencyProfilerAgent
from .quality_agent import QualityEvaluatorAgent

class CoordinatorAgent:
    def __init__(self, latency_threshold=200):
        self.agents = [
            CostAnalyzerAgent("CostAnalyzer"),
            LatencyProfilerAgent("LatencyProfiler"),
            QualityEvaluatorAgent("QualityEvaluator")
        ]
        self.latency_threshold = latency_threshold

    def run(self):
        messages = []
        for agent in self.agents:
            agent.analyze()
            messages.append(agent.message())

        # Combine heuristically
        cost_msg = messages[0]
        latency_msg = messages[1]
        quality_msg = messages[2]

        # Filter models that meet latency threshold
        allowed = latency_msg["value"] < self.latency_threshold
        chosen = quality_msg["recommendation"] if allowed else cost_msg["recommendation"]

        return {
            "chosen_model": chosen,
            "agent_messages": messages
        }
