# Terraforming Engine 단일 CONFIG. 하드코딩 최소화, 재현/감사용.

from __future__ import annotations

from typing import Any

# 파이프라인에서 사용할 기본 설정.
# joe/moe/cherubim 각자 config는 각 서브패키지 DEFAULT_CONFIG 사용하고,
# 여기서는 "이번 실행에 쓴 설정"만 기록해 TerraformingReport.config_used에 넣는다.
CONFIG: dict[str, Any] = {
    "pipeline_version": "0.1.0",
    "joe_config_override": None,   # dict or None
    "moe_config_override": None,
    "cherubim_config_override": None,
    "plan_rules_enabled": True,
}
