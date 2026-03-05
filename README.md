# Terraforming Engine — 최종 설계안 (방식 A)

**JOE(거시) → MOE(미시) → Cherubim(선정)** 엔진이 유기적으로 결합된 단일 독립 모듈.  
방식 A(단일 배포 통합 패키지)로 각 엔진의 독립성을 유지하면서 상용화 가능한 "완제품 탐사 패키지"를 구축한다.

- **PlanetSnapshot 표준**: [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md) — 전체 엔진 계약(키 정의·예시).
- **서명·재현성**: [SIGNATURE.md](SIGNATURE.md) — GPG 태그, 재현 가능 빌드, 의존성 없음.

---

## 1. 아키텍처

- **pipeline.py**에서만 JOE / MOE / Cherubim을 순차 호출. 엔진 간 상호 참조 **원천 차단**.
- 공통 입력: **PlanetSnapshot(dict)** 하나. 파이프라인 레이어에서 결과만 합친다.

```
terraforming_engine/               # 단일 제품 리포지터리 루트
├── README.md                      # 통합 엔진 명세 및 서사
├── pyproject.toml
├── requirements.txt               # 표준 라이브러리만 (비움)
└── terraforming_engine/           # 최상위 파이프라인 패키지
    ├── __init__.py                # run_survey(snapshot) 진입점
    ├── pipeline.py                # JOE → MOE → Cherubim 순차 오케스트레이션
    ├── schema.py                  # PlanetSnapshot 공통 규약 (Key 목록)
    ├── plan.py                    # TerraformingPlan (환경 개선 정책) 생성
    ├── report.py                  # TerraformingReport 정의
    ├── config.py                  # CONFIG 단일 dict (재현성 관리)
    ├── joe_engine/                # Stage 1: Macro Assessor (복사본)
    ├── moe_engine/                # Stage 2: Micro Assessor (복사본)
    ├── cherubim_engine/           # Stage 3: Eden Guard (복사본)
    └── extensions/                # 선택 기능 (코어 아님)
        └── history_reconstruction_adapter.py  # HDR 연동 시 어댑터만
```

---

## 2. 단계별 데이터 흐름 (Snapshot Protocol)

| 단계 | 엔진 | 역할 |
|------|------|------|
| 1 | **JOE** | 거시 물리 조건(질량, 회전 등)으로 행성 구조적 안정성 1차 필터링 |
| 2 | **MOE** | 스냅샷의 6도메인 리스크 정밀 진단 → 환경 디테일 리포트 |
| 3 | **Cherubim** | MOE 진단 결과 기반 행성 내 최적 정착지(Eden) 후보 선정 |
| 4 | **Plan** | 리스크 지표 분석 → 대기 보강, 자기권 보조, 수권 안정화 등 테라포밍 권장 조치 생성 |

**진단(JOE/MOE) → 선정(Cherubim) → 계획(Plan)** 흐름이 명확하다.

### 결과 구조 (계약)

- **report.joe**: PlanetAssessment (거시 평가)
- **report.moe**: MoeAssessment (6도메인 진단)
- **report.cherubim**: **EdenAssessment** — `candidate_sites`, `best_site`, `score`, `reasoning`, `summary`
- **report.plan**: **TerraformingPlan** — `recommendations`, `actions` (domain/action/priority), `flags`, `feasibility`, `estimated_time`, `summary`

---

## 3. 설계 원칙

- **독립성**: `joe_engine`에서 `moe_engine` import 금지 등 엔진 간 직접 호출 **절대 금지**. 오직 **pipeline.py**에서만 순서대로 호출.
- **재현성·감사**: 모든 설정은 **config.py**에서 관리. 최종 리포트에 사용된 계수 포함 → 동일 탐사 결과 재현 가능.
- **확장성**: 역사 역추적(HDR)은 코어에 넣지 않고 **extensions/** 에 어댑터 형태로 두어 선택 사용.

---

## 4. 설치 및 사용

```bash
pip install -e .
# 또는
pip install .
```

```python
from terraforming_engine import run_survey

snapshot = {
    "sigma_plate": 0.1, "P_w": 0.5, "S_rot": 0.2,
    "W_surface": 1e9, "W_total": 1.4e9, "dW_surface_dt_norm": 0.0,
    "greenhouse_proxy": 0.6, "hydrology_stability_proxy": 0.3,
    "strip_risk_proxy": 0.2, "biosphere_window_score": 0.8,
}
report = run_survey(snapshot)
# report.joe, report.moe, report.cherubim, report.plan, report.summary, report.config_used
```

**CLI**

```bash
python -m terraforming_engine
python -m terraforming_engine /path/to/snapshot.json
```

---

## 5. 버전

0.1.0 — 초안. Cherubim은 스텁. HDR은 extensions에 placeholder만 둠.  
**PlanetSnapshot 표준 확정** → [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md).
