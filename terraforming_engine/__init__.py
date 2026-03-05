# Terraforming Engine — JOE → MOE → Cherubim 오케스트레이션 + TerraformingPlan.
# 단일 패키지. 엔진 3개는 내부 서브패키지로 포함, 서로 import 하지 않음.

from __future__ import annotations

from .pipeline import run_survey
from .report import TerraformingReport
from .plan import TerraformingPlan, make_plan
from .schema import snapshot_keys_all, validate_snapshot_keys, JOE_CORE_KEYS, MOE_PROXY_KEYS

__version__ = "0.1.0"

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
