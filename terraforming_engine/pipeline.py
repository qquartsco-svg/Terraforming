# JOE → MOE → Cherubim 오케스트레이션. 여기서만 3개 엔진을 순서대로 호출.

from __future__ import annotations

from typing import Any, Dict

from . import config as _config
from .report import TerraformingReport
from .plan import make_plan, TerraformingPlan

# 파이프라인 레이어에서만 서브패키지 import
from .joe_engine import assess_planet as joe_assess
from .moe_engine import assess_planet_detail as moe_assess
from .cherubim_engine import find_sites as cherubim_find_sites


def run_survey(
    snapshot: Dict[str, Any],
    *,
    config_override: None | Dict[str, Any] = None,
) -> TerraformingReport:
    """
    스냅샷 하나로 JOE → MOE → Cherubim → Plan 까지 수행하고 TerraformingReport 반환.
    """
    cfg = dict(_config.CONFIG)
    if config_override:
        cfg.update({k: v for k, v in config_override.items() if k in cfg})

    joe_cfg = cfg.get("joe_config_override")
    moe_cfg = cfg.get("moe_config_override")
    cherubim_cfg = cfg.get("cherubim_config_override")

    # 1) JOE
    joe_result = joe_assess(snapshot, config=joe_cfg)

    # 2) MOE
    moe_result = moe_assess(snapshot, config=moe_cfg)

    # 3) Cherubim (스냅샷 + MOE 결과)
    cherubim_result = cherubim_find_sites(snapshot, moe_result, config=cherubim_cfg)

    # 4) Plan (룰 기반)
    plan = make_plan(snapshot, joe_result, moe_result, cherubim_result, config=cfg) if cfg.get("plan_rules_enabled") else TerraformingPlan(summary="plan 비활성화")

    # 5) Summary 한 줄
    summary = f"JOE={joe_result.habitability_label} | MOE={moe_result.label} | Cherubim={cherubim_result.summary} | Plan={plan.summary}"

    return TerraformingReport(
        joe=joe_result,
        moe=moe_result,
        cherubim=cherubim_result,
        plan=plan,
        summary=summary,
        config_used=cfg,
    )
