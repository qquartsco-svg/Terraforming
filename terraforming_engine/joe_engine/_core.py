# Joe_Engine (조/JOE) — PANGEA §4. Terraforming 내부 복사본. 상위만 참조.

from __future__ import annotations

from typing import Any, Dict

DEFAULT_REF_MIN = 0.0
DEFAULT_REF_MAX = 2.0
DEFAULT_A1 = 0.25
DEFAULT_A2 = 0.20
DEFAULT_A3 = 0.20
DEFAULT_A4 = 0.20
DEFAULT_A5 = 0.15
DEFAULT_B1 = 0.60
DEFAULT_B2 = 0.20
DEFAULT_B3 = 0.20
P_REF_DEFAULT = 1.0

DEFAULT_CONFIG = {
    "ref_min": DEFAULT_REF_MIN,
    "ref_max": DEFAULT_REF_MAX,
    "a1": DEFAULT_A1, "a2": DEFAULT_A2, "a3": DEFAULT_A3,
    "a4": DEFAULT_A4, "a5": DEFAULT_A5,
    "b1": DEFAULT_B1, "b2": DEFAULT_B2, "b3": DEFAULT_B3,
    "p_ref": P_REF_DEFAULT,
}


def _get_float(snapshot: Dict[str, Any], key: str, default: float = 0.0) -> float:
    v = snapshot.get(key)
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def planet_stress_raw(
    snapshot: Dict[str, Any],
    *,
    a1: float = DEFAULT_A1,
    a2: float = DEFAULT_A2,
    a3: float = DEFAULT_A3,
    a4: float = DEFAULT_A4,
    a5: float = DEFAULT_A5,
    p_ref: float = P_REF_DEFAULT,
) -> float:
    sigma_plate = _get_float(snapshot, "sigma_plate")
    p_w = _get_float(snapshot, "P_w")
    s_rot = _get_float(snapshot, "S_rot")
    w_surface = _get_float(snapshot, "W_surface")
    w_total = _get_float(snapshot, "W_total", default=1.0)
    if w_total <= 0:
        w_total = 1.0
    dW_norm = _get_float(snapshot, "dW_surface_dt_norm")
    return (
        a1 * sigma_plate
        + a2 * (p_w / p_ref if p_ref > 0 else 0.0)
        + a3 * s_rot
        + a4 * (w_surface / w_total)
        + a5 * dW_norm
    )


def normalize(
    x: float,
    ref_min: float = DEFAULT_REF_MIN,
    ref_max: float = DEFAULT_REF_MAX,
) -> float:
    if ref_max <= ref_min:
        return 0.0
    t = (x - ref_min) / (ref_max - ref_min)
    return max(0.0, min(1.0, t))


def instability_raw(
    planet_stress: float,
    snapshot: Dict[str, Any],
    *,
    b1: float = DEFAULT_B1,
    b2: float = DEFAULT_B2,
    b3: float = DEFAULT_B3,
) -> float:
    w_total = max(1.0, _get_float(snapshot, "W_total", 1.0))
    return (
        b1 * planet_stress
        + b2 * (_get_float(snapshot, "W_surface") / w_total)
        + b3 * _get_float(snapshot, "dW_surface_dt_norm")
    )


def saturate(x: float) -> float:
    return max(0.0, min(1.0, x))
