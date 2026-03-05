# PlanetSnapshot 계약 — Terraforming Engine 공통 입력 스키마.
# 엔진은 서로 모른다. 오직 이 키 목록과 dict 하나로 연결된다.

from __future__ import annotations

# JOE CORE 6키
JOE_CORE_KEYS = (
    "sigma_plate",
    "P_w",
    "S_rot",
    "W_surface",
    "W_total",
    "dW_surface_dt_norm",
)

# MOE 확장 proxy (도메인별)
MOE_PROXY_KEYS = (
    "greenhouse_proxy",
    "tau_atm",
    "albedo_eff",
    "hydrology_stability_proxy",
    "heat_flux_proxy",
    "volcanism_proxy",
    "strip_risk_proxy",
    "B_surface_equator_proxy",
    "climate_variance_proxy",
    "seasonality_proxy",
    "biosphere_window_score",
)

# Cherubim용(예정) region 키
CHERUBIM_OPTIONAL_KEYS = (
    "latitude_band",
    "tectonic_stability_proxy",
    "water_availability_proxy",
    "temperature_window_proxy",
    "radiation_proxy",
)


def snapshot_keys_all() -> tuple[str, ...]:
    """스냅샷에 올 수 있는 모든 표준 키 (순서: JOE → MOE → Cherubim)."""
    return JOE_CORE_KEYS + MOE_PROXY_KEYS + CHERUBIM_OPTIONAL_KEYS


def validate_snapshot_keys(snapshot: dict) -> set[str]:
    """snapshot에 있는 키 중 표준에 정의된 키 집합 반환. 누락/추가 검사용."""
    defined = set(snapshot_keys_all())
    present = set(snapshot.keys())
    return present & defined
