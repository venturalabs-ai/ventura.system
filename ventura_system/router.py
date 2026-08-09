from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Iterable


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model_id: str
    tier: str
    input_usd_per_mtok: float | None
    cached_input_usd_per_mtok: float | None
    output_usd_per_mtok: float | None
    quality: float
    latency: float
    capabilities: frozenset[str]
    enabled: bool = True


@dataclass(frozen=True)
class BudgetPolicy:
    max_cost_usd: float
    max_models: int = 1
    challenger_threshold: float = 0.72
    high_risk_requires_challenger: bool = True


@dataclass(frozen=True)
class TaskProfile:
    task_type: str
    required_capabilities: frozenset[str]
    input_tokens: int
    expected_output_tokens: int
    risk: str = "normal"
    prefer_low_latency: bool = False
    cached_fraction: float = 0.0


@dataclass(frozen=True)
class Candidate:
    model: ModelSpec
    estimated_cost_usd: float
    utility: float


@dataclass(frozen=True)
class RouteDecision:
    champion: Candidate
    challenger: Candidate | None
    reason: str


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def load_registry(path: str | Path) -> list[ModelSpec]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    models: list[ModelSpec] = []
    for row in payload["models"]:
        models.append(
            ModelSpec(
                provider=row["provider"],
                model_id=row["model_id"],
                tier=row["tier"],
                input_usd_per_mtok=_as_float(row.get("input_usd_per_mtok")),
                cached_input_usd_per_mtok=_as_float(row.get("cached_input_usd_per_mtok")),
                output_usd_per_mtok=_as_float(row.get("output_usd_per_mtok")),
                quality=float(row["quality"]),
                latency=float(row["latency"]),
                capabilities=frozenset(row.get("capabilities", [])),
                enabled=bool(row.get("enabled", True)),
            )
        )
    return models


def estimate_cost(model: ModelSpec, task: TaskProfile) -> float:
    if model.input_usd_per_mtok is None or model.output_usd_per_mtok is None:
        return float("inf")
    cached = min(max(task.cached_fraction, 0.0), 1.0)
    uncached_tokens = task.input_tokens * (1.0 - cached)
    cached_tokens = task.input_tokens * cached
    cached_rate = (
        model.cached_input_usd_per_mtok
        if model.cached_input_usd_per_mtok is not None
        else model.input_usd_per_mtok
    )
    input_cost = (
        uncached_tokens * model.input_usd_per_mtok
        + cached_tokens * cached_rate
    ) / 1_000_000
    output_cost = task.expected_output_tokens * model.output_usd_per_mtok / 1_000_000
    return input_cost + output_cost


def _capability_score(model: ModelSpec, required: frozenset[str]) -> float:
    if not required:
        return 1.0
    matched = len(required.intersection(model.capabilities))
    return matched / len(required)


def rank_models(
    models: Iterable[ModelSpec],
    task: TaskProfile,
    budget: BudgetPolicy,
) -> list[Candidate]:
    viable: list[Candidate] = []
    for model in models:
        if not model.enabled:
            continue
        capability = _capability_score(model, task.required_capabilities)
        if capability < 1.0:
            continue
        cost = estimate_cost(model, task)
        if cost > budget.max_cost_usd:
            continue

        cost_pressure = min(cost / max(budget.max_cost_usd, 1e-9), 1.0)
        latency_weight = 0.20 if task.prefer_low_latency else 0.10
        utility = (
            0.65 * model.quality
            + 0.15 * capability
            + latency_weight * (1.0 - model.latency)
            - 0.15 * cost_pressure
        )
        viable.append(Candidate(model=model, estimated_cost_usd=cost, utility=utility))
    return sorted(viable, key=lambda item: (item.utility, -item.estimated_cost_usd), reverse=True)


def choose_route(
    models: Iterable[ModelSpec],
    task: TaskProfile,
    budget: BudgetPolicy,
    confidence: float = 1.0,
) -> RouteDecision:
    ranked = rank_models(models, task, budget)
    if not ranked:
        raise ValueError("no model satisfies capabilities and budget")

    champion = ranked[0]
    needs_challenger = (
        budget.max_models > 1
        and (
            confidence < budget.challenger_threshold
            or (budget.high_risk_requires_challenger and task.risk == "high")
        )
    )
    challenger = None
    if needs_challenger:
        challenger = next(
            (candidate for candidate in ranked[1:] if candidate.model.provider != champion.model.provider),
            None,
        )

    reason = (
        "champion+challenger due to risk/confidence"
        if challenger
        else "single champion; early-exit avoids unnecessary model spend"
    )
    return RouteDecision(champion=champion, challenger=challenger, reason=reason)
