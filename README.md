# Terraforming Engine

**JOE → MOE → Cherubim** 파이프라인 + **TerraformingPlan** 생성까지 포함한 단일 패키지.

- 하나의 행성 스냅샷(`dict`)으로 거시 평가(JOE) → 미시 진단(MOE) → 에덴 후보 탐사(Cherubim) → 권장 테라포밍 조치(Plan)까지 수행.
- 엔진 3개는 **서로 import 하지 않음**. 오직 `pipeline`에서만 순서대로 호출.
- 표준 라이브러리만 사용. `requirements.txt` 비움.

## 설치

```bash
pip install -e .
# 또는
pip install .
```

## 사용

```python
from terraforming_engine import run_survey

snapshot = {
    "sigma_plate": 0.1,
    "P_w": 0.5,
    "S_rot": 0.2,
    "W_surface": 1e9,
    "W_total": 1.4e9,
    "dW_surface_dt_norm": 0.0,
    "greenhouse_proxy": 0.6,
    "hydrology_stability_proxy": 0.3,
    "strip_risk_proxy": 0.2,
    "biosphere_window_score": 0.8,
}

report = run_survey(snapshot)
# report.joe   → PlanetAssessment
# report.moe   → MoeAssessment
# report.cherubim → EdenAssessment (또는 스텁)
# report.plan  → TerraformingPlan
# report.summary
```

## CLI

```bash
python -m terraforming_engine
python -m terraforming_engine /path/to/snapshot.json
```

## 구조

```
terraforming_engine/
├── __init__.py      # run_survey, TerraformingReport, TerraformingPlan
├── __main__.py      # CLI
├── schema.py        # PlanetSnapshot 키 계약
├── pipeline.py      # JOE → MOE → Cherubim 오케스트레이션
├── plan.py          # 룰 기반 TerraformingPlan
├── report.py        # TerraformingReport
├── config.py        # CONFIG 단일 dict
├── joe_engine/      # 내부 복사 (JOE)
├── moe_engine/      # 내부 복사 (MOE)
└── cherubim_engine/ # 스텁 (실제 Cherubim_Engine 연동 시 교체)
```

## 독립성 규칙

- `joe_engine` 안에서 `moe_engine` / `cherubim_engine` import 금지.
- `moe_engine` 안에서 `joe_engine` / `cherubim_engine` import 금지.
- `cherubim_engine` 안에서 `joe_engine` / `moe_engine` import 금지.
- 연결은 **pipeline**에서만.

## 버전

0.1.0 — 초안. Cherubim은 스텁.
