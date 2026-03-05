"""MOE Engine core — 도메인별 리스크. Terraforming 내부 복사본."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _get_float(snapshot: Dict[str, Any], key: str, default: float = 0.0) -> float:
    v = snapshot.get(key)
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


DEFAULT_CONFIG: Dict[str, Any] = {
    "domain_weights": {
        "atmosphere_risk": 1.0,
        "water_cycle_risk": 1.0,
        "geophysics_risk": 1.0,
        "magnetosphere_risk": 1.0,
        "rotation_orbit_risk": 1.0,
        "biosphere_window_risk": 1.0,
    },
    "label_thresholds": {
        "low": 0.25,
        "moderate": 0.50,
        "high": 0.75,
    },
}

_DOMAIN_SPECS: Dict[str, Dict[str, Any]] = {
    "atmosphere_risk": {"keys": ["greenhouse_proxy", "tau_atm", "albedo_eff"], "invert": False},
    "water_cycle_risk": {"keys": ["hydrology_stability_proxy", "dW_surface_dt_norm"], "invert": False},
    "geophysics_risk": {"keys": ["sigma_plate", "heat_flux_proxy", "volcanism_proxy"], "invert": False},
    "magnetosphere_risk": {"keys": ["strip_risk_proxy", "B_surface_equator_proxy"], "invert": False},
    "rotation_orbit_risk": {"keys": ["S_rot", "climate_variance_proxy", "seasonality_proxy"], "invert": False},
    "biosphere_window_risk": {"keys": ["biosphere_window_score"], "invert": True},
}


def _score_domain(
    snapshot: Dict[str, Any],
    keys: List[str],
    invert: bool = False,
) -> Tuple[float, List[Dict[str, float]]]:
    values: List[float] = []
    reasons: List[Dict[str, float]] = []
    for k in keys:
        v = _get_float(snapshot, k, default=None)  # type: ignore[arg-type]
        if v is None:
            continue
        norm = _clamp01(v)
        score_contrib = 1.0 - norm if invert else norm
        values.append(score_contrib)
        reasons.append({"key": k, "contribution": score_contrib})
    if not values:
        return 0.0, []
    score = sum(values) / float(len(values))
    return score, reasons


def compute_domain_scores(
    snapshot: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, float], Dict[str, List[Dict[str, float]]]]:
    _ = config
    domain_scores: Dict[str, float] = {}
    attribution: Dict[str, List[Dict[str, float]]] = {}
    for domain_name, spec in _DOMAIN_SPECS.items():
        keys = spec.get("keys", [])
        invert = bool(spec.get("invert", False))
        score, reasons = _score_domain(snapshot, keys=keys, invert=invert)
        domain_scores[domain_name] = _clamp01(score)
        attribution[domain_name] = reasons
    return domain_scores, attribution
