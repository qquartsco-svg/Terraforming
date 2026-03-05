# 선택 확장. 코어에 넣지 않음. 있으면 쓰고 없으면 동작하는 기능.

from __future__ import annotations

from .history_reconstruction_adapter import (
    is_available as hdr_is_available,
    reconstruct_origin_from_snapshots,
)

__all__ = ["hdr_is_available", "reconstruct_origin_from_snapshots"]
