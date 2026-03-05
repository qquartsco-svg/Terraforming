# Terraforming Engine — 최종 설계안 (방식 A)

**JOE(거시) → MOE(미시) → Cherubim(선정)** 엔진이 유기적으로 결합된 단일 독립 모듈.  
방식 A(단일 배포 통합 패키지)로 각 엔진의 독립성을 유지하면서 상용화 가능한 "완제품 탐사 패키지"를 구축한다.

- **PlanetSnapshot 표준**: [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md) — 전체 엔진 계약(키 정의·예시).
- **서명·재현성**: [SIGNATURE.md](SIGNATURE.md) — GPG 태그, 재현 가능 빌드, 의존성 없음.

---

## 이게 뭔가요? — 개념·수식·엔지니어링 흐름 (최소 설명)

과학·물리·엔지니어링 관점에서 "무슨 개념이 어떻게 수식으로 이어지고, 왜 이 순서로 도는지"만 최소한으로 정리한다.

### 테라포밍이란

**테라포밍(terraforming)**은 행성을 인간·생명이 살 수 있는 환경으로 바꾸는 것을 말한다.  
이 엔진은 **"이 행성이 정주·개입 대상으로 쓸 만한가?"**를 단계적으로 판단하는 **탐사 파이프라인**이다.  
입력은 행성의 물리·환경 상태를 담은 **스냅샷(PlanetSnapshot)** 하나이고, 출력은 거시 평가 → 6도메인 리스크 진단 → 최적 거주 후보지(Eden) 선정 → 테라포밍 권장 조치까지 한 번에 나온다.

### 왜 JOE → MOE → Cherubim 순서인가 (공학적 이유)

- **JOE (거시)**: 질량·회전·판 구조·수량 등 **기초 물리**만 보고 "구조적으로 붕괴하거나 대기가 다 날아갈 운명인 행성"을 먼저 걸러 낸다. → 여기서 탈락하면 이후 단계에 쓸 리소스를 쓰지 않는다.
- **MOE (미시)**: JOE를 통과한 행성에 대해 **대기·수순환·지구물리·자기권·자전궤도·생물창** 6개 도메인별 리스크를 정밀 진단한다. → "어디가 문제인지"를 특정해, 나중에 Plan이 개입할 영역을 정한다.
- **Cherubim (선정)**: MOE의 6도메인 리스크를 **거주 적합도**로 바꿔, 임계값 이상인 지역을 **에덴(Eden) 후보**로 뽑는다. → "어디에 먼저 정주·국소 테라포밍할지" 우선순위를 준다.
- **Plan**: MOE의 `domain_scores`가 임계치를 넘는 도메인에 대해 **대기 보강·자기권 보조·수권 안정화·생물창 확보** 등 룰 기반 권장 조치를 생성한다.

정리하면, **진단(거시 → 미시) → 선정(거주지) → 계획(개입)** 순서로, 데이터는 **동일한 스냅샷 하나**가 파이프라인을 따라 흐르며 각 단계에서 **결과만 덧붙여** 다음 단계로 전달된다.

### 단계별 개념·수식 (구현된 것만)

#### 1) JOE — 거시 물리 1차 필터

JOE는 **6개 스냅샷 키**만 읽어, 두 개의 **가중 합**과 **정규화·라벨**을 쓴다.  
(중력·탈출속도·회전 안정성 등은 이 패키지 밖에서 계산되어 스냅샷에 이미 들어온다고 가정한다.)

- **행성 스트레스 (현상적 지표)**  
  `planet_stress_raw` = a₁·σ_plate + a₂·(P_w/p_ref) + a₃·S_rot + a₄·(W_surface/W_total) + a₅·dW_surface_dt_norm  
  → [ref_min, ref_max] 구간으로 선형 정규화한 값이 `planet_stress` (0~1).

- **불안정도 (붕괴·소실 위험 proxy)**  
  `instability_raw` = b₁·planet_stress + b₂·(W_surface/W_total) + b₃·dW_surface_dt_norm  
  → [0,1]로 포화한 값이 `instability`.

- **거주가능성 라벨**  
  stress 또는 instability가 0.7 이상 → `"extreme"`, 0.4 이상 → `"low"`, 0.2 이상 → `"moderate"`, 그 외 → `"high"`.

