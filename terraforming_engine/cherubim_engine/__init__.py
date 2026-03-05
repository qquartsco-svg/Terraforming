# cherubim_engine — 에덴/정착 후보지 탐사. Terraforming 내부 스텁.
# joe/moe import 금지. 실제 Cherubim_Engine 레포 연동 시 이 패키지만 교체.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EdenAssessment:
    """
    Cherubim 결과 구조. find_sites() 반환형.
    - candidate_sites: 에덴 후보지 목록
    - best_site: 최우선 후보 1건 (없으면 None)
    - score: 전체 선정 점수 [0,1]
    - reasoning: 선정 근거 요약
    """
    candidate_sites: List[Dict[str, Any]] = field(default_factory=list)
    best_site: Optional[Dict[str, Any]] = None
    score: float = 0.0
    reasoning: str = ""
    summary: str = ""  # 하위 호환

    @property
    def sites(self) -> List[Dict[str, Any]]:
        """하위 호환: candidate_sites와 동일."""
        return list(self.candidate_sites)


def find_sites(
    snapshot: Dict[str, Any],
    moe_result: Any,
    *,
    config: Any = None,
) -> EdenAssessment:
    """
    스냅샷 + MOE 결과 → 에덴 후보지.
    현재는 스텁: domain_scores 기반으로 후보 수만 반환. 실제 구현은 Cherubim_Engine 연동 시.
    """
    _ = config
    domain_scores = getattr(moe_result, "domain_scores", None) or {}
    biosphere = domain_scores.get("biosphere_window_risk", 1.0)
    count = 1 if biosphere < 0.6 else 0
    candidate_sites = [{"stub": True, "reason": "biosphere_window_risk"}] if count else []
    best_site = candidate_sites[0] if candidate_sites else None
    score = 1.0 - biosphere if count else 0.0
    reasoning = "biosphere_window_risk 기반 스텁 선정"
    summary = f"에덴 후보 {len(candidate_sites)}건 (스텁)"
    return EdenAssessment(
        candidate_sites=candidate_sites,
        best_site=best_site,
        score=score,
        reasoning=reasoning,
        summary=summary,
    )


__all__ = ["EdenAssessment", "find_sites"]
__version__ = "0.1.0"
