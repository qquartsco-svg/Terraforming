# Terraforming Engine — 단일 독립 모듈 (방식 A)
#
# 진입점: run_survey(snapshot) → TerraformingReport
# 진단(JOE → MOE) → 선정(Cherubim) → 계획(Plan). 엔진 3개는 서로 import 하지 않음.

from __future__ import annotations

from .pipeline import run_survey
from .report import TerraformingReport
from .plan import TerraformingPlan, make_plan
from .schema import (
    JOE_CORE_KEYS,
    MOE_PROXY_KEYS,
    snapshot_keys_all,
    validate_snapshot_keys,
)

__version__ = "0.2.0"

__all__ = [
    "run_survey",
    "TerraformingReport",
    "TerraformingPlan",
    "make_plan",
    "snapshot_keys_all",
    "validate_snapshot_keys",
    "JOE_CORE_KEYS",
    "MOE_PROXY_KEYS",
    "__version__",
]
