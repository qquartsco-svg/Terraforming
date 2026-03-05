# cherubim_engine — 에덴/정착 후보지 선정. Terraforming 내부.
# joe/moe import 금지. pipeline에서만 호출.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# 에덴 적합도 계산용 도메인 가중치 (낮을수록 좋은 리스크 → 높을수록 좋은 적합도)
DEFAULT_EDEN_WEIGHTS: Dict[str, float] = {
    "atmosphere_risk": 1.0,
    "water_cycle_risk": 1.0,
    "geophysics_risk": 1.2,      # 지질 안정성 중요
    "magnetosphere_risk": 1.0,
    "rotation_orbit_risk": 1.0,
    "biosphere_window_risk": 1.5,  # 생물창이 선정에 가장 중요
}


def _eden_fitness(domain_scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> tuple[float, Dict[str, float]]:
    """
    도메인 리스크 → 거주 적합도 [0,1]. 리스크 낮을수록 적합도 높음.
    반환: (종합 적합도, 도메인별 기여도 0~1)
    """
    w = dict(DEFAULT_EDEN_WEIGHTS) if weights is None else {**DEFAULT_EDEN_WEIGHTS, **(weights or {})}
    contrib: Dict[str, float] = {}
    total_w = 0.0
    weighted_sum = 0.0
    for domain, risk in domain_scores.items():
        weight = w.get(domain, 1.0)
        if weight <= 0:
            continue
        fit = 1.0 - max(0.0, min(1.0, risk))
        contrib[domain] = fit
        weighted_sum += fit * weight
        total_w += weight
    overall = weighted_sum / total_w if total_w > 0 else 0.0
    return max(0.0, min(1.0, overall)), contrib


@dataclass(frozen=True)
class EdenAssessment:
    """
    Cherubim 결과 구조. find_sites() 반환형.
    - candidate_sites: 에덴 후보지 목록 (각 항목: score, domain_contrib, label 등)
    - best_site: 최우선 후보 1건 (없으면 None)
    - score: 전체 선정 점수 [0,1]
    - reasoning: 선정 근거 요약
    """
    candidate_sites: List[Dict[str, Any]] = field(default_factory=list)
    best_site: Optional[Dict[str, Any]] = None
    score: float = 0.0
    reasoning: str = ""
    summary: str = ""

    @property
    def sites(self) -> List[Dict[str, Any]]:
        """하위 호환."""
        return list(self.candidate_sites)


def find_sites(
    snapshot: Dict[str, Any],
    moe_result: Any,
    *,
    config: Any = None,
) -> EdenAssessment:
    """
    스냅샷 + MOE 결과 → 에덴 후보지 선정.
    MOE 6도메인 리스크를 거주 적합도로 변환해, 임계값 이상이면 후보로 넣고
    best_site·score·reasoning을 채운다.
    """
    domain_scores = getattr(moe_result, "domain_scores", None) or {}
    attribution = getattr(moe_result, "attribution", None) or {}

    cfg = config if isinstance(config, dict) else {}
    weights = cfg.get("eden_weights")
    threshold = float(cfg.get("eden_threshold", 0.4))  # 적합도 >= 이면 후보

    fitness, domain_contrib = _eden_fitness(domain_scores, weights)

    candidate_sites: List[Dict[str, Any]] = []
    if fitness >= threshold:
        site = {
            "label": "global",
            "score": fitness,
            "domain_contrib": domain_contrib,
            "domain_scores_ref": dict(domain_scores),
        }
        candidate_sites.append(site)

    best_site = candidate_sites[0] if candidate_sites else None
    top_contrib = sorted(domain_contrib.items(), key=lambda x: -x[1])[:3]
    reasoning = " | ".join(f"{d}={c:.2f}" for d, c in top_contrib) if top_contrib else "domain_scores 기반 적합도"
    summary = f"에덴 후보 {len(candidate_sites)}건, 적합도={fitness:.3f}"

    return EdenAssessment(
        candidate_sites=candidate_sites,
        best_site=best_site,
        score=fitness,
        reasoning=reasoning,
        summary=summary,
    )


__all__ = ["EdenAssessment", "find_sites", "DEFAULT_EDEN_WEIGHTS"]
__version__ = "0.2.0"
