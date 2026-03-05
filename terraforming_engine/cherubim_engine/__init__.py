# cherubim_engine — 에덴/정착 후보지 탐사. Terraforming 내부 스텁.
# joe/moe import 금지. 실제 Cherubim_Engine 레포 연동 시 이 패키지만 교체.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class EdenAssessment:
    """에덴 후보지 목록 + 요약. find_sites() 반환형."""
    sites: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""


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
    # 스텁: biosphere_window가 좋은 쪽을 에덴 후보 1개로 가정
    biosphere = domain_scores.get("biosphere_window_risk", 1.0)
    count = 1 if biosphere < 0.6 else 0
    sites = [{"stub": True, "reason": "biosphere_window_risk"}] if count else []
    summary = f"에덴 후보 {len(sites)}건 (스텁)"
    return EdenAssessment(sites=sites, summary=summary)


__all__ = ["EdenAssessment", "find_sites"]
__version__ = "0.1.0"
