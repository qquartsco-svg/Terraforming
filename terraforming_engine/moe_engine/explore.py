"""MOE explore — 스냅샷 → MoeAssessment. Terraforming 내부 복사본."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ._core import DEFAULT_CONFIG, compute_domain_scores


@dataclass(frozen=True)
class MoeAssessment:
    moe_risk: float
    label: str
    domain_scores: Dict[str, float]
    attribution: Dict[str, List[Dict[str, float]]]
    summary: str
    config_used: Dict[str, Any] = field(default_factory=dict)


def _label_from_risk(risk: float, thresholds: Dict[str, float]) -> str:
    low = float(thresholds.get("low", 0.25))
    moderate = float(thresholds.get("moderate", 0.5))
    high = float(thresholds.get("high", 0.75))
    if risk >= high:
        return "extreme"
    if risk >= moderate:
        return "high"
    if risk >= low:
        return "moderate"
    return "low"


def assess_planet_detail(
    snapshot: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> MoeAssessment:
    cfg: Dict[str, Any] = dict(DEFAULT_CONFIG)
    if config:
        for key, value in config.items():
            if key in ("domain_weights", "label_thresholds") and isinstance(value, dict):
                merged = dict(cfg.get(key, {}))
                merged.update({k: v for k, v in value.items()})
                cfg[key] = merged
            else:
                cfg[key] = value
    domain_scores, attribution = compute_domain_scores(snapshot, config=cfg)
    weights: Dict[str, float] = dict(cfg.get("domain_weights", {}))
    weighted_sum = 0.0
    weight_total = 0.0
    for name, score in domain_scores.items():
        w = float(weights.get(name, 1.0))
        if w <= 0.0:
            continue
        weighted_sum += score * w
        weight_total += w
    moe_risk = weighted_sum / weight_total if weight_total > 0.0 else 0.0
    label_thresholds: Dict[str, float] = dict(cfg.get("label_thresholds", {}))
    label = _label_from_risk(moe_risk, label_thresholds)
    top_domains: List[Tuple[str, float]] = sorted(
        domain_scores.items(), key=lambda kv: kv[1], reverse=True
    )
    drivers = ", ".join(name for name, _ in top_domains[:2]) if top_domains else "none"
    summary = f"moe_risk={moe_risk:.3f} ({label}), drivers: {drivers}"
    return MoeAssessment(
        moe_risk=moe_risk,
        label=label,
        domain_scores=domain_scores,
        attribution=attribution,
        summary=summary,
        config_used=cfg,
    )
