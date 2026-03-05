# TerraformingPlan — 룰 기반 행성 개선(개입) 제안. 수치 적분 없음.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 도메인 리스크 키 (MOE domain_scores와 동일한 이름)
DOMAIN_RISK_KEYS = (
    "atmosphere_risk",
    "magnetosphere_risk",
    "water_cycle_risk",
    "geophysics_risk",
    "rotation_orbit_risk",
    "biosphere_window_risk",
)

# 도메인별 권장 조치 (§7.6)
DOMAIN_RECOMMENDATIONS: dict[str, str] = {
    "atmosphere_risk": "대기 보강 / 온실 조정 / 차폐",
    "magnetosphere_risk": "자기권 보조 (위성/자기장 발생장치)",
    "water_cycle_risk": "수권 안정화 / 물 공급 / 응축 제어",
    "geophysics_risk": "열류·판 구조 인공 조정은 고위험 → flag만",
    "rotation_orbit_risk": "장주기 안정화 (거울, 차폐, 계절 보정)",
    "biosphere_window_risk": "생물창 확보를 위한 온도·압력 범위 목표 제시",
}


@dataclass(frozen=True)
class TerraformingPlan:
    """권장 테라포밍 조치. 도메인별 리스크에 따른 룰 기반 제안."""

    recommendations: dict[str, str] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)  # 고위험 등 주의 플래그
    summary: str = ""


def make_plan(
    snapshot: Any,
    joe_result: Any,
    moe_result: Any,
    cherubim_result: Any,
    *,
    config: Any = None,
) -> TerraformingPlan:
    """
    스냅샷 + JOE/MOE/Cherubim 결과 → TerraformingPlan.
    moe_result.domain_scores를 기준으로 도메인별 권장 조치를 채운다.
    """
    _ = snapshot
    _ = joe_result
    _ = cherubim_result
    _ = config

    recommendations: dict[str, str] = {}
    flags: list[str] = []

    domain_scores = getattr(moe_result, "domain_scores", None) or {}
    for domain in DOMAIN_RISK_KEYS:
        risk = domain_scores.get(domain, 0.0)
        rec = DOMAIN_RECOMMENDATIONS.get(domain, "")
        if risk >= 0.5 and rec:
            recommendations[domain] = rec
        if domain == "geophysics_risk" and risk >= 0.6:
            flags.append("geophysics_high_risk")

    summary = (
        f"권장 조치 {len(recommendations)}건, 플래그 {len(flags)}개"
        if recommendations or flags
        else "현재 스냅샷 기준 특별 권장 없음"
    )
    return TerraformingPlan(
        recommendations=recommendations,
        flags=flags,
        summary=summary,
    )
