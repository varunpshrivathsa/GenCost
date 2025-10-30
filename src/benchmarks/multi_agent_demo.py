from agents.coordinator_agent import CoordinatorAgent

coord = CoordinatorAgent(latency_threshold=150)
decision = coord.run()

print("🤖 Final Decision:", decision["chosen_model"])
print("Messages:", decision["agent_messages"])
