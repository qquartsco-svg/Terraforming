# 역사 역추적(HDR) 어댑터 — 선택 기능. 코어 파이프라인과 분리.

from __future__ import annotations

"""
HistoricalDataReconstructor 연동. run_survey()에서는 호출하지 않음.
- HDR 설치 시: 흩어진 스냅샷 시퀀스 → 해시 체인 재구성 → 기원(origin) 스냅샷 반환.
- HDR 미설치 시: is_available() False, reconstruct_origin_from_snapshots() 는
  타임스탬프 기준 가장 과거 스냅샷 1건을 반환 (폴백).
"""

from typing import Any, Dict, List, Optional

_HDR_AVAILABLE = False
_origin_reconstructor: Any = None

try:
    import importlib.util
    for mod_name in ("historical_data_reconstructor", "HistoricalDataReconstructor"):
        spec = importlib.util.find_spec(mod_name)
        if spec is not None and spec.origin:
            _mod = importlib.import_module(mod_name)
            if hasattr(_mod, "reconstruct_from_scattered_data") and hasattr(_mod, "trace_back_to_origin"):
                _origin_reconstructor = _mod
                _HDR_AVAILABLE = True
                break
except Exception:
    pass


def is_available() -> bool:
    """HDR 연동 가능 여부."""
    return _HDR_AVAILABLE


def _snapshots_to_scattered(snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """스냅샷 리스트 → HDR scattered_data 형식 (content, source, timestamp)."""
    import json
    out = []
    for i, item in enumerate(snapshots):
        if "snapshot" in item:
            snap = item["snapshot"]
            ts = item.get("timestamp", float(i))
            src = item.get("source", "terraforming")
        else:
            snap = item
            ts = item.get("timestamp", float(i))
            src = "terraforming"
        out.append({
            "content": json.dumps(snap, sort_keys=True),
            "source": src,
            "timestamp": ts,
        })
    return out


def _fragment_to_snapshot(fragment: Any) -> Optional[Dict[str, Any]]:
    """HDR DataFragment 또는 dict → PlanetSnapshot dict."""
    import json
    if fragment is None:
        return None
    if isinstance(fragment, dict):
        if "snapshot" in fragment:
            return fragment["snapshot"]
        if "content" in fragment:
            try:
                return json.loads(fragment["content"])
            except Exception:
                return None
    if hasattr(fragment, "content"):
        try:
            return json.loads(getattr(fragment, "content", "{}"))
        except Exception:
            return None
    return None


def reconstruct_origin_from_snapshots(
    snapshots: List[Dict[str, Any]],
    *,
    sort_by_time: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    스냅샷 시퀀스에서 기원(origin) 스냅샷을 반환.
    - HDR 사용 가능 시: scattered_data 재구성 → trace_back_to_origin → 기원 스냅샷.
    - HDR 미사용 시: timestamp 기준 가장 과거 1건 반환 (폴백).
    각 항목: {"snapshot": dict, "timestamp": float, "source": str} 또는 snapshot dict만 있어도 됨.
    """
    if not snapshots:
        return None

    if _HDR_AVAILABLE and _origin_reconstructor is not None:
        try:
            scattered = _snapshots_to_scattered(snapshots)
            chain = _origin_reconstructor.reconstruct_from_scattered_data(scattered)
            origin = _origin_reconstructor.trace_back_to_origin(chain)
            return _fragment_to_snapshot(origin)
        except Exception:
            pass

    # 폴백: timestamp 기준 가장 과거
    def ts_key(item: Dict[str, Any]) -> float:
        if "timestamp" in item:
            return float(item["timestamp"])
        if "snapshot" in item and isinstance(item["snapshot"], dict) and "timestamp" in item["snapshot"]:
            return float(item["snapshot"]["timestamp"])
        return float("inf")

    if sort_by_time:
        ordered = sorted(snapshots, key=ts_key)
    else:
        ordered = snapshots
    first = ordered[0]
    if "snapshot" in first:
        return first["snapshot"]
    return first if isinstance(first, dict) and first else None


__all__ = ["is_available", "reconstruct_origin_from_snapshots"]