계수 a₁~a₅, b₁~b₃, p_ref, ref_min, ref_max는 `config`로 주입되며, 재현·감사용으로 리포트에 기록된다.

#### 2) MOE — 6도메인 리스크

MOE는 스냅샷의 **프록시 키**들을 도메인별로 묶어, 각 도메인당 **리스크 점수 [0,1]**을 낸다.  
(1에 가까울수록 위험, 0에 가까울수록 양호.)

| 도메인 | 의미 | 사용 키 (요지) |
|--------|------|----------------|
| atmosphere_risk | 대기·온실·알베도 | greenhouse_proxy, tau_atm, albedo_eff |
| water_cycle_risk | 수순환 안정성 | hydrology_stability_proxy, dW_surface_dt_norm |
| geophysics_risk | 판·열류·화산 | sigma_plate, heat_flux_proxy, volcanism_proxy |
| magnetosphere_risk | 대기 제거·자기장 | strip_risk_proxy, B_surface_equator_proxy |
| rotation_orbit_risk | 자전·기후 변동·계절성 | S_rot, climate_variance_proxy, seasonality_proxy |
| biosphere_window_risk | 생물창 개방도 | biosphere_window_score (**invert**: 높을수록 좋음 → 리스크 = 1−score) |

각 도메인 점수 = 해당 키들의 [0,1] 정규화값 평균 (invert 있는 도메인은 1−값).  
결과는 `domain_scores`(도메인별 리스크)와 `attribution`(키별 기여)로 나온다.

#### 3) Cherubim — 에덴 후보 선정

MOE의 `domain_scores`를 **거주 적합도**로 바꾼다.  
**적합도** = 도메인별 가중평균(1 − risk).  
가중치 기본값은 geophysics_risk·biosphere_window_risk 쪽을 약간 높게 둔다.  
이 적합도가 **eden_threshold**(기본 0.4) 이상이면 전역 1건을 에덴 후보로 넣고, `best_site`, `score`, `reasoning`(도메인별 기여 상위)을 채운다.

#### 4) Plan — 테라포밍 권장 조치

MOE의 `domain_scores`를 보고, **domain_scores[도메인] ≥ 0.5**이면 해당 도메인에 대한 권장 조치(대기 보강·자기권 보조·수권 안정화·생물창 등)를 추가한다.  
geophysics ≥ 0.6이면 별도 플래그를 세우는 등 룰이 있으며, 우선순위는 점수 구간에 따라 high/medium으로 나뉜다.

### 파라미터 의미 (물리·공학 관점)

스냅샷 키가 물리적으로 무엇을 proxy 하는지, 엔지니어가 코드 없이도 "무슨 입력인지" 알 수 있도록 요약한다.

| 키 | 물리·공학적 의미 |
|----|------------------|
| **sigma_plate** | 판 구조/텍토닉 활성도 proxy. [0,1] 권장. 높을수록 지질적으로 불안정·위험. |
| **P_w** | 내부 유체 압력 proxy. JOE에서 p_ref로 나누어 스트레스 항에 기여. |
| **S_rot** | 자전 안정성 지표. [0,1]. 문서상 S_rot∝(ω²R)/g 등으로 정의될 수 있음(본 패키지는 스냅샷 입력만 사용). |
| **W_surface** | 표면 수량(질량·부피 등 단위 통일된 값). |
| **W_total** | 총 수량. W_surface/W_total = 표면 수량 비율 → 스트레스·불안정도에 기여. |
| **dW_surface_dt_norm** | 표면 수량 변화율의 정규화값. [0,1]. 빠른 증발/고갈이면 높음. |
| **greenhouse_proxy** | 온실 효과 강도 proxy. 높을수록 대기 리스크 증가. |
| **hydrology_stability_proxy** | 수순환 안정성. 낮을수록 water_cycle_risk 증가. |
| **strip_risk_proxy** | 대기 제거(stripping) 위험. 높을수록 자기권 리스크. |
| **biosphere_window_score** | 생물창 개방도 [0,1]. 1에 가까울수록 온도·압력 등 생존 가능 창이 넓음 → MOE에서는 invert되어 리스크로 변환. |

