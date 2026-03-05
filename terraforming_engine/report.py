# TerraformingReport — 파이프라인 최종 출력. 한 번에 묶어서 반환.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 타입은 서브패키지에서 가져오면 pipeline이 엔진을 알아야 하므로,
# 여기서는 Any로 받고 pipeline에서 채운다.
# from .joe_engine import PlanetAssessment
# from .moe_engine import MoeAssessment
# 등은 report.py가 엔진을 알게 하므로 사용하지 않음.


@dataclass(frozen=True)
class TerraformingReport:
    """JOE → MOE → Cherubim → Plan 결과를 하나로 묶은 보고서."""

    joe: Any   # PlanetAssessment
    moe: Any   # MoeAssessment
    cherubim: Any   # EdenAssessment or list of sites
    plan: Any   # TerraformingPlan
    summary: str
    config_used: dict[str, Any] = field(default_factory=dict)
