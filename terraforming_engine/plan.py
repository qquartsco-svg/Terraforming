# plan.py — TerraformingPlan (환경 개선 정책)
#
# MOE domain_scores가 흐르면서 임계치를 넘는 도메인에 대해 대기 보강, 자기권 보조,
# 수권 안정화 등 권장 조치가 도출되도록 룰 기반으로 생성. "결론 고정 제시"보다
# 탐사 결과를 따라가며 개입 포인트를 찾아보게 하는 용도. 수치 적분 없음.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# MOE domain_scores 키와 동일
DOMAIN_RISK_KEYS = (
    "atmosphere_risk",
    "magnetosphere_risk",
    "water_cycle_risk",
    "geophysics_risk",
    "rotation_orbit_risk",
    "biosphere_window_risk",
)

# 도메인별 권장 조치 (설계안 §7.6)
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
    """
    권장 테라포밍 조치. 도메인별 리스크에 따른 룰 기반 제안.
    - recommendations: 도메인 → 권장 조치 문구
    - actions: 정렬된 조치 목록 (domain, action, priority)
    - flags: 고위험 등 주의 플래그
    - feasibility: 전체 실행 가능성 ("high"|"medium"|"low")
    - estimated_time: 추정 소요 (문자열, 향후 확장)
    """
    recommendations: dict[str, str] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)  # [{"domain": str, "action": str, "priority": str}, ...]
    flags: list[str] = field(default_factory=list)
    feasibility: str = "medium"  # high | medium | low
    estimated_time: str = ""     # 확장용
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
    스냅샷 + JOE/MOE/Cherubim 결과가 흐르면, domain_scores 기준으로 권장 조치가 도출된다.
    입력: snapshot(공통), joe_result(거시), moe_result(domain_scores 사용), cherubim_result(선택).
    룰: domain_scores[도메인] >= 0.5 이면 해당 권장 조치 추가; geophysics >= 0.6 이면 flag 추가.
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

    # actions: recommendations를 리스트 형태로 (domain, action, priority)
    actions: list[dict[str, Any]] = []
    for dom, act in recommendations.items():
        priority = "high" if domain_scores.get(dom, 0) >= 0.7 else "medium"
        actions.append({"domain": dom, "action": act, "priority": priority})
    feasibility = "low" if flags else ("high" if len(recommendations) <= 2 else "medium")
    estimated_time = ""  # 확장 시 채움

    summary = (
        f"권장 조치 {len(recommendations)}건, 플래그 {len(flags)}개"
        if recommendations or flags
        else "현재 스냅샷 기준 특별 권장 없음"
    )
    return TerraformingPlan(
        recommendations=recommendations,
        actions=actions,
        flags=flags,
        feasibility=feasibility,
        estimated_time=estimated_time,
        summary=summary,
    )
