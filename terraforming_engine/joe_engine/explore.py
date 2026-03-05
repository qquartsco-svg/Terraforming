# joe_engine explore — 스냅샷 → PlanetAssessment. Terraforming 내부 복사본.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from ._core import (
    DEFAULT_CONFIG,
    DEFAULT_REF_MAX,
    DEFAULT_REF_MIN,
    instability_raw,
    normalize,
    planet_stress_raw,
    saturate,
)


@dataclass(frozen=True)
class PlanetAssessment:
    """거시 평가: 스트레스·불안정도·거주가능성 라벨."""
    planet_stress: float
    instability: float
    habitability_label: str
    summary: str
    config_used: Dict[str, Any] = field(default_factory=dict)


def _label_habit(stress: float, inst: float) -> str:
    if stress >= 0.7 or inst >= 0.7:
        return "extreme"
    if stress >= 0.4 or inst >= 0.4:
        return "low"
    if stress >= 0.2 or inst >= 0.2:
        return "moderate"
    return "high"


def assess_planet(
    snapshot: Dict[str, Any],
    *,
    config: None | Dict[str, Any] = None,
    ref_min: float = DEFAULT_REF_MIN,
    ref_max: float = DEFAULT_REF_MAX,
) -> PlanetAssessment:
    cfg = dict(DEFAULT_CONFIG)
    if config:
        cfg.update({k: v for k, v in config.items() if k in cfg})
    ref_min, ref_max = cfg.get("ref_min", ref_min), cfg.get("ref_max", ref_max)
    raw = planet_stress_raw(
        snapshot,
        a1=cfg["a1"], a2=cfg["a2"], a3=cfg["a3"], a4=cfg["a4"], a5=cfg["a5"],
        p_ref=cfg["p_ref"],
    )
    planet_stress = normalize(raw, ref_min=ref_min, ref_max=ref_max)
    inst_raw = instability_raw(planet_stress, snapshot, b1=cfg["b1"], b2=cfg["b2"], b3=cfg["b3"])
    instability = saturate(inst_raw)
    label = _label_habit(planet_stress, instability)
    summary = f"planet_stress={planet_stress:.3f}, instability={instability:.3f}, habitability={label}"
    return PlanetAssessment(
        planet_stress=planet_stress,
        instability=instability,
        habitability_label=label,
        summary=summary,
        config_used=cfg,
    )
