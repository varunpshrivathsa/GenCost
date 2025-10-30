# GenCost
LLM Cost Optimizer Orchestration Framework

**Goal:** Adaptive multi-agent system that minimizes LLM inference cost while preserving quality and latency.

### Stage 1 – Foundation & Data Layer
- Unified LLM API wrapper
- Cost tracker
- SQLite metrics store
- Baseline benchmark scripts

### Upcoming Stages
Multi-agent reasoning → RL policy learner → SDK/API → Dashboard → Deployment

---

#### Setup
```bash
git clone https://github.com/<user>/llm-cost-optimizer.git
cd llm-cost-optimizer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
