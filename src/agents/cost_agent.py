# src/agents/cost_agent.py
import pandas as pd, sqlite3
from .base_agent import BaseAgent

class CostAnalyzerAgent(BaseAgent):
    def analyze(self):
        query = """
        SELECT r.model, AVG(s.cost_usd) AS avg_cost
        FROM requests r
        JOIN responses s ON r.request_id = s.request_id
        GROUP BY r.model
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn)
        self.results = df
        return df

    def message(self):
        best = self.results.loc[self.results['avg_cost'].idxmin()]
        return {"agent": self.name, "recommendation": best['model'], "metric": "cost", "value": best['avg_cost']}
