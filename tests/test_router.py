import json
from pathlib import Path
import tempfile
import unittest

from ventura_system import (
    BudgetPolicy,
    RunMetric,
    TaskProfile,
    append_metric,
    budget_for_repository,
    choose_route,
    compile_context,
    load_registry,
    load_repository_registry,
    resolve_repository_profile,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "model-registry.json"
REPOSITORIES = ROOT / "config" / "repositories.json"


class RouterTests(unittest.TestCase):
    def test_registry_has_ten_providers_and_no_unpriced_enabled_models(self):
        rows = json.loads(REGISTRY.read_text(encoding="utf-8"))["models"]
        providers = {row["provider"] for row in rows}
        self.assertGreaterEqual(len(providers), 10)
        self.assertTrue(
            all(
                (not row.get("enabled", True))
                or (row["input_usd_per_mtok"] is not None and row["output_usd_per_mtok"] is not None)
                for row in rows
            )
        )

    def test_ecosystem_registry_covers_all_accessible_repositories(self):
        profiles = load_repository_registry(REPOSITORIES)
        self.assertEqual(len(profiles), 15)
        self.assertEqual(len({p.repository.casefold() for p in profiles}), 15)

    def test_security_repository_gets_critical_three_model_budget(self):
        profiles = load_repository_registry(REPOSITORIES)
        seg = resolve_repository_profile(profiles, "venturalabs-ai/Ventura.SEG")
        budget = budget_for_repository(seg)
        self.assertEqual(seg.role, "security")
        self.assertEqual(budget.max_cost_usd, 2.0)
        self.assertEqual(budget.max_models, 3)

    def test_tool_first_repository_disables_challenger_spend(self):
        profiles = load_repository_registry(REPOSITORIES)
        build = resolve_repository_profile(profiles, "venturalabs-ai/ventura.build")
        budget = budget_for_repository(build)
        self.assertFalse(build.routing_enabled)
        self.assertEqual(budget.max_models, 1)
        self.assertFalse(budget.high_risk_requires_challenger)

    def test_economy_route_respects_budget(self):
        models = load_registry(REGISTRY)
        task = TaskProfile(
            task_type="classification",
            required_capabilities=frozenset({"reasoning", "structured_output"}),
            input_tokens=4_000,
            expected_output_tokens=300,
            cached_fraction=0.5,
        )
        decision = choose_route(models, task, BudgetPolicy(max_cost_usd=0.01, max_models=1))
        self.assertLessEqual(decision.champion.estimated_cost_usd, 0.01)
        self.assertIsNone(decision.challenger)

    def test_high_risk_selects_independent_challenger(self):
        models = load_registry(REGISTRY)
        task = TaskProfile(
            task_type="security_review",
            required_capabilities=frozenset({"reasoning", "coding", "tools"}),
            input_tokens=20_000,
            expected_output_tokens=2_000,
            risk="high",
        )
        decision = choose_route(
            models,
            task,
            BudgetPolicy(max_cost_usd=0.50, max_models=2),
            confidence=0.95,
        )
        self.assertIsNotNone(decision.challenger)
        assert decision.challenger is not None
        self.assertNotEqual(decision.champion.model.provider, decision.challenger.model.provider)

    def test_context_compiler_excludes_irrelevant_text(self):
        files = {
            "router.py": "budget router champion challenger",
            "logo.svg": "<svg>decorative</svg>",
            "README.md": "system architecture notes",
        }
        selected = compile_context("fix router budget selection", files, max_chars=500)
        self.assertTrue(selected)
        self.assertEqual(selected[0].path, "router.py")
        self.assertTrue(all(chunk.path != "logo.svg" for chunk in selected))

    def test_telemetry_appends_jsonl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "metrics.jsonl"
            append_metric(
                path,
                RunMetric(
                    provider="test",
                    model="test-model",
                    task_type="unit",
                    input_tokens=10,
                    cached_tokens=0,
                    output_tokens=5,
                    cost_usd=0.001,
                    latency_ms=10,
                    retries=0,
                    eval_score=1.0,
                    success=True,
                ),
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(payload["success"])
            self.assertEqual(payload["eval_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
