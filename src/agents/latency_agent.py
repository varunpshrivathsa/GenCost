# src/agents/latency_agent.py
import pandas as pd, sqlite3
from .base_agent import BaseAgent

class LatencyProfilerAgent(BaseAgent):
    def analyze(self):
        query = """
        SELECT model, AVG(latency_ms) AS avg_latency
        FROM requests
        GROUP BY model
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn)
        self.results = df
        return df

    def message(self):
        best = self.results.loc[self.results['avg_latency'].idxmin()]
        return {"agent": self.name, "recommendation": best['model'], "metric": "latency", "value": best['avg_latency']}
