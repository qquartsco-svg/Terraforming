# schema.py — PlanetSnapshot 공통 규약 (Key 목록)
#
# 전체 스키마 정의: PLANET_SNAPSHOT_SCHEMA.md
# 모든 엔진은 이 dict 하나를 공통 입력으로 사용. 엔진 간 직접 참조 없음.

from __future__ import annotations

# 기반(선택) — 행성 기본 물리. 상위 레이어 연동 시 사용
BASE_OPTIONAL_KEYS = ("mass", "radius", "gravity")

# JOE CORE 6키 (거시 물리)
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
    """스냅샷 표준 키 전체 (순서: 기반 → JOE → MOE → Cherubim)."""
    return BASE_OPTIONAL_KEYS + JOE_CORE_KEYS + MOE_PROXY_KEYS + CHERUBIM_OPTIONAL_KEYS


def validate_snapshot_keys(snapshot: dict) -> set[str]:
    """snapshot에 있는 키 중 규약에 정의된 키만 반환. 누락/추가 검사용."""
    defined = set(snapshot_keys_all())
    present = set(snapshot.keys())
    return present & defined
