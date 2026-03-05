# report.py — TerraformingReport (통합 결과물)
#
# 진단(JOE/MOE) → 선정(Cherubim) → 계획(Plan) 결과를 하나로 묶어 반환.
# report는 엔진 타입을 알지 않음; pipeline에서 채운 값을 그대로 담는다.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TerraformingReport:
    """파이프라인 최종 출력. 한 번에 묶어서 반환."""

    joe: Any       # PlanetAssessment (거시 평가)
    moe: Any       # MoeAssessment (6도메인 진단)
    cherubim: Any  # EdenAssessment 또는 sites (에덴 후보 선정)
    plan: Any      # TerraformingPlan (권장 조치)
    summary: str   # 한 줄 요약
    config_used: dict[str, Any] = field(default_factory=dict)  # 재현·감사용
