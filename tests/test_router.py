import json
from pathlib import Path

from ventura_system import (
    BudgetPolicy,
    RunMetric,
    TaskProfile,
    append_metric,
    choose_route,
    compile_context,
    load_registry,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "model-registry.json"


def test_registry_has_ten_providers_and_no_unpriced_enabled_models():
    rows = json.loads(REGISTRY.read_text(encoding="utf-8"))["models"]
    providers = {row["provider"] for row in rows}
    assert len(providers) >= 10
    assert all(
        (not row.get("enabled", True))
        or (row["input_usd_per_mtok"] is not None and row["output_usd_per_mtok"] is not None)
        for row in rows
    )


def test_economy_route_respects_budget():
    models = load_registry(REGISTRY)
    task = TaskProfile(
        task_type="classification",
        required_capabilities=frozenset({"reasoning", "structured_output"}),
        input_tokens=4_000,
        expected_output_tokens=300,
        cached_fraction=0.5,
    )
    decision = choose_route(models, task, BudgetPolicy(max_cost_usd=0.01, max_models=1))
    assert decision.champion.estimated_cost_usd <= 0.01
    assert decision.challenger is None


def test_high_risk_selects_independent_challenger():
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
    assert decision.challenger is not None
    assert decision.champion.model.provider != decision.challenger.model.provider


def test_context_compiler_excludes_irrelevant_text():
    files = {
        "router.py": "budget router champion challenger",
        "logo.svg": "<svg>decorative</svg>",
        "README.md": "system architecture notes",
    }
    selected = compile_context("fix router budget selection", files, max_chars=500)
    assert selected
    assert selected[0].path == "router.py"
    assert all(chunk.path != "logo.svg" for chunk in selected)


def test_telemetry_appends_jsonl(tmp_path):
    path = tmp_path / "metrics.jsonl"
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
    assert payload["success"] is True
    assert payload["eval_score"] == 1.0
