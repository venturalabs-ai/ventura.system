#!/usr/bin/env python3
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ventura_system import BudgetPolicy, TaskProfile, choose_route, load_registry

models = load_registry(ROOT / "config" / "model-registry.json")
cases = [
    TaskProfile("simple", frozenset({"reasoning", "structured_output"}), 2000, 300),
    TaskProfile("coding", frozenset({"reasoning", "coding", "tools"}), 12000, 1800),
    TaskProfile("critical", frozenset({"reasoning", "coding", "tools"}), 30000, 3000, risk="high"),
]
start = perf_counter()
for case in cases:
    decision = choose_route(models, case, BudgetPolicy(max_cost_usd=2.0, max_models=2), confidence=0.8)
    print(
        f"{case.task_type}: champion={decision.champion.model.provider}/{decision.champion.model.model_id} "
        f"cost=${decision.champion.estimated_cost_usd:.6f} "
        f"challenger={decision.challenger.model.model_id if decision.challenger else '-'}"
    )
print(f"routing_benchmark_ms={(perf_counter() - start) * 1000:.3f}")