자세한 키 목록·예시는 [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md)를 참고하면 된다.

---

## 통합 탐사 파이프라인 (서사·기술)

본 엔진은 **행성 탄생 이전 물리 조건부터 최종 거주지 확정 및 개입 계획까지** 관통하는 일괄 탐사 파이프라인으로 동작한다. 각 단계는 이전 단계의 결과를 필터로 삼아 탐사 범위를 좁혀 간다.

| 단계 | 엔진 | 서사적 위치 | 기술적 역할 | 테라포밍 연계 |
|------|------|-------------|-------------|----------------|
| **1** | **JOE** (Macro Physics) | Day 0 이전 거시 조건 탐색 관찰자 | 질량·회전·판 구조 등 기초 물리 뼈대로 구조적 안정성 판정 | 붕괴/대기 소실 운명 선별 → 무의미한 자원 낭비 방지 |
| **2** | **MOE** (Micro Environment) | JOE 승인 행성 내부 진입, 환경 디테일 스캔 | 6도메인 리스크 정밀 진단 및 원인(Attribution) 분석 | 생물창 개방도 파악 → 개입이 필요한 환경 요소 특정 |
| **3** | **Cherubim** (Settlement Search) | MOE 진단 기반 최적 거주구역(Eden) 선정·수호 가드 | 리스크가 낮은 도메인 조합으로 정착 시나리오·지표 추출 | 지역별 리스크 분석 → 국소 테라포밍(Eden 조성) 우선순위 결정 |
| **4** | **Terraforming Plan** | 실행 정책·개입 가이드 | MOE domain_scores 임계치 초과 시 룰 기반 정책 엔진으로 환경 개선 조치 생성 | — |

**Plan 분야별 개입 예시**

- **대기(Atmosphere)**: 온실 가스 농도 조정, 복사 차폐막 설치 제안.
- **자기권(Magnetosphere)**: 대기 소실(Strip risk) 방지용 인공 자기장 발생 장치 배치 제안.
- **수순환(Water Cycle)**: 수권 안정화를 위한 인공 응축·강수 제어 시스템 제안.
- **생물창(Biosphere)**: 생존 가능 온도·압력 창 확보를 위한 목표 수치 제시.

**독립성·무결성 규칙**

- **엔진 간 상호 참조 금지**: JOE, MOE, Cherubim은 서로를 모르며, **pipeline.py**에서만 순차 전달.
- **Snapshot Protocol**: 모든 엔진은 **schema.py** 공통 dict 스냅샷 규약으로 데이터 연속성 유지.
- **재현성·감사**: **config.py** 중앙 관리, 최종 리포트에 사용 계수 기록 → 동일 탐사 결과 재현 가능.

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

### 확장: 역사 역추적(HDR) 어댑터

코어 `run_survey()`에서는 호출하지 않음. 선택 사용:

```python
from terraforming_engine.extensions import hdr_is_available, reconstruct_origin_from_snapshots

# 스냅샷 시퀀스에서 기원(origin) 스냅샷 추출. HDR 미설치 시 timestamp 기준 가장 과거 1건 반환(폴백).
snapshots = [
    {"snapshot": {...}, "timestamp": 0.0, "source": "terraforming"},
    {"snapshot": {...}, "timestamp": 1.0, "source": "terraforming"},
]
origin = reconstruct_origin_from_snapshots(snapshots)
# HDR 설치 여부
print(hdr_is_available())
```

---

## 5. 버전

0.2.0 — Cherubim 선정 알고리즘 구체화(6도메인 적합도·후보/score/reasoning). HDR 어댑터 연동 로직(폴백 포함).  
**PlanetSnapshot 표준 확정** → [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md).

**다음 보강 옵션**: plan.py에 도메인별 테라포밍 장비·명령 세트 세부화.

---

## 6. 수정 후 GitHub 푸시 (필수)

**규칙**: 코드·문서를 수정하면 **커밋 + GitHub 푸시**까지 완료한다.

```bash
cd /Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/Terraforming_Engine
bash setup_git_and_push.sh
# 또는
bash push_to_github.sh
```

자세한 안내: [PUSH_AFTER_EDIT.md](PUSH_AFTER_EDIT.md).
