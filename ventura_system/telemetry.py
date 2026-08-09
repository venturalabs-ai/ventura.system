from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class RunMetric:
    provider: str
    model: str
    task_type: str
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    retries: int
    eval_score: float
    success: bool
    human_override: bool = False


def append_metric(path: str | Path, metric: RunMetric) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(metric)
    payload["recorded_at"] = datetime.now(timezone.utc).isoformat()
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
