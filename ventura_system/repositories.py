from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .router import BudgetPolicy


@dataclass(frozen=True)
class RepositoryRouteProfile:
    repository: str
    role: str
    budget_profile: str
    context_strategy: str
    routing_enabled: bool
    champion_challenger: bool


_BUDGETS = {
    "simple": BudgetPolicy(max_cost_usd=0.02, max_models=1, challenger_threshold=0.50),
    "normal": BudgetPolicy(max_cost_usd=0.20, max_models=2, challenger_threshold=0.72),
    "critical": BudgetPolicy(max_cost_usd=2.00, max_models=3, challenger_threshold=0.90),
}


def load_repository_registry(path: str | Path) -> list[RepositoryRouteProfile]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [RepositoryRouteProfile(**row) for row in payload["repositories"]]


def resolve_repository_profile(
    profiles: Iterable[RepositoryRouteProfile], repository: str
) -> RepositoryRouteProfile:
    normalized = repository.casefold()
    for profile in profiles:
        if profile.repository.casefold() == normalized:
            return profile
    raise KeyError(f"repository not registered: {repository}")


def budget_for_repository(profile: RepositoryRouteProfile) -> BudgetPolicy:
    try:
        policy = _BUDGETS[profile.budget_profile]
    except KeyError as exc:
        raise ValueError(f"unsupported budget profile: {profile.budget_profile}") from exc
    if not profile.routing_enabled:
        return BudgetPolicy(
            max_cost_usd=policy.max_cost_usd,
            max_models=1,
            challenger_threshold=policy.challenger_threshold,
            high_risk_requires_challenger=False,
        )
    if not profile.champion_challenger:
        return BudgetPolicy(
            max_cost_usd=policy.max_cost_usd,
            max_models=1,
            challenger_threshold=policy.challenger_threshold,
            high_risk_requires_challenger=False,
        )
    return policy
