#!/usr/bin/env python3
"""
테라포밍 파이프라인 전체 데모: JOE → MOE → Cherubim → Plan

설계 원칙:
  - terraforming_engine 패키지를 통해 파이프라인 실행
  - 엔진 간 직접 참조 없음 — snapshot dict 가 유일한 데이터 통로
  - JOE(거시) → MOE(미시 6도메인) → Cherubim(에덴 후보) → Plan(권장 조치)

실행 방법:
  python run_pipeline_demo.py
"""

from __future__ import annotations

from terraforming_engine import run_survey

# ── 데모 스냅샷 (JOE 6키 + MOE proxy + Cherubim optional) ───────────────────
DEMO_SNAPSHOT = {
    # ── JOE 핵심 6키 (거시 물리)
    "sigma_plate":               0.10,
    "P_w":                       0.50,
    "S_rot":                     0.20,
    "W_surface":                 1.00e9,
    "W_total":                   1.40e9,
    "dW_surface_dt_norm":        0.00,

    # ── MOE 확장 proxy (도메인별)
    "greenhouse_proxy":          0.30,
    "tau_atm":                   0.25,
    "albedo_eff":                0.30,
    "hydrology_stability_proxy": 0.20,
    "heat_flux_proxy":           0.15,
    "volcanism_proxy":           0.10,
    "strip_risk_proxy":          0.20,
    "B_surface_equator_proxy":   0.30,
    "climate_variance_proxy":    0.15,
    "seasonality_proxy":         0.10,
    "biosphere_window_score":    0.85,

    # ── Cherubim 선택 키 (에덴 후보 정밀화)
    "latitude_band":                  35.0,
    "tectonic_stability_proxy":       0.90,
    "water_availability_proxy":       0.85,
    "temperature_window_proxy":       0.90,
    "radiation_proxy":                0.10,
}


def main() -> None:
    print("=" * 60)
    print("  테라포밍 파이프라인: JOE → MOE → Cherubim → Plan")
    print("=" * 60)
    print()

    report = run_survey(DEMO_SNAPSHOT)

    # ── [JOE] 거시 평가
    print("[JOE]  거시 물리 평가")
    print(f"  planet_stress : {report.joe.planet_stress:.4f}")
    print(f"  instability   : {report.joe.instability:.4f}")
    print(f"  habitability  : {report.joe.habitability_label}")
    print(f"  요약          : {report.joe.summary}")
    print()

    # ── [MOE] 6도메인 미시 진단
    print("[MOE]  6도메인 미시 진단")
    print(f"  moe_risk : {report.moe.moe_risk:.4f}  ({report.moe.label})")
    print(f"  요약     : {report.moe.summary}")
    print("  domain_scores:")
    for domain, score in sorted(report.moe.domain_scores.items()):
        bar = "█" * int(score * 20)
        print(f"    {domain:<28s} {score:.3f}  |{bar:<20s}|")
    print()

    # ── [Cherubim] 에덴 후보 선정
    print("[Cherubim]  에덴 후보 선정")
    ch = report.cherubim
    print(f"  score     : {getattr(ch, 'score', '?')}")
    print(f"  요약      : {getattr(ch, 'summary', '?')}")
    reasoning = getattr(ch, 'reasoning', None)
    if reasoning:
        print(f"  reasoning : {reasoning}")
    print()

    # ── [Plan] 테라포밍 권장 조치
    print("[Plan]  테라포밍 권장 조치")
    print(f"  feasibility : {report.plan.feasibility}")
    print(f"  요약        : {report.plan.summary}")
    for a in report.plan.actions:
        print(f"  [{a['priority']}] {a['domain']}: {a['action']}")
    if report.plan.flags:
        print(f"  ⚠ flags : {', '.join(report.plan.flags)}")
    print()

    print("=" * 60)
    print("  종합:", report.summary)
    print("=" * 60)


if __name__ == "__main__":
    main()
