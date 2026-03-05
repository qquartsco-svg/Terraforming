# pipeline.py — JOE → MOE → Cherubim 순차 오케스트레이션
#
# 여기서만 3개 엔진을 호출. 엔진 간 상호 참조 원천 차단.
# 흐름: 진단(JOE 거시 → MOE 미시) → 선정(Cherubim 에덴 후보) → 계획(Plan 권장 조치).

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
    PlanetSnapshot 하나로 진단(JOE→MOE) → 선정(Cherubim) → 계획(Plan) 수행.
    반환 report.config_used 에 사용된 설정을 담아 재현·감사 가능.
    """
    cfg = dict(_config.CONFIG)
    if config_override:
        cfg.update({k: v for k, v in config_override.items() if k in cfg})

    joe_cfg = cfg.get("joe_config_override")
    moe_cfg = cfg.get("moe_config_override")
    cherubim_cfg = cfg.get("cherubim_config_override")

    # Stage 1: JOE — 거시 물리 1차 필터링 (구조적 안정성)
    joe_result = joe_assess(snapshot, config=joe_cfg)

    # Stage 2: MOE — 6도메인 리스크 정밀 진단 (환경 디테일 리포트)
    moe_result = moe_assess(snapshot, config=moe_cfg)

    # Stage 3: Cherubim — MOE 결과 기반 최적 정착지(Eden) 후보 선정
    cherubim_result = cherubim_find_sites(snapshot, moe_result, config=cherubim_cfg)

    # Stage 4: Plan — 리스크 지표 분석 → 테라포밍 권장 조치 생성
    plan = make_plan(snapshot, joe_result, moe_result, cherubim_result, config=cfg) if cfg.get("plan_rules_enabled") else TerraformingPlan(summary="plan 비활성화")

    summary = f"JOE={joe_result.habitability_label} | MOE={moe_result.label} | Cherubim={cherubim_result.summary} | Plan={plan.summary}"

    return TerraformingReport(
        joe=joe_result,
        moe=moe_result,
        cherubim=cherubim_result,
        plan=plan,
        summary=summary,
        config_used=cfg,
    )
