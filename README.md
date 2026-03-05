# Terraforming Engine — 방식 A 단일 패키지

스냅샷 하나가 파이프라인을 흐르며, 거시 필터(JOE) → 6도메인 리스크(MOE) → 에덴 후보(Cherubim) → 개입 가이드(Plan)가 순서대로 **도출**되도록 설계된 탐사 패키지. "답을 고정 제시"가 아니라 탐사가 흘러가게 하여 사용자가 결과를 따라가며 답을 찾아보게 하는 구조다.

- **스키마**: [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md) — 키 정의·예시.
- **재현·서명**: [SIGNATURE.md](SIGNATURE.md) — config 기록, 재현 가능 빌드.

---

## 1. What it is

**테라포밍**은 행성을 거주 가능하게 바꾸는 것을 가리킨다. 이 엔진은 행성이 정주·개입 대상으로서 가치가 있는지를 **단계적으로 탐사**하는 파이프라인이다. 입력은 **PlanetSnapshot(dict)** 하나, 출력은 한 번의 `run_survey()` 호출로 **report.joe**, **report.moe**, **report.cherubim**, **report.plan**, **report.summary**, **report.config_used** 가 도출된다. 엔진 간 상호 참조는 없고, **pipeline.py**에서만 JOE → MOE → Cherubim을 순차 호출한다.

---

## 2. Quickstart

**설치**

```bash
pip install -e .
# 또는
pip install .
```

**Python: run_survey**

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

## 3. Pipeline overview (JOE → MOE → Cherubim → Plan)

왜 이 순서인가:

- **JOE (거시)**: 기초 물리만 보고 구조적 붕괴·대기 소실 가능성이 큰 행성을 먼저 걸러서, 이후 단계 리소스 낭비를 줄인다.
- **MOE (미시)**: 6도메인(대기·수순환·지구물리·자기권·자전궤도·생물창) 리스크를 진단해 개입이 필요한 영역이 드러나게 한다.
- **Cherubim**: MOE 리스크를 거주 적합도로 바꿔 에덴 후보와 선정 이유(reasoning)가 도출되게 한다.
- **Plan**: domain_scores 임계치를 넘는 도메인에 대해 대기 보강·자기권 보조·수권 안정화·생물창 등 룰 기반 권장 조치가 도출된다.

진단(거시→미시) → 선정(거주지) → 계획(개입). 동일 스냅샷 하나가 파이프라인을 따라 흐르며 각 단계에서 결과만 덧붙여 전달된다.

---

## 4. Math implemented (JOE, MOE 핵심만)

**JOE**

- `planet_stress_raw` = a₁·σ_plate + a₂·(P_w/p_ref) + a₃·S_rot + a₄·(W_surface/W_total) + a₅·dW_surface_dt_norm → [ref_min, ref_max]로 정규화 → `planet_stress`.
- `instability_raw` = b₁·planet_stress + b₂·(W_surface/W_total) + b₃·dW_surface_dt_norm → [0,1] 포화 → `instability`.
- stress/instability 구간에 따라 habitability 라벨: extreme / low / moderate / high.

**MOE**

- 6도메인별로 스냅샷 키를 묶어 [0,1] 리스크 점수. 각 도메인 = 해당 키들의 [0,1] 정규화값 평균. biosphere_window_score 는 **invert**(높을수록 좋음 → 리스크 = 1−score).
- 결과: `domain_scores`, `attribution`.

**핵심 스냅샷 키**: sigma_plate, P_w, S_rot, W_surface, W_total, dW_surface_dt_norm (JOE). greenhouse_proxy, hydrology_stability_proxy, strip_risk_proxy, biosphere_window_score 등 (MOE). 자세한 목록·의미는 [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md).

---

## 5. PlanetSnapshot schema & Reproducibility

- **스키마**: [PLANET_SNAPSHOT_SCHEMA.md](PLANET_SNAPSHOT_SCHEMA.md) 에 전체 엔진 계약(키 정의·예시)이 있다. README에서는 핵심 키만 언급한다.
- **재현·감사**: 사용된 계수는 **config.py**에서 관리되며, `report.config_used` 에 기록된다. 동일 스냅샷·동일 config로 재현 가능. [SIGNATURE.md](SIGNATURE.md) 참고.

---

## 6. 현재 파일 구성 / 엔트리포인트 (배포 시 확인)

README가 말하는 **방식 A 단일 패키지**가 동작하려면, 아래 구조와 엔트리포인트가 맞아야 한다. **루트에 파일을 평평하게(flat) 올리면 안 되고**, 반드시 **terraforming_engine/** 파이썬 패키지 디렉터리가 있어야 한다.

**필수 디렉터리 구조**

```
리포 루트/
├── README.md, pyproject.toml, requirements.txt, LICENSE, SIGNATURE.md, PLANET_SNAPSHOT_SCHEMA.md
└── terraforming_engine/          # 파이썬 패키지 (이 폴더가 있어야 함)
    ├── __init__.py               # run_survey, TerraformingReport 등 Terraforming Engine 전용 export
    ├── __main__.py               # python -m terraforming_engine 용 CLI
    ├── pipeline.py, plan.py, report.py, schema.py, config.py
    ├── joe_engine/
    ├── moe_engine/
    ├── cherubim_engine/
    └── extensions/               # 선택 (없으면 HDR 미적용)
        └── history_reconstruction_adapter.py
```

**엔트리포인트 체크**

- `terraforming_engine/__init__.py` 는 **Terraforming Engine**용이어야 한다. `run_survey`, `TerraformingReport`, `TerraformingPlan` 등을 export. (다른 엔진의 Moe_Engine/Joe_Engine API를 export하면 안 됨.)
- `terraforming_engine/__main__.py` 는 **Terraforming Engine CLI**용이어야 한다. `from terraforming_engine import run_survey` 로 호출하고, `python -m terraforming_engine` / `python -m terraforming_engine /path/to/snapshot.json` 이 동작해야 한다. (Joe_Engine 전용 CLI 구조면 안 됨.)

배포·업로드 시 루트에 `__init__.py`, `__main__.py` 만 두고 `terraforming_engine/` 폴더를 빼면, `from terraforming_engine import run_survey` 와 `python -m terraforming_engine` 가 성립하지 않는다. 반드시 위 구조를 유지할 것.

**확장(선택)**  
`extensions/` 에 역사 역추적(HDR) 어댑터가 있으면 선택 사용. 해당 디렉터리·파일이 없으면 해당 기능은 미적용.

**수정 후 GitHub 푸시**

```bash
cd /path/to/Terraforming_Engine
bash setup_git_and_push.sh
# 또는
bash push_to_github.sh
```

자세한 안내: [PUSH_AFTER_EDIT.md](PUSH_AFTER_EDIT.md).

---

**버전**: 0.2.0. 다음 보강: plan.py 도메인별 테라포밍 장비·명령 세트 세부화, Cherubim 선정 알고리즘 코드 구체화.
