# src/agents/base_agent.py
class BaseAgent:
    def __init__(self, name, db_path="llmopt_stage1.sqlite"):
        self.name = name
        self.db_path = db_path

    def fetch_data(self):
        raise NotImplementedError

    def analyze(self):
        raise NotImplementedError

    def message(self):
        """Return structured JSON-style message for the coordinator."""
        raise NotImplementedError
