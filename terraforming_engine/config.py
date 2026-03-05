# config.py — CONFIG 단일 dict (재현성·감사)
#
# 모든 설정은 여기서 관리. TerraformingReport.config_used에 기록해
# 동일 탐사 결과를 재현할 수 있게 함.

from __future__ import annotations

from typing import Any

CONFIG: dict[str, Any] = {
    "pipeline_version": "0.1.0",
    "joe_config_override": None,   # dict or None → joe_engine에 전달
    "moe_config_override": None,
    "cherubim_config_override": None,
    "plan_rules_enabled": True,
}
