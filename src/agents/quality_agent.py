# src/agents/quality_agent.py
import pandas as pd, sqlite3
from .base_agent import BaseAgent

class QualityEvaluatorAgent(BaseAgent):
    def analyze(self):
        query = """
        SELECT r.model, AVG(s.quality_proxy) AS avg_quality
        FROM requests r
        JOIN responses s ON r.request_id = s.request_id
        GROUP BY r.model
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn)
        self.results = df
        return df

    def message(self):
        best = self.results.loc[self.results['avg_quality'].idxmax()]
        return {"agent": self.name, "recommendation": best['model'], "metric": "quality", "value": best['avg_quality']}
