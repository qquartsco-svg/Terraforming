# PlanetSnapshot 표준 스키마 (전체 엔진 계약)

**PlanetSnapshot**은 `dict` 하나로, JOE / MOE / Cherubim 전체의 **공통 입력**이다.  
이 키 집합이 확정되면 전체 시스템이 안정된다.

---

## 1. 스키마 개요

| 구간 | 키 그룹 | 용도 |
|------|----------|------|
| 기반(선택) | mass, radius, gravity | 행성 기본 물리 (Cherubim/물리 레이어 연동 시) |
| JOE CORE | 6키 | 거시 물리 → 구조적 안정성 1차 필터링 |
| MOE PROXY | 11키 | 6도메인 리스크 정밀 진단 |
| Cherubim | 5키(선택) | 지역별 정착 후보 선정 |

---

## 2. 키 정의

### 2.1 기반(선택) — 행성 기본 물리

| 키 | 의미 | 단위/범위 |
|----|------|-----------|
| `mass` | 행성 질량 | kg 또는 정규화값 |
| `radius` | 반지름 | m 또는 정규화값 |
| `gravity` | 표면 중력 | m/s² 또는 proxy |

→ 현재 pipeline은 이 키를 필수로 사용하지 않음. 상위 물리 레이어 연동 시 채움.

### 2.2 JOE CORE 6키 (거시 물리)

| 키 | 의미 | 단위/범위 |
|----|------|-----------|
| `sigma_plate` | 판 구조/텍토닉 proxy | [0,1] 권장 |
| `P_w` | 내부 유체 압력 proxy | — |
| `S_rot` | 자전 안정성 지표 | [0,1] |
| `W_surface` | 표면 수량 | — |
| `W_total` | 총 수량 (0이면 엔진 내부에서 1로 취급) | — |
| `dW_surface_dt_norm` | 표면 수량 변화율 정규화 | [0,1] |

→ **JOE**가 이 6키만 읽어 `planet_stress`, `instability`, `habitability_label` 산출.

### 2.3 MOE PROXY (6도메인 리스크용)

| 키 | 도메인 | 의미 |
|----|--------|------|
| `greenhouse_proxy`, `tau_atm`, `albedo_eff` | atmosphere | 온실·광학깊이·알베도 |
| `hydrology_stability_proxy`, `dW_surface_dt_norm` | water_cycle | 수순환 안정성 |
| `sigma_plate`, `heat_flux_proxy`, `volcanism_proxy` | geophysics | 판·열류·화산 |
| `strip_risk_proxy`, `B_surface_equator_proxy` | magnetosphere | 대기 제거 위험·자기장 |
| `S_rot`, `climate_variance_proxy`, `seasonality_proxy` | rotation_orbit | 자전·기후 변동·계절성 |
| `biosphere_window_score` | biosphere_window | 생물창 개방도 [0,1], 1=좋음 |

→ **MOE**가 위 키로 6도메인 `domain_scores`와 `attribution` 산출.

### 2.4 Cherubim 지역(선택)

| 키 | 의미 |
|----|------|
| `latitude_band` | 위도대 |
| `tectonic_stability_proxy` | 지역 텍토닉 안정성 |
| `water_availability_proxy` | 수 가용성 |
| `temperature_window_proxy` | 온도 구간 적합성 |
| `radiation_proxy` | 복사 환경 |

→ **Cherubim**은 스냅샷 + MOE 결과로 에덴 후보 선정. 지역 키는 다중 스냅샷/그리드 시 사용.

---

## 3. 예시 스냅샷 (최소 실행용)

```python
PlanetSnapshot = {
    # JOE CORE
    "sigma_plate": 0.1,
    "P_w": 0.5,
    "S_rot": 0.2,
    "W_surface": 1e9,
    "W_total": 1.4e9,
    "dW_surface_dt_norm": 0.0,
    # MOE PROXY
    "greenhouse_proxy": 0.6,
    "hydrology_stability_proxy": 0.3,
    "strip_risk_proxy": 0.2,
    "biosphere_window_score": 0.8,
}
```

---

## 4. 규칙

- 모든 엔진은 **동일한 snapshot dict**를 입력으로 받는다.
- 키가 없으면 각 엔진이 0 또는 기본값 처리 (에러로 중단하지 않음).
- 스키마 변경 시 이 문서와 `schema.py`를 함께 갱신한다.
